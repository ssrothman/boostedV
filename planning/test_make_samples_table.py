import unittest
from unittest import mock

import make_samples_table as m

SUF = "Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6"


def ds(pd, proc=SUF + "-v2"):
    return f"/{pd}/{proc}/MINIAODSIM"


TT = "TTto4Q_TuneCP5_13p6TeV_powheg-pythia8"


class TestParse(unittest.TestCase):
    def test_nominal(self):
        self.assertEqual(m.parse_dataset(ds(TT)), (TT, None, "v2"))

    def test_ext(self):
        self.assertEqual(m.parse_dataset(ds(TT, SUF + "_ext1-v3")), (TT, "ext1", "v3"))

    def test_rejects_special_processing(self):
        bad = SUF.replace("v4-", "v4-FS22_") + "-v2"
        self.assertIsNone(m.parse_dataset(ds(TT, bad)))

    def test_rejects_other_tier_and_campaign(self):
        self.assertIsNone(m.parse_dataset(ds(TT).replace("MINIAODSIM", "NANOAODSIM")))
        self.assertIsNone(m.parse_dataset(ds(TT, SUF.replace("22EE", "23") + "-v2")))


class TestGenerator(unittest.TestCase):
    def test_known(self):
        self.assertEqual(m.generator(TT), "POWHEG + Pythia8")
        self.assertEqual(m.generator("QCD_PT-50to80_TuneCP5_13p6TeV_pythia8"), "Pythia8")

    def test_unknown_raises(self):
        with self.assertRaises(KeyError):
            m.generator("X_TuneCP5_13p6TeV_sherpa")


class TestSelect(unittest.TestCase):
    def test_real_families_pick_nominal_only(self):
        pool = [
            ds(TT), ds(TT, SUF + "_ext1-v2"),
            ds("TTto4Q_TuneCP5Up_13p6TeV_powheg-pythia8"),
            ds("TTto4Q_TuneCP5_ERDOn_13p6TeV_powheg-pythia8"),
            ds("TWminusto4Q_TuneCP5_13p6TeV_powheg-pythia8"),
            ds("TWminusto4Q_DS_TuneCP5_13p6TeV_powheg-pythia8"),
            ds("TWminusto4Q_Hdamp-158_TuneCP5_13p6TeV_powheg-pythia8"),
            ds("QCD_PT-80to120_TuneCP5_13p6TeV_pythia8"),
            ds("QCD_PT-80to120_EMEnriched_TuneCP5_13p6TeV_pythia8"),
            ds("QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8"),
        ]
        fams = [f for f in m.FAMILIES if f[0] in (r"$t\bar t$", "Single top, $tW$", "QCD multijet")
                and "MLM" not in f[1]]
        with mock.patch.object(m, "FAMILIES", fams):
            rows = m.select(pool)
        got = {r[3]: r[2] for r in rows}
        self.assertEqual(set(got), {pool[0], pool[1], pool[4], pool[7]})
        self.assertTrue(got[pool[1]].endswith("; ext1"))
        self.assertFalse(got[pool[0]].endswith("ext1"))

    def test_empty_family_raises(self):
        with mock.patch.object(m, "FAMILIES", [("x", "NoSuchSample", m.LOW, "")]):
            with self.assertRaises(ValueError):
                m.select([ds(TT)])


class TestRender(unittest.TestCase):
    def test_row(self):
        row = m.latex_row("P", "G", "TBD", 1234567, "Available", "C", ds(TT), m.HIGH)
        self.assertEqual(row, r"P & G & TBD & 1\,234\,567 & Available & C & \nolinkurl{%s} & High \\"
                         % ds(TT))

    def test_missing_row(self):
        row = m.latex_row("P", "---", "---", None, "To be produced", "C", None, m.LOW)
        self.assertIn("& --- & To be produced & C & --- & Low", row)

    def test_midrule_between_processes_only(self):
        rows = [("A", m.LOW, "c", ds(TT)), ("A", m.LOW, "c", ds(TT, SUF + "_ext1-v2")),
                ("B", m.LOW, "c", ds(TT))]
        lines = m.render(rows, {r[3]: 1 for r in rows}).splitlines()
        self.assertEqual([i for i, l in enumerate(lines) if l == r"\midrule"],
                         [2, 4])


