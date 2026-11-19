"""Tests of the EEC accessors and the sample registry: python3 -m unittest discover -s tests (from analysis/)."""
import json
import os
import tempfile
import unittest

import awkward as ak

from bvana import eec, samples


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

    def test_fileset_over_tags(self):
        import argparse
        import functools
        from unittest import mock
        import run
        with tempfile.TemporaryDirectory() as d:
            for tag, names in (('t1', ('A', 'B')), ('t2', ('C',)), ('t3', ('A',))):
                for name in names:
                    os.makedirs(os.path.join(d, tag, name, 'merged'))
                    with open(os.path.join(d, tag, name, 'merged', 'sample.json'), 'w') as f:
                        json.dump({'isMC': True, 'nanoFiles': [tag + name + '.root'], 'genEventSumw': 2.0}, f)
            xs = os.path.join(d, 'xs.yaml')
            with open(xs, 'w') as f:
                f.write('A: {xsec: 1.0, source: test}\nB: {xsec: 3.0, source: test}\nC: {xsec: 5.0, source: test}\n')

            def fs(tags, names=None):
                a = argparse.Namespace(fileset=None, files=None, tag=tags, samples=names, lumi=10.0)
                return run.fileset(a)
            with mock.patch.object(run.samples, 'load', functools.partial(samples.load, work=d, xsecFile=xs)):
                out = fs(['t1', 't2'])
                self.assertEqual(sorted(out), ['A', 'B', 'C'])
                self.assertEqual(list(out['C']['files']), ['t2C.root'])
                self.assertAlmostEqual(out['C']['metadata']['lumiScale'], 25.0)
                self.assertEqual(sorted(fs(['t1', 't2'], ['C', 'A'])), ['A', 'C'])
                with self.assertRaises(SystemExit):
                    fs(['t1', 't2'], ['A', 'D'])
                with self.assertRaises(SystemExit):
                    fs(['t1', 't3'])


if __name__ == '__main__':
    unittest.main()
