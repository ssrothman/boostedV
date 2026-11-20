"""Tests of the jet truth match (bvana/truth.py) on a hand-made GenPart record."""
import unittest

import awkward as ak
import numpy as np
from coffea.nanoevents.methods import vector

from bvana.truth import truthColumns

HP = (1 << 7) | (1 << 8)      # isHardProcess and fromHardProcess
FHP = 1 << 8                  # fromHardProcess only


def gen(events):
    """events: [[(pdgId, status, flags, mother, pt, eta, phi)]]."""
    keys = ['pdgId', 'status', 'statusFlags', 'genPartIdxMother', 'pt', 'eta', 'phi']
    f = {k: [[p[i] for p in ev] for ev in events] for i, k in enumerate(keys)}
    f['mass'] = [[0.0] * len(ev) for ev in events]
    return ak.zip(f, with_name='PtEtaPhiMLorentzVector', behavior=vector.behavior)


def jets(events):
    f = {k: [[j[i] for j in ev] for ev in events] for i, k in enumerate(['pt', 'eta', 'phi'])}
    f['mass'] = [[0.0] * len(ev) for ev in events]
    return ak.zip(f, with_name='PtEtaPhiMLorentzVector', behavior=vector.behavior)


EVENTS = [
    [(21, 21, HP, -1, 50, 0.0, 0.1),        # 0 incoming gluon: never a candidate
     (23, 22, HP, -1, 401, 0.0, 0.05),      # 1 Z, not the last copy (daughter Z)
     (23, 62, 0, 1, 400, 0.0, 0.3),         # 2 Z last copy -> d dbar: the hadronic boson
     (1, 23, HP, 2, 200, 0.0, 0.02),        # 3 d from the Z, closer to jet 0 than the Z
     (-1, 23, HP, 2, 200, 0.0, 0.6),        # 4
     (21, 23, HP, -1, 300, 0.0, 2.05),      # 5 outgoing hard gluon
     (23, 62, 0, -1, 350, 0.0, -2.5),       # 6 Z -> mu mu: not hadronic
     (13, 1, 0, 6, 175, 0.0, -2.4),         # 7
     (-13, 1, 0, 6, 175, 0.0, -2.6),        # 8
     (22, 1, 0, -1, 30, 0.0, -2.45),        # 9 shower photon with a quark daughter: excluded
     (2, 1, 0, 9, 15, 0.0, -2.45),          # 10
     (22, 22, FHP, -1, 250, 1.5, 1.1),      # 11 hard photon -> u ubar: a boson
     (2, 1, 0, 11, 125, 1.5, 1.0),          # 12
     (21, 51, 0, 1, 5, 3.0, 3.0)],          # 13 gluon daughter of Z copy 1, which stays excluded by its Z daughter
    [],
    [(24, 62, 0, -1, 500, 0.0, 0.0),        # 0 W -> u dbar, beyond dRMax of the jet
     (2, 23, HP, 0, 250, 0.0, 1.5),         # 1 u from the W: decay quark
     (-1, 23, HP, 0, 250, 0.0, -1.5)],      # 2
    [(2, 21, HP, -1, 300, 0.0, 0.1)],       # incoming quark only: no match
]
JETS = [[(400, 0.0, 0.0), (300, 0.0, 2.0), (350, 0.0, -2.5), (250, 1.5, 1.0)], [(300, 0.0, 0.0)], [(250, 0.0, 1.5)], [(300, 0.0, 0.0)]]


class TruthMatch(unittest.TestCase):
    def setUp(self):
        self.out = {k: ak.to_list(v) for k, v in truthColumns(jets(JETS), gen(EVENTS), 0.8).items()}

    def test_status(self):
        self.assertEqual(self.out['truthStatus'], [[0, 3, 2, 0], [2], [1], [2]])

    def test_matched_particle(self):
        self.assertEqual(self.out['truthPdgId'][0][:2] + self.out['truthPdgId'][0][3:], [23, 21, 22])
        self.assertEqual(self.out['truthPt'][0][0], 400)       # the last copy, not 401 or the closer quark
        self.assertEqual(self.out['truthPt'][2], [250])

    def test_unmatched_is_nan(self):
        for k in ('truthPt', 'truthEta', 'truthPhi', 'truthMass', 'truthPdgId'):
            self.assertTrue(np.isnan(self.out[k][0][2]) and np.isnan(self.out[k][1][0]), k)

    def test_dRMax(self):
        out = truthColumns(jets(JETS), gen(EVENTS), 0.01)
        self.assertEqual(ak.to_list(out['truthStatus']), [[2, 2, 2, 2], [2], [1], [2]])


if __name__ == '__main__':
    unittest.main()
