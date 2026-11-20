"""Tests of the weighted quantiles of ptResolution.py."""
import unittest

import numpy as np

import ptResolution


class Quantiles(unittest.TestCase):
    def test_equal_weights_median(self):
        x = np.array([5.0, 1.0, 4.0, 2.0, 3.0])
        self.assertEqual(ptResolution.quantiles(x, np.ones(5), [0.5])[0], 3.0)

    def test_integer_weights_equal_repeated_sample(self):
        rng = np.random.default_rng(1)
        x, k = rng.normal(size=4000), rng.integers(1, 4, 4000)
        got = ptResolution.quantiles(x, k.astype(float), [0.16, 0.5, 0.84])
        np.testing.assert_allclose(got, np.quantile(np.repeat(x, k), [0.16, 0.5, 0.84]), atol=2e-3)

    def test_summary_tail(self):
        r, w = np.array([-0.5, 0.0, 0.1, 0.4]), np.array([1.0, 1.0, 1.0, 2.0])
        self.assertAlmostEqual(ptResolution.summary(r, w)[2], 0.6)


if __name__ == '__main__':
    unittest.main()
