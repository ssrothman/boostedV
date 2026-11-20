"""Tests of the hadronic W/Z lookup of vvBosonLocation.py on the hand-made GenPart record of test_truth."""
import unittest

import awkward as ak

import vvBosonLocation as vb
from test_truth import EVENTS, FHP, gen

PHOTON_FIRST = [(22, 22, FHP, -1, 600, 0.0, 1.0),   # 0 hard photon -> u: hadronic but neither W nor Z
                (2, 23, FHP, 0, 600, 0.0, 1.0),     # 1
                (23, 62, 0, -1, 300, 0.0, -1.0),    # 2 Z -> d dbar (+ an FSR photon), the harder of two Z
                (-1, 23, FHP, 2, 140, -0.2, -1.0),  # 3 softer quark first
                (1, 23, FHP, 2, 150, 0.2, -1.0),    # 4
                (22, 1, 0, 2, 200, 0.0, -1.0),      # 5 FSR photon: not a quark
                (23, 62, 0, -1, 100, 1.0, 2.0),     # 6 a softer hadronic Z -> s sbar
                (3, 23, FHP, 6, 50, 1.0, 2.0),      # 7
                (-3, 23, FHP, 6, 50, 1.0, 2.1)]     # 8
PHOTON_ONLY = PHOTON_FIRST[:2]                     # no W/Z: particle 0's daughters must not be taken


class HadronicBoson(unittest.TestCase):
    def test_boson_and_quarks(self):
        V, q1, q2, hasV = vb.hadronicBoson(gen(EVENTS + [PHOTON_FIRST, PHOTON_ONLY]))
        self.assertEqual(ak.to_list(hasV), [True, False, True, False, True, False])
        self.assertEqual(ak.to_list(V.pt), [400, None, 500, None, 300, None])
        self.assertEqual(ak.to_list(V.pdgId), [23, None, 24, None, 23, None])
        quarks = [sorted(x) if None not in x else list(x) for x in zip(ak.to_list(q1.phi), ak.to_list(q2.phi))]
        self.assertEqual(quarks, [[0.02, 0.6], [None, None], [-1.5, 1.5], [None, None], [-1.0, -1.0], [None, None]])
        self.assertEqual(ak.to_list(q1.pt)[4], 150)        # hardest first


if __name__ == '__main__':
    unittest.main()
