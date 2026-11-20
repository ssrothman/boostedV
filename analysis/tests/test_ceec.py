"""Tests of the constituent filters and the srcIdx join of bvana/ceec.py."""
import unittest

import awkward as ak
import numpy as np

from bvana import ceec


def parts(rows):
    """rows: [event][jet][dict] -> awkward particles."""
    return ak.Array(rows)


BASE = {'pt': 1.0, 'eta': 0.0, 'phi': 0.0, 'charge': 1, 'source': 0, 'fromPV': 3, 'dz': 0.0, 'dxy': 0.0,
        'puppiWeightRaw': 1.0}


def p(**kw):
    d = dict(BASE)
    d.update(kw)
    return d


class Select(unittest.TestCase):
    def mask(self, plist, sel, jet=(0.0, 0.0), bosonPhi=np.pi):
        a = parts([[plist]])
        jets = ak.Array([[{'eta': jet[0], 'phi': jet[1]}]])
        boson = ak.Array([{'phi': bosonPhi}])
        return ak.to_list(ceec.select(a, sel, jets, boson))[0][0]

    def test_vertex_cuts_spare_neutrals(self):
        ps = [p(), p(fromPV=1), p(dz=0.3), p(charge=0, fromPV=0, dz=np.nan, dxy=np.nan)]
        self.assertEqual(self.mask(ps, {'minFromPV': 2}), [True, False, True, True])
        self.assertEqual(self.mask(ps, {'maxAbsDz': 0.1}), [True, True, False, True])

    def test_displaced_and_lost_tracks(self):
        ps = [p(dxy=0.01), p(dxy=-0.2), p(dxy=0.2, source=1), p(charge=0, dxy=np.nan)]
        self.assertEqual(self.mask(ps, {'minAbsDxy': 0.05}), [False, True, True, True])
        self.assertEqual(self.mask(ps, {'minAbsDxy': 0.05, 'lostTracks': False, 'charged': True}),
                         [False, True, False, False])

    def test_dRJet_across_phi_wrap_and_hemisphere(self):
        ps = [p(phi=3.1), p(phi=-3.1), p(phi=2.0), p(eta=0.7, phi=3.0)]
        self.assertEqual(self.mask(ps, {'dRJet': 0.8}, jet=(0.0, 3.1)), [True, True, False, True])
        # boson at phi 0: the recoil hemisphere is |phi| > pi/2
        self.assertEqual(self.mask([p(phi=1.5), p(phi=1.6), p(phi=-3.0)], {'hemisphere': True}, bosonPhi=0.0),
                         [False, True, True])

    def test_puppi(self):
        ps = [p(puppiWeightRaw=0.0), p(puppiWeightRaw=0.4), p(puppiWeightRaw=1.0)]
        self.assertEqual(self.mask(ps, {'puppiWeighted': True}), [False, True, True])
        self.assertEqual(self.mask(ps, {'minPuppi': 0.5}), [False, False, True])


class Join(unittest.TestCase):
    def test_details_by_srcIdx_within_the_event(self):
        jet = ak.Array([[[{'srcIdx': 4}, {'srcIdx': 7}], [{'srcIdx': 9}]], [[{'srcIdx': 4}]]])
        ev = ak.Array([
            [{'srcIdx': 7, 'source': 0, 'fromPV': 3, 'dz': 0.1, 'dxy': 0.2, 'puppiWeightRaw': 0.5},
             {'srcIdx': 4, 'source': 0, 'fromPV': 1, 'dz': 0.3, 'dxy': 0.4, 'puppiWeightRaw': 1.0},
             {'srcIdx': 9, 'source': 1, 'fromPV': 3, 'dz': 0.5, 'dxy': 0.6, 'puppiWeightRaw': 1.0}],   # a lost track
            [{'srcIdx': 5, 'source': 0, 'fromPV': 3, 'dz': 0.7, 'dxy': 0.8, 'puppiWeightRaw': 1.0}]])
        out = ceec.joinDetails(jet, ev)
        self.assertEqual(ak.to_list(out.fromPV), [[[1, 3], [-1]], [[-1]]])
        dz = ak.to_list(out.dz)
        self.assertEqual(dz[0][0], [0.3, 0.1])
        self.assertTrue(np.isnan(dz[0][1][0]) and np.isnan(dz[1][0][0]))

    def test_check(self):
        good = {'source': 'jet', 'N': 2, 'n': 1.0, 'bins': 'b', 'norm': 'jetPt'}
        ceec.check('x', good)
        for bad in ({'source': 'evt'}, {'norm': 'sumE'}, {'select': {'dRJet': 0.8}}, {'select': {'foo': 1}},
                    {'shape': 'xi'}, {'source': 'event'}):
            with self.assertRaises(ceec.CeecError, msg=str(bad)):
                ceec.check('x', dict(good, **bad))


if __name__ == '__main__':
    unittest.main()
