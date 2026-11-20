"""Tests of the YAML configuration (run inside cmsenv): python3 -m unittest -v test_analysisConfig"""
import copy
import importlib
import os
import sys
import tempfile
import unittest

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analysisConfig  # noqa: E402

DEFAULT = os.path.join(HERE, 'default.yaml')
CFG = os.path.join(HERE, 'eecNano_cfg.py')
PACKAGES = ('EECs', 'JetSetup', 'EventSelection')


def loadDefault():
    with open(DEFAULT) as f:
        return yaml.safe_load(f)


def writeTmp(cfg):
    f = tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False)
    yaml.safe_dump(cfg, f)
    f.close()
    return f.name


TEST_GT = '130X_mcRun3_2022_realistic_postEE_v6'


def buildProcess(cfgDict=None, isMC=1, extra=('globalTag=' + TEST_GT,)):
    """Executes eecNano_cfg.py with the given configuration and returns its process."""
    path = writeTmp(cfgDict) if cfgDict is not None else DEFAULT
    argv = sys.argv
    sys.argv = [CFG, 'config=' + path, 'isMC=%d' % isMC] + list(extra)
    try:
        g = {'__name__': '__cfg__'}
        with open(CFG) as f:
            exec(compile(f.read(), CFG, 'exec'), g)
        return g['process']
    finally:
        sys.argv = argv


def labels(vtags):
    """Module labels of a VInputTag, whose entries may be InputTags or 'label:instance' strings."""
    return [t.getModuleLabel() if hasattr(t, 'getModuleLabel') else t.split(':')[0] for t in vtags]


def describedDefaults(moduleType):
    """The module type's fillDescriptions PSet (generated cfi), or None if the type is not ours."""
    for pkg in PACKAGES:
        try:
            mod = importlib.import_module('SRothman.%s.%s' % (pkg, moduleType))
        except ImportError:
            continue
        return getattr(mod, moduleType)()
    return None


