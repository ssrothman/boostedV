# Verification report: w3_2 (five claim files)

Verdict: the claims are largely accurate. Every HEPData-sourced number checked matches its JSON table, and every headline value matches the paper. Non-confirmed items are quote and location errors, one unsupported qualifier, one unverifiable block, and one omission set (Q3 values in hep-ex/0301027). One omission (f_00 frame in 2402.16365) can now be resolved from 2211.09435.

Method: HEPData JSON read from `<cache>/hepdata/tables/`. Paper text read from cache `fulltext.txt`, `paper.txt`, `html.txt` or `paper.pdf` text layer. Scratch checker scripts are in `/tmp/verify_w3_2/` (not in the repo). Quotes checked by grep and line reads.

## Non-CONFIRMED rows

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| 2402.16365 | Relative-uncertainty block, "HEPData Table 6" (10 rows; location "Data from Tables 7 and 8 of the paper") | UNVERIFIABLE (paper side) | HEPData `Table_6.json` location field is "Data from Tables 7 and 8 of the paper". Tables 7–8 are not in cache `fulltext.txt` (grep finds no "Table 7"/"Table 8"). All 10 values match the JSON (Jets 5.9/9.0/3.1/4.8; Total systematic 12.1/17.7/8.1/13.9; etc.). | Keep HEPData values, label "paper Tables 7–8 not checked against paper". |
| 2402.16365 | Model/observable bullet and Open issues: f_00 definition "as defined in Ref. [12]", frame "not stated", Ref. [12] "not fetched" | OMISSION (resolvable from cache) | Ref. [12] in `fulltext.txt` line 243–247 is "Observation of gauge boson joint-polarisation states in W±Z ... Phys. Lett. B 843, 2023, 137895". That is arXiv 2211.09435 (its HEPData `record.json` journal ref is "Phys.Lett.B 843 (2023) 137895"). 2211.09435 `paper.txt` Sec. 2 (lines ~91–111) defines f00 = ρ0000 and states the frame: "fix the reference z-axis to the direction of the corresponding boson in the diboson centre-of-mass frame ... modified helicity coordinate system". | Replace "frame not stated" with a pointer to 2211.09435 Sec. 2; the frame is the diboson CM frame with z along each boson. |
| 2211.09435 | f00 (W±Z) row, expected significance "6.2σ (no-signal hypothesis)" | UNSUPPORTED (qualifier) | Sec. 9.1, `paper.txt` line 642: "compared to 6.2σ expected." No hypothesis is named. The phrase "no spin-correlations hypothesis" (line 1288) refers to R_c only. | Delete "(no-signal hypothesis)" or cite where it is defined. |
| 2211.09435 | Model bullet: frame quote "maximises the decorrelation between 0 and T helicity states" | MISMATCH (quote) | Sec. 2, `paper.txt` line 111 and `paper.html`: "This choice also maximises the decorrelation between 00 and TT helicity states." | Quote as "between 00 and TT helicity states". |
| 2211.09435 | f0T (W±Z) row, location "Abstract; Table 2; Sec. 9.1" | WRONG_LOCATION | Quote "other joint helicity fractions f0T, fT0 and fTT are also measured with observed (expected) significances of 3.4σ (5.4σ)" is in Sec. 9.1 only (`paper.txt` line 643). The abstract (`paper.html`, ltx_abstract) gives only 7.1σ and the four fractions. | Location: Sec. 9.1 (drop "Abstract" for this quote). |
| hep-ex_0305025 | Frame bullet: "W decay angles ... 'in the corresponding W rest frame' (Sec. 1)" | WRONG_LOCATION | `fulltext.txt` lines 145–150: "W-decay fermions in the corresponding W rest frame". This lies in Sec. 2 (TGC section, Sec. 2 starts line 94). Sec. 1 is lines 77–93. | Cite "Sec. 2". |
| hep-ex_0305025 | Caveat: "Sec. 1 says 'Limits are set on CP-violating couplings...'" | WRONG_LOCATION | Sentence is in the abstract (`fulltext.txt` lines 66–67, before the Sec. 1 heading at line 77). | Cite "Abstract". |
| hep-ex_0305025 | Frame: "The angle definition is in Fig. 2 (left)" for the SDM | MISLABELED | Fig. 2 caption (`fulltext.txt` line 140): "Left: The definition of the angles used in the coupling extraction". The figure is for the TGC analysis, not the SDM. | State that the SDM section gives no figure for the quantization axis; Fig. 2 is for TGC extraction. |
| hep-ex_0312047 | Model bullet, CP-odd definitions: "Delta^CP_{+-,+0,-0} = sigma^{W-} - sigma^{W+}" | MISLABELED (minor shorthand) | `pdftotext` of paper.pdf, Eqs. 16–18: Δ^CP_{+−} = σ^{W−}_{+−} − σ^{W+}_{−+}; Δ^CP_{+0} = σ^{W−}_{+0} − σ^{W+}_{−0}; Δ^CP_{−0} = σ^{W−}_{−0} − σ^{W+}_{+0}. Subscripts differ per observable. | Write per-element subscripts as in Eqs. 16–18. |
| hep-ex_0301027 | Table 2 row "W− → ℓ− ν Data" quote | MISMATCH (quote) | PDF text (`paper.txt`, Table 2) and arXiv HTML (`html.txt`, Sx5.T2): "0.559 ± 0.038 ± 0.016 \| 0.201 ± 0.026 ± 0.015 \| 0.240 ± 0.051 ± 0.017". The claim quotes 0.200, which is the Table 4 W− f+ value. The row's value (f0 = 0.240) is correct. | Change quoted f+ to 0.201. |
| hep-ex_0301027 | Selection bullet: "reconstructed momentum ... 20 GeV for electrons and 15 GeV for muons" written as "p_T" | MISLABELED (minor) | `paper.txt` Sec. Data: "The reconstructed momentum must be greater than 20 GeV for electrons and 15 GeV for muons." Transverse momentum is not stated. | Write "momentum" unless pT is confirmed. |

