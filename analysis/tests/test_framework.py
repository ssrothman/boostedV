"""Tests of the expression language, regions, histograms and plotting helpers (run from analysis/:
python3 -m unittest discover -s tests). ANALYSIS_TEST_NANO=<ZX_test NANO> adds a comparison with uproot on a real file.
"""
import os
import unittest

import awkward as ak
import numpy as np

from bvana import plotting
from bvana.config import Config, ConfigError
from bvana.expr import Expr, ExprError, compileVariables
from bvana.histograms import makeAxis


def syntheticEvents():
    """Three events, reco level, channel Zmumu; jets with a veto flag (first jet of event 0, so kept and full jet
    positions differ) and an EEC observable 'X' (2 entries per jet)."""
    jets = [[(350, 1.0, True, 0.3), (400, 0.5, False, 0.1), (250, 2.2, False, 0.7)],
            [(500, -0.3, False, 0.9), (320, 0.1, False, 0.2)],
            [(210, 0.0, False, 0.5)]]
    jet = ak.Array([[{'pt': float(p), 'eta': e, 'vetoZmumu': v, 'tau': t} for p, e, v, t in ev] for ev in jets])
    nEnt = [[2] * len(ev) for ev in jets]
    entries = []
    for ev in jets:
        row = []
        for k in range(len(ev)):
            row += [{'iJet': k, 'dR': 0.0, 'weight': 0.01 * (k + 1), 'symfactor': 1},
                    {'iJet': k, 'dR': 0.1 * (k + 1), 'weight': 0.1 * (k + 1), 'symfactor': 2}]
        entries.append(row)
    per = ak.Array([[{'nEntries': n, 'E_jet': 100.0, 'n': 1.0, 'N': 2} for n in ev] for ev in nEnt])
    boson = ak.Array([[{'pt': 250.0, 'mass': 91.0}], [{'pt': 150.0, 'mass': 90.0}], [{'pt': 300.0, 'mass': 92.0}]])
    leptons = ak.Array([[{'pt': 120.0, 'tight': True}, {'pt': 60.0, 'tight': True}],
                        [{'pt': 80.0, 'tight': True}, {'pt': 50.0, 'tight': False}],
                        [{'pt': 200.0, 'tight': True}, {'pt': 100.0, 'tight': True}]])
    return ak.zip({'RecoJet': jet, 'RecoX': per, 'RecoXEntries': ak.Array(entries), 'ZmumuBoson': boson,
                   'ZmumuLeptons': leptons, 'Selection': ak.zip({'Zmumu': np.array([True, True, True])}),
                   'PuppiMET': ak.zip({'pt': np.array([10.0, 20.0, 30.0])}),
                   'genWeight': np.array([1.0, 2.0, 3.0])}, depth_limit=1)


def config(cuts, hist=None):
    return Config({'regions': {'R': {'level': 'reco', 'channel': 'Zmumu', 'cuts': cuts}},
                   'binning': {'b': {'regular': [10, 0, 1]}},
                   'histograms': hist or {'h': {'granularity': 'eec:X', 'axes': [{'var': 'eec.dR', 'bins': 'b'}]}}})