class LoaderRejects(unittest.TestCase):
    def assertRejected(self, mutate, *fragments):
        cfg = loadDefault()
        mutate(cfg)
        with self.assertRaises(analysisConfig.ConfigError) as ctx:
            analysisConfig.load(writeTmp(cfg))
        for frag in fragments:
            self.assertIn(frag, str(ctx.exception))

    def test_event_table_checks(self):
        out = lambda c: c['output']
        self.assertRejected(lambda c: out(c).update(mcEventTables=False), 'output/pileupWeights: needs mcEventTables')
        self.assertRejected(lambda c: out(c)['pileupWeights'].update(key=''), 'file and key are set together')
        self.assertRejected(lambda c: out(c).update(rhoTable=['fixedGridRhoNope']), 'output/rhoTable')
        self.assertRejected(lambda c: out(c)['metTables'].update(met='slimmedMETs'), 'output/metTables')
        self.assertRejected(lambda c: c['inputs'].pop('pileupInfo'), 'inputs', 'pileupInfo')

    def test_jet_extension_checks(self):
        tab = lambda c, n: c['jets']['collections'][n]['table']
        extra = lambda c: tab(c, 'Reco')['extraVariables']
        self.assertRejected(lambda c: tab(c, 'Gen').update(extraVariables=[dict(extra(c)[0])]),
                            'jets/collections/Gen/table/extraVariables: only for reco pat jets')
        self.assertRejected(lambda c: extra(c)[1].update(name='jecPt'), 'duplicate or reserved column names')
        self.assertRejected(lambda c: extra(c)[1].update(name='jerFactor'), "reserved column names ['jerFactor']")
        self.assertRejected(lambda c: extra(c)[1].update(type='double'), 'jets/collections/Reco/table/extraVariables/1')

    def test_ak4_checks(self):
        ak4 = lambda c: c['output']['ak4Jets']
        self.assertRejected(lambda c: ak4(c)['variables'][0].update(name='jecFactor'), 'output/ak4Jets/variables: duplicate or reserved')
        self.assertRejected(lambda c: ak4(c).update(name='ak4'), 'output/ak4Jets')
        self.assertRejected(lambda c: ak4(c)['jec'].pop('dataKey'), 'output/ak4Jets/jec', 'dataKey')

    def test_min_constituents(self):
        jc = lambda c, n: c['jets']['collections'][n]['jetCuts']
        self.assertRejected(lambda c: jc(c, 'Reco').update(minConstituents=1), 'jets/collections/Reco/jetCuts')
        self.assertRejected(lambda c: jc(c, 'Gen').update(minConstituents=0), 'jets/collections/Gen/jetCuts')
        self.assertRejected(lambda c: c['jets']['collections']['Reco']['variations'].update(
            Tight={'type': 'cuts', 'jetCuts': dict(jc(c, 'Reco'), minConstituents=1),
                   'constituentCuts': c['jets']['collections']['Reco']['constituentCuts']}), 'variations/Tight: jetCuts minConstituents must be >= 2')

    def test_jec_only_on_reco_pat_jets(self):
        self.assertRejected(lambda c: c['jets']['collections']['Reco'].pop('jec'),
                            'a jec block is needed exactly for reco MiniAOD jets')
        self.assertRejected(lambda c: c['jets']['collections']['Gen'].update(jec=c['jets']['collections']['Reco']['jec']),
                            'jets/collections/Gen: a jec block is needed exactly for reco MiniAOD jets')

    def test_axis_checks(self):
        sd = {'name': 'axisSoftDrop', 'type': 'softDrop', 'beta': 0.0, 'zcut': 0.1, 'R0': 0.8, 'corrected': True}
        jec = {'correctionFile': 'f', 'mcKey': 'k', 'dataKey': 'k', 'rho': 'fixedGridRhoFastjetAll'}
        def axes(c, recoDefs, genDefs, recoJec=True):
            c['jets']['collections']['Reco']['axes'] = dict({'definitions': recoDefs}, **({'subjetJec': jec} if recoJec else {}))
            c['jets']['collections']['Gen']['axes'] = {'definitions': genDefs}
        gen = dict(sd, corrected=False)
        self.assertRejected(lambda c: axes(c, [sd], [gen], recoJec=False), 'Reco/axes: subjetJec is needed exactly')
        self.assertRejected(lambda c: axes(c, [sd], [sd]), 'Gen/axes: gen axes cannot be corrected')
        self.assertRejected(lambda c: axes(c, [sd, sd], [gen]), 'Reco/axes: duplicate axis names')
        self.assertRejected(lambda c: axes(c, [dict(sd, name='softDrop')], [gen]), 'jets/collections/Reco/axes')
        def e1cAxis(c, frame='jetAxis', agg=False):
            axes(c, [sd], [gen])
            c['observables']['E1CSD'] = dict(c['observables']['E1C'], axis='axisSoftDrop', frame=frame)
            if agg:
                c['aggregation']['observables'].append('E1CSD')
        self.assertRejected(lambda c: e1cAxis(c, frame='jetHelicity'), 'observables/E1CSD: axis needs frame jetAxis')
        self.assertRejected(lambda c: e1cAxis(c, agg=True), 'axis observables (nominal jets only) cannot be aggregated')
        def missingOnGen(c):
            e1cAxis(c)
            c['jets']['collections']['Gen']['axes'] = {'definitions': [dict(gen, name='axisOther')]}
        self.assertRejected(missingOnGen, 'axis axisSoftDrop is not defined for jets/collections/Gen')
        cfg = loadDefault()
        e1cAxis(cfg)
        analysisConfig.load(writeTmp(cfg))   # the valid combination loads

    def test_default_is_valid(self):
        analysisConfig.load(DEFAULT)

    def test_unknown_keys(self):
        self.assertRejected(lambda c: c.update(extra=1), 'Additional properties')
        self.assertRejected(lambda c: c['selection']['reco']['channels']['Zmumu'].update(massMinn=81.0),
                            'selection/reco/channels/Zmumu', 'massMinn')
        self.assertRejected(lambda c: c['jets']['collections']['Reco']['jetCuts'].update(etaMax=2.0),
                            'jets/collections/Reco', 'etaMax')
        self.assertRejected(lambda c: c['observables']['E2C'].update(bins=3), 'observables/E2C', 'bins')

    def test_missing_keys(self):
        self.assertRejected(lambda c: c['selection']['reco']['channels']['Zmumu'].pop('massMin'),
                            'selection/reco/channels/Zmumu', 'massMin')
        self.assertRejected(lambda c: c['selection']['gen']['channels']['Zee'].pop('pairPtMin'),
                            'selection/gen/channels/Zee', 'pairPtMin')
        self.assertRejected(lambda c: c['jets']['collections']['Reco']['jerc'].pop('jesKey'),
                            'jets/collections/Reco/jerc', 'jesKey')
        self.assertRejected(lambda c: c.pop('aggregation'), 'aggregation')

    def test_muon_corrections_schema(self):
        self.assertRejected(lambda c: c['selection']['reco']['muonCorrections'].update(variation='scaleUpp'),
                            'selection/reco/muonCorrections')
        self.assertRejected(lambda c: c['selection']['reco']['muonCorrections'].update(resolutionVariationK='java'),
                            'selection/reco/muonCorrections')
        self.assertRejected(lambda c: c['selection']['reco']['muonCorrections'].pop('highPtThreshold'),
                            'selection/reco/muonCorrections', 'highPtThreshold')

    def test_high_pt_and_scale_factor_schema(self):
        mc = lambda c: c['selection']['reco']['muonCorrections']
        sfs = lambda c: c['selection']['reco']['muonScaleFactors']
        self.assertRejected(lambda c: mc(c).update(momentum='global'), 'selection/reco/muonCorrections')
        self.assertRejected(lambda c: mc(c)['highPt'].update(era='2024'), 'selection/reco/muonCorrections/highPt')
        self.assertRejected(lambda c: mc(c)['highPt'].update(kappaTarget='both'), 'selection/reco/muonCorrections/highPt')
        self.assertRejected(lambda c: mc(c)['highPt'].pop('ptMin'), 'selection/reco/muonCorrections/highPt', 'ptMin')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][0].pop('outOfRange'), 'selection/reco/muonScaleFactors/Zmumu/0')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][0].update(name='id_1'), 'selection/reco/muonScaleFactors/Zmumu/0')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][0].update(regime='low'), 'selection/reco/muonScaleFactors/Zmumu/0')
        self.assertRejected(lambda c: sfs(c).update(Zmumu=[]), 'selection/reco/muonScaleFactors/Zmumu')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][2].pop('paths'), 'selection/reco/muonScaleFactors/Zmumu/2')
        self.assertRejected(lambda c: c['inputs'].pop('triggerObjects'), 'inputs', 'triggerObjects')

    def test_muon_cross_checks(self):
        mc = lambda c: c['selection']['reco']['muonCorrections']
        sfs = lambda c: c['selection']['reco']['muonScaleFactors']
        self.assertRejected(lambda c: mc(c).update(variation='scaleUp'), 'variation scaleUp needs apply')
        met = lambda c: c['selection']['reco']['metCorrections']
        self.assertRejected(lambda c: met(c)['muons'].update(propagate=True), 'propagate has no effect')
        self.assertRejected(lambda c: met(c).pop('xy'), 'selection/reco/metCorrections', 'xy')
        self.assertRejected(lambda c: mc(c).update(apply=True, variation='highPtScaleUp'),
                            'variation highPtScaleUp has no effect with momentum pf')
        self.assertRejected(lambda c: mc(c).update(apply=True, momentum='tuneP', variation='resolutionUp'),
                            'variation resolutionUp has no effect with momentum tuneP')
        self.assertRejected(lambda c: sfs(c).update(Zmm=sfs(c)['Zmumu']), 'muonScaleFactors/Zmm: unknown channel')
        self.assertRejected(lambda c: sfs(c).update(Zee=sfs(c)['Zmumu']), 'muonScaleFactors/Zee: the channel does not select muons')
        self.assertRejected(lambda c: sfs(c).update(Hadronic=sfs(c)['Zmumu']), 'muonScaleFactors/Hadronic: the channel selects no leptons')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][1].update(name='id'), 'muonScaleFactors/Zmumu: duplicate term names')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][0].update(regime='high'), 'Zmumu/id: regime high never occurs with momentum pf')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][1].update(trigger=True), 'more than one medium trigger term')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][0].update(paths=['HLT_IsoMu24_v*']),
                            'Zmumu/id: paths must be set exactly for trigger terms')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][2].update(paths=[]), 'Zmumu/trig: paths must be set exactly for trigger terms')
        self.assertRejected(lambda c: sfs(c)['Zmumu'][2].update(paths=['HLT_IsoMu24_v*', 'HLT_Mu50_v*']),
                            "Zmumu/trig: paths ['HLT_Mu50_v*'] are not triggers of the channel")

        def hybridMediumTriggerOnly(c):
            mc(c)['momentum'] = 'hybrid'
            sfs(c)['Zmumu'] = sfs(c)['Zmumu'] + [dict(sfs(c)['Zmumu'][0], name='highId', regime='high')]
        self.assertRejected(hybridMediumTriggerOnly, 'Zmumu: trigger terms needed for every regime (high, medium) or none')

        def tuneP(c):
            mc(c)['momentum'] = 'tuneP'
        self.assertRejected(tuneP, 'regime medium never occurs with momentum tuneP')

    def test_levels_and_gen_schema(self):
        self.assertRejected(lambda c: c['selection'].update(levels=[]), 'selection/levels')
        self.assertRejected(lambda c: c['selection'].update(levels=['reco', 'reco']), 'selection/levels')
        self.assertRejected(lambda c: c['selection'].update(levels=['particle']), 'selection/levels')
        self.assertRejected(lambda c: c['selection']['gen']['channels']['Zmumu'].update(triggers=['HLT_IsoMu24_v*']),
                            'selection/gen/channels/Zmumu', 'triggers')
        self.assertRejected(lambda c: c['selection']['gen']['objects']['genTightMuons'].update(source='muons'),
                            'selection/gen/objects/genTightMuons')
        self.assertRejected(lambda c: c['selection']['gen']['particleLevel'].pop('lepConeSize'),
                            'selection/gen/particleLevel', 'lepConeSize')

    def test_dressing_config(self):
        self.assertRejected(lambda c: c['selection']['reco']['objects']['tightMuons'].update(dressedCut='pt > 15'),
                            'dressedCut applies only to dressed leptons (dressing mode none')

        def photonDressedCut(c):
            c['selection']['reco']['dressing']['mode'] = 'cone'
            c['selection']['reco']['objects']['tightPhotons']['dressedCut'] = 'pt > 230'
        self.assertRejected(photonDressedCut, 'tightPhotons: dressedCut applies only to dressed leptons')
        self.assertRejected(lambda c: c['selection']['reco']['dressing'].update(mode='rivet'), 'selection/reco/dressing')
        self.assertRejected(lambda c: c['selection']['reco']['objects']['tightMuons'].pop('dressedCut'),
                            'selection/reco/objects/tightMuons', 'dressedCut')

    def test_wrong_types_and_values(self):
        self.assertRejected(lambda c: c['selection']['reco']['channels']['Zmumu'].update(massMin='71'), 'selection/reco/channels/Zmumu')
        self.assertRejected(lambda c: c['observables']['E2C'].update(N=7), 'observables/E2C')
        self.assertRejected(lambda c: c['observables']['E2C'].update(weight='Mass'), 'observables/E2C')
        self.assertRejected(lambda c: c['observables']['E2C'].update(weight='Charge', angle='Angle3D'),
                            'observables/E2C: charge weights need an integer n')
        self.assertRejected(lambda c: c['observables']['E2C'].update(weight='Charge', n=1.5),
                            'observables/E2C: charge weights need an integer n')
        self.assertRejected(lambda c: c['observables']['E2C'].update(weight='ChargePt'), 'observables/E2C')
        self.assertRejected(lambda c: c['selection']['reco']['channels']['Zmumu'].pop('vetoes'),
                            'selection/reco/channels/Zmumu')
        self.assertRejected(lambda c: c['jets']['collections']['Reco']['variations']['TrkDrop'].update(
            dropProbability=1.5), 'jets/collections/Reco/variations/TrkDrop')

    def test_cross_references(self):
        self.assertRejected(lambda c: c['selection']['reco']['channels']['Zmumu'].update(objects='tightMuon'),
                            'unknown object collection tightMuon')
        self.assertRejected(lambda c: c['jets']['cleaning']['channels'].append('Zmm'), 'channel Zmm missing at reco level')
        self.assertRejected(lambda c: c['aggregation']['channels'].append('Ztautau'), 'channel Ztautau missing at reco level')
        self.assertRejected(lambda c: c['selection']['gen']['channels'].pop('Zee'), 'channel Zee missing at gen level')
        self.assertRejected(lambda c: c['selection']['gen']['channels']['Zmumu'].update(objects='tightMuons'),
                            'selection/gen/channels/Zmumu: unknown object collection tightMuons')

        def sharedLabel(c):
            c['selection']['gen']['objects']['tightMuons'] = c['selection']['gen']['objects'].pop('genTightMuons')
            c['selection']['gen']['channels']['Zmumu']['objects'] = 'tightMuons'
            c['selection']['gen']['channels']['Wmunu']['objects'] = 'tightMuons'
        self.assertRejected(sharedLabel, 'object labels used at both levels')

        def unbinned(c):
            c['observables']['E2C']['output'] = 'Unbinned'
            del c['observables']['E2C']['axes']
            c['observables']['E2C']['table'].update(coordNames=['dR'], coordPrecision=-1)
        self.assertRejected(unbinned, 'aggregation/observables: E2C is unbinned')

        def re3c(c, nAxes=3, coordNames=None):
            o = {'kind': 'resolvedE3C', 'n': 1.0, 'weight': 'Pt', 'angle': 'DeltaR', 'norm': 'jetPt',
                 'output': 'Dense' if coordNames is None else 'Unbinned', 'table': {'weightPrecision': -1}}
            if coordNames is None:
                o['axes'] = [{'type': 'regular', 'nbins': 4, 'lo': 0.0, 'hi': 1.0}] * nAxes
            else:
                o['table'].update(coordNames=coordNames, coordPrecision=-1)
            c['observables']['RE3C'] = o
        cfg = loadDefault()
        re3c(cfg)
        analysisConfig.load(writeTmp(cfg))
        re3c(cfg, coordNames=['RL', 'xi', 'phi'])
        analysisConfig.load(writeTmp(cfg))
        self.assertRejected(lambda c: re3c(c, nAxes=2), 'observables/RE3C')
        self.assertRejected(lambda c: re3c(c, coordNames=['RL', 'xi']), 'unbinned output needs 3 coordNames')

        def genJES(c):
            c['jets']['collections']['Gen']['variations'] = {'JESUp': {'type': 'jes', 'direction': 'up'}}
        self.assertRejected(genJES, 'JES/JER need reco MiniAOD jets')

        def recluster(c):
            c['jets']['collections']['Reco']['mode'] = 'recluster'
            c['jets']['collections']['Reco'].pop('variations')
        self.assertRejected(recluster, 'jets/collections/Reco/translator')

        def dupTable(c):
            c['jets']['collections']['Gen']['table']['name'] = 'RecoJet'
        self.assertRejected(dupTable, 'table name RecoJet')


