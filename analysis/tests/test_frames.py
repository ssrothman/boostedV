"""Tests of bvana.frames. ANALYSIS_TEST_NANO=<ZX_test NANO> adds the entry-by-entry closure against the C++
E1CHelicity (same jets, jet axis and jet mass), which boosts the actual four-vectors."""
import os
import unittest

import awkward as ak
import numpy as np
import uproot

from bvana import frames


def boostMatrix(betaVec):
    """Lorentz boost taking the rest frame to a frame where the rest frame moves with velocity betaVec."""
    b = np.linalg.norm(betaVec)
    g = 1 / np.sqrt(1 - b * b)
    n = betaVec / b
    L = np.eye(4)
    L[0, 0] = g
    L[0, 1:] = L[1:, 0] = g * b * n
    L[1:, 1:] += (g - 1) * np.outer(n, n)
    return L


class RestFrameRoundTrip(unittest.TestCase):
    """Rest-frame pions -> explicit Lorentz boost -> lab angles about the axis -> frames.restFrame."""

    @staticmethod
    def labSample(axisEta, axisPhi, P, M, n=400, seed=3):
        rng = np.random.default_rng(seed)
        a, x = frames.axisKinematics(np.array([P / np.cosh(axisEta)]), np.array([axisEta]), np.array([axisPhi]))
        a, x = a[:, 0], x[:, 0]
        y = np.cross(a, x)
        cosT, phi = rng.uniform(-1, 1, n), rng.uniform(-np.pi, np.pi, n)
        Estar = rng.uniform(0.3, 20, n)
        pstar = np.sqrt(Estar ** 2 - frames.M_PION ** 2)
        sT = np.sqrt(1 - cosT ** 2)
        dirs = (sT * np.cos(phi))[:, None] * x + (sT * np.sin(phi))[:, None] * y + cosT[:, None] * a
        lab = np.column_stack([Estar, pstar[:, None] * dirs]) @ boostMatrix(P / np.sqrt(P * P + M * M) * a).T
        pvec = lab[:, 1:]
        thetaLab = np.arccos(np.clip(pvec @ a / np.linalg.norm(pvec, axis=1), -1, 1))
        phiLab = np.arctan2(pvec @ y, pvec @ x)
        full = lambda v: np.full(n, v)
        labIn = (thetaLab, phiLab, np.hypot(pvec[:, 0], pvec[:, 1]), full(P / np.cosh(axisEta)), full(axisEta),
                 full(axisPhi), full(M))
        return labIn, (cosT, phi, Estar / M)

    def test_recovers_rest_frame_angles_and_energy(self):
        for axisEta, P, M in ((0.0, 300.0, 91.19), (1.7, 900.0, 80.4), (-2.2, 2500.0, 91.19)):
            labIn, (cosT, phi, e) = self.labSample(axisEta, 0.4, P, M)
            out = frames.restFrame(*labIn)
            np.testing.assert_allclose(out['cosThetaRest'], cosT, atol=1e-9)
            np.testing.assert_allclose(np.angle(np.exp(1j * (out['phiRest'] - phi))), 0, atol=1e-9)
            np.testing.assert_allclose(out['ERest'], e, rtol=1e-9)

    def test_massless_hypothesis_does_not_close_for_pions(self):
        labIn, (cosT, _, _) = self.labSample(0.5, 0.0, 400.0, 91.19)
        out = frames.restFrame(*labIn, particleMass=0.0)
        self.assertGreater(np.max(np.abs(out['cosThetaRest'] - cosT)), 1e-3)


