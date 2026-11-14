"""Tests: python3 -m unittest -v test_analysis (mambaforge dev env).
ANALYSIS_TEST_NANO=<ZX_test NANO file> enables the processor test against an independent uproot computation."""
import json
import os
import tempfile
import unittest

import awkward as ak
import numpy as np

import eec
import samples


def fakeEvents(nEntries, iJet):
    """Events with one EEC observable 'RecoX': per-jet nEntries [event][jet], entries iJet [event][entry]."""
    per = ak.zip({'nEntries': ak.Array(nEntries), 'E_jet': ak.Array([[100.0] * len(e) for e in nEntries]),
                  'n': ak.Array([[1.0] * len(e) for e in nEntries]), 'N': ak.Array([[2] * len(e) for e in nEntries])})
    w = [[0.1 * (k + 1) for k in range(len(e))] for e in iJet]
    ent = ak.zip({'iJet': ak.Array(iJet), 'weight': ak.Array(w), 'symfactor': ak.Array([[2] * len(e) for e in iJet])})
    return ak.zip({'RecoX': per, 'RecoXEntries': ent}, depth_limit=1)


class EEC(unittest.TestCase):
    def test_entries_by_jet(self):
        ev = fakeEvents([[2, 0, 1], [], [3]], [[0, 0, 2], [], [0, 0, 0]])
        n = eec.entriesByJet(ev, 'Reco', 'X')
        self.assertEqual(ak.num(n, axis=2).tolist(), [[2, 0, 1], [], [3]])
        self.assertEqual(n.iJet.tolist(), [[[0, 0], [], [2]], [], [[0, 0, 0]]])
        self.assertAlmostEqual(ak.sum(eec.tupleWeight(n)), 2 * (0.1 + 0.2 + 0.3 + 0.1 + 0.2 + 0.3))

    def test_entries_by_jet_rejects_inconsistent_tables(self):
        with self.assertRaises(ValueError):  # entries of jet 2 counted for jet 1
            eec.entriesByJet(fakeEvents([[2, 1, 0]], [[0, 0, 2]]), 'Reco', 'X')
        with self.assertRaises(ValueError):  # one entry missing
            eec.entriesByJet(fakeEvents([[2, 1]], [[0, 0]]), 'Reco', 'X')

    def test_renormalise(self):
        n = eec.entriesByJet(fakeEvents([[1]], [[0]]), 'Reco', 'X')
        per = fakeEvents([[1]], [[0]])['RecoX']
        self.assertAlmostEqual(ak.flatten(eec.renormalise(n, per, 50.0), axis=None)[0], 0.1 * 2 ** 2)


class Samples(unittest.TestCase):
    def test_load_and_normalise(self):
        with tempfile.TemporaryDirectory() as d:
            for name, sumw in (('A', 200.0), ('B', 5.0)):
                os.makedirs(os.path.join(d, 'tag', name, 'merged'))
                with open(os.path.join(d, 'tag', name, 'merged', 'sample.json'), 'w') as f:
                    json.dump({'isMC': True, 'nanoFiles': ['x.root'], 'genEventSumw': sumw}, f)
            xs = os.path.join(d, 'xs.yaml')
            with open(xs, 'w') as f:
                f.write('A: {xsec: 10.0, source: test}\nB: {xsec: null, source: ""}\n')
            s = samples.load('tag', work=d, xsecFile=xs)
            self.assertAlmostEqual(s['A'].lumiScale(1000.0), 10.0 * 1000.0 / 200.0)
            with self.assertRaises(ValueError):
                s['B'].lumiScale(1000.0)
            with self.assertRaises(ValueError):
                samples.load('tag', ['A', 'C'], work=d, xsecFile=xs)


@unittest.skipUnless(os.environ.get('ANALYSIS_TEST_NANO'), 'set ANALYSIS_TEST_NANO')
class Processor(unittest.TestCase):
    def test_eec_sums_match_uproot(self):
        import uproot
        from coffea.nanoevents import NanoEventsFactory
        from processor import ZXProcessor
        from schema import BoostedVSchema
        f = os.environ['ANALYSIS_TEST_NANO']
        events = NanoEventsFactory.from_root({f: 'Events'}, schemaclass=BoostedVSchema, mode='eager',
                                             metadata={'sample': 'S', 'isMC': True}).events()
        out = ZXProcessor().process(events)
        a = uproot.open(f)['Events'].arrays(library='np')
        checked = 0
        for ch in ('Zmumu', 'Zee'):
            for obs in ('E2Cn1', 'E1CHelicity'):
                total = 0.0
                for e in np.nonzero(a['Selection_' + ch])[0]:
                    good = ~a['RecoJet_veto' + ch][e]
                    sel = good[a['Reco%sEntries_iJet' % obs][e]]
                    if obs.startswith('E2C'):
                        sel &= a['Reco%sEntries_dR' % obs][e] > 0
                    total += a['genWeight'][e] * np.sum((a['Reco%sEntries_weight' % obs][e] *
                                                         a['Reco%sEntries_symfactor' % obs][e])[sel])
                h = out['hists']['S_%s_reco' % ch][obs]
                got = h.sum(flow=True).value
                self.assertAlmostEqual(got, total, delta=1e-9 * max(1.0, abs(total)))
                checked += total != 0
        self.assertGreater(checked, 0)


if __name__ == '__main__':
    unittest.main()