class BuiltProcess(unittest.TestCase):
    def assertNoHiddenDefaults(self, process):
        checked = 0
        for label, mod in list(process.producers_().items()) + list(process.filters_().items()) + \
                list(process.analyzers_().items()):
            ref = describedDefaults(mod.type_())
            if ref is None:
                continue
            checked += 1
            tracked = [n for n in ref.parameterNames_() if getattr(ref, n).isTracked()]
            missing = set(tracked) - set(mod.parameterNames_())
            self.assertFalse(missing, '%s (%s) relies on fillDescriptions defaults for %s' % (label, mod.type_(), sorted(missing)))
            for name in ref.parameterNames_():
                kind = type(getattr(ref, name)).__name__
                if kind == 'VPSet' and len(getattr(ref, name)):
                    for a in getattr(mod, name):
                        self.assertEqual(set(a.parameterNames_()), set(getattr(ref, name)[0].parameterNames_()),
                                         '%s.%s entry is incomplete' % (label, name))
                elif kind == 'PSet':
                    self.assertEqual(set(getattr(mod, name).parameterNames_()), set(getattr(ref, name).parameterNames_()),
                                     '%s.%s is incomplete' % (label, name))
        return checked

    def test_no_hidden_defaults_mc(self):
        self.assertGreater(self.assertNoHiddenDefaults(buildProcess(isMC=1)), 200)

    def test_no_hidden_defaults_data(self):
        p = buildProcess(isMC=0)
        self.assertGreater(self.assertNoHiddenDefaults(p), 40)
        self.assertFalse(hasattr(p, 'jetsGenRaw'))           # mcOnly collection skipped
        self.assertFalse(hasattr(p, 'jetsRecoJESUp'))        # variations are MC only
        self.assertFalse(hasattr(p, 'jetsRecoJER'))          # no JER smearing in data
        self.assertEqual(p.Zmumu_reco_eecRecoE2C.genEventInfo.getModuleLabel(), '')
        self.assertFalse(hasattr(p, 'genParticleLevel'))     # no gen level in data
        self.assertFalse(hasattr(p, 'Zmumu_gen_eecRecoE2C'))
        self.assertEqual(labels(p.anySelected.srcs), ['anyChannel'])

    def test_global_tag(self):
        for isMC, gt in ((1, TEST_GT), (0, '130X_dataRun3_PromptAnalysis_v1')):
            p = buildProcess(isMC=isMC, extra=('globalTag=' + gt,))
            self.assertEqual(p.GlobalTag.globaltag.value(), gt)
        with self.assertRaisesRegex(analysisConfig.ConfigError, 'globalTag is required'):
            buildProcess(extra=())

    def test_lumi_mask(self):
        self.assertFalse(hasattr(buildProcess().source, 'lumisToProcess'))
        mask = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False)
        mask.write('{"360458": [[215, 215], [236, 237]], "360459": [[6, 6]]}')
        mask.close()
        p = buildProcess(isMC=0, extra=('globalTag=x', 'lumiMask=' + mask.name))
        self.assertEqual(list(p.source.lumisToProcess),
                         ['360458:215', '360458:236-360458:237', '360459:6'])

    def test_gen_only_in_data_is_an_error(self):
        cfg = loadDefault()
        cfg['selection']['levels'] = ['gen']
        with self.assertRaises(analysisConfig.ConfigError):
            buildProcess(cfg, isMC=0)

    def test_levels_select_written_events_and_aggregation(self):
        for levels in (['reco'], ['gen'], ['reco', 'gen']):
            cfg = loadDefault()
            cfg['selection']['levels'] = levels
            p = buildProcess(cfg)
            anyFlags = labels(p.anySelected.srcs)
            self.assertEqual(anyFlags, [{'reco': 'anyChannel', 'gen': 'genAnyChannel'}[l] for l in levels])
            self.assertEqual(list(p.out.SelectEvents.SelectEvents), ['anySelectedPath'])
            for level in ('reco', 'gen'):
                self.assertEqual(hasattr(p, 'Zmumu_%s_eecGenE2C' % level), level in levels)
                self.assertEqual(hasattr(p, 'Zmumu_%s_AggPath' % level), level in levels)
            # Both levels are always evaluated in MC, so their flags and objects exist whatever `levels` is.
            self.assertTrue(hasattr(p, 'genZmumuSel') and hasattr(p, 'ZmumuSel'))
            self.assertEqual(labels(p.genZmumuFilter.srcs), ['genZmumu'])

    def test_dressing_modules(self):
        p = buildProcess()
        self.assertEqual(p.tightMuons.type_(), 'PATMuonSelector')
        self.assertFalse(hasattr(p, 'tightMuonsDressed') or hasattr(p, 'leptonFSRphotons'))
        for mode in ('fsr', 'cone'):
            cfg = loadDefault()
            reco = cfg['selection']['reco']
            reco['dressing']['mode'] = mode
            reco['objects']['tightMuons'].update(cut="abs(eta) < 2.4 && passed('CutBasedIdTight')", dressedCut='pt > 15')
            p = buildProcess(cfg)
            self.assertNoHiddenDefaults(p)
            self.assertEqual(p.tightMuonsUndressed.type_(), 'PATMuonSelector')
            self.assertEqual(p.tightMuonsUndressed.cut.value(), "abs(eta) < 2.4 && passed('CutBasedIdTight')")
            self.assertEqual(p.tightMuonsDressed.type_(), 'DressedLeptonProducer')
            self.assertEqual(p.tightMuonsDressed.mode.value(), mode)
            self.assertEqual(p.tightMuonsDressed.originals.getModuleLabel(), 'correctedMuons')  # made for the MC SFs
            self.assertEqual(p.tightMuonsDressed.fsrIndex.getProductInstanceLabel(), 'muFsrIndex')
            self.assertEqual(p.tightElectronsDressed.fsrIndex.getProductInstanceLabel(), 'eleFsrIndex')
            self.assertEqual(p.tightMuons.type_(), 'CandPtrSelector')
            self.assertEqual(p.tightMuons.cut.value(), 'pt > 15')
            self.assertEqual(p.tightPhotons.type_(), 'PATPhotonSelector')      # photons are never dressed
            self.assertEqual(hasattr(p, 'leptonFSRphotons'), mode == 'fsr')
            self.assertEqual(p.tightMuonsDressed.coneSize.value(), reco['dressing']['cone']['coneSize'])

    def test_muon_corrections(self):
        # Default: PF momentum, no corrections; correctedMuons exists in MC only, for the scale factors.
        p = buildProcess()
        self.assertEqual(p.correctedMuons.momentum.value(), 'pf')
        self.assertFalse(p.correctedMuons.applyCorrections.value())
        self.assertEqual(p.tightMuons.src.getModuleLabel(), 'correctedMuons')
        p = buildProcess(isMC=0)
        self.assertFalse(hasattr(p, 'correctedMuons'))
        self.assertEqual(p.tightMuons.src.getModuleLabel(), 'slimmedMuons')
        cfg = loadDefault()
        reco = cfg['selection']['reco']
        reco['muonCorrections'].update(apply=True, variation='resolutionUp', resolutionVariationK='python',
                                       highPtThreshold=1e9)
        reco['dressing']['mode'] = 'fsr'
        p = buildProcess(cfg)
        self.assertNoHiddenDefaults(p)
        c = p.correctedMuons
        self.assertEqual(c.type_(), 'MuonCorrectionProducer')
        self.assertTrue(c.applyCorrections.value())
        self.assertEqual(c.src.getModuleLabel(), 'slimmedMuons')
        self.assertFalse(c.isData.value())
        self.assertEqual(c.variation.value(), 'resolutionUp')
        self.assertEqual(c.resolutionVariationK.value(), 'python')
        self.assertEqual(c.highPtThreshold.value(), 1e9)
        for consumer in (p.tightMuonsUndressed.src, p.vetoMuonsUndressed.src, p.leptonFSRphotons.muons,
                         p.tightMuonsDressed.originals):
            self.assertEqual(consumer.getModuleLabel(), 'correctedMuons')
        self.assertEqual(p.tightElectronsUndressed.src.getModuleLabel(), 'slimmedElectrons')
        # Data: scale correction only, and variations are refused.
        reco['muonCorrections']['variation'] = 'nominal'
        self.assertTrue(buildProcess(cfg, isMC=0).correctedMuons.isData.value())
        reco['muonCorrections']['variation'] = 'scaleUp'
        with self.assertRaises(analysisConfig.ConfigError):
            buildProcess(cfg, isMC=0)

    def test_high_pt_muons_and_scale_factors(self):
        from SRothman.EventSelection.muonHighPtRun3_cff import ERAS
        cfg = loadDefault()
        reco = cfg['selection']['reco']
        reco['muonCorrections'].update(apply=True, momentum='hybrid', regimeThreshold=150.0, variation='highPtResolution',
                                       highPt={'era': '2023preBPix', 'ptMin': 180.0, 'kappaTarget': 'data'})
        high = dict(reco['muonScaleFactors']['Zmumu'][0], name='highId', regime='high')
        highTrig = dict(reco['muonScaleFactors']['Zmumu'][2], name='highTrig', regime='high')
        reco['muonScaleFactors'] = {'Zmumu': reco['muonScaleFactors']['Zmumu'] + [high, highTrig]}
        p = buildProcess(cfg)
        self.assertNoHiddenDefaults(p)
        c = p.correctedMuons
        self.assertEqual((c.momentum.value(), c.regimeThreshold.value(), c.variation.value()),
                         ('hybrid', 150.0, 'highPtResolution'))
        self.assertEqual(list(c.highPt.kappa), ERAS['2023preBPix']['kappa'])
        self.assertEqual(list(c.highPt.sigmaEndcap), ERAS['2023preBPix']['sigmaEndcap'])
        self.assertEqual((c.highPt.ptMin.value(), c.highPt.kappaTarget.value(), c.highPt.smearEndcap.value()),
                         (180.0, 'data', 0.46))
        sf = p.ZmumuMuonSFTable
        self.assertEqual(sf.type_(), 'MuonSFProducer')
        self.assertEqual((sf.src.getModuleLabel(), sf.src.getProductInstanceLabel()), ('ZmumuSel', 'leptons'))
        self.assertEqual(sf.muons.getModuleLabel(), 'correctedMuons')
        self.assertEqual(sf.name.value(), 'ZmumuMuonSF')
        self.assertEqual([(t.name.value(), t.regime.value(), t.trigger.value()) for t in sf.terms],
                         [('id', 'medium', False), ('iso', 'medium', False), ('trig', 'medium', True), ('highId', 'high', False),
                          ('highTrig', 'high', True)])
        self.assertEqual([list(t.paths) for t in sf.terms], [[], [], ['HLT_IsoMu24_v*'], [], ['HLT_IsoMu24_v*']])
        self.assertEqual((sf.triggerResults.getModuleLabel(), sf.triggerResults.getProcessName()), ('TriggerResults', 'HLT'))
        self.assertEqual(sf.triggerObjects.getModuleLabel(), 'slimmedPatTrigger')
        self.assertFalse(hasattr(p, 'WmunuMuonSFTable'))
        self.assertEqual(labels(p.Zmumu_reco_eecRecoE2C.weights), ['ZmumuMuonSFTable'])
        self.assertEqual(labels(p.Zmumu_gen_eecRecoE2C.weights), [])
        self.assertEqual(labels(p.Zee_reco_eecRecoE2C.weights), [])
        # Data: no scale factors, no weights; the regime and the kappa_b on data still apply.
        reco['muonCorrections']['variation'] = 'nominal'
        p = buildProcess(cfg, isMC=0)
        self.assertFalse(hasattr(p, 'ZmumuMuonSFTable'))
        self.assertEqual(labels(p.Zmumu_reco_eecRecoE2C.weights), [])
        self.assertTrue(p.correctedMuons.isData.value())

    def test_selected_lepton_and_met_tables(self):
        p = buildProcess()
        for level, prefix, met in (('reco', '', 'metXY'), ('gen', 'Gen', 'genParticleLevel')):
            lab = lambda ch: ('gen' + ch if level == 'gen' else ch)
            for ch in ('Zmumu', 'Zee', 'Wmunu', 'Wenu'):
                t = getattr(p, lab(ch) + 'LeptonsTable')
                self.assertEqual((t.src.getModuleLabel(), t.src.getProductInstanceLabel()), (lab(ch) + 'Sel', 'leptons'))
                self.assertEqual(t.name.value(), prefix + ch + 'Leptons')
                self.assertEqual(sorted(t.variables.parameterNames_()), ['charge', 'eta', 'mass', 'pdgId', 'phi', 'pt'])
                self.assertIn(lab(ch) + 'LeptonsTable', p.outPath.moduleNames())
            for ch in ('Hadronic', 'GammaJets'):
                self.assertFalse(hasattr(p, lab(ch) + 'LeptonsTable'))
            m = getattr(p, 'genSelectionMetTable' if level == 'gen' else 'selectionMetTable')
            self.assertEqual((m.src.getModuleLabel(), m.name.value(), m.singleton.value()), (met, prefix + 'SelectionMET', True))
            self.assertEqual(m.src.getModuleLabel(), getattr(p, lab('Wmunu') + 'Sel').met.getModuleLabel())
        cfg = loadDefault()
        for level in ('reco', 'gen'):
            chans = cfg['selection'][level]['channels']
            for ch in [c for c in chans if chans[c]['type'] == 'leptonMET']:
                del chans[ch]
        cfg['selection']['reco']['muonScaleFactors'].pop('Wmunu')
        cfg['jets']['cleaning']['channels'] = ['Zmumu', 'Zee', 'GammaJets']
        cfg['jets']['cleaning']['channels'] = ['Zmumu', 'Zee', 'GammaJets']
        p = buildProcess(cfg)
        self.assertFalse(hasattr(p, 'selectionMetTable') or hasattr(p, 'genSelectionMetTable'))
        self.assertTrue(hasattr(p, 'ZmumuLeptonsTable'))

    def test_event_tables(self):
        p = buildProcess()
        for name, src in (('MET', 'slimmedMETs'), ('PuppiMET', 'slimmedMETsPuppi')):
            t, r = getattr(p, 'met%sTable' % name), getattr(p, 'met%sRawTable' % name)
            self.assertEqual((t.src.getModuleLabel(), t.name.value(), r.name.value()), (src, name, 'Raw' + name))
            self.assertIn('ptJESUp', t.variables.parameterNames_())
            self.assertIn('ptUnclusteredUp', t.variables.parameterNames_())
            self.assertEqual(r.variables.pt.expr.value(), 'uncorPt')
        self.assertEqual(p.genMetTable.name.value(), 'GenMET')
        self.assertEqual(p.vertexTable.goodPvCut.value(), '!isFake && ndof > 4.0 && abs(z) <= 24.0 && position.Rho <= 2.0')
        self.assertEqual(p.vertexTable.svSrc.getModuleLabel(), 'slimmedSecondaryVertices')
        self.assertEqual(p.genVertexT0Table.variables.t0.src.getProductInstanceLabel(), 't0')
        self.assertEqual(len(p.rhoTable.variables.parameterNames_()), 6)
        self.assertEqual(p.genParticleTable.src.getModuleLabel(), 'finalGenParticles')
        self.assertEqual(p.finalGenParticles.src.getModuleLabel(), 'prunedGenParticles')
        pu = p.pileupWeightTable
        self.assertEqual((pu.name.value(), pu.extension.value(), pu.key.value()),
                         ('Pileup', True, 'Collisions2022_359022_362760_eraEFG_GoldenJson'))
        for m in ('metMETTable', 'metPuppiMETRawTable', 'vertexTable', 'svCandidateTable', 'genVertexTable', 'rhoTable',
                  'genParticleTable', 'pileupWeightTable'):
            self.assertIn(m, p.outPath.moduleNames())
        d = buildProcess(isMC=0)
        self.assertTrue(hasattr(d, 'metMETTable') and hasattr(d, 'vertexTable') and hasattr(d, 'rhoTable'))
        for m in ('genMetTable', 'genVertexTable', 'genParticleTable', 'pileupWeightTable'):
            self.assertFalse(hasattr(d, m), m)
        cfg = loadDefault()
        cfg['output'].update(metTables={'PuppiMET': 'slimmedMETsPuppi'}, vertexTables=False, rhoTable=['fixedGridRhoAll'],
                             genParticles=False, pileupWeights={'file': '', 'key': ''})
        p = buildProcess(cfg)
        self.assertFalse(any(hasattr(p, m) for m in ('metMETTable', 'vertexTable', 'genVertexTable', 'genParticleTable',
                                                      'pileupWeightTable')))
        self.assertEqual(p.rhoTable.variables.parameterNames_(), ['fixedGridRhoAll'])

    def test_jet_extension_table(self):
        p = buildProcess()
        t = p.jetsRecoExtTable
        self.assertEqual((t.type_(), t.src.getModuleLabel(), t.jets.getModuleLabel(), t.name.value()),
                         ('EECJetExtensionTableProducer', 'jetsReco', 'jetsRecoJEC', 'RecoJet'))
        names = [v.name.value() for v in t.variables]
        self.assertEqual(len(names), 43)
        for n in ('jecPt', 'area', 'msoftdrop', 'tau2', 'particleNetWithMass_WvsQCD', 'hadronFlavour'):
            self.assertIn(n, names)
        self.assertIn('jetsRecoExtTable', p.outPath.moduleNames())
        self.assertEqual([l for l in p.producers_() if l.startswith('jets') and l.endswith('ExtTable')], ['jetsRecoExtTable'])
        d = buildProcess(isMC=0)
        dn = [v.name.value() for v in d.jetsRecoExtTable.variables]
        self.assertEqual(len(dn), 39)
        self.assertNotIn('hadronFlavour', dn)

    def test_object_extension_tables(self):
        p = buildProcess()
        for ch, typ, objects, table, n in (('Zmumu', 'Muon', 'correctedMuons', 'ZmumuLeptons', 11),
                                           ('Zee', 'Electron', 'slimmedElectrons', 'ZeeLeptons', 6),
                                           ('Wmunu', 'Muon', 'correctedMuons', 'WmunuLeptons', 11),
                                           ('GammaJets', 'Photon', 'slimmedPhotons', 'GammaJetsObjects', 8)):
            t = getattr(p, ch + 'ObjectsExtTable')
            self.assertEqual((t.type_(), t.objects.getModuleLabel(), t.name.value(), len(t.variables)),
                             (typ + 'ExtensionTableProducer', objects, table, n))
            self.assertEqual(list(t.triggerPaths), list(getattr(p, ch + 'Trigger').paths))
            self.assertIn(ch + 'ObjectsExtTable', p.outPath.moduleNames())
        self.assertFalse(any(l.startswith('gen') and l.endswith('ObjectsExtTable') for l in p.producers_()))
        # Muons are matched to correctedMuons when it exists (MC: made for the SFs), otherwise to the MiniAOD muons.
        self.assertEqual(buildProcess(isMC=0).ZmumuObjectsExtTable.objects.getModuleLabel(), 'slimmedMuons')
        cfg = loadDefault()
        cfg['selection']['reco']['muonCorrections'].update(apply=True)
        self.assertEqual(buildProcess(cfg, isMC=0).ZmumuObjectsExtTable.objects.getModuleLabel(), 'correctedMuons')

    def test_ak4_jets(self):
        p = buildProcess()
        c, t = p.ak4JetsCorrected, p.ak4JetTable
        self.assertEqual((c.type_(), c.src.getModuleLabel(), c.key.value(), c.uncKey.value()),
                         ('PATJetJECProducer', 'slimmedJetsPuppi', 'Summer22EE_22Sep2023_V4_MC_L1L2L3Res_AK4PFPuppi',
                          'Summer22EE_22Sep2023_V4_MC_Total_AK4PFPuppi'))
        self.assertEqual((t.src.getModuleLabel(), t.name.value(), t.cut.value()), ('ak4JetsCorrected', 'AK4Jet', 'pt > 20 && abs(eta) < 4.7'))
        names = t.variables.parameterNames_()
        for n in ('pt', 'rawPt', 'jecFactor', 'jesUncTotal', 'jetId', 'srcIdx', 'btagDeepFlavB', 'btagPNetB',
                  'btagRobustParTAK4B', 'hadronFlavour'):
            self.assertIn(n, names)
        self.assertIn('ak4JetTable', p.outPath.moduleNames())
        d = buildProcess(isMC=0)
        self.assertEqual(d.ak4JetsCorrected.key.value(), 'Summer22EE_22Sep2023_V4_DATA_L1L2L3Res_AK4PFPuppi')
        self.assertNotIn('hadronFlavour', d.ak4JetTable.variables.parameterNames_())
        cfg = loadDefault()
        cfg['output']['ak4Jets']['jec']['uncKey'] = ''
        self.assertNotIn('jesUncTotal', buildProcess(cfg).ak4JetTable.variables.parameterNames_())
        cfg['output']['ak4Jets']['enabled'] = False
        self.assertFalse(hasattr(buildProcess(cfg), 'ak4JetTable'))

    def test_met_corrections(self):
        r = loadDefault()['selection']['reco']['metCorrections']
        t, x = r['type1'], r['xy']
        for isMC in (1, 0):
            p = buildProcess(isMC=isMC)
            m, xy, jec = p.metType1, p.metXY, p.metType1Jets
            self.assertEqual((jec.type_(), jec.src.getModuleLabel(), jec.key.value(), jec.sortByPt.value()),
                             ('PATJetJECProducer', 'slimmedJetsPuppi', t['mcKey' if isMC else 'dataKey'], False))
            self.assertEqual((m.type_(), m.met.getModuleLabel(), m.jets.getModuleLabel(), m.jecSource.value(),
                              m.l1Key.value(), m.key.value(), m.applyJER.value(), m.ptMin.value(), m.absEtaMax.value(),
                              m.emFractionMax.value()),
                             ('PATMETType1Producer', 'slimmedMETsPuppi', 'metType1JetsJer' if isMC else 'metType1Jets',
                              'correctionlib', t['l1McKey' if isMC else 'l1DataKey'], t['mcKey' if isMC else 'dataKey'],
                              bool(isMC), 15.0, 5.2, 0.9))
            self.assertEqual(m.muons.getModuleLabel(), 'slimmedMuons')
            self.assertEqual(hasattr(p, 'metType1JetsJer'), bool(isMC))
            if isMC:
                j = p.metType1JetsJer
                self.assertEqual((j.src.getModuleLabel(), j.type.value(), j.direction.value(), j.jetR.value(),
                                  j.genJets.getModuleLabel(), j.jerResolutionKey.value()),
                                 ('metType1Jets', 'jer', 'nominal', 0.4, 'slimmedGenJets', t['jer']['resolutionKey']))
            self.assertEqual((xy.type_(), xy.met.getModuleLabel(), xy.metType.value(), xy.epoch.value(), xy.isData.value(),
                              xy.vertices.getModuleLabel(), xy.ndofMin.value()),
                             ('PATMETXYCorrectionProducer', 'metType1', x['metType'], x['epoch'], not isMC,
                              'offlineSlimmedPrimaryVertices', 4.0))
            self.assertEqual(p.WmunuSel.met.getModuleLabel(), 'metXY')
            self.assertEqual(p.WenuSel.met.getModuleLabel(), 'metXY')
            self.assertFalse(hasattr(p, 'correctedMET'))
        # Switches: JER, XY, muon propagation, the whole correction.
        cfg = loadDefault()
        cfg['selection']['reco']['metCorrections']['type1']['jer']['enabled'] = False
        cfg['selection']['reco']['metCorrections']['xy']['enabled'] = False
        p = buildProcess(cfg)
        self.assertFalse(hasattr(p, 'metType1JetsJer') or hasattr(p, 'metXY'))
        self.assertEqual((p.metType1.applyJER.value(), p.metType1.jets.getModuleLabel(), p.WmunuSel.met.getModuleLabel()),
                         (False, 'metType1Jets', 'metType1'))
        cfg = loadDefault()
        mc = cfg['selection']['reco']['muonCorrections']
        mc['apply'] = True
        cfg['selection']['reco']['metCorrections']['muons']['propagate'] = True
        p = buildProcess(cfg)
        c = p.correctedMET
        self.assertEqual((c.type_(), c.met.getModuleLabel(), c.original.getModuleLabel(), c.corrected.getModuleLabel()),
                         ('PATMETMuonShiftProducer', 'metXY', 'slimmedMuons', 'correctedMuons'))
        self.assertEqual(p.WmunuSel.met.getModuleLabel(), 'correctedMET')
        cfg['selection']['reco']['metCorrections']['apply'] = False
        p = buildProcess(cfg)
        self.assertFalse(any(hasattr(p, n) for n in ('metType1', 'metType1Jets', 'metXY', 'correctedMET')))
        self.assertEqual(p.WmunuSel.met.getModuleLabel(), 'slimmedMETsPuppi')

    def test_event_cleaning(self):
        cfg = loadDefault()
        r = cfg['selection']['reco']
        for isMC, key in ((1, 'mcKey'), (0, 'dataKey')):
            p = buildProcess(isMC=isMC)
            j, f, e = p.jetVetoMapJets, p.jetVetoMapFlag, p.ecalBadCalibFlag
            v = r['jetVetoMap']
            self.assertEqual((j.type_(), j.src.getModuleLabel(), j.key.value(), j.jetIdFile.value(), j.jetIdType.value()),
                             ('PATJetJECProducer', 'slimmedJetsPuppi', v['jec'][key], v['jetId']['correctionFile'],
                              'AK4PUPPI'))
            self.assertEqual((f.type_(), f.src.getModuleLabel(), f.key.value(), f.mapType.value(), f.ptMin.value(),
                              f.emFractionMax.value(), f.idMask.value()),
                             ('JetVetoMapFlagProducer', 'jetVetoMapJets', 'Summer22EE_23Sep2023_RunEFG_V1', 'jetvetomap',
                              15.0, 0.9, 2))
            self.assertEqual((e.type_(), list(e.baddetEcal), e.ecalMinEt.value(), e.taggingMode.value(),
                              e.EcalRecHitSource.value()),
                             ('EcalBadCalibFilter', [838871812], 50.0, True, 'reducedEgamma:reducedEBRecHits'))
            t = dict(zip(p.selectionFlagsTable.names, labels(p.selectionFlagsTable.srcs)))
            self.assertEqual((t['jetVetoMap'], t['ecalBadCalib']), ('jetVetoMapFlag', 'ecalBadCalibFlag'))
            self.assertIn('jetVetoMapFlag', labels(p.Zmumu.srcs))
            self.assertTrue(hasattr(p, 'CaloGeometryBuilder') or hasattr(p, 'caloGeometryBuilder') or
                            any('CaloGeometry' in n for n in p.es_producers_()))
        from Configuration.Eras.Modifier_run3_common_cff import run3_common
        from Configuration.Eras.Modifier_run3_nanoAOD_pre142X_cff import run3_nanoAOD_pre142X
        self.assertTrue(p.isUsingModifier(run3_common) and p.isUsingModifier(run3_nanoAOD_pre142X))
        r['ecalBadCalib']['crystals'] = []
        p = buildProcess(cfg)
        self.assertFalse(hasattr(p, 'ecalBadCalibFlag'))
        self.assertNotIn('ecalBadCalibFlag', labels(p.Zmumu.srcs))
        self.assertNotIn('ecalBadCalib', list(p.selectionFlagsTable.names))
        # Jet ID from the JME correctionlib file for the EEC jets and the AK4 table.
        p = buildProcess()
        self.assertEqual((p.jetsRecoRaw.jetIdFile.value(), p.jetsRecoRaw.jetIdType.value()),
                         (cfg['jets']['collections']['Reco']['translator']['jetId']['correctionFile'], 'AK8PUPPI'))
        self.assertEqual(p.ak4JetsCorrected.jetIdType.value(), 'AK4PUPPI')

    def test_ak8_jec(self):
        p = buildProcess()
        c = p.jetsRecoJEC
        self.assertEqual((c.type_(), c.src.getModuleLabel(), c.key.value(), c.uncKey.value(), c.sortByPt.value()),
                         ('PATJetJECProducer', 'slimmedJetsAK8', 'Summer22EE_22Sep2023_V4_MC_L1L2L3Res_AK8PFPuppi', '', False))
        # MC: JEC -> JER on the pat::Jets -> translator; data: no JER.
        self.assertEqual((p.jetsRecoJER.type_(), p.jetsRecoJER.src.getModuleLabel(), p.jetsRecoJER.type.value()),
                         ('PATJetJERCProducer', 'jetsRecoJEC', 'jer'))
        self.assertEqual(p.jetsRecoRaw.src.getModuleLabel(), 'jetsRecoJER')
        # Variations: JES on the corrected pat::Jets, then the nominal JER, then their own translator.
        self.assertEqual((p.jetsRecoJESUpJES.type.value(), p.jetsRecoJESUpJES.direction.value(),
                          p.jetsRecoJESUpJES.src.getModuleLabel()), ('jes', 'up', 'jetsRecoJEC'))
        self.assertEqual((p.jetsRecoJESUpJER.direction.value(), p.jetsRecoJESUpJER.src.getModuleLabel()),
                         ('nominal', 'jetsRecoJESUpJES'))
        self.assertEqual(p.jetsRecoJESUpRaw.src.getModuleLabel(), 'jetsRecoJESUpJER')
        self.assertEqual((p.jetsRecoJERUpJER.direction.value(), p.jetsRecoJERUpJER.src.getModuleLabel()),
                         ('up', 'jetsRecoJEC'))
        self.assertFalse(hasattr(p, 'jetsGenJEC'))
        self.assertEqual(p.ak4JetsCorrected.sortByPt.value(), True)
        d = buildProcess(isMC=0)
        self.assertEqual(d.jetsRecoJEC.key.value(), 'Summer22EE_22Sep2023_V4_DATA_L1L2L3Res_AK8PFPuppi')
        self.assertEqual(d.jetsRecoRaw.src.getModuleLabel(), 'jetsRecoJEC')
        self.assertFalse(hasattr(d, 'jetsRecoJER'))

    def test_lhe_tables(self):
        p = buildProcess()
        t = p.lheInfoTable
        self.assertEqual(t.type_(), 'LHETablesProducer')
        self.assertEqual(labels(t.lheInfo), ['externalLHEProducer', 'source'])
        self.assertTrue(t.storeLHEParticles.value())
        self.assertEqual(t.precision.value(), 14)
        self.assertIn('lheInfoTable', p.outPath.moduleNames())
        self.assertFalse(hasattr(buildProcess(isMC=0), 'lheInfoTable'))
        cfg = loadDefault()
        cfg['output']['lheTables'] = False
        self.assertFalse(hasattr(buildProcess(cfg), 'lheInfoTable'))

    def test_default_scale_factors(self):
        p = buildProcess()
        for ch in ('Zmumu', 'Wmunu'):
            sf = getattr(p, ch + 'MuonSFTable')
            self.assertEqual([t.key.value() for t in sf.terms],
                             ['NUM_TightID_DEN_TrackerMuons', 'NUM_TightPFIso_DEN_TightID',
                              'NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight'])
        self.assertEqual(labels(p.Zmumu_reco_eecRecoE2C.weights), ['ZmumuMuonSFTable'])

    def test_jets_cleaned_against_own_level(self):
        p = buildProcess()
        chans = ['Zmumu', 'Zee', 'Wmunu', 'Wenu', 'GammaJets']
        # Jets are not removed; every jet table (nominal and variations) gets per-channel veto flags.
        self.assertEqual(list(p.jetsReco.vetoSrcs), [])
        for jets, prefix, table in (('jetsReco', '', 'RecoJet'), ('jetsRecoJESUp', '', 'RecoJetJESUp'), ('jetsGen', 'gen', 'GenJet')):
            v = getattr(p, jets + 'VetoTable')
            self.assertEqual((v.src.getModuleLabel(), list(v.channels), v.name.value(), v.vetoDR.value()), (jets, chans, table, 0.8))
            self.assertEqual(labels(v.vetoSrcs), [prefix + c + 'Sel' for c in chans])
            self.assertIn(jets + 'VetoTable', p.outPath.moduleNames())
        # Channel X's aggregators skip the jets vetoed by X only.
        for ch in ('Zmumu', 'Zee'):
            for level in ('reco', 'gen'):
                for obs, jets in (('RecoE2C', 'jetsReco'), ('RecoJESUpE3C', 'jetsRecoJESUp'), ('GenE1C', 'jetsGen')):
                    m = getattr(p, '%s_%s_eec%s' % (ch, level, obs)).jetMask
                    self.assertEqual((m.getModuleLabel(), m.getProductInstanceLabel()), (jets + 'VetoTable', ch))
        cfg = loadDefault()
        cfg['jets']['cleaning']['channels'] = ['GammaJets']
        p2 = buildProcess(cfg)
        self.assertEqual(p2.Zmumu_reco_eecRecoE2C.jetMask.getModuleLabel(), '')
        self.assertEqual(list(p2.jetsRecoVetoTable.channels), ['GammaJets'])
        self.assertEqual(p.genWmunuSel.met.getModuleLabel(), 'genParticleLevel')
        self.assertEqual(p.genWmunuSel.met.getProductInstanceLabel(), 'mets')
        self.assertEqual(p.WmunuSel.met.getModuleLabel(), 'metXY')

    def test_yaml_values_reach_modules(self):
        cfg = loadDefault()
        cfg['selection']['reco']['channels']['Zmumu']['massMin'] = 81.0
        cfg['selection']['gen']['channels']['Zee']['pairPtMin'] = 120.0
        cfg['jets']['collections']['Reco']['jetCuts']['ptMin'] = 250.0
        cfg['jets']['collections']['Reco']['variations']['TrkDrop']['dropProbability'] = 0.05
        cfg['observables']['E2C']['axes'][0]['nbins'] = 40
        cfg['aggregation']['channels'] = ['Wmunu']
        p = buildProcess(cfg)
        self.assertEqual(p.ZmumuSel.massMin.value(), 81.0)
        self.assertEqual(labels(p.ZmumuSel.vetoSrcs), ['vetoMuons', 'vetoElectrons'])
        self.assertEqual(labels(p.genZeeSel.vetoSrcs), ['genVetoMuons', 'genVetoElectrons'])
        self.assertEqual(p.ZeeSel.massMin.value(), 71.0)
        self.assertEqual(p.ZmumuSel.pairPtMin.value(), 0.0)
        self.assertEqual(p.genZeeSel.pairPtMin.value(), 120.0)
        self.assertEqual(p.ZeeSel.pairPtMin.value(), 0.0)
        self.assertEqual(p.jetsReco.ptMin.value(), 250.0)
        self.assertEqual(p.jetsRecoJESUp.ptMin.value(), 250.0)
        self.assertEqual(p.jetsGen.ptMin.value(), 200.0)
        self.assertEqual(p.jetsRecoTrkDropVar.dropProbability.value(), 0.05)
        self.assertEqual(p.eecRecoE2C.axes[0].nbins.value(), 40)
        self.assertEqual(p.eecRecoE2CTable.axes[0].nbins.value(), 40)
        self.assertEqual(p.Wmunu_reco_eecRecoE2C.axes[0].nbins.value(), 40)
        self.assertTrue(hasattr(p, 'Wmunu_reco_AggPath') and hasattr(p, 'Wmunu_gen_AggPath'))
        self.assertFalse(hasattr(p, 'Zmumu_reco_AggPath'))

    def test_default_matches_previous_hardcoded_setup(self):
        # The values that used to be hard-coded in the python helpers, now coming from default.yaml.
        p = buildProcess()
        self.assertEqual(list(p.metFilterFlag.paths)[0], 'Flag_goodVertices')
        self.assertEqual(p.ZmumuSel.leadPtMin.value(), 26.0)
        self.assertEqual(p.ZeeSel.leadPtMin.value(), 35.0)
        self.assertEqual(p.WenuSel.ptMin.value(), 35.0)
        self.assertEqual(p.HadronicSel.nMax.value(), 0)
        self.assertEqual(p.jetsRecoRaw.ptMin.value(), 180.0)
        self.assertEqual(p.jetsRecoJER.jerScaleFactorKey.value(), 'Summer22EE_22Sep2023_JRV2_MC_ScaleFactor_AK8PFPuppi')
        self.assertEqual(p.jetsRecoJERUpJER.jerScaleFactorUncertaintyKey.value(),
                         'Summer22EE_22Sep2023_JRV2_MC_SFUncertainty_AK8PFPuppi')
        self.assertEqual(p.jetsRecoTrkDropVar.seedSalt.value(), 1)
        self.assertEqual(p.jetsRecoJER.seedSalt.value(), 0)


