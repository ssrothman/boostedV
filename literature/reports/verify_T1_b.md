# Verification report: limits.md rows R37 to R71 (T1_b)

Scope: main table rows R37 to R71 in `limits.md` (Section 2), checked against `notes/<id>.md` and `.cache/<id>/` (HEPData JSON and paper text). Sections 3 and 5 sentences that cite these rows were also checked (see the last section). Section 4 cites notes, not rows, and was not checked in this pass.

Verdict: the numbers are right. 256 of 312 items are CONFIRMED. The problems are source labels, "inferred" qualifiers that HEPData headers already settle, missing flags, and one row-value claim (R52, "1.03 TeV") that the table cannot reproduce. There is one MISMATCH, in R54 (obs/exp), and one in Section 3 (R52 missing from the ">1 TeV" list).

## 1. Non-CONFIRMED items

| row | item | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| R37 | source column "values in Sec. 9" | MISLABELED | Sec. 9 holds only the text range "g_q<0.04 to g_q<0.11"; limit values are in Fig. 9b, Sec. 8 (arxiv.html) | Source: "HEPData Z' limits (J50/J100), Fig. 9b, Sec. 8; text range Sec. 9" |
| R37 | x-axis label | MISSING_FLAG | HEPData header is "$m_{G}$ [GeV]"; location and Fig. 9b caption say m_Z'. Note's "Assumed x = m_Z'" not carried into row | Add: "HEPData x-header reads m_G; x taken as m_Z' per Fig. 9b" |
| R37 | obs/exp mapping vs plot | MISSING_FLAG | Fig. 9 plot not read; mapping rests on HEPData headers (which do state Observed/Expected) | Add: "obs/exp from HEPData headers; plot not checked" |
| R37 | model scope | MISSING_FLAG | arxiv.html Sec. 3: "did not model interference with the SM"; DM decays "negligible" | Add to notes: one benchmark; no interference; DM decays negligible |
| R38 | source column "values in Sec. 9" | MISLABELED | Same as R37; Gaussian values are in Fig. 9a, Sec. 8 | Source: "HEPData Gaussian resonance limits (J50/J100), Fig. 9a, Sec. 8; text range Sec. 9" |
| R38 | stale flag "text range not checked against table" | (stale, not counted) | Table minimum 0.016955 pb (17 fb, 1800 GeV) and maximum 15.623 pb (16 pb, 400 GeV) match the text "17 fb to 16 pb" | Remove the flag; add "table min/max match text" |
| R38 | Gaussian usage conditions | MISSING_FLAG | arxiv.html Sec. 8: limits apply "when PDF and non-perturbative effects can be safely truncated or neglected"; widths below 5% use the 5% limit | Add both conditions |
| R38 | J50/J100 sample per value | MISSING_FLAG | 375 GeV from J50; 1000 and 1800 GeV from J100 | Label each value with its sample |
| R38 | figure-to-header mapping | MISSING_FLAG | Same as R37 (plot not read) | Same note as R37 |
| R39 | exclusion assumption | MISSING_FLAG | paper.txt l.644-646: "Z' masses up to 2 TeV" excluded "assuming the maximal cross-section" | Append "exclusion under maximal-cross-section assumption" |
| R40 | "below 1.2 TeV" OUT flag | MISSING_FLAG | 1.2 TeV is outside 10 GeV to 1 TeV; R39 and R45 carry "(OUT)", R40 does not (paper.txt l.679) | Add "(OUT)" |
| R40 | limit form | MISSING_FLAG | Table_4 header "sigma x BR [pb]", description omits acceptance; paper.txt l.459, l.630 say model limits are acceptance/efficiency-corrected | Add the R39 limit-form flag |
| R45 | "(from top)" | UNSUPPORTED | Paper does not state the lepton origin for tbH+; only "fewer isolated leptons" (Sec. 5) | Drop, or write "lepton origin not stated in paper" |
| R45 | mass axis | MISSING_FLAG | Table_3 header "Mass [GeV]" unlabelled; paper.txt Sec. 4: m_jj peak "shifted from the m_H+ value by about 30% to lower masses" | Add axis flag with the shift |
| R45 | limit form | MISSING_FLAG | Table_3 header "sigma x BR(H+ -> tb) [pb]", no acceptance in description | Add the R39 limit-form flag |
| R45 | scoping | MISSING_FLAG | paper.txt l.279-283, l.654-655: four-flavour scheme and narrow-width approximation | Add "4FS, m_h^mod-, NWA" to model cell |
| R41 | provenance | MISSING_FLAG | Quotes come from arXiv v3 cache (header "14 Oct 2026"); note open issue 7 says not reconciled with JHEP 07 (2023) 161 | Add to source or flags |
| R42 | "column map inferred", "obs/exp inferred" | MISLABELED | HEPData headers are explicit: "Exp. [fb]" (col 1), "Obs. [fb]" (col 2) in Cross-section_limit_in_the_nonresonant_search.json | Drop "inferred"; cite the header labels |
| R43 | "obs/exp inferred" | MISLABELED (minor) | hep/table_44.json qualifier group 0 = "Observed"; only the expected column ("Fit") is inferred | Say expected = qualifier "Fit"; observed labelled |
| R44 | "obs/exp inferred" | MISLABELED (minor) | hep/table_68.json group 0 "Observed sigma/M = 0.05" | As R43 |
| R64 | provenance | MISSING_FLAG | Same as R41 | Same |
| R65 | "column map inferred" | MISLABELED | Headers "Exp. [fb]" and "Obs. [fb]" explicit in both alpha tables | Drop "inferred" |
| R65 | source for alpha=0.11 exclusion | MISLABELED | arxiv text l.147: "Based on Figs. 11 and 12 ... for an alpha_true value of 0.11"; alpha=0.11 table is t18 (Fig. 12); t17 is alpha=0.25 (Fig. 11) | Cite t18 (Fig. 12) for the alpha=0.11 exclusion |
| R46 | duplicate 1600 GeV rows | MISSING_FLAG | HEPData t3 has two 1600.0 rows: (0.33655 / 0.18659 / 0.16385) and (0.37191 / 0.27434 / 0.20736) | Flag the duplicate, low- and high-mass searches |
| R47 | duplicate 1600 GeV rows | MISSING_FLAG | t5: 0.10606 (low-mass) and 0.11932 (high-mass) | As R46 |
| R47 | asymerror convention | MISSING_FLAG | Expected bands are HEPData asymerror offsets; sign and unit convention not stated (note open issue 8) | Add the flag |
| R48 | mass limits are not HEPData | MISSING_FLAG (low) | Note Caveats: "they are not HEPData values" | Add: "mass limits are theory-vs-observed comparisons, not HEPData" |
| R49 | note definition of A | MISLABELED | Note line 13 says A includes the minimum-m_jj acceptance; note line 92 and paper text_clean.txt l.68 say it does not: "the acceptance of the minimum dijet mass requirement does not appear in the acceptance A" | Rewrite note line 13: A is the parton-level two-body acceptance |
| R50 | "text 0.04 vs table 0.037342" | MISLABELED | 0.037342 rounds to 0.04 at one significant figure; text is consistent with the table, so not a disagreement | Reword as a rounding note |
| R50 | units of g'_q | MISSING_FLAG | t8 headers "Observed g_q' exclusion" with no units (note open issue 4) | Add "units not stated" |
| R50 | asymerror convention | MISSING_FLAG | t8 expected bands are asymerror offsets | Add the flag |
| R59 | "g_q > 0.42 (narrow)" | MISSING_FLAG | paper.txt l.1633: "the narrow-resonance limit is g q > 0.42", no obs/exp label; narrow-width validity to about 0.4 (l.1634-1635); Fig. 19 narrow curve figure-only | Label "text only, obs/exp not stated; narrow-width approximation valid to g_q ~ 0.4" |
| R59 | asymerror convention | MISSING_FLAG | DM JSON expected bands are asymerror offsets (note open issue 8) | Add the flag |
| R51 | luminosity for cited points | MISSING_FLAG | Cited 0.6 and 1.0 TeV points lie below the 1.2 TeV overlap; Sec. 4 (l.100) gives the low-mass sample as 24.3 fb-1; HEPData qualifier says 36.1 | Keep qualifier; state the conflict |
| R51 | B(Z' -> bb) convention | MISSING_FLAG | l.96: B = 13.8% (SSM), 18.9% (leptophobic); row does not say which B the sigma x B uses | Add model-specific B |
| R52 | "masses up to 1.03 TeV excluded (OUT edge)" | UNVERIFIABLE | Text quote confirmed (l.184, l.198). Table_9 gives about 2.07 pb at 1.0 TeV, but LO sigma x B(Z'->qq) = 2.7 fb at 1 TeV (l.98), about a 770x gap; the table cannot produce a 1.03 TeV crossing. Fig. 7(a) not extracted | Mark "text only; not reproducible from Table 9"; do not present as table-supported |
| R53 | level flag "particle vs detector level unresolved for aux. tables" | MISLABELED | Table 12 is main-text Fig. 9 (HEPData "Figure 9 from Page 15"), not auxiliary. Caption states no level; l.185: "A MC-based transfer matrix is used to fold in the detector effects" | Replace with "level not stated in caption; transfer matrix folds in detector effects; reco vs particle unresolved" |
| R57 | level flag | MISSING_FLAG | Table 11 caption states no level; same as R53 | Add the R53 flag |
| R58 | B(b* -> bg) = 85% behind 2.6 TeV claim | MISSING_FLAG | l.184: "b* model with an assumed branching fraction for b*->bg of 85% is excluded ... up to 2.6 TeV" | Add the assumption |
| R54 | obs/exp "not stated" | MISMATCH | Fig. 5 caption (paper.txt l.154): "Observed (filled circles) and expected (dotted line) 95% credibility-level upper limits"; Fig. 6 caption (l.159) same | Write "obs and exp curves in Figs. 5-7 (figure-only); exclusion sentences do not label obs or exp" |
| R54 | leading-order QCD | MISSING_FLAG | l.152, l.157, l.180: exclusions "at leading-order in QCD" | Add the flag |
| R54 | b* observed vs expected | MISSING_FLAG | l.180: "The expected contribution from the b* model is excluded in the mass range 1.1-2.1 TeV"; l.152 says "is excluded" without label | Add the flag |
| R54 | sigma terminology | MISSING_FLAG (minor) | Abstract l.36 "effective cross sections" vs l.162, l.182 "visible cross sections sigma x A x BR" | Add the terminology flag |
| R55 | expected background hypothesis | MISSING_FLAG (minor) | Note Caveats: not stated in text | Add the flag |
| R60 | "A at parton level", "B only five light quarks" | UNSUPPORTED (note-level) | Stated in note Sec. 0.6; no parton-level statement for A found in paper.txt or paper.html | Verify against paper, or remove from note |
| R62 | Z' SM-like 3.1-3.3 TeV | MISSING_FLAG (minor) | Table 1 caption: "also excluded within the mass interval between 3.1 and 3.3 TeV" | Add to row |
| R62 | theory dependence | MISSING_FLAG | Mass limits come from theory curves (Figs. 6-7, not in HEPData), LO with K-factors (note Open issues) | Add the flag |
| R67 | "95% CL (CLs)" | UNSUPPORTED (minor) | text.txt l.93 says only "modified frequentist criterion [33, 34]"; "CLs" appears only in a reference title (l.371) | Write "modified frequentist (CLs per cited ref.)" |
| R67 | LO and efficiency-corrected mass limits | MISSING_FLAG | text.txt l.98 uses LO sigma BA prediction; note Sec. 0.5 describes efficiency factor | Add the flag |
| R68 | edge "up to m_R ~ 70 GeV" | MISSING_FLAG | Sec. 3.2: bound given "until m_R ~ 70 GeV, where it becomes comparable to the upper bound (14) from perturbativity" | Add: "perturbativity crossover, not an experimental edge" |
| R69 | luminosity scope | MISLABELED | "36.3 fb-1" appears only in the Z'+jet section (paper_math.txt l.206); "300 fb-1 and 3 ab-1" only in App. 3 (l.661); Z'gamma luminosity never stated | Scope to "Z'j channel only; Z'gamma luminosity not stated" |
| R69 | CMS-derived curve | MISSING_FLAG | Fig. 3: solid red "expected limit from the CMS Collaboration ... taken from [49]"; dashed blue "Our recast of the CMS bounds" | Add "RECAST (Z'gamma, CMS 1905.10331); CMS expected curve quoted from [49], not derived" |
| R70 | production mode "single" | UNSUPPORTED | No production mode in the INSPIRE abstract or note | Replace with "not stated (abstract)" |
| R71 | 630 GeV source | MISLABELED | Value is in HEPData Table_1.json (qualifier "630.0 GeV"), not in the abstract the row cites | Cite "HEPData ins298412 Table 1" |
| R71 | production mode "single" | UNSUPPORTED | As R70 | As R70 |
| R71 | limit values, CL, mass range | UNVERIFIABLE | Abstract confirms a limit "as a function of the boson mass" only; paper.pdf in cache is a "no-access" landing page; no arXiv copy found | Keep "not extractable (full text inaccessible)" |
| R71 | missing flag | MISSING_FLAG | Note Open issues say "NO FULL TEXT ACCESSIBLE"; row does not say abstract/HEPData only | Add "abstract + HEPData only; full text not accessed" |

Not counted, but relevant: R70 full text (m > 261 GeV) is verified against the abstract only. The CDS record is a bot challenge and the DOI is paywalled; the row's "abstract only" flag is correct and must stay.

## 2. Counts per verdict (all rows R37 to R71)

| verdict | count |
|---|---|
| CONFIRMED | 256 |
| MISMATCH | 1 (R54 obs/exp) |
| MISLABELED | 12 |
| UNSUPPORTED | 5 |
| MISSING_FLAG | 36 |
| UNVERIFIABLE | 2 (R52 "1.03 TeV"; R71 limit values) |
| total items | 312 |

Per-batch tallies, as reported by the verifiers. The batch for R41, R42, R43, R44, R64, R65, R66 stated 52 items but its own tallies sum to 47 (40 + 5 + 2); the 47 are used here and the discrepancy is not resolved.

## 3. Row coverage

| rows | CONFIRMED | non-confirmed |
|---|---|---|
| R37, R38 | 20 | 2 MISLABELED, 6 MISSING_FLAG (plus 1 stale flag) |
| R39, R40, R45 | 26 | 1 UNSUPPORTED, 6 MISSING_FLAG |
| R41-R44, R64-R66 | 40 | 5 MISLABELED, 2 MISSING_FLAG |
| R46-R50, R59 | 44 | 2 MISLABELED, 8 MISSING_FLAG |
| R51-R53, R57, R58 | 35 | 1 MISLABELED, 4 MISSING_FLAG, 1 UNVERIFIABLE |
| R54-R56, R60-R63, R67 | 52 | 1 MISMATCH, 7 MISSING_FLAG, 2 UNSUPPORTED |
| R68-R71 | 39 | 2 MISLABELED, 2 UNSUPPORTED, 3 MISSING_FLAG, 1 UNVERIFIABLE |

## 4. Sections 3 and 5 (sentences citing rows)

| location | item | verdict | evidence | suggested fix |
|---|---|---|---|---|
| Sec. 3, ">1 TeV (all OUT)" list | R52 omitted | MISMATCH | R52 range 0.6-1.25 TeV overlaps the >1 TeV interval; the list rule is "rows are listed if their stated mass range overlaps" | Add R52 to the list |
| Sec. 3, 500-1000 GeV | "ATLAS g_q (R37) and CMS g_q' (R47, R50) give HEPData values every 50 GeV" | MISMATCH (minor) | Z_limits_J50 steps by 25 GeV from 500 to 600 GeV; J100 steps by 50 GeV from 600 | "every 50 GeV above 600 GeV (J100); 25 GeV steps in J50 at 500-600 GeV" |
| Sec. 5 item 5 vs R39, R40, R45 | "Bayesian credibility limits (..., 2002.11325, ...)" vs rows labelled "95% CL (Bayesian)" | MISLABELED (minor) | 2002.11325 text (Batch B, paper.txt l.441-444): "95% credibility level" | Change rows to "95% credibility (Bayesian)" |
| Sec. 5 item 3 | R59 "0.53 vs 0.54659 / 0.47534" | CONFIRMED | paper.txt l.1633; DM JSON 3700 GeV | none |
| Sec. 5 item 3 | R50 "0.04 vs 0.037342" | MISLABELED | Rounding, not disagreement (see R50 above) | Reword |
| Sec. 5 item 4 | 2002.11325 Table 1-2 limit form | CONFIRMED | Table_2 header "sigma x BR", description "times acceptance times branching ratio" | none |
| Sec. 5 item 9 | 2307.14944 identical values at 600-800 GeV (Table 46) | NOT CHECKED | Verifiers checked only 500-700 GeV (Table 44) | Check Table 46 |
| Sec. 5 items 9, 10, 11, 12 | R37, R41, R43, R50, R51 notes | CONFIRMED | Local significances (3.4 sigma at 650 GeV; 3.6 sigma at 0.95 TeV; 2.2 sigma at 0.8 TeV) and luminosity remark match the papers | none |
| Sec. 5 item 8 | ins298412 "abstract only" | CONFIRMED | paper.pdf is a no-access landing page; HEPData Table 1 exists | Note the HEPData table in the caveat |

Section 4 (coupling conventions) cites notes rather than row numbers and was not verified.

## 5. Method and limits

- HEPData values were checked by parsing the cached JSON with `python3 -I`, mapping Observed and Expected from the header or qualifier group, not from column position.
- arXiv was consulted only through the arXiv API and the cached texts. HEPData was not contacted.
- Helper scripts written by verifiers (outside the literature tree, in /tmp): dump_hep.py, dump_hep2.py, check_rows.py, chk.py, arxiv_text.txt, hd_dump.py, hd2.py, hd3.py. These were not deleted by the verifiers. Their presence breaks the "no other files" instruction for those agents; they can be removed if not wanted.
- The R37 note cites `Zp_limits_J50/J100.json`; the files under `hepdata/tables/` are named `Z_limits_J50/J100.json`. The cache root copies are byte-identical, so content is unaffected.
