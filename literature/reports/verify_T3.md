# Verification of spin_density_matrix.md (sections 2.1–2.4, 3.1–3.2, 4, 5)

Verdict: no numerical mismatch found. Every value in all 38 table rows matches its cited note, and the sampled primary sources (HEPData JSON, arXiv text, CDF PDF text layer) agree. The table has 4 MISMATCH items in Sec. 5 and 12 row-level flag problems, plus smaller claim issues listed below.

## Method and coverage

- Numbers: every numeric token in every row was matched against its cited note with token-boundary matching (script run, 38/38 rows, no missing tokens). Presence alone is weak, so each row's values were also read in context in the note (bin, stat/syst split, units, frame, observed vs expected).
- Primary sources re-opened:
  - CDF Table I (1103.5699): compared to PDF text layer (`pdftotext -layout`), all 20 A0/A2/A3/A4 entries match.
  - ATLAS 8 TeV Z (1606.00689): HEPData Tables 11, 12, 14, 17 values and headers; paper Table 9 (A0−A2 = 0.018 ± 0.003 ± 0.007); paper text "3.0 (3.2)"; Eq. 15–16 in paper.txt lines 3533–3576.
  - CMS 2024 (2604.25678): HEPData Figure_3_A__0/__2 values; Figure_4_A__1 header is "A5"; text "2.8 standard deviations for A6 ... 55<pT<80, 1.2<|y|<2.4".
  - CMS 8 TeV Z (1504.03512): HEPData Table_1 (|y|<1) and Table_2 (1<|y|<2.1) placement.
  - ATLAS 7 TeV W (1203.2165): Table 11 layout in paper.txt; Eqs. 4–5 in paper.txt.
  - ATLAS W (2509.13759): neutrino-pz sentence "dilutes ... namely A0 and A4" (arxiv_text2.txt).
  - ATLAS WZ joint (2211.09435): paper.txt lines 91–94 and 1278 (joint and consistency maps); values in text.
  - ATLAS H→ZZ* (2603.26463): paper.txt lines 120–127, Table 1 lines 170–191.
  - Mirkes & Ohnemus (hep-ph/9406381): Eq. 26 prose and Eq. 27 from paper.html.
  - Ricci & Riembau (2207.03511): Eq. 6 from paper.txt line 129.
  - Grossi et al. (2409.16731): Eqs. 9, 11, 12, 16, 18–20 and the positive/negative-lepton statement from arxiv_2409.16731.html.
  - Gao et al. (2610.38688): ≈14% / 2–3% sentence and Table 1 values (presence in paper.txt).
  - Mirkes 1992 (ins335604): INSPIRE abstract (inspire.json) for the "T-odd / V−A" sentence.
  - LEP SDM (hep-ex/0305025): Eqs. 4–5 and CPT/CP relations from arXiv HTML.
  - OPAL (hep-ex/0312047): Eqs. 10–11 (hep-ex_0312047 PDF text); HEPData Table_2/Table_3 contain 0.712 and 0.407.
  - LHCb, WZ 36.1, CMS 13 TeV W, CMS 7 TeV W, ATLAS ttbar, ATLAS+CMS, CMS single top, CDF+D0, ZZ CP, ZZ 13.6 TeV: values read in the notes; a presence check in the primary text or HEPData was run for the key numbers.
- Flags and claims: each row's flags were checked against the note's open issues, verifier lines and caveats. Each sentence in Sec. 1, 3.2 (sources), 4 and 5 that states a fact about a paper was checked against its note, and against the primary source where the note was ambiguous.
- Not done: a full character-by-character read of every HEPData JSON value (the note values were matched to the files for the rows listed above). Some notes' Table 1 values (Gao et al.) were checked for presence only.

## Non-CONFIRMED items

