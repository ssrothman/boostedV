"""Sample registry for merged production outputs (simulation/production/merge.py writes work/<tag>/<sample>/merged/sample.json).

MC normalisation: weight = Generator_weight * xsec * lumi / genEventSumw, with genEventSumw from sample.json, which
sums the Runs tree over exactly the jobs whose NANO files are listed. Cross sections come from xsec.yaml and are never
defaulted: a sample without one can only be used unnormalised.
"""
import json
import os

import yaml

ANALYSIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(os.path.dirname(ANALYSIS), 'simulation', 'production', 'work')
XSEC = os.path.join(ANALYSIS, 'xsec.yaml')


class Sample:
    def __init__(self, name, info, xsec):
        self.name = name
        self.info = info
        self.isMC = info['isMC']
        self.files = info['nanoFiles']
        self.xsec = xsec  # pb, or None

    @property
    def sumw(self):
        return self.info['genEventSumw']

    def lumiScale(self, lumi):
        """Per-event factor multiplying Generator_weight for `lumi` in pb^-1."""
        if not self.isMC:
            return 1.0
        if self.xsec is None:
            raise ValueError('%s: no cross section in xsec.yaml' % self.name)
        return self.xsec * lumi / self.sumw

    def fileset(self):
        """coffea fileset entry."""
        return {'files': {f: 'Events' for f in self.files}, 'metadata': {'sample': self.name, 'isMC': self.isMC}}


def load(tag, names=None, work=WORK, xsecFile=XSEC):
    """Samples of a production tag that have been merged; names restricts the list."""
    with open(xsecFile) as f:
        xs = yaml.safe_load(f) or {}
    base = os.path.join(work, tag)
    out = {}
    for name in sorted(os.listdir(base)):
        path = os.path.join(base, name, 'merged', 'sample.json')
        if (names and name not in names) or not os.path.exists(path):
            continue
        with open(path) as f:
            info = json.load(f)
        out[name] = Sample(name, info, (xs.get(name) or {}).get('xsec'))
    missing = set(names or ()) - set(out)
    if missing:
        raise ValueError('not merged under %s: %s' % (tag, sorted(missing)))
    return out
