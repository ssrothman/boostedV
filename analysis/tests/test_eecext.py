"""Tests of bvana/eecext.py (the EEC library's Python module). ANALYSIS_TEST_EECNANO=<NANO with writeConstituents and
unbinned E2Cn1, E2Cn2, E3Cn1 (Reco) and EvtE2Cn1 (RecoEvtCh) tables, e.g. from simulation/configs/ZX_jetfree.yaml
before the constituents-only change> adds the closure against the production tables."""
import itertools
import os
import unittest

import awkward as ak
import numpy as np

from bvana import eecext


def particles(rows):
    return ak.Array([[{'pt': p, 'eta': e, 'phi': f, 'E': p * np.cosh(e)} for p, e, f in jet] for jet in rows])


def bruteForce(jet, norm, N, n, edges):
    """Every ordered N-tuple (self tuples included) at its largest pairwise Delta R: the projected ENC."""
    out = np.zeros(len(edges) + 1)
    for t in itertools.product(range(len(jet)), repeat=N):
        w = np.prod([(jet[i][0] / norm) ** n for i in t])
        dR = max([0.0] + [np.hypot(jet[a][1] - jet[b][1], np.remainder(jet[a][2] - jet[b][2] + np.pi, 2 * np.pi) - np.pi)
                          for a, b in itertools.combinations(t, 2)])
        out[np.searchsorted(edges, dR, side='right')] += w
    return out


def dRpy(p, q):
    return np.hypot(p[1] - q[1], np.remainder(p[2] - q[2] + np.pi, 2 * np.pi) - np.pi)


def shapePy(a, b, c):
    """(xi, phi) of arXiv:2201.07800 Eq. (3); (-1, -1) for R_S = 0."""
    rs, rm, rl = sorted((a, b, c))
    if rs == 0:
        return -1.0, -1.0
    return rs / rm, np.arcsin(np.sqrt(np.clip(1 - ((rl - rm) / rs) ** 2, 0, 1)))


def bruteForceResolved(jet, norm, n, eRL, eXi, ePhi):
    out = np.zeros((len(eRL) + 1, len(eXi) + 1, len(ePhi) + 1))
    for i, j, k in itertools.product(range(len(jet)), repeat=3):
        a, b, c = dRpy(jet[i], jet[j]), dRpy(jet[i], jet[k]), dRpy(jet[j], jet[k])
        xi, phi = shapePy(a, b, c)
        idx = tuple(np.searchsorted(e, x, side='right') for e, x in ((eRL, max(a, b, c)), (eXi, xi), (ePhi, phi)))
        out[idx] += np.prod([(jet[m][0] / norm) ** n for m in (i, j, k)])
    return out


class Synthetic(unittest.TestCase):
    EDGES = np.geomspace(1e-3, 3.0, 12)

    def test_matches_brute_force(self):
        rng = np.random.default_rng(4)
        jets = [[(rng.uniform(1, 50), rng.normal(0, 0.4), rng.normal(0, 0.4)) for _ in range(k)] for k in (2, 5, 7)]
        jets.append([(20.0, 0.0, 3.1), (10.0, 0.1, -3.1)])   # across the phi wrap
        norms = np.array([sum(p for p, _, _ in j) for j in jets]) * 1.3
        for N, n in ((2, 1.0), (2, 2.0), (3, 1.0), (4, 1.0)):
            got = eecext.projectedENC(particles(jets), norms, N, n, self.EDGES)
            for j, jet in enumerate(jets):
                np.testing.assert_allclose(got[j], bruteForce(jet, norms[j], N, n, self.EDGES), rtol=1e-10, atol=1e-14,
                                           err_msg='N=%d n=%g jet %d' % (N, n, j))

    def test_resolved_e3c(self):
        rng = np.random.default_rng(6)
        jets = [[(rng.uniform(1, 50), rng.normal(0, 0.4), rng.normal(0, 0.4)) for _ in range(k)] for k in (1, 4, 6)]
        jets.append([(20.0, 0.0, 3.1), (10.0, 0.1, -3.1), (5.0, -0.2, 3.0)])   # across the phi wrap
        norms = np.array([sum(p for p, _, _ in j) for j in jets])
        eRL, eXi, ePhi = self.EDGES, np.linspace(0, 1, 4), np.linspace(0, np.pi / 2, 5)
        got = eecext.resolvedE3C(particles(jets), norms, 1.0, eRL, eXi, ePhi)
        self.assertEqual(got.shape, (len(jets), len(eRL) + 1, len(eXi) + 1, len(ePhi) + 1))
        for j, jet in enumerate(jets):
            np.testing.assert_allclose(got[j], bruteForceResolved(jet, norms[j], 1.0, eRL, eXi, ePhi), rtol=1e-10,
                                       atol=1e-14, err_msg='jet %d' % j)
        np.testing.assert_allclose(got.sum(axis=(2, 3)), eecext.projectedENC(particles(jets), norms, 3, 1.0, eRL),
                                   rtol=1e-12)
        with self.assertRaises(ValueError):
            eecext.resolvedE3C(particles(jets), norms, 1.0, eRL, [0.5, 0.2], ePhi)

    def test_empty_jet_and_errors(self):
        got = eecext.projectedENC(particles([[], [(5.0, 0.0, 0.0)]]), [1.0, 5.0], 2, 1.0, self.EDGES)
        np.testing.assert_array_equal(got[0], 0)
        self.assertAlmostEqual(got[1][0], 1.0)   # one particle: its self pair at angle 0
        for bad in (dict(norms=[1.0]), dict(edges=[1.0, 0.5]), dict(norms=[1.0, 0.0])):
            kw = dict(norms=[1.0, 5.0], edges=self.EDGES)
            kw.update(bad)
            with self.assertRaises(ValueError, msg=str(bad)):
                eecext.projectedENC(particles([[], [(5.0, 0.0, 0.0)]]), kw['norms'], 2, 1.0, kw['edges'])

    def test_by_jet(self):
        c = ak.Array([[{'iJet': 0, 'pt': 1.0}, {'iJet': 0, 'pt': 2.0}, {'iJet': 2, 'pt': 3.0}], [], [{'iJet': 0, 'pt': 4.0}]])
        out = eecext.byJet(c, [3, 1, 1])
        self.assertEqual(out.pt.tolist(), [[1.0, 2.0], [], [3.0], [], [4.0]])
        with self.assertRaises(ValueError):
            eecext.byJet(ak.Array([[{'iJet': 1, 'pt': 1.0}, {'iJet': 0, 'pt': 2.0}]]), [2])