| row (paper + bin) | item | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| Sec. 5.1, bullet 1 (pT-binned multi-element results) | list of pT-binned DY A_i results | MISMATCH | Says pT-binned multi-element results "exist only for inclusive Drell–Yan A_i:" and lists 2604.25678, 1606.00689, 1504.03512, 2509.13759. Omits LHCb 2203.01602 (pT(Z) 0–10 … 80–100 GeV, A0–A3, ΔA4; notes/2203.01602.md, Table 2 rows) and CDF 1103.5699 (pT 0–10 … >55 GeV/c, A0, A2, A3, A4; Table I). | Add 2203.01602 and 1103.5699 to the list, or drop "only". |
| Sec. 5.1, bullet 2 ("W+jets fractions … inclusive or single-bin") | W+jets fraction binning | MISMATCH | 1203.2165 is pT^W-binned: f_0 and f_L−f_R at "35 < p_T^W < 50 GeV" and "p_T^W > 50 GeV" (row 72; notes/1203.2165.md line 26–29; paper.txt Table 11). | Replace with "W fractions in 1203.2165 are binned in pT^W (35–50, >50 GeV); CMS 1104.3829 is single-bin; CMS 2008.04174 is |y_W|-binned." |
| Sec. 5.2 ("No measurement on hadronic or boosted V decays. Every hadronic-V SDM item in the corpus is THEORY or PROJECTION") | hadronic-V measurements | MISMATCH | L3 measures hadronic-W fractions: "f0 (hadronic only) 0.215 ± 0.042 ± 0.039" (row 75; notes/hep-ex_0301027.md Table 3, line 33). The same caveat's next sentence concedes "Hadronic-W measurements exist only at LEP". | Delete the first sentence or restate: "No measurement on boosted V decays; hadronic-W measurements exist only at LEP (L3, OPAL), where ρ++ and ρ-- are folded and off-diagonal elements use leptonic decays only." |
| Sec. 5.3 ("The only stated maps are: …") | list of stated maps | MISMATCH | The list gives four maps (1606.00689 App. A; 2409.16731; 2610.38688; 1203.2165). Sec. 3.1–3.2 of the same table also list stated maps from Mirkes & Ohnemus (hep-ph/9406381 Eqs. 26–27), 2211.09435 (f00 = ρ0000 etc., Sec. 2), 2603.26463 (C ↔ ρ at LO, Main text), OPAL hep-ex/0312047 (Eqs. 10–11), LEP hep-ex/0305025 (Eqs. 4–8), and 2008.04174 / 1104.3829 (proportionalities). | Replace "only" with a pointer to Sec. 3.1–3.2, or add the missing maps to the list. |
| 2.2 / row 62 (ATLAS ZZ CP, 2310.04350), "Interference term is a fixed template" | interference treatment | UNSUPPORTED (by note) | Note has no statement that the interference term is a fixed template (notes/2310.04350.md lines 14, 80–87). Source supports it: "A dedicated template for the interference term is therefore constructed by reweighting the inclusive Sherpa qq̄→ZZ events" (.cache/2310.04350/fulltext.txt line 229). | Add the source sentence to the note, then keep the table claim. |
| Sec. 1 ("All Q1 dijet/resonance notes: each states that no polarisation quantity is measured") | Q1 notes | UNSUPPORTED | notes/ins355978.md (UA2 dijet resonance) contains no polarisation, spin or helicity statement (grep: no matches). Other Q1 notes do state it (e.g. notes/2609.21850.md line 14; notes/2206.09997.md line 19). | Either add a statement to ins355978.md or narrow the claim to the notes that state it. |
| Sec. 1 (borderline list, 2503.11317) | "the note itself says … for the lead to decide" | UNSUPPORTED | notes/2503.11317.md line 13 and open issue: "Q2 has no qualifying quantity … The lead should confirm whether adjacent cross-section results should be recorded for Q2." It does not say the Q3 "more than one element" question is for the lead. | Reword: "2503.11317: the note asks the lead to confirm Q2 scope." |
| 2.4 row 44 (ATLAS W, 2509.13759), flags | "Post-fit rebinning; which coefficients it applies to is not stated" | MISLABELED (minor) | notes/2509.13759.md line 233: "Figs. 14–16 captions state the rebinning; Figs. 12–13 captions do not. Whether A0, A2–A4 (Figs. 12–13) are rebinned is not stated." | "Figs. 14–16 captions state post-fit rebinning; Figs. 12–13 do not say." |
| 2.3 row 58 (ATLAS WZ, 2211.09435), frame/flags | "Effective fractions …; interference included." | MISLABELED (minor) | notes/2211.09435.md line 86: "Interference is treated only as a fit effect (Sec. 7.1)." | Replace "interference included" with "interference treated only as a fit effect (Sec. 7.1)". |
| 2.3 row 63 (CMS same-sign WW, 2009.09429), BORDERLINE | rationale for BORDERLINE | MISLABELED (minor) | The note's only scope question is Q2: "The lead should decide whether this paper is in scope for Q2 or should be marked 'cross sections only'" (notes/2009.09429.md line 79). It does not raise the Q3 "more than one element" question. The row's stated reason (frame difference) is not a scope issue. | Give the Q2-scope reason in the row flag. |
| Sec. 1 (borderline list, 2009.09429) | "the note itself says … for the lead to decide" (for "more than one element") | MISLABELED (minor) | Same as above: the note's lead question is Q2 scope, line 79. | Reword as in row 63. |
| 2.1 row 40 (ATLAS 8 TeV Z, 1606.00689), flags | paper syst vs HEPData sys,reg_bias | MISSING_FLAG (minor) | notes/1606.00689.md line 90 [verifier w1R_b]: "The paper's syst equals the quadrature sum of HEPData sys,sys and sys,reg_bias (e.g. 0.011 at 132–173 GeV)." The table gives the three columns but not this mapping. | Add: "paper syst = quadrature sum of HEPData sys,sys and sys,reg_bias (w1R_b)." |
| 2.2 row 51 (LEP summary), flags | OPAL CP-coupling status | MISSING_FLAG (minor) | notes/hep-ex_0305025.md Caveats: the abstract says "Limits are set on CP-violating couplings", Sec. 3 gives two-sided errors, and "the CL / interval definition is not stated". The table omits the OPAL couplings and this ambiguity. | Add a flag: "OPAL CP couplings: abstract says limits, Sec. 3 says results; CL not stated." |
| 2.2 row 52 (ATLAS H→ZZ*), SM expected and test | channel and expectation definition | MISSING_FLAG (minor) | "SM expected | −0.97 | 0.64" has no channel column in Table 1 (paper.txt lines 190–191); the note says "Whether these are combined or another column is not stated. Do not assume." (notes/2603.26463.md line 65). Expected 4.9σ definition not stated (line 69). | Add both to the flags. |
| 2.3 row 61 (ATLAS ZZ 13.6 TeV, 2607.12879), f_LL and 180–240 bin | interference normalisation | MISSING_FLAG | Values depend on the normalisation choice: f_LL 0.080 ± 0.017 is "scaled" and 0.080 ± 0.018 is fixed (notes/2607.12879.md lines 24, 26); 0.108 ± 0.028 is "scaled normalization, nominal" (line 27) with fixed value 0.110 ± 0.030 (line 27). The table gives no normalisation. | State "scaled normalisation" for each value; give the fixed-normalisation values. |
| 2.4 row 75 (L3 hadronic/leptonic W, hep-ex/0301027), flags | hadronic f0 method | MISSING_FLAG | "For the correction of f0 in the hadronic W decay, the ratio f−/f+ is taken from the measurement in the leptonic W decay, as only the sum of f+ and f− is known from hadronic decays." (notes/hep-ex_0301027.md, Sec. Analysis; line 68). Hadronic f0 therefore depends on the leptonic ratio. | Add flag: "hadronic f0 uses the leptonic f−/f+ ratio (model input)." |
| 2.4 row 77 (ATLAS+CMS combination, 2005.03799), FR limit | limit method | MISSING_FLAG (minor) | notes/2005.03799.md line 37: "95% CL upper limit FR < 0.007 (Feldman–Cousins, FR ≥ 0 imposed)". The combined FR value (−0.008) is not given. | Add "Feldman–Cousins, FR ≥ 0 imposed" to the flag. |
| 2.4 row 78 (CMS single top, 1410.1154), flags | F_R outside single-channel interval | MISSING_FLAG (minor) | "Combined F_R (−0.018) lies outside the muon/electron F_R interval; the paper attributes this to the sum constraint and channel weighting (Sec. 8)." (notes/1410.1154.md line 61). | Add the sentence to the flags. |
| 3.1 row 89 (Grossi et al., 2409.16731), Eq. 16 | normalisation source | MISSING_FLAG (minor) | notes/2409.16731.md open issues: "Eq. 16 normalisations rely on Ref. [44] (arXiv 2209.13441), not checked; present Eq. 16 as this paper's convention only." The table says only "convention of Ref. [44]". | Add "Ref. [44] normalisation not checked." |
| Sec. 5.5 ("Open data discrepancies carried from the notes") | completeness | MISSING_FLAG (minor) | The list omits OPEN flags from the table's own rows: L3 Table 6 caption "W−" vs column "W±" (row 75; notes/hep-ex_0301027.md line 45), LEP Fig. 5 left/right conflict between text and caption (row 51; notes/hep-ex_0305025.md Caveats), and OPAL HEPData Tables 5–7 have no units (row 50; notes/hep-ex_0312047.md line 252). | Add the three items, or retitle the list as partial. |
| 2.3 row 59 (ATLAS WZ pT-binned, 2402.16365), caveat | "The only pT-binned joint diboson result in the corpus." | UNVERIFIABLE | Corpus-wide negative claim. Checked the notes that cover joint diboson fractions (2211.09435, 2607.12879, 2607.20246, 2310.04350, 2009.09429, 2503.11317): none is pT-binned. Did not exhaustively search all 57 notes. | Keep as "the only pT-binned joint diboson result among the notes read here". |

