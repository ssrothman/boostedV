# Verification of W1 claim files (verify_w1_5)

Counting unit: one row = one claim-table row. Coefficient rows in 1606.00689 are grouped across the three pT bins when all three bins share one verdict. Pin-point locations are paper.txt line numbers in the cache, or HEPData table numbers.

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| 1104.3829 | Table 1, mu (f_L-f_R)-, 0.240 +/-0.036 +/-0.031 | CONFIRMED | Table 1 text (text.txt L72) and Abstract (L35): "( f L − f R ) − = 0.240 ± 0.036 (stat.) ± 0.031 (syst.)" | none |
| 1104.3829 | Table 1, mu f0-, 0.183 +/-0.087 +/-0.123 | CONFIRMED | Table 1 (L74), Abstract (L35) | none |
| 1104.3829 | Table 1, mu (f_L-f_R)+, 0.310 +/-0.036 +/-0.017 | CONFIRMED | Table 1 (L78), Abstract | none |
| 1104.3829 | Table 1, mu f0+, 0.171 +/-0.085 +/-0.099 | CONFIRMED | Table 1 (L80), Abstract | none |
| 1104.3829 | Table 1, e (f_L-f_R)-, 0.187 +/-0.069 +/-0.066 | CONFIRMED | Table 1 (L60) | none |
| 1104.3829 | Table 1, e f0-, 0.130 +/-0.200 +/-0.174 | CONFIRMED | Table 1 (L62) | none |
| 1104.3829 | Table 1, e (f_L-f_R)+, 0.277 +/-0.060 +/-0.050 | CONFIRMED | Table 1 (L66) | none |
| 1104.3829 | Table 1, e f0+, 0.240 +/-0.190 +/-0.090 | CONFIRMED | Table 1 (L68) | none |
| 1104.3829 | Table 1, combined (f_L-f_R)-, 0.226 +/-0.031 +/-0.050 | CONFIRMED | Table 1 (L84) | none |
| 1104.3829 | Table 1, combined f0-, 0.162 +/-0.078 +/-0.136 | CONFIRMED | Table 1 (L86) | none |
| 1104.3829 | Table 1, combined (f_L-f_R)+, 0.300 +/-0.031 +/-0.034 | CONFIRMED | Table 1 (L90) | none |
| 1104.3829 | Table 1, combined f0+, 0.192 +/-0.075 +/-0.089 | CONFIRMED | Table 1 (L92) | none |
| 1104.3829 | Table 1 correlation pairs (W-/W+, e/mu/comb) | CONFIRMED | Table 1 text rows (L60-L92): e −0.204/−0.283 [W-], e −0.295/0.001 [W+], mu 0.395/−0.308 [W-], mu −0.721/−0.269 [W+], comb 0.304/−0.326 [W-], comb −0.660/−0.121 [W+]. The paper does not name the parameter pair; the claim already says so. | none |
| 1104.3829 | 7.8 sigma (W+), 5.1 sigma (W-) L-R significance | CONFIRMED | Conclusion (L176): "a significance of 7.8 standard deviations for W+ bosons and 5.1 standard deviations for W-" | none |
| 1104.3829 | Table 2 systematics (electron, muon, combined; recoil scale/resolution, electron and muon scale) | CONFIRMED | Table 2 text (L100-L140), all 4 columns checked for every row quoted | none |
| 1104.3829 | Setup: 36 +/-1.4 pb-1, 7 TeV, counts 5485/8626, lepton and jet cuts, 0.0<L_P<1.3, EW norm fixed, helicity frame, phi* convention | CONFIRMED | Text L35, L48-L52, L92-L100, L176; "36 ± 1.4 pb -1" present in text | none |
| 1203.2165 | Table 11, f0 data 35-50 GeV, 21.9 +3.3 (stat) +13.4 (syst) | CONFIRMED | Table 11 (paper.txt L1066-1075): "Data 23.8 \pm 2.0 \pm 3.4 25.2 \pm 1.7 \pm 3.0 21.9 \pm 3.3 \pm 13.4 12.7 \pm 3.0 \pm 10.8". Column order (f_L-f_R 35-50, f_L-f_R >50, f0 35-50, f0 >50) confirmed by the Abstract (f0 = 0.127 for >50, f_L-f_R = 0.252 for >50) | none |
| 1203.2165 | Table 11, f0 data >50 GeV, 12.7 +3.0 +10.8 | CONFIRMED | Table 11 (L1075); Abstract "f_{0} = 0.127 \pm 0.030 \pm 0.108" | none |
| 1203.2165 | Table 11, f_L-f_R data 35-50 GeV, 23.8 +2.0 +3.4 | CONFIRMED | Table 11 (L1075) | none |
| 1203.2165 | Table 11, f_L-f_R data >50 GeV, 25.2 +1.7 +3.0 | CONFIRMED | Table 11; Abstract "f_{\mathrm{L}}-f_{\mathrm{R}} = 0.252 \pm 0.017 \pm 0.030" | none |
| 1203.2165 | Table 8, muon f0 23.6 (35-50) and 7.6 (>50), with 3 uncertainties each | CONFIRMED | Table 8 (L974-L1000): "muon average 23.6 \pm 3.8 \pm 12.0 \pm 7.2 / 7.6 \pm 4.8 \pm 9.0 \pm 5.2"; uncertainty split per caption (stat / instr.+analysis / template) | none |
| 1203.2165 | Table 8, electron f0 20.1 and 17.7 | CONFIRMED | Table 8: "electron average 20.1 \pm 6.9 \pm 12.0 \pm 5.0 / 17.7 \pm 4.3 \pm 9.0 \pm 6.0" | none |
| 1203.2165 | Table 8, muon f_L-f_R 21.7 and 25.0 | CONFIRMED | Table 8: "muon average 21.7 \pm 3.0 \pm 3.6 \pm 2.0 / 25.0 \pm 2.5 \pm 2.3 \pm 2.5"; cross-checked to Table 10 | none |
| 1203.2165 | Table 8, electron f_L-f_R 26.0 and 25.5 | CONFIRMED | Table 8: "electron average 26.0 \pm 2.8 \pm 3.4 \pm 2.0 / 25.5 \pm 2.6 \pm 2.0 \pm 2.0"; Table 10 | none |
| 1203.2165 | mc@nlo f_L-f_R 27.1 and 26.2 (stat only) | CONFIRMED | Table 11 (L1076-1077): "mc@nlo 27.1 \pm 0.7 26.2 \pm 0.5 17.9 \pm 1.2 21.0 \pm 1.0" | none |
| 1203.2165 | powheg f_L-f_R 19.9 and 21.2 (stat only) | CONFIRMED | Table 11: "powheg 19.9 \pm 1.0 21.2 \pm 0.8 22.9 \pm 1.0 19.4 \pm 0.8" | none |
| 1203.2165 | mc@nlo f0 17.9 and 21.0 (stat only) | CONFIRMED | Table 11 (same row) | none |
| 1203.2165 | powheg f0 22.9 and 19.4 (stat only) | CONFIRMED | Table 11 (same row) | none |
| 1203.2165 | Trigger: single-muon p_T >= 13 GeV, single-electron p_T >= 15 GeV, cited "(Sec. 3.2)" | WRONG_LOCATION | Trigger text is in Sec. 3.4 "Event selection" (paper.txt L291-L293): "a single-muon trigger with a requirement on the transverse momentum p_T^l of at least 13 GeV, or a single-electron trigger, with a p_T^l requirement of at least 15 GeV". Sec. 3.2 (L221) covers only the data sample and luminosity. Values are correct. | Change "Sec. 3.2" to "Sec. 3.4". |
| 1203.2165 | Acceptance |eta_l|<2.4, p_T^nu>25, p_T^l>20, 50<m_T^W<110, cited "(Sec. 8.6)" | WRONG_LOCATION | Sentence is in Sec. 10 (Summary, paper.txt L1116; arxiv_html): "Corrected results correspond to the following acceptance region: |ηℓ| < 2.4, pTν > 25 GeV, pTℓ > 20 GeV and 50 < mTW < 110 GeV". Sec. 8.6 (L958-1028) refers to "acceptance and m_T^W cuts as used here" without numbers. Values are correct. | Cite Sec. 10 (or Sec. 3.4 for the m_T cut at 50 and 110 GeV). |
| 1203.2165 | Luminosity 37.3 pb-1 (e), 31.4 pb-1 (mu); "about 35 pb-1" | CONFIRMED | paper.txt L223 (Sec. 3.2): "integrated luminosities of 37.3 pb-1 for the electron channel and 31.4 pb-1 for the muon channel"; Abstract "about 35 pb-1" | none |
| 1203.2165 | cos theta_2D "transverse helicity" measured variable, cited "(Sec. 2.2, Sec. 10)" | WRONG_LOCATION | Definition is in Sec. 2.3 (heading L183; definition L188-L189: "cos\theta_{\rm 2D}=..."). Sec. 10 (L1111) mentions it, so Sec. 10 is correct. Sec. 2.2 is the helicity-fraction section. | Cite Sec. 2.3 instead of Sec. 2.2. |
| 1203.2165 | Eq. 4 relations and upper/lower sign for W+/W- | CONFIRMED | Sec. 2.2, Eq. (4) (L168-L178): "where the upper (lower) sign corresponds to W^{+} ( W^{-} ) boson production respectively" | none |
| 1203.2165 | Eq. 5, f_L - f_R = -/+ A4/2 | CONFIRMED | Sec. 2.2, Eq. (5) (L180-L183): "f_{\mathrm{L}}-f_{\mathrm{R}}=\mp\frac{A_{4}}{2}" | none |
| 1203.2165 | Eq. 1 coefficients A0-A7; A5-A7 neglected | CONFIRMED | Sec. 2.1 (L108-L134): "They are neglected in this analysis." | none |
| 1203.2165 | Helicity frame definition (Sec. 2.2) | CONFIRMED | L152: "The helicity frame is the W rest frame with the z -axis along the W laboratory direction of flight and the x -axis in the event plane, in the hemisphere opposite to the recoil system." | none |
| 1203.2165 | Sec. 8.5 recoil scale: "largest systematic ... worst case 16% on f0" | CONFIRMED | Sec. 8.5 (L953): "This is the largest systematic uncertainty on the helicity fractions measured in this study. In the worst case (muons in the low p_{\rm T}^{W} bin), the resulting uncertainty on f_{\mathrm{0}} is 16%." | none |
| 1203.2165 | Sec. 8.5 lepton scale: about 3-5% on f0, about 2% on f_L-f_R | CONFIRMED | Sec. 8.5 (L951): "The resulting uncertainties are about 3% to 5% on f_{\mathrm{0}} and around 2% on f_{\mathrm{L}}-f_{\mathrm{R}} ." | none |
| 1203.2165 | Sec. 8.6 template systematic = half the difference, minimum 2% | CONFIRMED | Sec. 8.6 (L998): "the systematic uncertainty associated with the choice of templates was taken as half the difference between the two numbers, with a minimum value of 2%." | none |
| 1203.2165 | Sec. 8.6 generator-level "true" cos theta_3D correction | CONFIRMED | Sec. 8.6 (L961), quote matches | none |
| 1203.2165 | Sec. 8.6 Sherpa cross-check "very good agreement" (electron only) | CONFIRMED | Sec. 8.6 (after Table 8): "In the case of sherpa, only the uncertainty associated with the choice of template is reported. A very good agreement is observed." | none |
| 1203.2165 | Sec. 9: "For p_T^W > 50 GeV, the data are close to the mc@nlo values, while powheg predicts a somewhat smaller difference" | CONFIRMED | Sec. 9 (L1033), verbatim | none |
| 1203.2165 | Charge-averaging rationale (cited Sec. 9) | CONFIRMED | Sec. 9 (L1093-L1094): "In order to reduce the statistical uncertainties, which are also large, and the uncorrelated instrumental and analysis systematic uncertainties, the measurements in each p_{\mathrm{T}}^{W} bin were averaged over charges and lepton flavours." | none |
| 1203.2165 | Sec. 10 "The longitudinal fraction is the most difficult to extract ..." | CONFIRMED | Sec. 10 (L1113-L1118), verbatim | none |
| 1203.2165 | Interpretation "in the high pT bin, the data favour f0 values smaller than the predictions of mc@nlo and powheg, which are close to each other", cited "(Sec. 10)" | WRONG_LOCATION | Verbatim sentence is in Sec. 9 (paper.txt L1102), before the "10 Summary" heading (L1106). Sec. 10 (L1116-L1118) has the paraphrase "in the high p_T^W bin, they favour lower values than predicted by either of the simulations". Value and content are correct. | Cite Sec. 9 for the verbatim sentence, or quote the Sec. 10 paraphrase. |
| 1203.2165 | "Due to the large uncertainties on the measurements, however, no stringent constraints nor clear inconsistencies can be deduced", cited "(Sec. 10)" | WRONG_LOCATION | Sec. 9 (paper.txt L1103). Sec. 10 begins at L1106. | Cite Sec. 9. |
| 1203.2165 | Sherpa cross-check, Table 9 values | CONFIRMED (claim only says "Table 9 values not extracted") | Table 9 (L~1005-L1020): Data (sherpa) f_L-f_R 25.5 +/-2.2 (35-50), 26.6 +/-2 (>50); f0 21.0 +/-9.1, 15.6 +/-6.1. See omissions. | see omissions |
| 1606.00689 | A0, three pT bins (5.0-8.0, 22.0-25.5, 132-173 GeV) with stat / sys / reg_bias | CONFIRMED | HEPData Table_12/T12 values 0.0148195, 0.158708, 0.856275 with the listed errors; Table 9 (paper.txt L2477-L2479): "0.015 ± 0.002 ± 0.007", "0.159 ± 0.003 ± 0.007", "0.856 ± 0.008 ± 0.008". Column assignment: HEPData "value" = measured central value; the table has no expected-value column. | none |
| 1606.00689 | A1, three pT bins | CONFIRMED | T13: 0.0130937, 0.0423734, 0.0654514; Table 9: "0.013 ± 0.002 ± 0.002", "0.042 ± 0.002 ± 0.002", "0.065 ± 0.008 ± 0.005" | none |
| 1606.00689 | A2, three pT bins | CONFIRMED | T14: -0.00304493, 0.0998477, 0.708345; Table 9: "-0.003 ± 0.003 ± 0.003", "0.100 ± 0.003 ± 0.003", "0.708 ± 0.022 ± 0.020" | none |
| 1606.00689 | A3, three pT bins | CONFIRMED | T15: 0.000876837, 0.00574819, 0.0544258; Table 9: "0.001", "0.006", "0.054" | none |
| 1606.00689 | A4, three pT bins | CONFIRMED | T16: 0.0819608, 0.0654512, 0.0271226; Table 9: "0.082", "0.065", "0.027" | none |
| 1606.00689 | A5, three pT bins | CONFIRMED (to HEPData) with discrepancy note | T17 5.0-8.0 = -0.00287439 (rounds to -0.003). Paper Table 9 (L2485) prints "–0.002 ± 0.001 ± 0.001" for 5.0-8.0. Other two bins agree (0.003, 0.011). The claim cites HEPData only, so no row error; the paper's printed value differs. | Note in claim: paper Table 9 prints -0.002 for A5 at 5-8 GeV, HEPData gives -0.00287. |
| 1606.00689 | A6, three pT bins | CONFIRMED | T18: -0.00140185, 7.63375e-05, 0.00338895; Table 9: "-0.001", "0.000", "0.003" | none |
| 1606.00689 | A7, three pT bins | CONFIRMED | T19: -0.000414005, 0.000608314, 0.00389319; Table 9: "0.000", "0.001", "0.004" (sign of the 5-8 GeV value is lost in the printed 0.000) | none |
| 1606.00689 | A0-A2, 5.0-8.0 GeV, value 0.015138 | MISMATCH | Paper Table 9 (paper.txt L2477): "5.0–8.0 0.015 ± 0.002 ± 0.007 –0.003 ± 0.003 ± 0.003 0.018 ± 0.003 ± 0.007"; Table 11 (L5202) gives the same 0.018 ± 0.003 ± 0.007. HEPData T11 gives 0.015138. The paper's A0 - A2 is consistent with its own A0 and A2 (0.0148 + 0.0030 = 0.0178). | Use the paper value 0.018 +/-0.003 +/-0.007 (Table 9/11) and flag the HEPData T11 discrepancy. |
| 1606.00689 | A0-A2, 22.0-25.5 GeV, value 0.0590683 | CONFIRMED | T11 0.0590683 with stat 0.00455052, sys 0.00641167; Table 9 "0.059 ± 0.005 ± 0.006" | none |
| 1606.00689 | A0-A2, 132-173 GeV, value 0.147444 | MISMATCH (rounding level) | HEPData T11 = 0.147444 (prints 0.147). Paper Table 9 (paper.txt L2479) prints "0.148 ± 0.019 ± 0.011", and Table 11 agrees; A0 - A2 from the paper's own A0 and A2 is 0.14793. | Use 0.148 +/-0.019 +/-0.011 from paper, or state the HEPData value 0.147444 with the paper value. |
| 1606.00689 | "A5,6,7 jointly non-zero: observed 3.0 sigma, expected 3.2 sigma", cited "Sec. 7.2" | WRONG_LOCATION | Quote is verbatim: "This test gives an observed (expected) significance of 3.0 (3.2) standard deviations." It is in Sec. 8 "Comparisons with theory" (heading L2509; quote L2578), not Sec. 7.2 (7.2 spans L1881-L2224). | Cite Sec. 8. |
| 1606.00689 | Regularisation: "the Ai coefficients are regularised by imposing a Gaussian penalty term on the significance of their higher-order derivatives with respect to pZT" (App. C) | MISMATCH | Not a verbatim quote. Paper.txt L1367-L1368 (Sec. 5.2, Likelihood): "the Ai spectra are regularised by multiplying the unregularised likelihood by a Gaussian penalty term, which is a function of the significance of higher-order derivatives of the Ai with respect to pZT". Details are in App. C (L1373). | Replace with the verbatim sentence and cite Sec. 5.2 (App. C for details). |
| 1606.00689 | "lepton ... defined at the Born level, i.e. before final-state QED radiation" (Sec. 2) | MISLABELED | Quote drops its qualifier. Paper text (Sec. 2): "Throughout this paper, the leptons from Z-boson decays are defined at the Born level, i.e. before final-state QED radiation, when discussing theoretical calculations or predictions at the event-generator level." The fit itself is at detector level (Sec. 5). | Add the qualifier "when discussing theoretical calculations or predictions at the event-generator level". |
| 1606.00689 | Lam-Tung quote "The data confirm that the Lam–Tung relation (A0 − A2 = 0) does not hold at O(α2s)" (Sec. 8) | CONFIRMED | paper.txt L2562-L2563 (Sec. 8) | none |
| 1606.00689 | Sec. 6.5 regularisation bias "approaching the statistical uncertainty of A0 and A2"; Sec. 6.6 dominance statements | CONFIRMED | L1586-L1589 (6.5); L1596-L1601 (6.6), verbatim | none |
| 1606.00689 | Sec. 9 uncertainties "range from 0.002 at low pZT to 0.008 at pZT = 150 GeV"; PDF "below 0.004 in all cases" | CONFIRMED | paper.txt L3451-L3454 (Sec. 9, heading L3436) | none |
| 1606.00689 | Sec. 7.3 higher-order Pi "beyond the sensitivity"; A1 absent in third yZ bin (Table 15 caption) | CONFIRMED | L2504-L2506 (Sec. 7.3, heading L2224-L2509); Table 15 caption L5326 "The A1 measurements are missing from the third yZ bin" | none |
| 1606.00689 | Eq. 1 structure and normalisation (3/16pi) and CS frame, z-axis bisector, y normal, angles w.r.t. negative lepton, A1 and A3 positive | CONFIRMED | Eq. (1) L62-L68; CS definition L183-L193 | none |
| 1606.00689 | Appendix A map: H_mm', Eq. 12-13; sigma_alpha in terms of H (Eq. 15) | CONFIRMED | Eq. (15) paper.txt L3533-L3535: "σU+L ∝ H00 + H++ + H−− / σL ∝ H00 / σT ∝ 1/2(H+− + H−+)" | none |
| 1606.00689 | HEPData table map: T1-9 unregularised, T11-19 regularised, T21-40 and T41-60 for the two low y bins, T61-76 for 2-3.5 with A0, A2, A3, A4, A5, A7 only | CONFIRMED | HEPData descriptions and qualifiers of T1-T76; 76 tables present in cache hepdata/ | none |
| 1606.00689 | Unregularised A0 at 132-173 = 0.882853 (HEPData T2) | CONFIRMED | T2 value 0.882853 | none |
| 1606.00689 | Open issue 1: A0-A2 at 0.0-2.5 GeV, HEPData -0.0422871 vs paper -0.039 +/-0.010 +/-0.008 | CONFIRMED (discrepancy is real) | T11 0.0-2.5 = -0.0422871; paper Table 11 (L5199-L5200) "–0.039 ± 0.010 ± 0.008". Paper A0 for that bin is -0.014 (T12 gives -0.0145192, which prints -0.015) | Report as a HEPData-paper discrepancy, see row above |
| 1606.00689 | Open issue 2: whether paper "syst" includes sys,reg_bias, "not stated" | CONFIRMED (not stated) with an evidence note | Text does not state it. Rounding evidence says it is included: A1 at 132-173: sys,sys 0.00366 alone prints as 0.004, but paper prints +/-0.005; quadrature with reg_bias 0.00315 gives 0.00483 -> 0.005. A2 at 132-173: sys,sys 0.0107 alone prints 0.011; paper prints 0.020; quadrature with reg_bias 0.0172 gives 0.0203 -> 0.020. | Replace "not stated" with the inferred statement, labelled as an inference. |
| 1606.00689 | Open issue 3: Eq. 16 prefactors "not verified" | CONFIRMED (claim is out of date) | Eq. (16) is legible in paper.txt L3567-L3580: A0 = 2 dσL/dσU+L; A1 = 2√2 dσI/dσU+L; A2 = 4 dσT/dσU+L; A3 = 4√2 dσA/dσU+L; A4 = 2 dσP/dσU+L; A5 = 2 dσ7/dσU+L; A6 = 2√2 dσ8/dσU+L; A7 = 4√2 dσ9/dσU+L | Replace open issue 3 with these prefactors |
| 2610.38688 | Table 1, e+e- W+W-, sqrt(s)=162: rho-- 0.377, rho00 0.329, rho++ 0.294 | CONFIRMED | Table 1 (paper.txt L444-L447) | none |
| 2610.38688 | Table 1, 189 GeV: 0.574 / 0.251 / 0.175 ; 206 GeV: 0.644 / 0.212 / 0.144 ; 240 GeV: 0.739 / 0.155 / 0.106 ; 365 GeV: 0.881 / 0.0644 / 0.0543 ; 500 GeV: 0.926 / 0.0359 / 0.0380 | CONFIRMED | Table 1 (L448-L466), same column order (rho--, rho00, rho++) | none |
| 2610.38688 | Sec. IV.3 quotes: rho00 = 0.329 at 162 GeV; rho00 = 0.0359 and rho-- = 0.926 at 500 GeV | CONFIRMED | L439: "At \sqrt{s}=162 GeV, close to threshold, \rho_{00}\simeq 0.329 . It decreases to 0.0359 at 500 GeV, where the W^{-} is predominantly h=-1 polarized, with \rho_{--}\simeq 0.926" | none |
| 2610.38688 | rho00/(1-rho00) "approx 14%" at gamma approx 1.7 and "2-3%" at gamma approx 7 (Z, NNLO) | CONFIRMED | Sec. IV.2 (L419): "decreasing from {\approx}14\% at \gamma\approx 1.7 to 2 – 3\% at \gamma\approx 7 for the Z" | none |
| 2610.38688 | "suppressed by up to ~10%" (Sec. IV.2, Fig. 5) | CONFIRMED | L425: "suppresses the spectrum by up to {\sim}10\%" | none |
| 2610.38688 | Scale uncertainty = 7-point envelope | CONFIRMED | L413: "The scale uncertainty is the envelope of the seven-point variation" (as quoted in claim) | none |
| 2610.38688 | Eq. (39): rho_lambda lambda(gamma) = dsigma_lambda/dsigma; sum = 1 | CONFIRMED | Sec. IV.1 (L386-L400) | none |
| 2610.38688 | Helicity density matrix quantized along boson direction (Sec. II) | CONFIRMED | L113: "The EEC distribution between the helicity states \lambda,\lambda^{\prime}=\pm 1,0 , quantized along the boson direction" | none |
| 2610.38688 | Eqs. (9)-(11): W^(0,0), W^(2,0), W^(2,2) map onto diagonal rho entries | CONFIRMED | L314: "By Eq. (9), each diagonal entry \mathcal{W}_{\lambda\lambda} is a sum of \mathcal{W}^{(0,0)}, \mathcal{W}^{(2,0)}, and \mathcal{W}^{(2,2)}"; bisector-frame Eq. (11) at L164 | none |
| 2610.38688 | App. D Eq. (82) quote on rho00, rho+-, rho+0 - rho0- | CONFIRMED | L821 verbatim; parity-even/odd split L823 "in the same parity-even and parity-odd split as the angular coefficients of the leptonic decay [89, 73]" | none |
| 2610.38688 | pp setup: NNLO, NNPDF3.1 NLO, sqrt(s)=13.6 TeV, alpha_s(mZ)=0.118 | CONFIRMED | L411 | none |
| 2610.38688 | Polarimeter windows: Z 66<m<116, W 60<m<100 GeV; no individual lepton cuts | CONFIRMED | L409 | none |
| 2610.38688 | e+e- setup: unpolarized beams, no ISR, no angular cuts | CONFIRMED | App. C (L723): "We assume unpolarized beams, massless electrons, on-shell W bosons, zero widths, no initial-state radiation, and no angular cuts." | none |
| 2610.38688 | pT bins 100-800 GeV, |y|<0.5; gamma ranges 1.48-8.83 (Z), 1.60-10.0 (W) | CONFIRMED | L414 | none |
| 2610.38688 | Authors, affiliations, preprint numbers | CONFIRMED | Author block in arxiv.html (Gao, Lee, Zhang with affiliations); arXiv 2610.38688v1, SLAC-PUB-261006, MIT-CTP 6127 | none |
| 2610.38688 | No map from rho to lepton-decay A0-A7 in the paper | CONFIRMED | No A_i notation in paper.txt; only the qualitative "same split" remark at L823 and A_e (electron asymmetry) at L825 | none |
| 2610.38688 | Q2: no measurement of f_L, f0, A0, rho00; all values are predictions | CONFIRMED | Paper is theory-only (no data, no uncertainties; Sec. IV, App. B-D) | Note that Q2 asks for measurements, so these rows are out of Q2 scope and should be labelled as such |

