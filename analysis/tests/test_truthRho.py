"""Tests of truthRho: per-event window flags and the pairing of the hadronic and leptonic decays of an event."""
import unittest

import numpy as np

import truthRho


class EventLogic(unittest.TestCase):
    def test_all_in_event(self):
        evt = np.array([0, 0, 1, 1, 2])
        np.testing.assert_array_equal(truthRho.allInEvent(evt, np.array([1, 0, 1, 1, 0], bool)), [0, 0, 1, 1, 0])

    def test_joint_pairs_the_decays_of_the_same_event(self):
        # Events 0-3: (had, lep), lep listed first in event 1; event 4: had only; event 5: two leptonic.
        n = 400
        rng = np.random.default_rng(0)
        evt = np.repeat(np.arange(n), 2)
        had = np.tile([True, False], n)
        had[2:4] = [False, True]
        thetaHad = rng.uniform(0, np.pi, n)
        theta = np.empty(2 * n)
        theta[had] = thetaHad
        theta[~had] = np.pi - thetaHad   # the leptonic fermion is always opposite: P(+,-) + P(-,+) + P(0,0) = 1 only if paired
        D = {'evt': np.concatenate([evt, [n, n + 1, n + 1]]), 'had': np.concatenate([had, [True, False, False]]),
             'theta': np.concatenate([theta, [1.0, 1.0, 2.0]]), 'aF': np.ones(2 * n + 3), 'w': np.ones(2 * n + 3),
             'bos': np.full(2 * n + 3, 23.0), 'Vpt': np.full(2 * n + 3, 100.0)}
        ok = np.ones(2 * n + 3, bool)
        res = truthRho.joint(D, ok, [0, 1e9])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['n'], n)
        P = np.array(res[0]['P'])
        # cos theta_lep = -cos theta_had: f_+(had) f_-(lep) etc.; check against the direct per-event product.
        from bvana import spin
        fh, fl = spin.helicityWeights(thetaHad, 1.0), spin.helicityWeights(np.pi - thetaHad, 1.0)
        np.testing.assert_allclose(P, (fh[:, None] * fl[None, :]).mean(axis=-1), atol=1e-12)


if __name__ == '__main__':
    unittest.main()
