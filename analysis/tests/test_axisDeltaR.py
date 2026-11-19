"""Tests of axisDeltaR: the jets selected for each truth reference."""
import unittest

import awkward as ak

import axisDeltaR


class TruthMask(unittest.TestCase):
    def test_selection_per_truth(self):
        # Status 0 bosons of 4 (gamma*), 80, 91, 125 and 200 GeV; a decay quark (1); QCD partons (3); no match (2), whose
        # axis is the jet itself and can have a boson-like mass.
        jets = ak.Array([[{'axisTruthStatus': s, 'axisTruthMass': m} for s, m in
                          ((0, 4.0), (0, 80.0), (0, 91.2), (0, 125.0), (0, 200.0), (1, 0.33), (3, 0.0), (3, 4.8),
                           (2, 0.0), (2, 91.0))]])
        expect = {'vw': [0, 1, 1, 0, 0, 0, 0, 0, 0, 0], 'higgs': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                  'parton': [0, 0, 0, 0, 0, 0, 1, 1, 0, 0]}
        for truth, e in expect.items():
            self.assertEqual(ak.to_list(axisDeltaR.truthMask(jets, truth))[0], [bool(x) for x in e], truth)


if __name__ == '__main__':
    unittest.main()