def enableBackToBack(cfg, channels=('Zmumu',), levels=('reco', 'gen')):
    for level in levels:
        for ch in channels:
            cfg['selection'][level]['channels'][ch]['backToBack'].update(enabled=True)
    return cfg


class BackToBack(unittest.TestCase):
    """selection/<level>/channels/<ch>/backToBack (simulation/backToBack_plan.md)."""

    def assertRejected(self, mutate, *fragments):
        LoaderRejects.assertRejected(self, mutate, *fragments)

    def test_checks(self):
        noVar = lambda c: c['jets']['collections']['Reco'].update(variations={})
        # Allowed: dilepton and single-object channels with cleaning and no jet variations.
        cfg = enableBackToBack(loadDefault(), ['Zmumu', 'GammaJets'])
        noVar(cfg)
        analysisConfig.load(writeTmp(cfg))
        self.assertRejected(lambda c: enableBackToBack(c), 'channels/Zmumu/backToBack', 'jet variations')
        self.assertRejected(lambda c: (noVar(c), enableBackToBack(c, ['Wmunu'])), 'channels/Wmunu/backToBack',
                            'leptonMET')
        self.assertRejected(lambda c: (noVar(c), enableBackToBack(c, ['Hadronic'])), 'channels/Hadronic/backToBack',
                            'nMin >= 1')
        self.assertRejected(lambda c: (noVar(c), enableBackToBack(c, ['Zee']), c['jets']['cleaning']['channels'].remove('Zee')),
                            'channels/Zee/backToBack', 'jets/cleaning/channels')
        self.assertRejected(lambda c: (noVar(c), enableBackToBack(c), c['jets']['collections'].update(
            Reco2=dict(c['jets']['collections']['Reco'], table=dict(c['jets']['collections']['Reco']['table'], name='R2')))),
                            'needs exactly one reco jet collection')
        self.assertRejected(lambda c: c['selection']['gen']['channels']['Zee'].pop('backToBack'),
                            'selection/gen/channels/Zee', 'backToBack')
        self.assertRejected(lambda c: c['selection']['reco']['channels']['Zee']['backToBack'].update(dPhiMin=4.0),
                            'selection/reco/channels/Zee')
        self.assertRejected(lambda c: c['selection']['reco']['channels']['Zee']['backToBack'].pop('extraJetAlphaMax'),
                            'selection/reco/channels/Zee')
        self.assertRejected(lambda c: c['selection']['reco'].pop('extraJets'), 'selection/reco', 'extraJets')
        self.assertRejected(lambda c: c['selection']['gen'].pop('extraJets'), 'selection/gen', 'extraJets')

    def test_wiring(self):
        cfg = enableBackToBack(loadDefault(), levels=('reco',))
        cfg['jets']['collections']['Reco'].update(variations={})
        cfg['selection']['reco']['channels']['Zmumu']['backToBack'].update(dPhiMin=2.5, asymmetryMax=0.4)
        p = buildProcess(cfg)
        b = p.jetsRecoBackToBackZmumu
        self.assertEqual((b.dPhiMin.value(), b.asymmetryMax.value()), (2.5, 0.4))
        self.assertEqual(b.extraJetAlphaMax.value(), -1.0)
        cfg['selection']['reco']['channels']['Zmumu']['backToBack'].update(extraJetAlphaMax=0.3)
        cfg['selection']['reco']['extraJets'].update(dRJet=1.1, dRLepton=0.3, ptMin=25.0, absEtaMax=2.5)
        p2 = buildProcess(cfg)
        b2 = p2.jetsRecoBackToBackZmumu
        self.assertEqual((b2.extraJetAlphaMax.value(), b2.extraJets.value(), b2.extraJetDRJet.value(),
                          b2.extraJetDRLepton.value(), b2.extraJetPtMin.value(), b2.extraJetAbsEtaMax.value()),
                         (0.3, 'extraJets', 1.1, 0.3, 25.0, 2.5))
        # Reco extra jets: JEC (with jet ID bits), nominal JER in MC, then the ID mask.
        self.assertEqual(p2.extraJets.src.value(), 'extraJetsJER')
        self.assertEqual(p2.extraJetsJER.src.value(), 'extraJetsJEC')
        self.assertEqual(p2.extraJetsJEC.src.value(), cfg['selection']['reco']['extraJets']['src'])
        self.assertEqual(p2.extraJets.cut.value(), "userInt('jetId') == 2 || userInt('jetId') == 3 || "
                         "userInt('jetId') == 6 || userInt('jetId') == 7")
        self.assertEqual((b.src.value(), b.flag.value(), b.objects.value(), b.vetoFlags.value()),
                         ('jetsReco', 'ZmumuSel', 'ZmumuSel:boson', 'jetsRecoOverlap:Zmumu'))
        # Jets without constituents are seen before the jet selection, with the nominal pt, eta and ID cuts.
        jc = cfg['jets']['collections']['Reco']['jetCuts']
        self.assertEqual((b.emptyJets.value(), b.vetoObjects.value(), b.vetoDR.value()),
                         ('jetsRecoRaw', 'ZmumuSel:leptons', cfg['jets']['collections']['Reco']['cleaningDR']))
        self.assertEqual((b.ptMin.value(), b.absEtaMax.value(), b.idMask.value()), (jc['ptMin'], jc['absEtaMax'], jc['idMask']))
        self.assertTrue(p.jetsRecoRaw.allowNoDaughters.value())
        self.assertEqual(list(p.jetsRecoOverlap.channels), ['Zmumu'])
        self.assertEqual(p.jetsRecoB2B.src.value(), 'jetsReco')
        # Only the reco Zmumu channel flag gains the back-to-back requirement; Zee and the gen level are unchanged.
        clean = ['goodVertexFlag', 'metFilterFlag', 'ecalBadCalibFlag', 'jetVetoMapFlag']
        self.assertEqual(labels(p.Zmumu.srcs), ['ZmumuTrigger'] + clean + ['ZmumuSel', 'jetsRecoBackToBackZmumu'])
        self.assertEqual(labels(p.Zee.srcs), ['ZeeTrigger'] + clean + ['ZeeSel'])
        self.assertEqual(labels(p.genZmumu.srcs), ['genZmumuSel'])
        self.assertEqual(sorted(labels(p.anyChannel.srcs)), sorted(['Zmumu', 'Zee', 'Wmunu', 'Wenu', 'Hadronic',
                                                                    'GammaJets']))
        names, srcs = list(p.selectionFlagsTable.names), labels(p.selectionFlagsTable.srcs)
        self.assertEqual(dict(zip(names, srcs))['ZmumuB2B'], 'jetsRecoBackToBackZmumu')
        self.assertNotIn('ZeeB2B', names)
        self.assertNotIn('ZmumuB2B', list(p.genSelectionFlagsTable.names))
        self.assertFalse(hasattr(p, 'jetsGenB2B'))
        # Reco jets after the selection feed the tables, the EECs and the aggregators; the pre-selection table is not
        # written ('*Table' labels only).
        for m in ('jetsRecoB2BTable', 'jetsRecoB2BExtTable', 'jetsRecoB2BVetoTable', 'jetsRecoB2BFlagTable', 'eecRecoE2C'):
            self.assertEqual(getattr(p, m).src.value(), 'jetsRecoB2B')
        self.assertFalse(hasattr(p, 'jetsRecoTable'))
        self.assertEqual(p.Zmumu_reco_eecRecoE2C.jetMask.value(), 'jetsRecoB2BVetoTable:Zmumu')
        self.assertIn('ZmumuFilter', p.Zmumu_reco_AggPath.moduleNames())
        self.assertEqual(labels(p.ZmumuFilter.srcs), ['Zmumu'])

    def test_extra_jets_levels(self):
        # Gen: the gen jets directly; data: no JER step.
        cfg = enableBackToBack(loadDefault())
        cfg['jets']['collections']['Reco'].update(variations={})
        for lev in ('reco', 'gen'):
            cfg['selection'][lev]['channels']['Zmumu']['backToBack'].update(extraJetAlphaMax=0.0)
        p = buildProcess(cfg)
        self.assertEqual(p.jetsGenBackToBackZmumu.extraJets.value(), cfg['selection']['gen']['extraJets']['src'])
        self.assertEqual(p.jetsRecoBackToBackZmumu.extraJets.value(), 'extraJets')
        pd = buildProcess(cfg, isMC=0)
        self.assertEqual(pd.extraJets.src.value(), 'extraJetsJEC')
        self.assertFalse(hasattr(pd, 'extraJetsJER'))