class TestInclusive(unittest.TestCase):
    NLO, ALT = "NLO", "LO alternative"

    def rows(self, *spec):
        return [(proc, m.LOW, comment, ds(pd, proc_str)) for proc, comment, pd, proc_str in spec]

    def test_unbinned_non_ext_from_preferred_family(self):
        dy = "DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8"
        rows = self.rows(
            ("Z", self.NLO, "DYto2L-2Jets_MLL-50_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8", SUF + "-v3"),
            ("Z", self.NLO, "DYto2L-2Jets_MLL-50_PTLL-100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8", SUF + "-v2"),
            ("Z", self.NLO, dy, SUF + "_ext1-v2"),
            ("Z", self.NLO, dy, SUF + "-v5"),
            ("Z", self.ALT, "DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8", SUF + "-v2"),
        )
        chosen, missing = m.inclusive(rows)
        self.assertEqual([r[3] for r in chosen], [ds(dy, SUF + "-v5")])
        self.assertEqual(missing, [])

    def test_keeps_all_decay_splits(self):
        pds = ["TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8", "TTto4Q_TuneCP5_13p6TeV_powheg-pythia8"]
        rows = self.rows(*[("tt", self.NLO, pd, SUF + "-v2") for pd in pds])
        self.assertEqual([r[3] for r in m.inclusive(rows)[0]], [r[3] for r in rows])

    def test_falls_back_to_alternative_then_missing(self):
        alt = "WtoLNu-4Jets_TuneCP5_13p6TeV_madgraphMLM-pythia8"
        rows = self.rows(
            ("W", self.NLO, "WtoLNu-2Jets_PTLNu-100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8", SUF + "-v2"),
            ("W", self.ALT, alt, SUF + "-v2"),
            ("Q", self.NLO, "QCD_PT-80to120_TuneCP5_13p6TeV_pythia8", SUF + "-v2"),
            ("Q", self.ALT, "QCD-4Jets_HT-40to70_TuneCP5_13p6TeV_madgraphMLM-pythia8", SUF + "-v2"),
            ("G", self.NLO, "GJ_PTG-40_TuneCP5_13p6TeV_amcatnlo-pythia8", SUF + "-v2"),
        )
        chosen, missing = m.inclusive(rows)
        self.assertEqual([r[3] for r in chosen], [ds(alt)])
        self.assertEqual(missing, ["Q", "G"])

    def test_decay_inclusive_supersedes_split(self):
        tq = "TBbarQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8"
        tbq = "TbarBQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8"
        rows = self.rows(
            ("st", self.NLO, "TBbarQto2Q-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8", SUF + "-v2"),
            ("st", self.NLO, tq, SUF + "-v2"),
            ("st", self.NLO, "TbarBQtoLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8", SUF + "-v2"),
            ("st", self.NLO, tbq, SUF + "-v2"),
            ("tt", self.NLO, "TTto4Q_TuneCP5_13p6TeV_powheg-pythia8", SUF + "-v2"),
            ("tt", self.NLO, "TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8", SUF + "-v2"),
        )
        chosen = [r[3] for r in m.inclusive(rows)[0]]
        self.assertEqual(chosen, [ds(tq), ds(tbq), rows[4][3], rows[5][3]])

    def test_new_higgs_families_pick_intended_samples(self):
        fams = [f for f in m.FAMILIES if "HtoGG" in f[1] or "Hto2Tau" in f[1]]
        self.assertEqual(len(fams), 3)
        want = [ds("GluGluHtoGG_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8"),
                ds("GluGluHto2Tau_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8"),
                ds("VBFHtoGG_M-125_TuneCP5_13p6TeV_amcatnlo-pythia8")]
        reject = [ds("GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8"),
                  ds("GluGluHto2Tau_M-125_TuneCP5_13p6TeV_powhegMiNNLO-pythia8"),
                  ds("GluGluHto2Tau_M-125_2HDM-II_TuneCP5_13p6TeV_powheg-pythia8"),
                  ds("VBFHto2G_M-125_TuneCP5_13p6TeV_powheg-pythia8")]
        with mock.patch.object(m, "FAMILIES", fams):
            got = {r[3] for r in m.select(want + reject)}
        self.assertEqual(got, set(want))

    def test_tth_family_matches_both_powheg_samples_only(self):
        (fam,) = [f for f in m.FAMILIES if f[0] == r"Higgs, $t\bar tH$"]
        pool = [ds("TTH_Hto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8"),
                ds("TTHtoNon2B_M-125_TuneCP5_13p6TeV_powheg-pythia8"),
                ds("TTHtoNon2B-1Jets_M-125_TuneCP5_13p6TeV_amcatnloFXFX-madspin-pythia8"),
                ds("TTH_ctcvcp_4f_TuneCP5_13p6TeV_madgraph-pythia8")]
        with mock.patch.object(m, "FAMILIES", [fam]):
            self.assertEqual([r[3] for r in m.select(pool)], pool[:2])

    def test_tchannel_family_matches_inclusive_not_variations(self):
        (fam,) = [f for f in m.FAMILIES if f[0] == "Single top, $t$-channel"]
        pool = [ds("TBbarQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8"),
                ds("TbarBQtoLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8"),
                ds("TBbarQtoLNu-t-channel-4FS_Par-pThard-1p0_TuneCP5_13p6TeV_powheg-madspin-pythia8"),
                ds("TQbarto2Q-t-channel_TuneCP5_13p6TeV_powheg-pythia8")]
        with mock.patch.object(m, "FAMILIES", [fam]):
            self.assertEqual([r[3] for r in m.select(pool)], pool[:2])

    def test_render(self):
        rows = [("P", m.LOW, "c", ds(TT))]
        lines = m.render_inclusive(rows, ["Q"], {ds(TT): 1234}).splitlines()
        self.assertEqual(lines[0], r"$t\bar t\to 4q$ & POWHEG + Pythia8 & 1\,234 & \nolinkurl{%s} \\"
                         % ds(TT))
        self.assertEqual(lines[1], r"\midrule")
        self.assertEqual(lines[2], r"Q & --- & --- & No inclusive sample; binned samples only \\")
        self.assertEqual(len(lines), 3 + len(m.MISSING))

    def test_splice_two_tables_independent(self):
        text = f"{m.BEGIN_INCL}\na\n{m.END_INCL}\n{m.BEGIN}\nb\n{m.END}\n"
        out = m.splice(m.splice(text, "B"), "A", m.BEGIN_INCL, m.END_INCL)
        self.assertEqual(out, f"{m.BEGIN_INCL}\nA\n{m.END_INCL}\n{m.BEGIN}\nB\n{m.END}\n")