## Verifier-noted omissions (hep-ex_0301027; the claim's own omission bullet)

Claim: "f− and f+ values (Tables 2–4 and 6) are diagonal SDM elements and are in Q3 scope; not transcribed." Confirmed in scope: the paper measures f−, f+ and f0 as diagonal SDM elements (`paper.txt` Sec. 2, lines 46–49). Caveat: the paper fixes f+ by unitarity ("The fraction f+ is obtained by constraining the sum of all three parameters to unity", line 137), so f+ is not an independent measurement. Values as printed (PDF text layer, consistent with `html.txt`):

- Table 2 (leptonic, W− parameters): W− f− 0.559 ± 0.038 ± 0.016, f+ 0.201 ± 0.026 ± 0.015; W+ f− 0.625 ± 0.037 ± 0.016, f+ 0.179 ± 0.023 ± 0.015; W± f− 0.589 ± 0.027 ± 0.016, f+ 0.189 ± 0.017 ± 0.015. KORALW MC: f− 0.592 ± 0.003, f+ 0.170 ± 0.002, f0 0.238 ± 0.004.
- Table 3 (hadronic): only f± (= f+ + f−) and f0 are given. f± is 0.750 ± 0.056 ± 0.039 (W−), 0.833 ± 0.062 ± 0.039 (W+), 0.785 ± 0.042 ± 0.039 (W±). No separate f− or f+.
- Table 4 (combined, W− parameters): W− f− 0.555 ± 0.037 ± 0.016, f+ 0.200 ± 0.026 ± 0.015; W+ f− 0.634 ± 0.038 ± 0.016, f+ 0.181 ± 0.024 ± 0.015; W± f− 0.592 ± 0.027 ± 0.016, f+ 0.190 ± 0.017 ± 0.015. KORALW MC: f− 0.590 ± 0.003, f+ 0.169 ± 0.002.
- Table 6 (cos Θ_W− bins; MC in parentheses), f− and f+ per bin:
  - [−1.0, −0.3]: f− 0.173 ± 0.041 ± 0.033 (0.156 ± 0.006); f+ 0.418 ± 0.060 ± 0.043 (0.431 ± 0.008)
  - [−0.3, 0.3]: f− 0.509 ± 0.055 ± 0.029 (0.446 ± 0.006); f+ 0.303 ± 0.040 ± 0.032 (0.282 ± 0.005)
  - [0.3, 0.9]: f− 0.683 ± 0.042 ± 0.026 (0.723 ± 0.004); f+ 0.135 ± 0.027 ± 0.030 (0.119 ± 0.003)
  - [0.9, 1.0]: f− 0.708 ± 0.093 ± 0.056 (0.647 ± 0.007); f+ −0.010 ± 0.055 ± 0.028 (0.029 ± 0.004)

Table 6 header reads "W± Data"; caption reads "W− helicity fractions". The claim's open issue on this is correct.

## Other omissions

- 2402.16365: the f_00 frame omission above (Ref. [12] = 2211.09435). No other in-scope omission found in the cached text.
- 2211.09435: none beyond figure-only values (Fig. 4, Fig. 5 differential cross sections, not Q2/Q3 fractions).
- hep-ex_0305025: none in text. The DELPHI longitudinal fraction is referred to ("In DELPHI and OPAL ... measure ... longitudinally polarised W") but no DELPHI number appears in the text.
- hep-ex_0312047: none. Results rows are all extracted.

## Verified items (CONFIRMED summary, by file)

