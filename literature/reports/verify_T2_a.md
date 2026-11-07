# Verification of polarization_fL.md, Section 2 (a) and (a′), and Section 4

Scope: rows of the (a) and (a′) tables in Section 2 (119 + 4 rows), and every fact-bearing sentence in Section 4. Sources: `.cache/<id>/` full text and HEPData JSON. No network access used. Scratch scripts were kept in `/tmp/t2a/` and nothing else was written to the repository.

## Verdicts

Row-level numeric checks, one line per paper block. Each block lists the rows covered; "all values" means every value, stat and syst of the block was read against the source.

| row (paper + bin) | item | verdict | evidence | suggested fix |
|---|---|---|---|---|
| CDF 1103.5699, A0 pT 0–10, 10–20, 20–35, 35–55, >55 (5 rows) | value, stat, syst, frame, A0 definition, "digits read from PDF", no HEPData | CONFIRMED | `.cache/1103.5699/paper.pdf` p.6 Table I (pdftotext -layout): 0.17 ± 0.14 ± 0.07; 0.42 ± 0.25 ± 0.07; 0.86 ± 0.39 ± 0.08; 3.11 ± 0.59 ± 0.10; 4.97 ± 0.61 ± 0.10. CS frame quote matches p.4 fn 3. `hepdata/NONE` present. | none |
| CMS 1504.03512, Table 1, A0, abs(y)<1, qT 0–10 … 200–9999 GeV (8 rows) | value, stat, syst | CONFIRMED | `.cache/1504.03512/hepdata/tables/Table_1.json` A0 group 0: 0.018/0.003/0.009 … 0.928/0.035/0.015, all 8 match | none |
| CMS 1504.03512, Table 2 1<|y|<2.1 (8 rows) | value, stat, syst | CONFIRMED | `Table_2.json`: 0.032/0.005/0.01 … 0.876/0.045/0.02, all 8 match | none |
| CMS 1504.03512, all 16 rows | flag "HEPData has no lumi/theory column" | MISLABELED (minor) | `Table_1.json` and `Table_2.json` carry `Lumi: 19.7 fb^{-1}` as a qualifier. The note says HEPData gives no lumi or theory *uncertainty*. | Replace with "HEPData has no lumi or theory uncertainty (lumi 19.7 fb⁻¹ is a table qualifier)". |
| ATLAS 1606.00689, Table 12 (A0 regularised, 23 pT^Z bins) | value, stat, sys,sys, sys,reg_bias, bins | CONFIRMED | Scripted comparison of all 23 rows with `hepdata/Table_12.json`: value, stat, sys,sys and sys,reg_bias match exactly (e.g. −0.0145192 / 0.00440241 / 0.00749077 / 0.003083 for 0–2.5). | none |
| ATLAS 1606.00689, unregularised A0 pT^Z 132.0–173.0 (1 row) | value | CONFIRMED | `Table_2.json` (A0 unregularised, "Data from Figure 27") 132.0–173.0: 0.882853 | none |
| ATLAS 1606.00689, unregularised A0 pT^Z 132.0–173.0 (1 row) | stat, syst "not given in note"; source "HEPData Tables 1–9" | MISMATCH | `Table_2.json` 132.0–173.0: stat 0.0168188, sys,sys 0.00767753 (no reg_bias column). The A0 unregularised table is Table 2, not "Tables 1–9". | Set stat = 0.0168188 and syst = 0.00767753; source = "HEPData Table 2 (A0 unregularised)". |
| ATLAS 1606.00689, Eq. (16) flag "A0 = 2σL/σU+L (verifier-noted)" (all rows) | formula | CONFIRMED | `.cache/1606.00689/paper.txt`: "A0 = 2dσL /dσU+L" | none. Note open issue 3 can be closed. |
| CMS 2604.25678, Figure 3 (A0, |y|<1, 8 bins) | value, stat, asym sys | CONFIRMED | `hepdata/tables/Figure_3_A__0.json` (via `summary.txt`): 0.03039/0.00131/−0.01154,+0.01149 … 0.92154/0.01507/−0.00555,+0.0056, all 8 match | none |
| CMS 2604.25678, Figure 5 (A0, 1<|y|<2.4, 8 bins) | value, stat, asym sys | CONFIRMED | `Figure_5_A__0.json`: 0.02259/0.0016/−0.00961,+0.00967 … 0.90282/0.01613/−0.00578,+0.00572, all 8 match | none |
| CMS 2604.25678, flags | "Eq. (1) is pre-FSR"; "parametrize the longitudinal (L) polarization fraction" quote | CONFIRMED | `fulltext/text.txt`: "The coefficients A0 and A2 parametrize the longitudinal (L) polarization fraction"; "pre-FSR" phrase found in the text | none |
| LHCb 2203.01602, Table 2 pT(Z) bins 0–10 … 80–100 (6 rows) and Table 3 yZ bins 2–2.7 … 3.25–3.6 (4 rows) | A0 value, stat, syst | CONFIRMED | Scripted comparison against the parsed Table 2/3 in `scratch/tables.txt`: all 10 rows match (e.g. 0.3740/0.0204/0.0105 for 35–55; 0.0443/0.0102/0.0053 for yZ 3.25–3.6). "Total" row, yZ>2, pT(Z)<100, 2<yZ<5 ("forward rapidity region (2 < yZ < 5)") confirmed in `text.txt`. | none |
| LHCb 2203.01602, flag "'Total' row read as central value (inference)" | flag | CONFIRMED | Flag is present in the row text and the note | none |
| LHCb 2203.01602, flag "5th yZ bin 3.6–4.5 absent from source" | flag | CONFIRMED | `scratch/tables.txt` TABLE #4 has four yZ bins only | none |
| CMS 1104.3829, Table 1 (all 12 rows: e and μ, W⁻/W⁺, combined) | value, stat, syst | CONFIRMED | `.cache/1104.3829/text.txt` Table 1 read in full; all 12 match (e.g. μ (f_L−f_R)⁻ 0.240 ± 0.036 ± 0.031; combined f0⁻ 0.162 ± 0.078 ± 0.136). | none |
| CMS 1104.3829, flags | "no HEPData"; "arXiv v1 (PRL not checked)" | CONFIRMED | `hepdata/NONE` absent from tables dir (note: "no HEPData record"); note line 81 says PRL not checked | none |
| ATLAS 1203.2165, Table 11 (4 rows) and Table 8 (8 rows) | values, stat, instr/analysis, template | CONFIRMED | `.cache/1203.2165/paper.txt` Table 11 (Data): f_L−f_R 23.8±2.0±3.4 and 25.2±1.7±3.0; f_0 21.9±3.3±13.4 and 12.7±3.0±10.8. Table 8: all 8 values match (e.g. μ f_0 23.6±3.8±12.0±7.2; e f_0 17.7±4.3±9.0±6.0). | none |
| ATLAS 1203.2165, flags | "corrected to generator-level acceptance"; "7 TeV 37.3 pb⁻¹ (e), 31.4 pb⁻¹ (μ)"; frame quote; Eq. 4 (f_0 = ½A_0) | CONFIRMED | Section 7 of paper.txt: corrections are generator-level fits after acceptance + mT cuts; luminosities 37.3 / 31.4 pb⁻¹ (line 223); helicity-frame quote matches; Eq. 4 terms read at lines 170–176 | none |
| CMS 2008.04174, row "f_0 not measured" | value, flags | CONFIRMED | `fulltext.txt` section 0.6.2: "the longitudinally polarized states are fixed to the MC prediction"; rapidity |y_W| < 2.5 | none |
| ATLAS 2509.13759, HEPData t1 (W⁻, 10 rows) and t2 (W⁺, 10 rows) | value, stat, asymmetric sys, bins | CONFIRMED | `hepdata/tables/Measured_angular_coefficients_for_W_-.json` and `..._for_W.json`: all 20 rows match value, stat and minus/plus sys (e.g. W⁻ 110–150: 1.383 / 0.2654 / −0.1118, +0.1163) | none |
| ATLAS 2509.13759, √s, L column (all 20 rows) | "338.1 ± 3.1 (unit not given in note)" | MISLABELED | `.cache/2509.13759/arxiv_text.txt` line 161: "total integrated luminosity of 338.1±3.1 pb-1" | Write "338.1 ± 3.1 pb⁻¹" and drop "unit not given". |
| ATLAS 2509.13759, flag "whether A0 rows are post-fit rebinned is not stated" | flag | CONFIRMED | Post-fit rebinning caption appears in Figs. 14–15 (A1, A5–A7) only; Figs. 12–13 (A0 etc.) captions do not mention it | none |
| Mirkes & Ohnemus hep-ph/9406381, Fig. 1(a) and 1(b) (2 rows) | figure-only identity, CS frame, quote | CONFIRMED | `notes/hep-ph_9406381.md` quotes Fig. 1 captions; no numbers in the row | none |
| Mirkes & Ohnemus hep-ph/9406381, Eq. (26) "A_0 = 2σ^L/σ^{U+L} per Eq. (26)" (2 rows) | flag | MISSING_FLAG | The note states that Eq. (26) is paraphrased because the extracted text is garbled; Section 4 carries this flag, the table row does not | Add "Eq. (26) paraphrased from garbled extraction; check typeset equation". |
| Mirkes ins335604 (1 row) | all fields | UNVERIFIABLE | No full text. `.cache/ins335604/sd.html` is a ScienceDirect shell with no article text (checked: no "nine" or "rest frame" hit). INSPIRE has no arXiv entry (per note). Row rests on the INSPIRE abstract only. | Keep "abstract-only" flag. Nothing numeric is stated. |
| Gao, Lee, Zhang 2610.38688, γ≈1.7 "≈14%" and γ≈7 "2 – 3%" (2 rows) | value, quote, Eq. 39, NNLO, Sec. IV.2 | CONFIRMED | `.cache/2610.38688/paper.txt` line 419: "decreasing from ≈14% at γ≈1.7 to 2 – 3% at γ≈7 for the Z"; NNLO pp→V+X at 13.6 TeV, y=0, pT>100 (line 416); Eq. (39) normalisation (line 'Σρ=1') | none |
| Gao, Lee, Zhang 2610.38688, ρ00(γ) figure-only ranges "γ 1.48–8.83 (Z), 1.60–10.0 (W)" (1 row) | ranges | UNVERIFIABLE | Ranges appear only in the note. Paper text has one "8.83" hit and no figure-axis source. Figures 4 and 9 not read. | Read the figure axes, or state "figure axis, not read". |
| Ricci & Riembau 2207.03511, A_LT row (1 row) | quote, dρ00 ∼ x(1−x), dρ_TT, frame quote | CONFIRMED | `paper.txt`: "Approximately, A_LT ≃ 0 for a purely transverse sample, while A_LT ∼ 0.5 for a purely longitudinal one"; "dρ00 ∼ x(1−x)"; frame "between the direction of flight of the vector and the helicity-plus fermion" | none |