class TestProcessName(unittest.TestCase):
    CASES = [
        ("x", "TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8", r"$t\bar t\to 2\ell2\nu$"),
        ("x", "TTtoLminusNu2Q-3Jets_TuneCP5_13p6TeV_madgraphMLM-pythia8", r"$t\bar t\to \ell^-\bar\nu 2q$"),
        ("x", "TbarBQtoLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8",
         r"$t$-channel $\bar t$: $\bar t\to\bar b\ell\nu$"),
        ("x", "TWminusto4Q_TuneCP5_13p6TeV_powheg-pythia8", r"$tW^-\to 4q$"),
        ("x", "TbarBQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8", r"$t$-channel $\bar t$"),
        ("x", "TbarBtoLminusNuB-s-channel-4FS_TuneCP5_13p6TeV_amcatnlo-pythia8",
         r"$s$-channel $\bar t$: $\bar tb\to\ell^-\bar\nu\bar bb$"),
        ("Triboson", "WWZ_4F_TuneCP5_13p6TeV_amcatnlo-pythia8", "WWZ"),
        ("BSM Z", "ZprimeTobb_M1000_TuneCP5_13p6TeV_pythia8", r"BSM Z, $m_{Z'}=1000$ GeV"),
        ("Higgs, ggH", "GluGluHtoCC_PT-200_M-125_TuneCP5_13p6TeV_powheg-minlo-pythia8",
         r"$gg\to H$: $H\to c\bar c$"),
        ("Higgs, ggZH", "ggZH_Hto2B_Zto2L_M-125_TuneCP5_13p6TeV_powheg-pythia8",
         r"$gg\to ZH$: $Z\to \ell\ell$, $H\to b\bar b$"),
        ("Higgs, ZH", "ZH_Zto2Q_Hto2WtoLNu2Q_M-125_TuneCP5_13p6TeV_powheg-minlo-jhugen-pythia8",
         r"$q\bar q\to ZH$: $Z\to q\bar q$, $H\to WW^*\to\ell\nu q\bar q'$"),
        ("Higgs, WH", "WplusH_Hto2Glu_WtoLNu_M-125_TuneCP5_13p6TeV_powheg-minlo-pythia8",
         r"$W^+H$: $W\to \ell\nu$, $H\to gg$"),
        ("Higgs, VBF", "VBFHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8", r"VBF $H$: $H\to b\bar b$"),
        ("Higgs, VBF", "VBFHtoGG_M-125_TuneCP5_13p6TeV_amcatnlo-pythia8", r"VBF $H$: $H\to gg$"),
        ("Higgs, ggH", "GluGluHto2Tau_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8", r"$gg\to H$: $H\to \tau\tau$"),
        ("Higgs, ttH", "TTHtoNon2B_M-125_TuneCP5_13p6TeV_powheg-pythia8",
         r"$t\bar tH$: $H\to \textrm{non-}b\bar b$"),
        ("Z(qq)+jets", "Zto2Q-2Jets_PTQQ-100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8", "Z(qq)+jets"),
    ]

    def test_cases(self):
        for family, primary, want in self.CASES:
            with self.subTest(primary=primary):
                self.assertEqual(m.process_name(family, primary), want)

    def test_unknown_decay_token_raises(self):
        with self.assertRaises(KeyError):
            m.process_name("x", "TTto2L2Q_TuneCP5_13p6TeV_powheg-pythia8")

    def test_midrules_follow_family_not_name(self):
        tt2l = ds("TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8")
        rows = [("tt", m.LOW, "c", ds(TT)), ("tt", m.LOW, "c", tt2l)]
        lines = m.render(rows, {r[3]: 1 for r in rows}).splitlines()
        self.assertNotEqual(lines[0].split(" & ")[0], lines[1].split(" & ")[0])
        self.assertEqual(lines[2], r"\midrule")