## Counts

Rows: 85 (1104.3829: 17; 1203.2165: 29; 1606.00689: 23; 2610.38688: 16).

- CONFIRMED: 75
- MISMATCH: 3 (1606 A0-A2 5-8 GeV; 1606 A0-A2 132-173 GeV, rounding level; 1606 Gaussian-penalty quote)
- WRONG_LOCATION: 6 (1203 trigger Sec. 3.2 -> 3.4; 1203 acceptance Sec. 8.6 -> Sec. 10; 1203 cos theta_2D Sec. 2.2 -> 2.3; 1203 two Sec. 10 citations -> Sec. 9; 1606 significance Sec. 7.2 -> Sec. 8)
- MISLABELED: 1 (1606 Born-level quote drops its qualifier)
- UNSUPPORTED: 0
- UNVERIFIABLE: 0

Non-CONFIRMED rows are listed in the table above with their evidence.

## Omissions (in scope, clearly more relevant than what was extracted)

- 1203.2165, Table 9 (Sec. 8.6, paper.txt L1016-L1023): sherpa-template data values, electron channel only: f_L-f_R = 25.5 +/-2.2 (35-50 GeV), 26.6 +/-2 (>50 GeV); f0 = 21.0 +/-9.1 (35-50), 15.6 +/-6.1 (>50). An alternative measurement of the same quantities; it has only template-choice uncertainties. Moderate relevance.
- 1606.00689, rapidity-binned A0-A7 (HEPData Tables 21-76; paper Tables 15-20 and Sec. 8 Figs. 16-18): not extracted. These give the pT dependence in 0-1, 1-2 and 2-3.5 |yZ| bins, which is what Q3 asks for beyond the yZ-integrated values. Sec. 8 (L2582-L2589) says A1, A3, A4 agree with predictions in all three bins.
- 1606.00689, Sec. 8 (L2562-L2566): the paper states that for pZT > 50 GeV the A0 - A2 deviations from zero are "almost a factor of two larger than those predicted by the calculations". This is a result in the scope of Q3 and is not in the claim file.
- 2610.38688: no omissions in scope. All content is theory and is labelled as such.
- 1104.3829: none in scope beyond the f_L/f_R note already in the file.

## Other notes

- The 1606 claim's open issue 2 (whether syst includes reg_bias) can be resolved by the rounding evidence in the table above. This is an inference, not a stated result.
- The 1606 claim's open issue 3 (Eq. 16) can be closed: the prefactors are legible in paper.txt L3567-L3580.