class Expressions(unittest.TestCase):
    def test_rejected(self):
        for text in ('__import__("os")', 'jets.pt[0]', '"a" == jets.pt', 'foo(jets.pt)', 'lambda: 1', 'x.pt',
                     'abs(jets.pt, 2)', 'max(jets.pt, axis=1)', 'jets.pt if True else 1', 'num(boson.pt)',
                     'jets.pt + leptons.pt', 'eec.dR < leptons.pt'):
            with self.assertRaises(ExprError, msg=text):
                Expr(text)

    def test_levels(self):
        for text, level in (('jets.pt', 'jet'), ('num(jets)', 'event'), ('jets.pt / boson.pt', 'jet'),
                            ('sum(eec.weight)', 'jet'), ('max(sum(eec.weight))', 'event'), ('all(leptons.tight)', 'event'),
                            ('event.PV.npvsGood > 3', 'event'), ('200 < boson.pt < 400', 'event'), ('eec.dR * jets.pt', 'eec')):
            self.assertEqual(Expr(text).level, level, text)

    def test_evaluation(self):
        ns = {'jets': ak.Array([[{'pt': 1.0}, {'pt': 5.0}], []]), 'boson': ak.Array([{'pt': 2.0}, {'pt': 9.0}])}
        self.assertEqual(Expr('0 < jets.pt < 4')(ns).tolist(), [[True, False], []])
        self.assertEqual(Expr('not (jets.pt > 2) or jets.pt == 5').__call__(ns).tolist(), [[True, True], []])
        from bvana.expr import asBool
        self.assertEqual(asBool(Expr('max(jets.pt) > 3')(ns)).tolist(), [True, False])  # no jets: None -> False
        v = compileVariables({'r': 'jets.pt / boson.pt', 'r2': 'r * 2'})
        self.assertEqual(Expr('r2', v)(ns).tolist(), [[1.0, 5.0], []])

    def test_field_shadowed_by_vector_method(self):
        import vector
        vector.register_awkward()
        jets = ak.zip({'pt': [[300.0]], 'eta': [[0.0]], 'phi': [[0.0]], 'mass': [[10.0]], 'tau2': [[0.25]]},
                      with_name='Momentum4D')
        self.assertEqual(Expr('jets.tau2')({'jets': jets}).tolist(), [[0.25]])   # getattr gives the proper time squared
        self.assertAlmostEqual(Expr('jets.energy')({'jets': jets}).tolist()[0][0], np.hypot(300.0, 10.0))


class Regions(unittest.TestCase):
    def test_chained_jet_cuts_and_eec_entries(self):
        cfg = config(['jets.pt > 300', 'abs(jets.eta) < 0.8'])
        view, flow = cfg.regions['R'].select(syntheticEvents(), ak.Array([1.0, 2.0, 3.0]))
        # The vetoed jet (event 0, jet 0) is never seen; pt > 300 keeps ev0 j1 and ev1 j0, j1, which all pass the eta cut.
        self.assertEqual(view.jetIdx.tolist(), [[1], [0, 1], []])
        self.assertEqual([v['jets'] for v in flow.values()], [5, 3, 3])
        nested, perJet = view.entries('X')
        self.assertEqual(nested.dR.tolist(), [[[0.0, 0.2]], [[0.0, 0.1], [0.0, 0.2]], []])

    def test_second_jet_cut_is_relative_to_kept_jets(self):
        cfg = config(['jets.pt > 300', 'jets.tau > 0.5'])
        view, _ = cfg.regions['R'].select(syntheticEvents(), ak.Array([1.0, 2.0, 3.0]))
        self.assertEqual(view.jetIdx.tolist(), [[], [0], []])

    def test_event_and_lepton_cuts(self):
        cfg = config(['all(leptons.tight)', 'boson.pt > 200', 'num(jets) >= 1'])
        view, flow = cfg.regions['R'].select(syntheticEvents(), ak.Array([1.0, 2.0, 3.0]))
        self.assertEqual([v['n'] for v in flow.values()], [3, 2, 2, 2])
        self.assertEqual([v['sumw'] for v in flow.values()], [6.0, 4.0, 4.0, 4.0])
        self.assertEqual(ak.to_list(view.weight), [1.0, 3.0])

    def test_misaligned_jet_mask_is_rejected(self):
        view, _ = config([]).regions['R'].select(syntheticEvents(), ak.Array([1.0, 2.0, 3.0]))
        with self.assertRaises(ValueError):
            view.keepJets(ak.Array([[True], [True, True], [True]]))  # event 0 has two kept jets

    def test_lepton_level_cut_requires_every_lepton(self):
        view, flow = config(['leptons.tight']).regions['R'].select(syntheticEvents(), ak.Array([1.0, 2.0, 3.0]))
        self.assertEqual(ak.to_list(view.weight), [1.0, 3.0])

    def test_back_to_back_columns(self):
        """With b2b<ch> in the NANO: the jets are the b2b<ch> ones (not the non-vetoed ones: in event 0 those would be
        jets 1 and 2); <ch> already includes <ch>B2B, which is not applied again."""
        ev = syntheticEvents()
        ev['Selection'] = ak.zip({'Zmumu': np.array([True, False, True]), 'ZmumuB2B': np.array([True, True, False])})
        b2b = ak.Array([[False, False, True], [True, False], [True]])
        ev['RecoJet'] = ak.zip({f: ev['RecoJet'][f] for f in ev['RecoJet'].fields} | {'b2bZmumu': b2b})
        view, flow = config([]).regions['R'].select(ev, ak.Array([1.0, 2.0, 3.0]))
        self.assertEqual(list(flow), ['channel'])
        self.assertEqual([(v['n'], v['sumw'], v['jets']) for v in flow.values()], [(2, 4.0, 2)])
        self.assertEqual(view.jetIdx.tolist(), [[2], [0]])
        dR = view.entries('X')[0].dR
        self.assertEqual(ak.num(dR, axis=2).tolist(), [[2], [2]])
        np.testing.assert_allclose(ak.flatten(dR, axis=None).to_numpy(), [0.0, 0.3, 0.0, 0.1])
        view, flow = config(['jets.pt > 240']).regions['R'].select(ev, ak.Array([1.0, 2.0, 3.0]))
        self.assertEqual(list(flow), ['channel', 'jets.pt > 240'])
        self.assertEqual(view.jetIdx.tolist(), [[2], []])

    def test_config_errors(self):
        with self.assertRaises(ConfigError):
            config(['eec.dR > 0'])  # per-entry cuts belong to histograms
        with self.assertRaises(ConfigError):
            config([], {'h': {'granularity': 'jet', 'axes': [{'var': 'eec.dR', 'bins': 'b'}]}})
        with self.assertRaises(ConfigError):
            config([], {'h': {'granularity': 'jet', 'axes': [{'var': 'jets.pt', 'bins': 'nope'}]}})
        with self.assertRaises(ConfigError):
            config([], {'h': {'granularity': 'jet', 'axs': []}})


