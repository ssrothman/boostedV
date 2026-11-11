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


def buildProcess(cfgDict=None, isMC=1):
    """Executes eecNano_cfg.py with the given configuration and returns its process."""
    path = writeTmp(cfgDict) if cfgDict is not None else DEFAULT
    argv = sys.argv
    sys.argv = [CFG, 'config=' + path, 'isMC=%d' % isMC]
    try:
        g = {'__name__': '__cfg__'}
        with open(CFG) as f:
            exec(compile(f.read(), CFG, 'exec'), g)
        return g['process']
    finally:
        sys.argv = argv


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
        self.assertRejected(lambda c: c['selection']['channels']['Zmumu'].update(massMinn=81.0),
                            'selection/channels/Zmumu', 'massMinn')
        self.assertRejected(lambda c: c['jets']['collections']['Reco']['jetCuts'].update(etaMax=2.0),
                            'jets/collections/Reco', 'etaMax')
        self.assertRejected(lambda c: c['observables']['E2C'].update(bins=3), 'observables/E2C', 'bins')

    def test_missing_keys(self):
        self.assertRejected(lambda c: c['selection']['channels']['Zmumu'].pop('massMin'),
                            'selection/channels/Zmumu', 'massMin')
        self.assertRejected(lambda c: c['jets']['collections']['Reco']['jerc'].pop('jesKey'),
                            'jets/collections/Reco/jerc', 'jesKey')
        self.assertRejected(lambda c: c.pop('aggregation'), 'aggregation')

    def test_wrong_types_and_values(self):
        self.assertRejected(lambda c: c['selection']['channels']['Zmumu'].update(massMin='71'), 'selection/channels/Zmumu')
        self.assertRejected(lambda c: c['observables']['E2C'].update(N=7), 'observables/E2C')
        self.assertRejected(lambda c: c['observables']['E2C'].update(weight='Charge'), 'observables/E2C')
        self.assertRejected(lambda c: c['jets']['collections']['Reco']['variations']['TrkDrop'].update(
            dropProbability=1.5), 'jets/collections/Reco/variations/TrkDrop')

    def test_cross_references(self):
        self.assertRejected(lambda c: c['selection']['channels']['Zmumu'].update(objects='tightMuon'),
                            'unknown object collection tightMuon')
        self.assertRejected(lambda c: c['jets']['cleaning']['channels'].append('Zmm'), 'unknown channel Zmm')
        self.assertRejected(lambda c: c['aggregation']['channels'].append('Ztautau'), 'unknown channel Ztautau')

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
        self.assertEqual(p.Zmumu_eecRecoE2C.genEventInfo.getModuleLabel(), '')

    def test_yaml_values_reach_modules(self):
        cfg = loadDefault()
        cfg['selection']['channels']['Zmumu']['massMin'] = 81.0
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
        self.assertEqual(p.Wmunu_eecRecoE2C.axes[0].nbins.value(), 40)
        self.assertTrue(hasattr(p, 'WmunuAggPath'))
        self.assertFalse(hasattr(p, 'ZmumuAggPath'))

    def test_default_matches_previous_hardcoded_setup(self):
        # The values that used to be hard-coded in the python helpers, now coming from default.yaml.
        p = buildProcess()
        self.assertEqual(list(p.metFilterFlag.paths)[0], 'Flag_goodVertices')
        self.assertEqual(p.ZmumuSel.leadPtMin.value(), 26.0)
        self.assertEqual(p.ZeeSel.leadPtMin.value(), 35.0)
        self.assertEqual(p.WenuSel.ptMin.value(), 35.0)
        self.assertEqual(p.HadronicSel.nMax.value(), 0)
        self.assertEqual(p.jetsRecoRaw.ptMin.value(), 180.0)
        self.assertEqual(p.jetsRecoJER.jerScaleFactorKey.value(), 'Summer22EE_22Sep2023_JRV1_MC_ScaleFactor_AK8PFPuppi')
        self.assertEqual(p.jetsRecoTrkDropVar.seedSalt.value(), 1)
        self.assertEqual(p.jetsRecoJER.seedSalt.value(), 0)


if __name__ == '__main__':
    unittest.main()
