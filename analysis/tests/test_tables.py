"""Tests of the per-jet tables (bvana/tables.py), on the synthetic events of test_framework."""
import unittest

import awkward as ak
import numpy as np
from coffea import processor
from coffea.nanoevents.methods import vector

from bvana.config import Config, ConfigError
from bvana.processor import Processor
from bvana.tables import ak4Columns
from test_framework import syntheticEvents

EDGES = [0.05, 0.15, 0.25]


def config(cuts, table):
    return Config({'regions': {'R': {'level': 'reco', 'channel': 'Zmumu', 'cuts': cuts}},
                   'binning': {'b': {'edges': EDGES}}, 'tables': {'t': table}})


class Tables(unittest.TestCase):
    def select(self, cfg):
        return cfg.regions['R'].select(syntheticEvents(), ak.Array([1.0, 2.0, 3.0]))[0]

    def test_rows_columns_and_eec(self):
        cfg = config(['jets.pt > 300'], {'columns': {'pt': 'jets.pt', 'zpt': 'boson.pt'},
                                         'eec': {'cut': {'observable': 'X', 'var': 'eec.dR', 'bins': 'b', 'cuts': ['eec.dR > 0']},
                                                 'all': {'observable': 'X', 'var': 'eec.dR', 'bins': 'b'}}})
        out = cfg.tables['t'].fill(self.select(cfg))
        # kept jets: ev0 j1 (weight 1), ev1 j0 and j1 (weight 2); entries of jet k: (dR 0, w 0.01(k+1)), (dR 0.1(k+1), w 0.1(k+1) x 2)
        np.testing.assert_array_equal(out['pt'], [400, 500, 320])
        np.testing.assert_array_equal(out['zpt'], [250, 150, 150])
        np.testing.assert_array_equal(out['weight'], [1, 2, 2])
        np.testing.assert_allclose(out['cut'], [[0, 0, 0.4, 0], [0, 0.2, 0, 0], [0, 0, 0.4, 0]], rtol=1e-6)
        np.testing.assert_allclose(out['all'], [[0.02, 0, 0.4, 0], [0.01, 0.2, 0, 0], [0.02, 0, 0.4, 0]], rtol=1e-6)
        self.assertEqual(out['cut'].dtype, np.float32)

    def test_matches_histogram_fill(self):
        """Event-weighted sum of the rows equals the EEC histogram of the same region (flow bins included)."""
        spec = {'regions': {'R': {'level': 'reco', 'channel': 'Zmumu', 'cuts': ['jets.pt > 200']}},
                'binning': {'b': {'edges': EDGES}},
                'histograms': {'h': {'granularity': 'eec:X', 'cuts': ['eec.dR > 0'], 'axes': [{'var': 'eec.dR', 'bins': 'b'}]}},
                'tables': {'t': {'eec': {'e': {'observable': 'X', 'var': 'eec.dR', 'bins': 'b', 'cuts': ['eec.dR > 0']}}}}}
        cfg = Config(spec)
        view = self.select(cfg)
        h = cfg.histograms['h'].fill(view).values(flow=True)
        t = cfg.tables['t'].fill(view)
        np.testing.assert_allclose((t['weight'][:, None] * t['e']).sum(axis=0), h, rtol=1e-6)
        self.assertGreater(h[1:-1].sum(), 0)

    def test_processor_accumulates_rows(self):
        cfg = config([], {'columns': {'pt': 'jets.pt'}, 'eec': {'e': {'observable': 'X', 'var': 'eec.dR', 'bins': 'b'}}})
        ev, p = syntheticEvents(), Processor(cfg)
        acc = processor.accumulate(p.process(_WithMetadata(ev[sl], {'sample': 'S', 'isMC': True}))
                                   for sl in (slice(0, 2), slice(2, 3)))
        cols = acc['tables']['t']['R']['S']
        np.testing.assert_array_equal(cols['pt'].value, [400, 250, 500, 320, 210])
        self.assertEqual(cols['e'].value.shape, (5, len(EDGES) + 1))
        np.testing.assert_array_equal(cols['weight'].value, [1, 1, 2, 2, 3])

    def test_truth_without_genpart(self):
        out = config([], {'truth': {'dRMax': 0.8}}).tables['t'].fill(self.select(config([], {})))
        self.assertEqual(out['truthStatus'].tolist(), [2] * 5)
        self.assertTrue(np.isnan(out['truthPt']).all())

    def test_config_errors(self):
        for table in ({'columns': {'x': 'eec.dR'}}, {'columns': {'x': 'leptons.pt'}}, {'colums': {}},
                      {'eec': {'e': {'observable': 'X', 'bins': 'b'}}},
                      {'eec': {'e': {'observable': 'X', 'var': 'eec.dR', 'bins': 'nope'}}},
                      {'columns': {'weight': 'jets.pt'}}, {'ak4': {'ptMin': 30}}, {'regions': ['nope']},
                      {'truth': {}}, {'truth': {'dRMax': 0.8}, 'columns': {'truthPt': 'jets.pt'}}):
            with self.assertRaises(ConfigError, msg=str(table)):
                config([], table)


class _WithMetadata:
    """An awkward record array with the metadata attribute the processor expects of NanoEvents."""

    def __init__(self, arr, md):
        self._arr, self.metadata = arr, md

    def __getattr__(self, k):
        return getattr(self._arr, k)

    def __getitem__(self, k):
        return self._arr[k]

    def __len__(self):
        return len(self._arr)


def lv(rows, **extra):
    fields = {k: [[r[i] for r in ev] for ev in rows] for i, k in enumerate(['pt', 'eta', 'phi', 'mass'])}
    for k, v in extra.items():
        fields[k] = v
    return ak.zip(fields, with_name='PtEtaPhiMLorentzVector', behavior=vector.behavior)


class AK4(unittest.TestCase):
    def test_columns(self):
        jets = lv([[(400, 0.0, 0.0, 90)], [(300, 1.0, 1.0, 20)]])
        leptons = lv([[(100, 0.0, 3.0, 0)], [(100, 0.0, -2.0, 0)]])
        # event 0: dR 0.5 to the AK8 jet (removed), two kept, below ptMin, dR 0.1 to the lepton (removed), |eta| > 2.5
        rows = [[(60, 0.0, 0.5, 5), (50, 0.0, 2.0, 5), (40, 1.0, 2.0, 5), (20, 0.0, 1.5, 5), (70, 0.0, 3.1, 5),
                 (80, 2.7, 1.5, 5)], []]
        ak4 = lv(rows, btagRobustParTAK4B=[[0.99, 0.2, 0.7, 0.95, 0.98, 0.97], []])
        out = ak4Columns(ak4, jets, leptons, ptMin=30, absEtaMax=2.5, dRJet=0.8, dRLepton=0.4)
        self.assertEqual(out['ak4N'].tolist(), [[2], [0]])
        self.assertEqual(out['ak4HT'].tolist(), [[90.0], [0.0]])
        np.testing.assert_allclose(ak.flatten(out['ak4MaxBtag']).to_numpy(), [0.7, -1.0])


if __name__ == '__main__':
    unittest.main()
