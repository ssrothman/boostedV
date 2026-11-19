"""Tests of bvana/sensitivity.py."""
import unittest

import numpy as np

from bvana import sensitivity as sv


class StatsAndSignificance(unittest.TestCase):
    def test_stats_match_explicit_block_vectors(self):
        rng = np.random.default_rng(1)
        V, w = rng.random((50, 3)), rng.normal(1, 0.5, 50)
        pt = rng.choice([250.0, 350.0, 1500.0], 50)
        st = sv.Stats(V, w, pt)
        nS = len(sv.PT_SLICES) - 1
        full = np.zeros((50, nS * 3))
        sl = {250.0: 0, 350.0: 1, 1500.0: 4}
        for j in range(50):
            full[j, sl[pt[j]] * 3:(sl[pt[j]] + 1) * 3] = V[j]
        np.testing.assert_allclose(st.H, w @ full)
        np.testing.assert_allclose(st.C, full.T @ (full * w[:, None]))
        np.testing.assert_allclose(st.Cmc, full.T @ (full * (w ** 2)[:, None]))
        edge = sv.Stats(np.ones((1, 3)), np.ones(1), np.array([300.0]))   # a slice's lower edge belongs to it
        self.assertEqual(np.flatnonzero(edge.H).tolist(), [3, 4, 5])
        tot = st + st
        np.testing.assert_allclose(tot.C, 2 * st.C)

    def test_one_bin_per_jet_is_poisson(self):
        """Each jet fills one bin with 1: C is diagonal with C_ii = b_i, so Z^2 = sum s_i^2 / b_i."""
        b, s = np.array([100.0, 400.0, 25.0]), np.array([10.0, 20.0, 5.0])
        z, shape = sv.significance(s, b, np.diag(b))
        self.assertAlmostEqual(z, np.sqrt(np.sum(s ** 2 / b)))
        self.assertAlmostEqual(sv.significance(0.1 * b, b, np.diag(b))[1], 0.0, places=6)
        self.assertGreater(shape, 0)

    def test_fully_correlated_bins_reduce_to_counting(self):
        """Every jet has the same row u: only the jet count carries information, Z = S / sqrt(N)."""
        u = np.array([0.1, 0.5, 0.3])
        N, S = 1e4, 300.0
        z, shape = sv.significance(S * u, N * u, N * np.outer(u, u))
        self.assertAlmostEqual(z, S / np.sqrt(N), places=6)
        self.assertAlmostEqual(shape, 0.0, places=6)
        C = N * np.outer(u, u)   # dropping the correlations overstates Z by sqrt(number of bins)
        self.assertAlmostEqual(sv.significance(S * u, N * u, np.diag(np.diag(C)))[0], np.sqrt(3) * z, places=6)

    def test_merging_bins_never_increases_z(self):
        """With a well-conditioned covariance, a linear projection (bin merging) cannot add information."""
        rng = np.random.default_rng(3)
        V, w = rng.random((5000, 8)), np.full(5000, 0.7)
        st = sv.Stats(V, w, np.full(5000, 250.0), np.array([200.0, np.inf]))
        s = 0.01 * st.H * np.linspace(0.5, 1.5, 8)
        z8 = sv.significance(s, st.H, st.C)
        A = np.kron(np.eye(4), np.ones((1, 2)))   # merge pairs of bins
        z4 = sv.significance(A @ s, A @ st.H, A @ st.C @ A.T)
        self.assertLess(z4[0], z8[0])
        self.assertLess(z4[1], z8[1])
        self.assertGreater(z4[1], 0)

    def test_shape_chi2(self):
        H = np.array([100.0, 300.0])
        self.assertAlmostEqual(sv.shapeChi2(H, np.diag(H), 2 * H)[0], 0.0)
        # two Poisson bins: p1 = 0.25 with variance p1 (1 - p1) / n against 0.2
        chi2, ndf = sv.shapeChi2(H, np.diag(H), np.array([1.0, 4.0]))
        self.assertEqual(ndf, 1)
        self.assertAlmostEqual(chi2, 0.05 ** 2 / (0.25 * 0.75 / 400))
        # a pure normalisation fluctuation (C + a H H^T) does not change the normalised shape's covariance
        H3, ref = np.array([100.0, 300.0, 50.0]), np.array([1.0, 2.0, 1.0])
        M = np.array([[100.0, 40.0, 0.0], [40.0, 300.0, 30.0], [0.0, 30.0, 50.0]])   # correlated bins
        self.assertAlmostEqual(sv.shapeChi2(H3, M + 0.3 * np.outer(H3, H3), ref)[0], sv.shapeChi2(H3, M, ref)[0], places=6)


    def test_sliced_shape_chi2_ignores_the_pt_spectrum(self):
        """Rescaling whole pT slices (a different jet-pT spectrum, same Delta R shapes) gives 0; the unsliced chi2
        does not; a shape change inside one slice is seen."""
        H = np.array([100.0, 300.0, 50.0, 20.0, 80.0, 40.0])
        C = np.diag(H)
        scale = np.repeat([1.0, 3.0], 3)
        self.assertAlmostEqual(sv.slicedShapeChi2(H * scale, C * scale, H, 2)[0], 0.0)
        self.assertGreater(sv.shapeChi2(H * scale, C * scale, H)[0], 1.0)
        bent = H * np.array([1.0, 1.0, 1.0, 1.3, 1.0, 1.0])
        chi2, ndf = sv.slicedShapeChi2(bent, np.diag(bent), H, 2)
        self.assertEqual(ndf, 4)
        self.assertGreater(chi2, 1.0)
        self.assertEqual(sv.slicedShapeChi2(np.r_[H[:3], 0, 0, 0], np.diag(np.r_[H[:3], 0, 0, 0]), H, 2)[1], 2)