@unittest.skipUnless(os.environ.get('ANALYSIS_TEST_NANO'), 'set ANALYSIS_TEST_NANO (a ZX_test NANO with writeConstituents=1)')
class ClosureAgainstCpp(unittest.TestCase):
    def test_e1clab_boosted_equals_e1chelicity(self):
        from bvana import eec
        ev = uproot.open(os.environ['ANALYSIS_TEST_NANO'])['Events'].arrays(
            filter_name=['nRecoJet', 'RecoJet_*', 'RecoE1CLab_*', 'RecoE1CLabEntries_*', 'RecoE1CHelicityEntries_*',
                         'RecoJetConstituents_*'])
        z = lambda pre: ak.zip({k[len(pre):]: ev[k] for k in ev.fields if k.startswith(pre)})
        events = ak.zip({'RecoJet': z('RecoJet_'), 'RecoE1CLab': z('RecoE1CLab_'),
                         'RecoE1CLabEntries': z('RecoE1CLabEntries_')}, depth_limit=1)
        out = frames.addRestFrame(eec.entriesByJet(events, 'Reco', 'E1CLab'), events['RecoE1CLab'], events['RecoJet'],
                                  'jet', 'axis')
        flat = lambda x: ak.to_numpy(ak.flatten(x, axis=None)).astype(float)
        th, ph, Er = flat(out.thetaRest), flat(out.phiRest), flat(out.ERest)
        ref = z('RecoE1CHelicityEntries_')
        thr, phr = flat(ref.theta), flat(ref.phi)
        # Entries follow the constituent order (both E1Cs loop over the same constituents).
        c = z('RecoJetConstituents_')
        pt, eta, E, w = flat(c.pt), flat(c.eta), flat(c.E), flat(c.puppiWeight)
        self.assertEqual(len(th), len(thr))
        self.assertEqual(len(th), len(pt))
        M = flat(ak.broadcast_arrays(events['RecoJet'].mass, out.thetaRest)[0])
        pstar = np.sqrt(np.maximum((Er * M) ** 2 - frames.M_PION ** 2, 0))
        m2 = E ** 2 - (pt * np.cosh(eta)) ** 2
        # The C++ boosts the stored four-vectors: compare where those are unit-weight pions, and where the rest-frame
        # momentum is large enough that float32 inputs do not dominate (p* -> 0 leaves the direction undefined).
        sel = (w == 1) & (np.abs(flat(c.pdgId)) == 211) & (np.abs(m2 - frames.M_PION ** 2) < 1e-3) & (pstar > 0.5)
        self.assertGreater(sel.sum(), 1000)
        dth, dph = np.abs(th - thr)[sel], np.abs(np.angle(np.exp(1j * (ph - phr))))[sel]
        self.assertLess(np.quantile(dth, 0.99), 1e-4)
        self.assertLess(dth.max(), 5e-3)
        self.assertLess(dph.max(), 1e-5)
        print('closure (%d of %d entries): |dtheta| median %.1e q99 %.1e max %.1e; |dphi| max %.1e'
              % (sel.sum(), len(th), np.median(dth), np.quantile(dth, 0.99), dth.max(), dph.max()))


if __name__ == '__main__':
    unittest.main()


class RestFrameHistograms(unittest.TestCase):
    """The restFrame histogram option fills frames.restFrame values, and two mass hypotheses do not share caches."""

    def test_fill_matches_direct_computation_and_caches_are_separate(self):
        from bvana.config import Config
        jets = ak.Array([[{'pt': 400.0, 'eta': 0.3, 'phi': 1.0, 'mass': 80.0, 'vetoZmumu': False}]])
        th, ph, w = [0.05, 0.2, 0.4], [0.1, -2.0, 3.0], [0.3, 0.2, 0.01]
        entries = ak.Array([[{'iJet': 0, 'theta': a, 'phi': b, 'weight': c, 'symfactor': 1} for a, b, c in zip(th, ph, w)]])
        per = ak.Array([[{'nEntries': 3, 'E_jet': 400.0, 'n': 1.0, 'N': 1}]])
        events = ak.zip({'RecoJet': jets, 'RecoY': per, 'RecoYEntries': entries,
                         'ZmumuBoson': ak.Array([[{'pt': 400.0, 'mass': 91.0}]]),
                         'ZmumuLeptons': ak.Array([[{'pt': 200.0}, {'pt': 200.0}]]),
                         'Selection': ak.zip({'Zmumu': np.array([True])}), 'PuppiMET': ak.zip({'pt': np.array([1.0])}),
                         'genWeight': np.array([1.0])}, depth_limit=1)
        bins = {'regular': [4, -1, 1]}
        h = lambda m: {'granularity': 'eec:Y', 'restFrame': {'axis': 'jet', 'mass': m},
                       'axes': [{'var': 'eec.cosThetaRest', 'bins': bins}], 'weight': 'eec.ERest / eec.weight'}
        cfg = Config({'regions': {'R': {'level': 'reco', 'channel': 'Zmumu'}}, 'binning': {},
                      'histograms': {'own': h('axis'), 'mV': h(91.19)}})
        view, _ = cfg.regions['R'].select(events, ak.Array([1.0]))
        own, mV = cfg.histograms['own'].fill(view), cfg.histograms['mV'].fill(view)
        for M, got in ((80.0, own), (91.19, mV)):
            ref = frames.restFrame(np.array(th), np.array(ph), np.array(w) * 400.0, np.full(3, 400.0), np.full(3, 0.3),
                                   np.full(3, 1.0), np.full(3, M))
            expect, _ = np.histogram(ref['cosThetaRest'], bins=4, range=(-1, 1), weights=ref['ERest'])
            np.testing.assert_allclose(got.values(), expect, rtol=1e-12)
        self.assertFalse(np.allclose(own.values(), mV.values()))
