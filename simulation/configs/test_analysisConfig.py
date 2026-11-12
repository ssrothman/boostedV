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
        self.assertRejected(lambda c: c['observables']['E2C'].update(weight='Charge'), 'observables/E2C')
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
                if type(getattr(ref, name)).__name__ == 'VPSet':
                    for a in getattr(mod, name):
                        self.assertEqual(set(a.parameterNames_()), set(ref.axes[0].parameterNames_()),
                                         '%s.%s entry is incomplete' % (label, name))
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
            self.assertEqual(p.tightMuonsDressed.originals.getModuleLabel(), 'slimmedMuons')
            self.assertEqual(p.tightMuonsDressed.fsrIndex.getProductInstanceLabel(), 'muFsrIndex')
            self.assertEqual(p.tightElectronsDressed.fsrIndex.getProductInstanceLabel(), 'eleFsrIndex')
            self.assertEqual(p.tightMuons.type_(), 'CandPtrSelector')
            self.assertEqual(p.tightMuons.cut.value(), 'pt > 15')
            self.assertEqual(p.tightPhotons.type_(), 'PATPhotonSelector')      # photons are never dressed
            self.assertEqual(hasattr(p, 'leptonFSRphotons'), mode == 'fsr')
            self.assertEqual(p.tightMuonsDressed.coneSize.value(), reco['dressing']['cone']['coneSize'])

    def test_muon_corrections(self):
        p = buildProcess()
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

    def test_jets_cleaned_against_own_level(self):
        p = buildProcess()
        reco = labels(p.jetsReco.vetoSrcs)
        gen = labels(p.jetsGen.vetoSrcs)
        self.assertEqual(reco, ['ZmumuSel', 'ZeeSel', 'WmunuSel', 'WenuSel', 'GammaJetsSel'])
        self.assertEqual(gen, ['genZmumuSel', 'genZeeSel', 'genWmunuSel', 'genWenuSel', 'genGammaJetsSel'])
        self.assertEqual(p.genWmunuSel.met.getModuleLabel(), 'genParticleLevel')
        self.assertEqual(p.genWmunuSel.met.getProductInstanceLabel(), 'mets')
        self.assertEqual(p.WmunuSel.met.getModuleLabel(), 'slimmedMETsPuppi')

    def test_yaml_values_reach_modules(self):
        cfg = loadDefault()
        cfg['selection']['reco']['channels']['Zmumu']['massMin'] = 81.0
        cfg['jets']['collections']['Reco']['jetCuts']['ptMin'] = 250.0
        cfg['jets']['collections']['Reco']['variations']['TrkDrop']['dropProbability'] = 0.05
        cfg['observables']['E2C']['axes'][0]['nbins'] = 40
        cfg['aggregation']['channels'] = ['Wmunu']
        p = buildProcess(cfg)
        self.assertEqual(p.ZmumuSel.massMin.value(), 81.0)
        self.assertEqual(p.ZeeSel.massMin.value(), 71.0)
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


if __name__ == '__main__':
    unittest.main()
