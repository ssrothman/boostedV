"""Loads and validates the production manifest (samples.yaml, schema samples.schema.yaml)."""
import os
import re
import sys

import jsonschema
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIGS = os.path.join(os.path.dirname(HERE), 'configs')
SCHEMA = os.path.join(HERE, 'samples.schema.yaml')
sys.path.insert(0, CONFIGS)
import analysisConfig  # noqa: E402

TAG_RE = re.compile(r'^\d{8}_[A-Za-z0-9-]+$')
# GT embedded in a central MC processed-dataset name, e.g. Run3Summer22EEMiniAODv4-130X_mcRun3_..._v6-v3
MC_GT_RE = re.compile(r'-(?:[A-Za-z0-9]+_)?(\d+X_mc\w+?)(?:_ext\d+)?-v\d+$')


class ManifestError(ValueError):
    pass


def load(path):
    """Returns the validated manifest with config/lumiMask/fileList made absolute; raises ManifestError."""
    with open(path) as f:
        man = yaml.safe_load(f)
    with open(SCHEMA) as f:
        schema = yaml.safe_load(f)
    errors = sorted(jsonschema.Draft7Validator(schema).iter_errors(man), key=lambda e: list(e.absolute_path))
    if errors:
        raise ManifestError('%s:\n' % path + '\n'.join(
            '  %s: %s' % ('/'.join(str(p) for p in e.absolute_path) or '<root>', e.message) for e in errors))
    base = os.path.dirname(os.path.abspath(path))
    problems = []
    for name, s in man['samples'].items():
        s['config'] = os.path.join(base, s['config'])
        if s['lumiMask']:
            s['lumiMask'] = os.path.join(base, s['lumiMask'])
        if 'fileList' in s['input']:
            s['input']['fileList'] = os.path.join(base, s['input']['fileList'])
        problems += ['samples/%s: %s' % (name, p) for p in _check(s)]
    if problems:
        raise ManifestError('%s:\n' % path + '\n'.join('  ' + p for p in problems))
    return man


def _check(s):
    p = []
    if s['isMC'] and s['lumiMask']:
        p.append('lumiMask is for data only')
    if not s['isMC'] and not s['lumiMask']:
        p.append('data needs a lumiMask')
    if s['lumiMask'] and not os.path.isfile(s['lumiMask']):
        p.append('lumiMask %s not found' % s['lumiMask'])
    if s['backend'] == 'condor' and s['splitting']['mode'] != 'files':
        p.append('condor supports only files splitting')
    if 'fileList' in s['input']:
        if s['backend'] != 'condor':
            p.append('fileList input needs the condor backend')
        if not os.path.isfile(s['input']['fileList']):
            p.append('fileList %s not found' % s['input']['fileList'])
    try:
        cfg = analysisConfig.load(s['config'])
        if not s['isMC'] and 'reco' not in cfg['selection']['levels']:
            p.append('data with selection levels %s, which need gen' % cfg['selection']['levels'])
    except (analysisConfig.ConfigError, OSError) as e:
        p.append('config: %s' % e)
    return p


def datasetGlobalTag(dataset):
    """The GT in a central MC dataset name, or None (data and private names carry none)."""
    m = MC_GT_RE.search(dataset.split('/')[2])
    return m.group(1) if m else None


def checkTag(tag):
    if not TAG_RE.match(tag):
        raise ManifestError('tag %r is not YYYYMMDD_<desc>' % tag)
    return tag