@unittest.skipUnless(os.environ.get('ANALYSIS_TEST_EECNANO'), 'set ANALYSIS_TEST_EECNANO')
class ProductionClosure(unittest.TestCase):
    """Binned from the stored constituents vs the production's unbinned tables, binned the same way."""
    EDGES = np.geomspace(1e-3, 6.0, 81)

    @classmethod
    def setUpClass(cls):
        import uproot
        cls.t = uproot.open(os.environ['ANALYSIS_TEST_EECNANO'])['Events']

    def check(self, table, jetTable, obs, N, n, norm):
        a = self.t.arrays(filter_name=['n' + jetTable, jetTable + '_*', jetTable + 'Constituents_*', table + 'Entries_*'])
        c = ak.zip({k: a[jetTable + 'Constituents_' + k] for k in ('iJet', 'pt', 'eta', 'phi', 'E')})
        jets = eecext.byJet(c, a['n' + jetTable])
        norms = ak.to_numpy(ak.sum(jets.pt, axis=1)) if norm == 'sumPt' else ak.to_numpy(ak.flatten(a[jetTable + '_pt']))
        got = eecext.projectedENC(jets, norms, N, n, self.EDGES)
        e = a[table + 'Entries_dR']
        w = ak.to_numpy(ak.flatten(a[table + 'Entries_weight'] * a[table + 'Entries_symfactor']))
        jetOf = ak.to_numpy(ak.flatten(a[table + 'Entries_iJet'] + np.concatenate([[0], np.cumsum(ak.to_numpy(a['n' + jetTable]))[:-1]])))
        ref = np.zeros_like(got)
        np.add.at(ref, (jetOf, np.searchsorted(self.EDGES, ak.to_numpy(ak.flatten(e)), side='right')), w)
        self.assertGreater(len(got), 10)
        np.testing.assert_allclose(got.sum(axis=0), ref.sum(axis=0), rtol=1e-4, atol=1e-9, err_msg=obs)
        rel = np.abs(got - ref).sum() / ref.sum()
        self.assertLess(rel, 1e-4, obs)

    def test_ak8(self):
        self.check('RecoE2Cn1', 'RecoJet', 'E2Cn1', 2, 1.0, 'jetPt')
        self.check('RecoE2Cn2', 'RecoJet', 'E2Cn2', 2, 2.0, 'jetPt')
        self.check('RecoE3Cn1', 'RecoJet', 'E3Cn1', 3, 1.0, 'jetPt')

    def test_jet_free(self):
        self.check('RecoEvtChEvtE2Cn1', 'RecoEvtChJet', 'EvtE2Cn1', 2, 1.0, 'sumPt')


if __name__ == '__main__':
    unittest.main()