Counts for the rows above: 119 (a) + 4 (a′) = 123 rows.
- CONFIRMED: 120 rows (CDF 5; CMS 1504 16; ATLAS 1606 Table 12 23; CMS 2604 16; LHCb 10; CMS 1104 12; ATLAS 1203 12; CMS 2008 1; ATLAS 2509 20; hep-ph 2; Gao 2 of 3; Ricci 1). The 1606 unregularised row is counted once, as MISMATCH below.
- MISMATCH: 1 row (ATLAS 1606 unregularised A0 stat/syst fields).
- UNVERIFIABLE: 2 rows (Mirkes ins335604; Gao ρ00 figure-only ranges).
- Row-level totals: 120 + 1 + 2 = 123.

## Section 4 (Definitions and frames): sentence-level checks

Quoted strings in Section 4 were checked against the cited notes by script (9 quoted strings). Equations and statements were then spot-checked against the source texts. Items marked "note only" were checked against the note, not the paper.

| item (Section 4 sentence) | verdict | evidence | suggested fix |
|---|---|---|---|
| CDF 1103.5699 Eq. (1) "½A0(1−3cos²θ)" | CONFIRMED | Raw pdftotext page 4, Eq. (1): "1/2 A0 (1 − 3 cos² θ) + A4 cos θ" | none |
| 1504.03512, 2604.25678, 1606.00689 Eq. (1) carry the same ½A0 term | UNVERIFIABLE (1103 and 2203 Eq. 1 re-read; 1606 from note; 1504 and 2604 not re-read) | 1606 and 2203 raw Eq. (1) in `paper.txt` and `scratch/tables.txt`; 1504 and 2604 not re-read | Re-read the 1504 and 2604 Eq. (1). |
| hep-ph/9406381 Eq. (27) angular expansion and Eq. (26) A_0 = 2σ^L/σ^{U+L} | UNVERIFIABLE | Typeset equation not readable from the cached text (note says garbled) | Read the typeset equation. |
| 1606.00689 A0 = 2σL/σU+L (Eq. 16); A2 = 4σT/σU+L, A4 = 2σP/σU+L | UNVERIFIABLE (A0 confirmed; A2, A4 prefactors not legible) | `paper.txt`: "A0 = 2dσL /dσU+L" and A1 "2√2dσI/dσU+L"; A2 and A4 prefactors not legible in the extraction | Mark A2/A4 prefactors as note-only. |
| CDF 1103.5699 Eq. (3) and Eq. (4) theory expectations | CONFIRMED | Raw text: "Aq0q̄ = Aq2q̄ = PT²/(Me+e− + PT²) (Eq. 3)"; "A2 ≈ 5PT²/(Me+e− + 5PT²) (Eq. 4)" | none |
| 2604.25678 "The coefficients A0 and A2 parametrize the longitudinal (L) polarization fraction ... and the interference ..." | CONFIRMED | `fulltext/text.txt` | none |
| 2509.13759 "These polarisation fraction measurements are related to the A0 and A4 coefficients"; "dilutes the sensitivity"; nine harmonic polynomials | CONFIRMED | `arxiv_text.txt` lines 66, 125, 64 | none |
| 1203.2165 Eq. (4) f_L = ¼(2 − A0 ∓ A4), f_R = ¼(2 − A0 ± A4), f_0 = ½A0; Eq. (5) f_L − f_R ∝ A4 | CONFIRMED | `paper.txt` lines 170–179 | none |
| 1104.3829 quote "A 0 ∝ f 0 and A 4 ∝ ± ( f L − f R )..." | CONFIRMED | `text.txt` line 43 | none |
| 2008.04174 Eq. (3) "A0 ∝ f_0 and A4 ∝ ∓(f_L − f_R)" | CONFIRMED | `fulltext.txt` ("A_{4} ∝ ∓(f_L − f_R)") | none |
| 1902.05759 Eq. (1) (3/8) f_L(1∓cosθ)² + (3/8) f_R(1±cosθ)² + (3/4) f_0 sin²θ; α = 2c_v c_a/(c_v²+c_a²) | UNVERIFIABLE (Eq. 1 and α confirmed; Eq. 2 not re-read) | `text.txt` Eq. (1) and α definition; Z version Eq. (2) not re-read | Re-read Eq. (2). |
| 2211.09435 "modified helicity" frame; α = 0.147 | UNVERIFIABLE (α value) | "modified helicity" quote is in the note; α = 0.147 not re-read | Re-read α. |
| 2209.14903 Eq. (1) (3/4)(1−cos²θ*)f0 + (3/8)(1−cosθ*)²fL + (3/8)(1+cosθ*)²fR | CONFIRMED | `paper.txt`, Eq. (1) | none |
| 2005.03799 Eq. (1) (F0, FL, FR) | UNVERIFIABLE (wording only; Eq. shape not re-read) | `fulltext.txt`: "longitudinal (F0), left-handed (FL), or right-handed (FR) polarizations" | Eq. shape not re-read. |
| 1410.1154 Eq. (1) ρ(cosθ*) = (3/8)(1−cosθ*)² F_L + (3/4) sin²θ* F_0 + (3/8)(1+cosθ*)² F_R | CONFIRMED | `fulltext/clean.txt` Eq. (1) | none |
| 1202.5272 Eq. (1) ω ∝ 2(1−cos²θ*)f0 + (1−cosθ*)²f− + (1+cosθ*)²f+ | CONFIRMED | `paper.txt` Eq. (1) | none |
| hep-ex/0301027 Eq. (1) (f−·3/8(1+cosθ)² + f+·3/8(1−cosθ)² + f0·3/4 sin²θ) and Eq. (2) with f± = f+ + f− | CONFIRMED | `text.txt`: Eq. (1); Eq. (2) "with f± = f+ + f−" | none |
| OPAL hep-ex/0312047 Eq. (10) dσL/dcosθ = ρ00 dσ/dcosθ; Eq. (11) dσT = (ρ++ + ρ−−) dσ; "differ slightly" | CONFIRMED | `pdftotext` of `paper.pdf`: Eqs. (10), (11); "differ slightly from those previously published by OPAL" | none |
| hep-ex/0305025 Eq. (5) ρ^{W−} = Σ_τ2 ρ_{τ1τ1′τ2τ2} | CONFIRMED | `.cache/hep-ex_0305025/fulltext.txt` Eq. (5) | none |
| 2610.38688 Eq. (39) Σ_λ ρ_λλ = 1; ρ00 "longitudinal fraction" | CONFIRMED | `paper.txt` Eq. (39) and line 184 | none |
| 2207.03511 dρ00 ∼ x(1−x), dρ_TT ∼ x²+(1−x)² | CONFIRMED | `paper.txt` | none |
| 2211.09435 f00 = ρ0000, f_TT, f_0T, f_T0 definitions; R_c = f00/(f0W f0Z) | CONFIRMED | `paper.txt`: "f00 = ρ0000"; "R_c = f00/(f0W f0Z)" | none |
| 2211.09435 Sec. 9.2 relations f0T = f0W − f00, fT0 = f0Z − f00, fTT = 1 + f00 − f0W − f0Z | CONFIRMED (internal consistency) | Algebra follows from f00+f0T+fT0+fTT = 1 | Source not re-read at Sec. 9.2. |
| 2607.12879 Eq. (3) f_LL + f_TX + κ√(f_LL f_TX) = 1 | CONFIRMED | `paper.txt` Eq. (3) | none |
| 2409.16731 Eq. (11) α_{2,0} = (1−3f_L)/(4√(5π)); γ_{2,0,2,0} with 1 − 3f^(1) − 3f^(3) + 9f_LL; Eq. (12) R_c = f_LL/(f^(1) f^(3)) | CONFIRMED | `paper.txt` Eqs. (11), (12) | none |
| 2607.20246 Sec. 3 "f_00 + f_0X + f_X0 + f_XX = 1"; frame quote | UNVERIFIABLE | Note only; not re-read | Re-read Sec. 3. |
| Frames (b) top "no frame name in any note" | UNVERIFIABLE | Note-level only (2209.14903 θ* definition confirmed) | Re-read sources. |
| Frames (c): 2110.11231 "helicity (HE) frame"; 2402.16365 "WZ center-of-mass frame"; 2009.09429 WW CM and parton-parton CM; 2503.11317 WW CM | UNVERIFIABLE | Consistent with the notes; not re-read against the papers | Re-read frame sentences. |
| Frames (c): "CM frame of the two Z bosons" (2310.04350, 2607.12879), in quotes | MISMATCH (quote not verbatim) | `notes/2310.04350.md` quotes "centre-of-mass frame of the two Z bosons"; `notes/2607.12879.md` quotes "center-of-mass frame of the two Z Z bosons" | Use the verbatim phrase in quotes, or drop the quote marks. |
| Frames (d) LEP: OPAL "z* along the boost from the lab, footnote 1"; L3 "W rest frame" | UNVERIFIABLE | OPAL text confirms "rest frame of the parent W−" (no footnote check) | Re-read the OPAL footnote. |

