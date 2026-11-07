# Verification of polarization_fL.md, Section 2(b), 2(c) and Section 5

Scope: `polarization_fL.md` Section 2 tables (b) and (c) (21 + 63 rows) and Section 5 (Caveats, 21 sub-claims). Section 2(a), 2(a′), 2(d) and Section 3–4 were not checked.

Method: every row's numbers, units, frames, stat/syst columns and flags were compared with the cited note. Values were then re-read from the source: HEPData JSON in `.cache/<id>/hepdata/tables/` where it exists, otherwise `paper.txt` / `fulltext.txt` / `text.txt`. For 1410.1154 the printed page was checked against `paper.pdf` with pdftotext. The values were compared by reading and grep, not by a single script over all rows, so treat the CONFIRMED rows as checked by hand. No HEPData was contacted.

## Non-CONFIRMED items

| row (paper + bin) | item | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| 2209.14903, f0 / fL / fR (b1–b3) | flags: Table 3 totals and linearity non-closure | MISSING_FLAG | notes/2209.14903.md, Open issues: "I did not verify the total"; linearity-test term "not clear ... whether ... in the Table 3 totals; flagged, not resolved". Source `.cache/2209.14903/paper.txt`, Sec. 9: "A small degree of non-closure is observed but the corresponding uncertainty is negligible and does not change the total uncertainties listed in Table 3." | Add flag: Table 3 totals not checked against quadrature; whether the linearity-test term is inside them is unresolved. |
| 2005.03799, CMS e+jets, CMS μ+jets, CMS single top (b9–b11) | stat column is stat-only for CMS; values are pre-combination inputs with CMS ttbar modelling uncertainties modified | MISSING_FLAG | `.cache/2005.03799/fulltext.txt`: "For CMS measurements, the first uncertainty is statistical, while the second is the total systematic uncertainty, including that on background determination." Sec. 0.2.3: "polarization fractions from the input measurements before applying the modifications concerning the combination". Sec. 0.3 modifies CMS (ee and μμ+jets) ttbar modelling. The ATLAS input row carries a "before symmetrisation" flag; the CMS rows carry none. | Add to each CMS input row: "stat only (CMS); published values before combination modifications". |
| 1410.1154, μ channel (b12) and e channel (b13) | flag "note page labels are off by one" | MISMATCH | notes/1410.1154.md, Open issues: "printed page = PDF index − 2". Checked: `.cache/1410.1154/fulltext/paper.pdf`, PDF page 11 prints page number "9". | Replace with "printed page = PDF index − 2 (PDF p.11 = printed p.9)". |
| 1410.1154, combined mu+e (b14) | derived F_R; F_R outside μ/e interval | MISSING_FLAG | notes/1410.1154.md, Caveats: "Combined F_R (-0.018) lies outside the muon/electron F_R interval; the paper attributes this to the sum constraint". Table row gives F_R with no "derived" flag. | Add "F_R derived from sum = 1; lies outside μ and e intervals (Sec. 8)". |
| 2211.09435, f0T W±Z (c19) | "obs 3.4σ (exp 5.4σ) stated jointly for f0T, fT0, fTT" | MISMATCH | `.cache/2211.09435/paper.txt`, Sec. 9.1: "other joint helicity fractions f0T, fT0 and fTT are also measured with observed (expected) significances of 3.4σ (5.4σ), 7.1σ (6.6σ) and 11σ (9.7σ)" (one value per fraction, in that order). notes/2211.09435.md agrees (fT0 obs 7.1σ, fTT obs 11σ). | Replace with "obs 3.4σ (exp 5.4σ) for f0T; fT0 obs 7.1σ (exp 6.6σ); fTT obs 11σ (exp 9.7σ) (Sec. 9.1)". |
| 2211.09435, f0T W±Z (c19) | Table 3 total inconsistency not flagged on this row (it is flagged on f00) | MISSING_FLAG | notes/2211.09435.md, Open issues: f0T total 18% does not match Table 2 (0.029 on 0.110, i.e. 26%). Table 3 in `.cache/2211.09435/tables.txt`: f0T total 18. | Add the same "Table 3 totals unverified" flag as on the f00 row. |
| 2402.16365, f_00 rows (c31–c38) | frame cell attributes "modified helicity frame" to the measured f_00 | UNSUPPORTED | notes/2402.16365.md, Open issues: "Measurement frame: not stated." The only frame sentence in `.cache/2402.16365/fulltext.txt` is "The boson polarizations are defined in the WZ center-of-mass frame", which applies to polarised MC templates. The modified-helicity frame is that of Ref. [12] = 2211.09435, not a statement about this measurement. | Frame cell: "not stated for the measurement; polarised MC templates in WZ CM frame; f_00 defined in Ref. [12] (2211.09435, modified helicity frame)". |
| 2607.12879, f_LL inclusive (c41) | level (particle vs detector) not stated; preprint status | MISSING_FLAG | notes/2607.12879.md, Caveats: "Whether f_LL and μ_LL are extracted at detector level is not stated explicitly". Header: "journal ref: preprint (ATLAS journal field reads PRL, not published as of this note)". | Add "level not stated; preprint, not published". |
| 2607.20246, f_X0 (c48) | journal reference unconfirmed | MISSING_FLAG | notes/2607.20246.md, Open issues 6: "Journal reference unconfirmed (preprint only)." | Add "preprint; journal reference unconfirmed". |
| 2009.09429, CMS WW σ×B rows (c53–c58) | no level flag; fiducial cross sections are at generator level with dressed leptons | MISSING_FLAG | notes/2009.09429.md, Caveats: "defined at generator level (dressed leptons, anti-k_T R = 0.4 jets)". Source `.cache/2009.09429/_verify_text.txt`: "The leptons at the generator level are selected at ..." and "The jets at generator level are clustered from stable ...". | Add "generator-level fiducial, dressed leptons (ΔR = 0.1)". |
| 2409.16731, ZZ α^(1)_{2,0} / γ_{2,0,2,0} (c60) | NLO QCD values differ between paper Table 1 and Table 3; not flagged | MISSING_FLAG | notes/2409.16731.md, Open issues: Table 1 gives α^(1)_{2,0} = 0.02807(5) and Table 3 gives 0.02794(13); "Not reconciled". Source `.cache/2409.16731/paper.txt` shows both 0.02807(5) and 0.02794(13) in the ZZ block. | Add the Table 1 vs Table 3 discrepancy as a flag. |
| 2409.16731, R_c comparison (c63) | compares theory for ZZ and W⁺Z with ATLAS R_c for W±Z | MISSING_FLAG | notes/2409.16731.md: R_c "defined as in ATLAS 2211.09435"; notes/2211.09435.md: measured R_c = 1.54 ± 0.35 is "in W±Z events". The row's ZZ and W⁺Z theory values are compared with the W±Z measurement without a flag. | Add "channel differs: measured value is W±Z; theory rows are ZZ and W⁺Z". |
| Section 5, caveat 2: "W+jets f_0 is in the helicity frame (1104.3829, 1203.2165)" | 1203.2165 cited as an f_0 example | MISLABELED | notes/1203.2165.md records the measured quantities as the coefficients A_0–A_7 (Eq. 1), with no f_0 value. The paper's Sec. 2.2 discusses helicity fractions, but no f_0 is measured there. Only 1104.3829 measures f_0 (notes/1104.3829.md, Table 1). | Cite 1203.2165 only for A_i in the helicity frame (its Sec. 2.2 frame definition). Keep 1104.3829 as the f_0 example. |
| Section 5, caveat 2: "diboson fractions are in the diboson CM frame" | general claim; 2110.11231 is not in that frame by its note | UNSUPPORTED | notes/2110.11231.md, Model/observable: "Frame: helicity (HE) frame", with no diboson CM named. Source `.cache/2110.11231/text.txt`: "results are shown in terms of the helicity (HE) frame, as defined in Ref. [78]". | Exclude 2110.11231 from the claim, or say its frame is the HE frame of Ref. [78]. |
| Section 5, caveat 3: "f_00 / f_LL / f_X0 / f_0X ... are joint diboson quantities" (2211, 2402, 2607.12879, 2607.20246) | f_X0 and f_0X are single-boson | MISMATCH | notes/2607.20246.md, Model/observable: "Single-boson fractions f_0X (W longitudinal, Z any), f_X0 (Z longitudinal, W any)". The f_X0 and f_0X rows of Section 2(c) label them single-boson. | Split the sentence: joint = f_00 (2211, 2402, 2607.20246) and f_LL (2607.12879); single-boson = f_X0, f_0X (2607.20246). |
| Section 5, caveat 4: "No hadronic (boosted) V longitudinal fraction has been measured in any note" | universal negative | UNVERIFIABLE | Keyword sweep of notes for "hadronic"/"boosted" (grep over `notes/*.md`) found no hadronic-V longitudinal fraction. The sweep was not an exhaustive reading of every note, so the universal claim cannot be fully verified. | Restrict to "in the notes listed in Section 1", or read the remaining notes. |
| Section 5, caveat 9: "L3 21.8 ± 2.7 ± 1.6 % ... and the L3 paper's 0.218 ... are listed separately" | 21.8 % value listed | MISMATCH | notes/hep-ex_0305025.md (row "L3 longitudinal fraction ... 21.8 %"). Section 2(d) has only the hep-ex/0301027 row (0.218 ± 0.027 ± 0.016); no row carries 21.8 %. | Add a 21.8 % row citing hep-ex/0305025, or remove "listed separately". |