class TestCache(unittest.TestCase):
    def test_miss_fetches_once_then_hits(self):
        calls = []
        fetch = lambda q: calls.append(q) or {"nevents": 5}
        cache = {}
        self.assertEqual(m.cached(cache, "q", fetch), {"nevents": 5})
        self.assertEqual(m.cached(cache, "q", fetch), {"nevents": 5})
        self.assertEqual(calls, ["q"])
        self.assertEqual(cache, {"q": {"nevents": 5}})

    def test_hit_skips_fetch(self):
        fetch = mock.Mock(side_effect=AssertionError("queried DAS on a cache hit"))
        self.assertEqual(m.cached({"q": [1]}, "q", fetch), [1])

    def test_load(self):
        import json, tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "c.json"
            self.assertEqual(m.load_cache(path, False), {})
            path.write_text(json.dumps({"q": 1}))
            self.assertEqual(m.load_cache(path, False), {"q": 1})
            self.assertEqual(m.load_cache(path, True), {})

    def test_summary_and_listing_parse(self):
        with mock.patch.object(m, "das", return_value=[{"summary": [{"nevents": 7, "nfiles": 2}]}]):
            self.assertEqual(m.summary_of("q"), {"nevents": 7, "nfiles": 2})
        with mock.patch.object(m, "das", return_value=[{"dataset": [{"name": "/a/b/C"}]}]):
            self.assertEqual(m.list_datasets("q"), ["/a/b/C"])