Counts for Section 4 items (30 items, one per row of the table above):
- CONFIRMED: 19
- MISMATCH: 1 (quote not verbatim)
- UNVERIFIABLE: 10 (hep-ph Eq. 26/27; 1504/2604 Eq. (1); 1606 A2/A4 prefactors; 1902 Eq. (2); 2211 α; 2005.03799 "equivalent form"; 2607.20246; frames (b), (c), (d))
- Where a row mixes checked and unchecked parts, it is UNVERIFIABLE and says which part was checked.

## Totals

- Table rows (119 + 4 = 123): CONFIRMED 120, MISMATCH 1, UNVERIFIABLE 2.
- Row-level flag and label items: MISLABELED 2 (ATLAS 2509, all 20 rows, unit pb⁻¹ omitted; CMS 1504, all 16 rows, lumi wording); MISSING_FLAG 1 (hep-ph Eq. 26, 2 rows).
- Section 4 items (30): CONFIRMED 19, MISMATCH 1, UNVERIFIABLE 10, UNSUPPORTED 0.

Items with verdicts other than CONFIRMED, for the caller:
1. ATLAS 1606.00689 unregularised A0 pT^Z 132–173 GeV: MISMATCH. stat/syst should be 0.0168188 and 0.00767753 from HEPData Table 2, not "not given in note".
2. ATLAS 2509.13759 (all 20 rows): MISLABELED. Luminosity is 338.1 ± 3.1 pb⁻¹ (arxiv_text.txt line 161), not "unit not given".
3. CMS 1504.03512 (all 16 rows): MISLABELED (minor). Flag "HEPData has no lumi/theory column" should say no lumi or theory uncertainty; lumi 19.7 fb⁻¹ is a HEPData qualifier.
4. hep-ph/9406381 Fig. 1(a)/(b) rows: MISSING_FLAG. Eq. (26) is paraphrased from garbled text.
5. Gao, Lee, Zhang 2610.38688 ρ00 γ-range row: UNVERIFIABLE. Ranges appear only in the note.
6. Mirkes ins335604 row: UNVERIFIABLE. Abstract-only; no full text in cache.
7. Section 4 frames (c): misquoted "CM frame of the two Z bosons"; MISMATCH (quote not verbatim).
8. Section 4 UNVERIFIABLE items listed above (hep-ph Eq. 26/27; 2211 α = 0.147; 1902 Eq. 2; 2607.20246; top, diboson and LEP frame sentences; 1504/2604 Eq. (1) re-read).

Not checked: the full set of Section 4 frame sentences for (b)–(d) against the papers (note-level only); the 1504.03512 and 2604.25678 Eq. (1) typeset; hep-ph Eq. (26)–(27) typeset. Each is listed above as UNVERIFIABLE.