class Histograms(unittest.TestCase):
    def test_binnings(self):
        np.testing.assert_allclose(makeAxis({'log': [3, 1e-3, 1]}, 'a', '').edges, [1e-3, 1e-2, 1e-1, 1])
        np.testing.assert_allclose(makeAxis({'regular': [2, 0, 1]}, 'a', '').edges, [0, 0.5, 1])
        np.testing.assert_allclose(makeAxis({'edges': [0, 1, 5]}, 'a', '').edges, [0, 1, 5])
        self.assertEqual(len(makeAxis({'integer': [0, 4]}, 'a', '').edges), 5)

    def test_eec_fill_weights(self):
        hist = {'h': {'granularity': 'eec:X', 'cuts': ['eec.dR > 0'], 'axes': [{'var': 'eec.dR', 'bins': 'b'}]},
                'r': {'granularity': 'eec:X', 'renormalise': 'jets.pt', 'axes': [{'var': 'eec.dR', 'bins': 'b'}]}}
        cfg = config(['jets.pt > 300'], hist)
        view, _ = cfg.regions['R'].select(syntheticEvents(), ak.Array([1.0, 2.0, 3.0]))
        h = cfg.histograms['h'].fill(view)
        # kept: ev0 j1 (w 1), ev1 j0 and j1 (w 2); dR > 0 entries of jet k: weight 0.1 (k+1) x symfactor 2
        self.assertAlmostEqual(h.sum(flow=True).value, 1 * 0.4 + 2 * 0.2 + 2 * 0.4)
        r = cfg.histograms['r'].fill(view)
        expect = 1 * (0.02 + 0.4) * (100 / 400) ** 2 + 2 * (0.01 + 0.2) * (100 / 500) ** 2 + 2 * (0.02 + 0.4) * (100 / 320) ** 2
        self.assertAlmostEqual(r.sum(flow=True).value, expect)

    def test_shared_intermediates_match_fresh_fills(self):
        hist = {'cut': {'granularity': 'eec:X', 'cuts': ['eec.dR > 0'], 'axes': [{'var': 'eec.dR', 'bins': 'b'}]},
                'cut2': {'granularity': 'eec:X', 'cuts': ['eec.dR > 0'],
                         'axes': [{'var': 'eec.dR', 'bins': 'b'}, {'var': 'eec.dR * jets.pt / 1000', 'bins': 'b', 'name': 'x'}]},
                'nocut': {'granularity': 'eec:X', 'axes': [{'var': 'eec.dR', 'bins': 'b'}]},
                'renorm': {'granularity': 'eec:X', 'cuts': ['eec.dR > 0'], 'renormalise': 'jets.pt',
                           'axes': [{'var': 'eec.dR', 'bins': 'b'}]},
                'jet': {'granularity': 'jet', 'axes': [{'var': 'jets.tau', 'bins': 'b'}]}}
        cfg = config([], hist)
        sel = lambda: cfg.regions['R'].select(syntheticEvents(), ak.Array([1.0, 2.0, 3.0]))[0]
        calls = []
        orig = Expr._eval

        def spy(self, n, ns):
            if n is self.tree:
                calls.append(self.text)
            return orig(self, n, ns)
        Expr._eval = spy
        try:
            view = sel()
            shared = {k: d.fill(view) for k, d in cfg.histograms.items()}
        finally:
            Expr._eval = orig
        self.assertEqual(calls.count('eec.dR'), 1)
        self.assertEqual(calls.count('eec.dR > 0'), 1)
        for k, d in cfg.histograms.items():
            fresh = d.fill(sel())
            np.testing.assert_array_equal(shared[k].values(flow=True), fresh.values(flow=True))
            np.testing.assert_array_equal(shared[k].variances(flow=True), fresh.variances(flow=True))
        # the cut, the renormalisation and the weightless path must not share results with each other
        self.assertNotEqual(shared['cut'].sum(flow=True).value, shared['nocut'].sum(flow=True).value)
        self.assertNotEqual(shared['cut'].sum(flow=True).value, shared['renorm'].sum(flow=True).value)

    def test_mixed_granularity_axes(self):
        hist = {'h': {'granularity': 'jet', 'axes': [{'var': 'jets.tau', 'bins': 'b'},
                                                     {'var': 'boson.pt / 1000', 'bins': 'b', 'name': 'zpt'}]}}
        cfg = config([], hist)
        view, _ = cfg.regions['R'].select(syntheticEvents(), ak.Array([1.0, 2.0, 3.0]))
        h = cfg.histograms['h'].fill(view)
        self.assertAlmostEqual(h.sum(flow=True).value, 1 * 2 + 2 * 2 + 3 * 1)
        # boson.pt / 1000 = 0.25, 0.15, 0.30 -> bins 2, 1, 3 with 2, 2 and 1 jets of weights 1, 2, 3
        self.assertEqual(h[{'jets_tau': sum}].values()[:4].tolist(), [0.0, 4.0, 2.0, 3.0])