class TestMainCache(unittest.TestCase):
    def run_main(self, d, *extra):
        from pathlib import Path
        tex, lst, cache = Path(d) / "s.tex", Path(d) / "l.txt", Path(d) / "c.json"
        if not tex.exists():
            tex.write_text(f"{m.BEGIN_INCL}\n{m.END_INCL}\n{m.BEGIN}\n{m.END}\n")
            lst.write_text(ds(TT))
        fams = [("tt", "TTto4Q_TuneCP5_13p6TeV_powheg-pythia8", m.LOW, "c")]
        argv = ["x", "--tex", str(tex), "--datasets", str(lst), "--cache", str(cache), *extra]
        with mock.patch.object(m, "FAMILIES", fams), mock.patch.object(m, "MISSING", []), \
                mock.patch("sys.argv", argv), mock.patch("builtins.print"), \
                mock.patch.object(m, "das", return_value=[{"summary": [{"nevents": 42}]}]) as das:
            m.main()
        return das, tex, cache

    def test_second_run_uses_cache_and_refresh_requeries(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as d:
            das, tex, cache = self.run_main(d)
            self.assertEqual(das.call_count, 1)
            self.assertIn("& 42 &", tex.read_text())
            self.assertEqual(json.loads(cache.read_text()),
                             {f"summary dataset={ds(TT)}": {"nevents": 42}})
            self.assertEqual(self.run_main(d)[0].call_count, 0)
            self.assertEqual(self.run_main(d, "--refresh")[0].call_count, 1)

    def test_completed_queries_saved_when_another_fails(self):
        import json, tempfile
        from pathlib import Path
        ok, bad = ds(TT), ds(TT, SUF + "_ext1-v2")

        def das(query):
            if bad in query:
                raise RuntimeError("DAS down")
            return [{"summary": [{"nevents": 42}]}]
        with tempfile.TemporaryDirectory() as d:
            tex, lst, cache = Path(d) / "s.tex", Path(d) / "l.txt", Path(d) / "c.json"
            tex.write_text(f"{m.BEGIN_INCL}\n{m.END_INCL}\n{m.BEGIN}\n{m.END}\n")
            lst.write_text(f"{ok}\n{bad}\n")
            fams = [("tt", "TTto4Q_TuneCP5_13p6TeV_powheg-pythia8", m.LOW, "c")]
            argv = ["x", "--tex", str(tex), "--datasets", str(lst), "--cache", str(cache)]
            with mock.patch.object(m, "FAMILIES", fams), mock.patch("sys.argv", argv), \
                    mock.patch.object(m, "das", side_effect=das):
                with self.assertRaises(RuntimeError):
                    m.main()
            self.assertEqual(json.loads(cache.read_text()),
                             {f"summary dataset={ok}": {"nevents": 42}})


class TestSplice(unittest.TestCase):
    def test_replaces_between_markers(self):
        text = f"keep\n{m.BEGIN}\nold\n{m.END}\ntail\n"
        self.assertEqual(m.splice(text, "new"), f"keep\n{m.BEGIN}\nnew\n{m.END}\ntail\n")

    def test_idempotent(self):
        text = f"{m.BEGIN}\nold\n{m.END}\n"
        once = m.splice(text, "new")
        self.assertEqual(m.splice(once, "new"), once)

    def test_missing_markers_raise(self):
        with self.assertRaises(ValueError):
            m.splice("no markers", "x")


if __name__ == "__main__":
    unittest.main()
