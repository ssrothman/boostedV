"""Tests of the shape-compatibility chi2 of vvTruthSplit.py."""
import unittest

import numpy as np

import vvTruthSplit as vs


class CompatChi2(unittest.TestCase):
    def test_identical_shapes(self):
        H = np.array([10.0, 30.0, 60.0])
        c, n = vs.compatChi2(H, np.diag(H), 3 * H, np.diag(3 * H))
        self.assertAlmostEqual(c, 0.0, places=12)
        self.assertEqual(n, 2)

    def test_two_bins_analytic(self):
        # two bins: chi2 = (p1 - q1)^2 / (var p1 + var q1), var p1 = (b^2 var a + a^2 var b) / n^4
        a, b, c_, d = 30.0, 70.0, 50.0, 50.0
        va, vb, vc, vd = 4.0, 9.0, 16.0, 1.0
        varP = (b ** 2 * va + a ** 2 * vb) / (a + b) ** 4
        varQ = (d ** 2 * vc + c_ ** 2 * vd) / (c_ + d) ** 4
        expect = (a / (a + b) - c_ / (c_ + d)) ** 2 / (varP + varQ)
        got, n = vs.compatChi2(np.array([a, b]), np.diag([va, vb]), np.array([c_, d]), np.diag([vc, vd]))
        self.assertAlmostEqual(got, expect, places=9)
        self.assertEqual(n, 1)

    def test_poisson_toys_have_mean_chi2_ndf(self):
        rng = np.random.default_rng(3)
        mu = np.array([50.0, 200.0, 400.0, 120.0, 30.0])
        chi2 = []
        for _ in range(4000):
            x, y = rng.poisson(mu).astype(float), rng.poisson(2 * mu).astype(float)
            c, n = vs.compatChi2(x, np.diag(x), y, np.diag(y))
            chi2.append(c / n)
        self.assertAlmostEqual(np.mean(chi2), 1.0, delta=0.05)


class HistRows(unittest.TestCase):
    def test_clipped_one_hot(self):
        r = vs.histRows(np.array([-0.1, 0.0, 0.55, 1.0, 2.0]), np.linspace(0, 1, 3))
        np.testing.assert_array_equal(r, [[1, 0], [1, 0], [0, 1], [0, 1], [0, 1]])


if __name__ == '__main__':
    unittest.main()