class Plotting(unittest.TestCase):
    def test_log_width_integrates_to_total(self):
        import hist
        h = hist.Hist(makeAxis({'log': [5, 1e-3, 1]}, 'x', ''), storage='weight')
        h.fill([2e-3, 0.02, 0.3, 0.5], weight=[1, 2, 3, 4])
        v, _ = plotting.values(h, norm='area', width='log')
        self.assertAlmostEqual(np.sum(v * np.diff(np.log(h.axes[0].edges))), 1.0)

    def test_slice(self):
        import hist
        h = hist.Hist(makeAxis({'edges': [0, 1, 2, 3]}, 'a', ''), makeAxis({'regular': [2, 0, 2]}, 'b', ''))
        h.fill([0.5, 1.5, 2.5], [0.5, 1.5, 0.5])
        r = plotting.reduce(h, [plotting.parseSlice('a=1:3')], ['b'])
        self.assertEqual(r.values().tolist(), [1.0, 1.0])
        with self.assertRaises(ValueError):
            plotting.reduce(h, [plotting.parseSlice('a=1.5:3')])

    def test_ratio_sum_lines_per_sample_and_total(self):
        import hist
        hs = {}
        for name, v in (('DYa', [2.0, 4.0]), ('DYb', [2.0, 4.0]), ('VV', [1.0, 3.0]), ('TT', [2.0, 4.0])):
            h = hist.Hist(makeAxis({'regular': [2, 0, 2]}, 'x', ''), storage='weight')
            h.fill([0.5, 1.5], weight=v)
            hs[name] = h
        hs = plotting.group(hs, ['DY=DY'])
        self.assertEqual(list(hs), ['DY', 'VV', 'TT'])
        np.testing.assert_allclose(hs['DY'].values(), [4, 8])
        fig = plotting.plot1d(hs, stack=True, ratioSum=('DY', ['DY']))
        conts = fig.axes[1].containers[::2]                  # histplot adds two containers per curve
        self.assertEqual(len(fig.axes[1].containers), 6)
        self.assertEqual(len(conts), 3)                      # VV, TT, all
        np.testing.assert_allclose(conts[0][0].get_ydata(), [5 / 4, 11 / 8])
        np.testing.assert_allclose(conts[1][0].get_ydata(), [6 / 4, 12 / 8])
        np.testing.assert_allclose(conts[2][0].get_ydata(), [7 / 4, 15 / 8])
        # VV err = sqrt(var VV) / DY; each bin has one weighted entry
        np.testing.assert_allclose(conts[0][2][0].get_segments()[0][:, 1], [1.25 - 0.25, 1.25 + 0.25])
        with self.assertRaises(ValueError):
            plotting.plot1d(hs, norm='area', ratioSum=('DY', ['DY']))
        with self.assertRaises(ValueError):
            plotting.group(hs, ['X=nomatch'])