## Counts per verdict

Section 2(b) and 2(c), counted by row (84 rows; each row takes its worst verdict; each value in each row was checked):

| verdict | rows |
|---|---|
| CONFIRMED | 63 |
| MISLABELED | 0 |
| MISMATCH | 3 (2 in b, 1 in c) |
| UNSUPPORTED | 1 (c) |
| MISSING_FLAG | 17 (7 in b, 10 in c) |
| UNVERIFIABLE | 0 |

Section 5, counted per sub-claim (21 sub-claims):

| verdict | sub-claims |
|---|---|
| CONFIRMED | 16 |
| MISLABELED | 1 |
| MISMATCH | 2 |
| UNSUPPORTED | 1 |
| UNVERIFIABLE | 1 |

## Confirmed rows (summary)

- 2209.14903: NNLO prediction row (b4). Its value and "same value in 2005 Sec. 0.1 and 1410 Sec. 1" are confirmed (both source texts give 0.687 ± 0.005).
- 2005.03799: F0, FL and FR combination rows, ATLAS input row (b5–b8). Feldman–Cousins with FR ≥ 0 is confirmed in `.cache/2005.03799/fulltext.txt`.
- 1410.1154: all nine values match HEPData Tables 1–3 (`.cache/1410.1154/hepdata/tables/`).
- 1202.5272: all 7 rows (b15–b21) match Abstract, Eqs. (3)–(6) and Table I, including the 0.030 vs 0.031 f+ 1D syst.
- 1902.05759: all 9 rows (c1–c9) match HEPData Table 24 and paper Tables 5–6. Significances match Sec. 11.2.
- 2110.11231: all 8 rows (c10–c17) match HEPData `Polarization_fraction_measurements_1D.json`.
- 2211.09435: rows c18, c20–c30 match paper Tables 2–4 (`.cache/2211.09435/tables.txt`); significances match Sec. 9.1.
- 2402.16365: values and significances of rows c32–c38 match HEPData Tables 1–4 and the paper text.
- 2310.04350: μ_LL and σ_fid rows match the text and HEPData metadata (c39–c40).
- 2607.12879: all seven rows (c42–c47) match the paper text and Tables 3–4.
- 2607.20246: values, uncertainties and upper limits (c49–c50) match HEPData Table 5 and paper text.
- 2503.11317: both rows (c51–c52) match Table 1 and the Conclusions.
- 2507.03500: "not measured" row (c59) matches the note.
- 2409.16731: rows c61–c62 match Table 3 and Table 7 values in the source text; the Eq. (11) mapping is confirmed.

## Source notes

- Verification method: manual reading plus targeted grep and HEPData JSON. No single script was run over all rows.
- Section 2(d), Sections 3–4 and the Q2/Q3 scope decisions were not checked.
- Notes for 1104.3829, 1203.2165, 1606.00689, 2203.01602, 2509.13759 and 2604.25678 were read only for the Section 5 claims, not in full.