## Items confirmed with a fix only

- 3.2 row 97 (ATLAS 8 TeV Z, 1606.00689): the Eq. 16 line still carries the flag "to be checked by the re-verifier". Eq. 15 and Eq. 16 are confirmed in the source (.cache/1606.00689/paper.txt lines 3533–3540 and 3567–3576). Replace the flag with "checked against paper.txt lines 3533–3576".

## Counts per verdict

Item definitions: one item = a row's value block (38 rows), a row's flag/claim block (38 rows), each Sec. 4 bullet (7), each Sec. 5 sub-claim or list entry (21), and each Sec. 1 claim (13).

| verdict | count |
|---|---|
| CONFIRMED | 96 (38 value blocks, 26 flag blocks, 7 Sec. 4 bullets, 15 Sec. 5 items, 10 Sec. 1 claims) |
| MISMATCH | 4 (Sec. 5.1 list, Sec. 5.1 W+jets, Sec. 5.2, Sec. 5.3) |
| MISLABELED | 4 (row 44, row 58, row 63, Sec. 1 for 2009.09429) |
| UNSUPPORTED | 3 (row 62 interference template, Sec. 1 Q1 claim, Sec. 1 for 2503.11317) |
| MISSING_FLAG | 9 (rows 40, 51, 52, 61, 75, 77, 78, 89; Sec. 5.5) |
| UNVERIFIABLE | 1 (row 59 "only pT-binned joint diboson result") |

Total items 117; non-CONFIRMED 21. Row-level value blocks: 38/38 CONFIRMED.

Value mismatches (wrong number, stat/sys split, unit, frame, bin): 0.

## Summary of the main problems

1. Sec. 5 contains four factual errors: an incomplete list of pT-binned results, a W+jets binning claim contradicted by 1203.2165, a "no hadronic measurement" claim contradicted by L3 (row 75), and a "only stated maps" claim contradicted by Sec. 3.
2. Several BORDERLINE and scope statements in Sec. 1 attribute to notes a question the notes do not raise.
3. Missing flags are mostly minor. The most important are the hadronic-f0 dependence on the leptonic ratio (row 75) and the interference-normalisation choice (row 61).