def addEventCollections(cfg):
    """Back-to-back Zmumu (no jet variations) plus jet-free collections: reco charged-PV, reco PUPPI recoil hemisphere,
    gen; E3C restricted to the AK8 collections. The names sort after Reco and Gen (writeTmp sorts keys), so a jet-free
    collection that wrongly set the channels' back-to-back flags would override the AK8 one."""
    enableBackToBack(cfg)
    cfg['jets']['collections']['Reco'].update(variations={})
    cfg['jets']['cleaning']['channels'] = ['Zmumu', 'Zee']
    base = dict(mcOnly=False, jetCuts=dict(ptMin=0.0, absEtaMax=1e9, idMask=0, minConstituents=2), cleaningDR=0.0)
    tr = dict(applyPuppiWeights=False, puppiValueMap='', dropAbsPdgIds=[], absEtaMax=2.4, minFromPV=2,
              recoilHemisphere=False, constituentDetails=False, extraSrcs=[])
    cc = dict(ptMin=0.0, chargedOnly=True, keepAbsPdgIds=[], dropAbsPdgIds=[], minPuppiWeight=0.0)
    table = lambda n: dict(name=n, precision=-1, extraVariables=[])
    cfg['jets']['collections'].update(
        RecoEvtCh=dict(base, level='reco', mode='event', src='packedPFCandidates',
                       translator=dict(tr, constituentDetails=True, extraSrcs=['lostTracks']), constituentCuts=cc,
                       table=table('RecoEvtCh')),
        RecoEvtPuppiHemi=dict(base, level='reco', mode='event', src='packedPFCandidates',
                          translator=dict(tr, applyPuppiWeights=True, minFromPV=-1, recoilHemisphere=True),
                          constituentCuts=dict(cc, chargedOnly=False), table=table('RecoEvtPuppiHemi')),
        GenEvt=dict(base, level='gen', mode='event', mcOnly=True, src='packedGenParticles',
                    translator=dict(tr, minFromPV=-1, dropAbsPdgIds=[12, 14, 16]), constituentCuts=cc,
                    table=table('GenEvt')))
    cfg['observables']['E3C']['collections'] = ['Reco', 'Gen']
    return cfg