- 2402.16365: HEPData Tables 1–4, 20, 21, 34–45 match JSON (values, stat/syst signs, totals). Paper Table 2 values, correlations (−0.84, −0.82), significances (5.2/4.3, 1.6/2.5, 7.7/6.9, 3.2/4.2), SM predictions, f_TT values, Sec. 2 and RAZ quotes, selections (electrons 15 GeV, crack, jets 30 GeV, |m_ll − m_Z| < 10 GeV, m_T^W > 30 GeV, BDT with seven variables), and the 10% / 27% background subtraction all match. Observation that the paper's own D formula labels the central and side regions with different variables (|ΔY(WZ)| vs |ΔY(ℓ_W Z)|) is recorded as written, which the claim already notes.
- 2211.09435: all Table 2, 3, 4, 5 entries and the Table 3 and Table 5 systematic totals match the cache `tables.txt`. Abstract values, significances (7.1/6.2, 3.4/5.4, 7.1/6.6, 11/9.7, W+Z 6.9, W−Z 4.1), R_c = 1.54 ± 0.35 with 1.6σ and NLO 1.3, α = 0.147, Eqs. 1–2, joint and individual relations (Sec. 9.2), interference 0.6% and ≤4% (HTML alttext "4"; the text layer's "44%" is an extraction artefact), jets (25 GeV, |η|<4.5, R=0.4), lepton and fiducial cuts, and the HEPData record (DOI 10.17182/hepdata.135074.v2; cross sections and correlation matrices only) all match. The claim's own open issue is correct: Table 3 relative totals disagree with Table 2 values (f00: 0.010/0.067 = 15% vs printed 19%; f0T: 0.029/0.110 = 26% vs 18%). fT0 also differs slightly (0.023/0.179 = 13% vs 14%). Table 5 Z f0 (10%) vs Table 4 (0.019/0.231 = 8%) is confirmed.
- hep-ex_0305025: abstract luminosity (700 pb^-1 per experiment), OPAL CP couplings (g4Z, κ̃γ, λ̃γ) with "Both statistical and systematic uncertainties are included", OPAL σL/σtot 21.0 ± 3.3 ± 1.6% vs SM 25.7%, L3 21.8 ± 2.7 ± 1.6% vs 24.1%, KORALW, "statistical only" captions, CPT/CP equations (7–8), and the Fig. 5 left/right text-caption disagreement all match.
- hep-ex_0312047: all 131 HEPData rows (Tables 1–7, script-checked for Tables 2–7 and manually for Table 1) match the JSON. Table 3 bias shifts (14 rows), Table 4 systematics (10 rows), Table 5 MC column, Table 6 CP/CPT values, abstract 23.9 ± 2.1 ± 1.1, 678.5 pb^-1, 4176 events, 78–81% efficiency and 93–95% purity, 40% bin correlations, and the normalisation statement all match. Journal ref (Phys.Lett.B 585 (2004) 223) matches HEPData record 49660. The Tables 5–7 column mapping is supported by Eqs. 16–18 (HEPData header labels equal the Eq. 16–18 structure), though the P=3/P=4 to W± mapping is not stated in the paper.
- hep-ex_0301027: Table 1 per-energy luminosities sum to 684.8 pb^-1; 2010 events, 65.7% efficiency, 96.3% purity; Table 2–4 f0 values and uncertainties; Table 4 MC; Table 5 systematics (0.017, 0.039); Table 6 f0 rows and bin bounds; "seven standard deviations, including systematic uncertainties" (verbatim); 0.271 → 0.223; Eq. 2 coefficients (3/4, 3/2, from HTML). Journal header "Submitted to Phys. Lett. B" and arXiv v1 16 Jan 2003 match the PDF text layer. Note the claim's own open issue (Table 6 "W±" vs caption "W−") is correct.

## Counts (claim rows as defined above)

- CONFIRMED: 230 (2402.16365: 14 quoted-result rows plus 12 uncertainty tables checked; 2211.09435: 23 rows; hep-ex_0305025: 8 rows; hep-ex_0312047: 163 rows; hep-ex_0301027: 22 rows)
- MISMATCH: 2 (2211.09435 frame quote; hep-ex_0301027 W− leptonic f+ quote)
- WRONG_LOCATION: 3 (2211.09435 f0T row; hep-ex_0305025 two bullets)
- MISLABELED: 3 (hep-ex_0305025 Fig. 2 attribution; hep-ex_0312047 CP shorthand, minor; hep-ex_0301027 "p_T" vs momentum, minor)
- UNSUPPORTED: 1 (2211.09435 "no-signal hypothesis" qualifier)
- UNVERIFIABLE: 1 block, 10 rows (2402.16365 HEPData Table 6; paper Tables 7–8 not in cache, HEPData values match)
- OMISSION: 2 items (2402.16365 f_00 frame, resolvable from 2211.09435 Sec. 2; hep-ex_0301027 f−/f+ values, Tables 2, 4, 6, listed above)

## Non-CONFIRMED rows (summary)

Listed in the table above. None of the errors changes a headline value. The two MISMATCH items are quote-level and the two WRONG_LOCATION items in hep-ex_0305025 and 2211.09435 concern citation locations only.
