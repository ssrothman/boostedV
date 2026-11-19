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


def _muonChecks(reco):
    p = []
    mc = reco['muonCorrections']
    regimes = {'pf': {'medium'}, 'tuneP': {'high'}, 'hybrid': {'medium', 'high'}}[mc['momentum']]
    var = mc['variation']
    if var != 'nominal':
        if not mc['apply']:
            p.append('selection/reco/muonCorrections: variation %s needs apply' % var)
        if ('high' if var.startswith('highPt') else 'medium') not in regimes:
            p.append('selection/reco/muonCorrections: variation %s has no effect with momentum %s' % (var, mc['momentum']))
    m = reco['metCorrections']
    if m['apply'] and m['muons']['propagate'] and not (mc['apply'] or mc['momentum'] != 'pf'):
        p.append('selection/reco/metCorrections/muons: propagate has no effect, the muons are not corrected '
                 '(muonCorrections apply false and momentum pf)')
    for ch, terms in reco['muonScaleFactors'].items():
        where = 'selection/reco/muonScaleFactors/%s' % ch
        if ch not in reco['channels']:
            p.append('%s: unknown channel' % where)
        elif reco['channels'][ch]['type'] == 'singleObject':
            p.append('%s: the channel selects no leptons' % where)
        elif reco['objects'].get(reco['channels'][ch]['objects'], {}).get('source', 'muons') != 'muons':
            p.append('%s: the channel does not select muons' % where)
        names = [t['name'] for t in terms]
        if len(set(names)) != len(names):
            p.append('%s: duplicate term names' % where)
        for t in terms:
            if t['regime'] not in regimes:
                p.append('%s/%s: regime %s never occurs with momentum %s' % (where, t['name'], t['regime'], mc['momentum']))
        for r in ('medium', 'high'):
            if sum(t['trigger'] and t['regime'] == r for t in terms) > 1:
                p.append('%s: more than one %s trigger term' % (where, r))
        triggered = {t['regime'] for t in terms if t['trigger']}
        if triggered and not regimes <= triggered:
            p.append('%s: trigger terms needed for every regime (%s) or none' % (where, ', '.join(sorted(regimes))))
        for t in terms:
            if t['trigger'] != bool(t['paths']):
                p.append('%s/%s: paths must be set exactly for trigger terms' % (where, t['name']))
            missing = [x for x in t['paths'] if x not in reco['channels'].get(ch, {}).get('triggers', [])]
            if missing:
                p.append('%s/%s: paths %s are not triggers of the channel' % (where, t['name'], missing))
    return p


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
    p += _muonChecks(sel['reco'])
    base = {'pt', 'eta', 'phi', 'mass', 'rawPt', 'srcIdx', 'jetId', 'nConstituents', 'jerFactor'}
    for name, c in cfg['jets']['collections'].items():
        extra = [v['name'] for v in c['table']['extraVariables'] + c.get('retag', {'variables': []})['variables']]
        where = 'jets/collections/%s/table/extraVariables' % name
        if extra and not (c['level'] == 'reco' and c['mode'] == 'pat'):
            p.append('%s: only for reco pat jets' % where)
        axisCols = {d['name'] + x for d in c.get('axes', {'definitions': []})['definitions']
                    for x in ('Pt', 'Eta', 'Phi', 'Mass', 'Status')}
        if len(set(extra)) != len(extra) or (base | axisCols) & set(extra):
            p.append('%s: duplicate or reserved column names %s' % (where, sorted((base | axisCols) & set(extra))))
    out = cfg['output']
    ak4 = [v['name'] for v in out['ak4Jets']['variables']]
    reserved = {'pt', 'eta', 'phi', 'mass', 'rawPt', 'jecFactor', 'jetId', 'srcIdx', 'jesUncTotal'}
    if len(set(ak4)) != len(ak4) or reserved & set(ak4):
        p.append('output/ak4Jets/variables: duplicate or reserved column names %s' % sorted(reserved & set(ak4)))
    if out['pileupWeights']['file'] and not out['mcEventTables']:
        p.append('output/pileupWeights: needs mcEventTables (the weights extend the Pileup table)')
    if bool(out['pileupWeights']['file']) != bool(out['pileupWeights']['key']):
        p.append('output/pileupWeights: file and key are set together or not at all')
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
    for level in ('reco', 'gen'):
        jetColls = {n: c for n, c in cfg['jets']['collections'].items() if c['level'] == level and c['mode'] != 'event'}
        for name, ch in sel[level]['channels'].items():
            if not ch['backToBack']['enabled']:
                continue
            where = 'selection/%s/channels/%s/backToBack' % (level, name)
            if ch['type'] == 'leptonMET':
                p.append('%s: not available for leptonMET channels until the W selection is refined' % where)
            if ch['type'] == 'singleObject' and ch['nMin'] < 1:
                p.append('%s: needs a triggering object (nMin >= 1)' % where)
            if name not in cfg['jets']['cleaning']['channels']:
                p.append('%s: the channel must be in jets/cleaning/channels (its jets are the non-vetoed ones)' % where)
            if len(jetColls) != 1:
                p.append('%s: needs exactly one %s jet collection, found %s' % (where, level, sorted(jetColls)))
            for n, c in jetColls.items():
                if c.get('variations'):
                    p.append('%s: not yet implemented with jet variations (jets/collections/%s); see '
                             'simulation/backToBack_plan.md' % (where, n))
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
    for name, o in cfg['observables'].items():
        bad = set(o.get('collections', [])) - set(cfg['jets']['collections'])
        if bad:
            p.append('observables/%s/collections: unknown jet collections %s' % (name, sorted(bad)))
    for name, c in cfg['jets']['collections'].items():
        if c['mode'] != 'event':
            continue
        where = 'jets/collections/%s' % name
        for k in ('variations', 'axes', 'jec', 'jerc', 'retag'):
            if c.get(k):
                p.append('%s: %s is not available for event collections' % (where, k))
        if c['translator'].get('recoilHemisphere') and not any(
                ch['backToBack']['enabled'] for ch in sel[c['level']]['channels'].values()):
            p.append('%s/translator: recoilHemisphere needs a back-to-back channel at %s level' % (where, c['level']))
        if c['level'] == 'gen' and c['translator'].get('minFromPV', -1) >= 0:
            p.append('%s/translator: minFromPV needs reco candidates (use -1 at gen level)' % where)
        if c['level'] == 'gen' and c['translator'].get('constituentDetails'):
            p.append('%s/translator: constituentDetails needs reco candidates' % where)
        if c['level'] == 'gen' and c['translator'].get('extraSrcs'):
            p.append('%s/translator: extraSrcs needs reco candidates' % where)
        notDilepton = [ch for ch in cfg['jets']['cleaning']['channels']
                       if sel[c['level']]['channels'][ch]['type'] != 'dilepton']
        if notDilepton:
            p.append('%s: the selected leptons are removed exactly only for dilepton channels; jets/cleaning/channels '
                     'has %s' % (where, notDilepton))
    for name, o in cfg['observables'].items():
        if o['weight'] == 'Charge' and (o['n'] != int(o['n']) or (o['kind'] == 'penc' and o['angle'] != 'DeltaR')):
            p.append('observables/%s: charge weights need an integer n (and angle DeltaR for penc)' % name)
        if 'axis' in o:
            if o['frame'] != 'jetAxis':
                p.append('observables/%s: axis needs frame jetAxis' % name)
            if name in cfg['aggregation']['observables']:
                p.append('observables/%s: axis observables (nominal jets only) cannot be aggregated' % name)
            for cname, c in cfg['jets']['collections'].items():
                if cname not in o.get('collections', [cname]):
                    continue
                if o['axis'] not in [d['name'] for d in c.get('axes', {'definitions': []})['definitions']]:
                    p.append('observables/%s: axis %s is not defined for jets/collections/%s' % (name, o['axis'], cname))
    tables = {}
    jetCutKeys = set(['ptMin', 'absEtaMax', 'idMask', 'minConstituents'])
    constCutKeys = set(['ptMin', 'chargedOnly', 'keepAbsPdgIds', 'dropAbsPdgIds', 'minPuppiWeight'])
    for name, c in cfg['jets']['collections'].items():
        where = 'jets/collections/%s' % name
        t = set(c['translator'])
        expect = ({'applyPuppiWeights', 'puppiValueMap', 'dropAbsPdgIds', 'absEtaMax', 'minFromPV', 'recoilHemisphere',
                   'constituentDetails', 'extraSrcs'} if c['mode'] == 'event'
                  else {'ptMin', 'algorithm', 'applyPuppiWeights', 'puppiValueMap', 'dropAbsPdgIds'} if c['mode'] == 'recluster'
                  else {'ptMin', 'applyPuppiWeights', 'puppiValueMap', 'jetId'} if c['level'] == 'reco'
                  else {'ptMin'})
        if t != expect:
            p.append('%s/translator: %s/%s needs exactly %s' % (where, c['level'], c['mode'], sorted(expect)))
        recoPat = c['level'] == 'reco' and c['mode'] == 'pat'
        if recoPat and not c['mcOnly'] and 'jerc' not in c:
            p.append('%s: reco MiniAOD jets need a jerc block (JER smearing in MC)' % where)
        if recoPat != ('jec' in c):
            p.append('%s: a jec block is needed exactly for reco MiniAOD jets' % where)
        if 'axes' in c:
            axisNames = [d['name'] for d in c['axes']['definitions']]
            if len(set(axisNames)) != len(axisNames):
                p.append('%s/axes: duplicate axis names' % where)
            corrected = any(d.get('corrected') for d in c['axes']['definitions'])
            if (c['level'] == 'reco' and corrected) != ('subjetJec' in c['axes']):
                p.append('%s/axes: subjetJec is needed exactly for reco jets with a corrected softDrop axis' % where)
            if 'subjetJer' in c['axes'] and 'subjetJec' not in c['axes']:
                p.append('%s/axes: subjetJer needs subjetJec' % where)
            if c['level'] == 'gen' and corrected:
                p.append('%s/axes: gen axes cannot be corrected' % where)
        for v, spec in c.get('variations', {}).items():
            if spec['type'] in ('jes', 'jer') and not recoPat:
                p.append('%s/variations/%s: JES/JER need reco MiniAOD jets' % (where, v))
            if spec['type'] == 'cuts':
                bad = (set(spec.get('jetCuts', {})) - jetCutKeys) | (set(spec.get('constituentCuts', {})) - constCutKeys)
                if bad:
                    p.append('%s/variations/%s: unknown cut keys %s' % (where, v, sorted(bad)))
                if spec.get('jetCuts', {}).get('minConstituents', 2) < 2:
                    p.append('%s/variations/%s: jetCuts minConstituents must be >= 2' % (where, v))
        names = [c['table']['name'] + v for v in [''] + list(c.get('variations', {}))]
        for n in names:
            if n in tables:
                p.append('%s: table name %s also produced by %s' % (where, n, tables[n]))
            tables[n] = name
    return p