class EventCollections(unittest.TestCase):
    """Jet-free collections (mode event; simulation/jetFreeEEC_plan.md)."""

    def assertRejected(self, mutate, *fragments):
        LoaderRejects.assertRejected(self, lambda c: (addEventCollections(c), mutate(c)), *fragments)

    def test_checks(self):
        analysisConfig.load(writeTmp(addEventCollections(loadDefault())))   # one AK8 collection per level still
        coll = lambda c, n: c['jets']['collections'][n]
        self.assertRejected(lambda c: coll(c, 'RecoEvtCh').update(R=0.8), 'jets/collections/RecoEvtCh')
        self.assertRejected(lambda c: coll(c, 'Reco').pop('R'), 'jets/collections/Reco')
        self.assertRejected(lambda c: coll(c, 'RecoEvtCh')['translator'].pop('constituentDetails'), 'jets/collections/RecoEvtCh')
        self.assertRejected(lambda c: coll(c, 'GenEvt')['translator'].update(constituentDetails=True), 'GenEvt/translator',
                            'constituentDetails')
        self.assertRejected(lambda c: coll(c, 'GenEvt')['translator'].update(extraSrcs=['lostTracks']), 'GenEvt/translator',
                            'extraSrcs')
        self.assertRejected(lambda c: c['jets']['cleaning'].update(channels=['Zmumu', 'Zee', 'Wmunu']),
                            'RecoEvtCh: the selected leptons are removed exactly only for dilepton channels')
        self.assertRejected(lambda c: coll(c, 'GenEvt')['translator'].update(minFromPV=1), 'GenEvt/translator',
                            'minFromPV')
        var = loadDefault()['jets']['collections']['Reco']['variations']
        self.assertTrue(var)
        self.assertRejected(lambda c: coll(c, 'RecoEvtCh').update(variations=var), 'RecoEvtCh: variations')
        self.assertRejected(lambda c: c['observables']['E2C'].update(collections=['Nope']), 'observables/E2C/collections')
        self.assertRejected(lambda c: c['jets']['cleaning'].update(channels=[]), 'RecoEvtCh: event collections are made per')

    def test_wiring(self):
        cfg = addEventCollections(loadDefault())
        p = buildProcess(cfg, extra=('globalTag=' + TEST_GT, 'writeConstituents=1'))
        ch, hemi, gen = p.jetsRecoEvtChZmumuRaw, p.jetsRecoEvtPuppiHemiZeeRaw, p.jetsGenEvtZeeRaw
        self.assertEqual(ch.type_(), 'EventEECJetProducer')
        self.assertEqual((ch.src.value(), ch.minFromPV.value(), ch.applyPuppiWeights.value(), ch.absEtaMax.value(),
                          ch.recoilHemisphere.value()), ('packedPFCandidates', 2, False, 2.4, False))
        # one collection per cleaning channel, removing that channel's selected leptons only, by pointer, and
        # produced only when that channel's dilepton selection passes
        for coll in ('RecoEvtCh', 'RecoEvtPuppiHemi', 'GenEvt'):
            pre = 'gen' if coll == 'GenEvt' else ''
            for c in ('Zmumu', 'Zee'):
                raw = getattr(p, 'jets%s%sRaw' % (coll, c))
                sel = (pre + c[0].upper() + c[1:]) if pre else c
                self.assertEqual(list(raw.excludePtrs), ['%sSel:leptonPtrs' % sel], (coll, c))
                self.assertEqual(raw.requireFlag.value(), '%sSel' % sel, (coll, c))
                self.assertEqual(getattr(p, 'jets%s%sTable' % (coll, c)).name.value(), coll + c)
                self.assertEqual(getattr(p, 'eec%s%sE2C' % (coll, c)).src.value(), 'jets%s%s' % (coll, c))
            self.assertFalse(hasattr(p, 'jets%sRaw' % coll))
        self.assertEqual((ch.excludeBy.value(), gen.excludeBy.value()), ('sourceCandidates', 'daughters'))
        # packed-candidate details only where asked
        d = p.jetsRecoEvtChZmumuConstituentDetailsTable
        self.assertEqual((d.jets.value(), labels(d.candidates), d.name.value()),
                         ('jetsRecoEvtChZmumu', ['packedPFCandidates', 'lostTracks'], 'RecoEvtChZmumu'))
        self.assertEqual((labels(ch.extraSrcs), labels(hemi.extraSrcs)), (['lostTracks'], []))
        self.assertFalse(hasattr(p, 'jetsRecoEvtPuppiHemiZmumuConstituentDetailsTable'))
        self.assertTrue(p.jetsRecoEvtChZmumuTable.writeConstituents.value())
        self.assertEqual(list(ch.recoilFlags), [])
        # the recoil hemisphere of the collection's own channel (Zee has no back-to-back selection here)
        self.assertEqual((labels(hemi.recoilFlags), list(hemi.recoilObjects)), (['ZeeSel'], ['ZeeSel:boson']))
        self.assertEqual((hemi.applyPuppiWeights.value(), hemi.minFromPV.value()), (True, -1))
        self.assertEqual(list(gen.dropAbsPdgIds), [12, 14, 16])
        self.assertEqual(p.jetsRecoEvtChZmumuConst.chargedOnly.value(), True)
        self.assertEqual(p.jetsRecoEvtChZmumu.minConstituents.value(), 2)
        # observables: E2C everywhere, E3C only on the AK8 collections; no aggregation or back-to-back for event jets
        self.assertFalse(hasattr(p, 'eecRecoEvtChZmumuE3C'))
        self.assertTrue(hasattr(p, 'eecRecoE3C'))
        self.assertFalse(hasattr(p, 'Zmumu_reco_eecRecoEvtChZmumuE2C'))
        self.assertTrue(hasattr(p, 'Zmumu_reco_eecRecoE2C'))
        self.assertFalse(hasattr(p, 'jetsRecoEvtChZmumuBackToBackZmumu'))
        clean = ['goodVertexFlag', 'metFilterFlag', 'ecalBadCalibFlag', 'jetVetoMapFlag']
        self.assertEqual(labels(p.Zmumu.srcs), ['ZmumuTrigger'] + clean + ['ZmumuSel', 'jetsRecoBackToBackZmumu'])

if __name__ == '__main__':
    unittest.main()