class Kinematics(unittest.TestCase):
    def test_peak_window(self):
        m = sv.peakWindow(np.array([0.3, 0.6, 0.9, 1.5]), np.array([300.0]), 91.0)
        self.assertEqual(m.tolist(), [[False, True, True, False]])   # x = 0.49, 0.99, 1.48, 2.47

    def test_cos_theta_helicity(self):
        mZ, beta = 91.0, 0.95
        g = 1 / np.sqrt(1 - beta ** 2)
        for th in (0.3, 1.2, 2.5):
            # rest-frame lepton in the x-z plane at angle th to the Z direction (x), Z boosted along x
            E, px, pz = mZ / 2, mZ / 2 * np.cos(th), mZ / 2 * np.sin(th)
            pxL = g * (px + beta * E)
            pt, eta = abs(pxL), np.arcsinh(pz / abs(pxL))
            phi = 0.0 if pxL > 0 else np.pi
            c = sv.cosThetaHelicity(np.array([pt]), np.array([eta]), np.array([phi]), np.array([g * beta * mZ]),
                                    np.array([0.0]), np.array([0.0]), np.array([mZ]))
            self.assertAlmostEqual(c[0], np.cos(th), places=9)


if __name__ == '__main__':
    unittest.main()


class Thresholds(unittest.TestCase):
    def test_per_slice_threshold_flattens_the_dy_efficiency(self):
        import sensitivity
        rng = np.random.default_rng(5)
        n = 40000
        pt = rng.choice([250.0, 700.0, 1200.0], n)
        x = rng.random(n) ** np.where(pt > 1000, 4.0, np.where(pt > 600, 2.0, 1.0))   # DY tagger shape depends on pT
        isDY, base, w = np.ones(n, bool), np.ones(n, bool), np.ones(n)
        keep = sensitivity.slicedThresholdMask(x, pt, base, isDY, w, 0.1, sensitivity.TEN_SLICES)
        for p in (250.0, 700.0, 1200.0):
            self.assertAlmostEqual(keep[pt == p].mean(), 0.1, delta=0.002)
        c = sensitivity.thresholds(x, base, isDY, w, True, effs=(0.1,))[0]
        glob = x > c
        self.assertAlmostEqual(glob.mean(), 0.1, delta=0.002)
        self.assertGreater(np.ptp([glob[pt == p].mean() for p in (250.0, 700.0, 1200.0)]), 0.1)   # global cut is not flat