@unittest.skipUnless(os.environ.get('ANALYSIS_TEST_NANO'), 'set ANALYSIS_TEST_NANO')
class RealFile(unittest.TestCase):
    def test_against_uproot(self):
        import uproot
        from coffea.nanoevents import NanoEventsFactory
        from bvana.processor import Processor
        from bvana.schema import BoostedVSchema
        f = os.environ['ANALYSIS_TEST_NANO']
        hist = {'bosonPt': {'axes': [{'var': 'boson.pt', 'bins': {'regular': [10, 0, 2000]}}]},
                'jetPt': {'granularity': 'jet', 'axes': [{'var': 'jets.pt', 'bins': {'regular': [10, 0, 3000]}}]},
                'E2C': {'granularity': 'eec:E2Cn1', 'cuts': ['eec.dR > 0'], 'axes': [{'var': 'eec.dR', 'bins': 'b'}]}}
        cfg = Config({'regions': {'R': {'level': 'reco', 'channel': 'Zmumu',
                                        'cuts': ['jets.pt > 250', 'abs(jets.eta) < 1.5']}},
                      'binning': {'b': {'log': [10, 1e-4, 1]}}, 'histograms': hist})
        ev = NanoEventsFactory.from_root({f: 'Events'}, schemaclass=BoostedVSchema, mode='eager',
                                         metadata={'sample': 'S', 'isMC': True}).events()
        out = Processor(cfg).process(ev)
        a = uproot.open(f)['Events'].arrays(library='np')
        zpt = jpt = e2c = 0.0
        nJets = 0
        # A back-to-back NANO: the jets are the b2bZmumu ones.
        b2b = 'RecoJet_b2bZmumu' in a
        passed = a['Selection_Zmumu']
        for e in np.nonzero(passed)[0]:
            w = float(a['genWeight'][e])  # float64 sums, as the histograms
            zpt += w
            mine = a['RecoJet_b2bZmumu'][e] if b2b else ~a['RecoJet_vetoZmumu'][e]
            keep = mine & (a['RecoJet_pt'][e] > 250) & (np.abs(a['RecoJet_eta'][e]) < 1.5)
            nJets += keep.sum()
            jpt += w * keep.sum()
            iJ, dR = a['RecoE2Cn1Entries_iJet'][e], a['RecoE2Cn1Entries_dR'][e]
            sel = keep[iJ] & (dR > 0)
            e2c += w * np.sum((a['RecoE2Cn1Entries_weight'][e] * a['RecoE2Cn1Entries_symfactor'][e])[sel])
        self.assertGreater(nJets, 0)
        self.assertGreater(e2c, 0)
        for name, ref in (('bosonPt', zpt), ('jetPt', jpt), ('E2C', e2c)):
            got = out['hists'][name]['R']['S'].sum(flow=True).value
            self.assertAlmostEqual(got, ref, delta=1e-9 * abs(ref), msg=name)


if __name__ == '__main__':
    unittest.main()
