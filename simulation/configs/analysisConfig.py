"""Loads and validates an analysis configuration YAML (see default.yaml and analysis.schema.yaml)."""
import os

import jsonschema
import yaml

SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analysis.schema.yaml')


class ConfigError(ValueError):
    pass


def load(path):
    """Returns the validated configuration dict; raises ConfigError listing every problem."""
    with open(path) as f:
        cfg = yaml.safe_load(f)
    with open(SCHEMA) as f:
        schema = yaml.safe_load(f)
    errors = sorted(jsonschema.Draft7Validator(schema).iter_errors(cfg), key=lambda e: list(e.absolute_path))
    if errors:
        raise ConfigError('%s:\n' % path + '\n'.join(
            '  %s: %s' % ('/'.join(str(p) for p in e.absolute_path) or '<root>', _message(e)) for e in errors))
    problems = crossCheck(cfg)
    if problems:
        raise ConfigError('%s:\n' % path + '\n'.join('  ' + p for p in problems))
    return cfg


def _message(e):
    """For a oneOf failure, the errors of the alternative whose type/kind tag matches, if exactly one does."""
    if e.validator == 'oneOf' and e.context:
        byAlt = {}
        for c in e.context:
            byAlt.setdefault(c.relative_schema_path[0], []).append(c)
        matching = [errs for errs in byAlt.values()
                    if not any(list(c.relative_path)[:1] in (['type'], ['kind']) for c in errs)]
        if len(matching) == 1:
            return '; '.join(c.message for c in matching[0])
        return jsonschema.exceptions.best_match(e.context).message
    return e.message


def crossCheck(cfg):
    """Checks between sections that the schema cannot express; returns a list of problems."""
    p = []
    sel, obs = cfg['selection'], cfg['observables']
    for level in ('reco', 'gen'):
        objects = sel[level]['objects']
        for name, ch in sel[level]['channels'].items():
            for o in [ch['objects']] + ch.get('vetoes', []):
                if o not in objects:
                    p.append('selection/%s/channels/%s: unknown object collection %s' % (level, name, o))
    dressing = sel['reco']['dressing']['mode']
    for name, o in sel['reco']['objects'].items():
        if o['dressedCut'] and (dressing == 'none' or o['source'] == 'photons'):
            p.append('selection/reco/objects/%s: dressedCut applies only to dressed leptons (dressing mode %s, source %s)'
                     % (name, dressing, o['source']))
    if set(sel['reco']['objects']) & set(sel['gen']['objects']):
        p.append('selection: object labels used at both levels: %s'
                 % sorted(set(sel['reco']['objects']) & set(sel['gen']['objects'])))
    # Reco jets are cleaned against reco objects and gen jets against gen objects, so both levels need the channels.
    for c in cfg['jets']['cleaning']['channels']:
        for level in ('reco', 'gen'):
            if c not in sel[level]['channels']:
                p.append('jets/cleaning/channels: channel %s missing at %s level' % (c, level))
    agg = cfg['aggregation']
    for c in agg['channels']:
        for level in sel['levels']:
            if c not in sel[level]['channels']:
                p.append('aggregation/channels: channel %s missing at %s level' % (c, level))
    for o in agg['observables']:
        if o not in obs:
            p.append('aggregation/observables: unknown observable %s' % o)
        elif obs[o]['output'] == 'Unbinned':
            p.append('aggregation/observables: %s is unbinned' % o)
    for name, o in obs.items():
        binned = o['output'] != 'Unbinned'
        if binned and 'axes' not in o:
            p.append('observables/%s: binned output needs axes' % name)
        if not binned and 'axes' in o:
            p.append('observables/%s: unbinned output takes no axes' % name)
        if binned and set(o['table']) - {'weightPrecision'}:
            p.append('observables/%s/table: coordNames/coordPrecision are for unbinned outputs only' % name)
        if not binned:
            D = 1 if o['kind'] == 'penc' else 2
            if len(o['table'].get('coordNames', [])) != D or 'coordPrecision' not in o['table']:
                p.append('observables/%s/table: unbinned output needs %d coordNames and coordPrecision' % (name, D))
    tables = {}
    jetCutKeys = set(['ptMin', 'absEtaMax', 'idMask', 'minConstituents'])
    constCutKeys = set(['ptMin', 'chargedOnly', 'keepAbsPdgIds', 'dropAbsPdgIds', 'minPuppiWeight'])
    for name, c in cfg['jets']['collections'].items():
        where = 'jets/collections/%s' % name
        t = set(c['translator'])
        expect = ({'ptMin', 'algorithm', 'applyPuppiWeights', 'puppiValueMap', 'dropAbsPdgIds'} if c['mode'] == 'recluster'
                  else {'ptMin', 'applyPuppiWeights', 'puppiValueMap', 'jetIdVersion'} if c['level'] == 'reco'
                  else {'ptMin'})
        if t != expect:
            p.append('%s/translator: %s/%s needs exactly %s' % (where, c['level'], c['mode'], sorted(expect)))
        recoPat = c['level'] == 'reco' and c['mode'] == 'pat'
        if recoPat and not c['mcOnly'] and 'jerc' not in c:
            p.append('%s: reco MiniAOD jets need a jerc block (JER smearing in MC)' % where)
        for v, spec in c.get('variations', {}).items():
            if spec['type'] in ('jes', 'jer') and not recoPat:
                p.append('%s/variations/%s: JES/JER need reco MiniAOD jets' % (where, v))
            if spec['type'] == 'cuts':
                bad = (set(spec.get('jetCuts', {})) - jetCutKeys) | (set(spec.get('constituentCuts', {})) - constCutKeys)
                if bad:
                    p.append('%s/variations/%s: unknown cut keys %s' % (where, v, sorted(bad)))
        names = [c['table']['name'] + v for v in [''] + list(c.get('variations', {}))]
        for n in names:
            if n in tables:
                p.append('%s: table name %s also produced by %s' % (where, n, tables[n]))
            tables[n] = name
    return p
