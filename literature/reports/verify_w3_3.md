# verify_w3_3: adversarial check of five claim notes

Sources: `.cache/<id>/` (arXiv HTML/text, HEPData JSON in `hepdata/tables/`, `record.json`, `inspire.json`). No network access was used. No "Verifier-noted omissions" heading exists in any claim file; the omissions below are the verifier's own.

Verdict counts (111 rows checked): CONFIRMED 107; MISMATCH 1; WRONG_LOCATION 2; MISLABELED 1; UNSUPPORTED 0; UNVERIFIABLE 0.

## Rows

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| 2607.20246 | A1 f_X0 0.324 ±0.088 (HEPData stat +0.091/−0.084, syst +0.017/−0.018, lumi +0.0015/−0.0014) | CONFIRMED | HEPData Table 5 row f_X0, column Data = 0.324; paper Table 5 "$0.324\pm 0.088$ $(\pm 0.086,\;\pm 0.017,\;\pm 0.001)$" (fulltext.txt ~L1316) | none |
| 2607.20246 | A2 f_0X 0.007 ±0.151 | CONFIRMED | paper Table 5 "$0.007\pm 0.151$ $(\pm 0.150,\;\pm 0.018,\;\pm 0.001)$" (~L1310); HEPData stat +0.093/−0.000 | none |
| 2607.20246 | A3 f_00 0.000 ±0.134 | CONFIRMED | paper Table 5 (~L1304); HEPData stat +0.053/−0.000 | none |
| 2607.20246 | A4 f_X0 significance 4.0σ obs, 2.9σ exp | CONFIRMED | "observed with a significance of $4.0\,\sigma$ , compared with $2.9\,\sigma$ expected" (~L1260) | none |
| 2607.20246 | A5 expected 1.3σ (f_00), 2.6σ (f_0X) | CONFIRMED | "expected significances ... $1.3\sigma$ and $2.6\sigma$" (~L1261) | none |
| 2607.20246 | A6 f_00 UL 0.12 obs (0.21 exp), 95% CL | CONFIRMED | "upper limits on $f_{00}$ and $f_{0X}$ are 0.12 (0.21) and 0.19 (0.46)" (~L1262) | none (CL method not stated in source; claim already says so) |
| 2607.20246 | A7 f_0X UL 0.19 obs (0.46 exp) | CONFIRMED | same sentence (~L1262); Conclusion ~L1354 | none |
| 2607.20246 | A8 P = 0.60% (2.5σ) for f_0X < 0.007 | CONFIRMED | "is $0.60\%$ , corresponding to $2.5\,\sigma$" (~L1269) | none |
| 2607.20246 | A9 MoCaNLO f_X0 = 0.2745 ±0.0008; QCD-scale-only uncertainty | CONFIRMED | paper Table 5 "$0.2745\pm 0.0008$"; Table 5 caption "uncertainties in the NLO EW fixed-order prediction include QCD scale uncertainties" (~L1283-1290) | none |
| 2607.20246 | A10 f_X0 MadGraph 0.2758 ±0.0003, Sherpa 3.0 0.274 ±0.001 | CONFIRMED | paper Table 5 row f_X0 (~L1316-1320); HEPData Table 5 row f_X0, columns MadGraph and Sherpa 3.0 | none |
| 2607.20246 | A11 f_00 predictions 0.0902/0.087/0.0902 | CONFIRMED | paper Table 5 f_00 row (~L1304-1307); HEPData Table 5 | none |
| 2607.20246 | A12 f_0X predictions 0.2808/0.2793/0.2758 | CONFIRMED | paper Table 5 f_0X row (~L1311); HEPData Table 5 | none |
| 2607.20246 | A13 Table 3 f_X0 entries: stat 26.6, jets 3.6, MC stat 2.4, WZjj-EW theory 1.7, QCD theory 1.6, electrons 1.3, all 5.3 (paper) / 5.2 (HEPData) | CONFIRMED | paper Table 3 (~L936-1002: "All systematics | 5.3 | 10.2", "Statistics | 26.6"); HEPData Table 3 "All systematics" 5.2, "Statistics" 26.6 | none (5.3 vs 5.2 disagreement correctly flagged in claim) |
| 2607.20246 | A14 Table 3 remaining f_X0 entries (lumi 0.4, pile-up 0.5, muons 0.8, other bkg 0.8, misid 0.6, b-tag 0.5, PDFs 0.3, MET 0.3) | CONFIRMED | paper Table 3 (~L936-1002); HEPData Table 3 | none |
| 2607.20246 | A15 quote "The uncertainty related to data statistics is dominant ... determines its precision" | CONFIRMED | fulltext.txt ~L1267 | none |
| 2607.20246 | A16 quote "dominant source ... jet energy calibration and the modelling of pile-up" (Sec. 8) | CONFIRMED | fulltext.txt ~L915 (Sec. 8 spans ~L889-1017) | none |
| 2607.20246 | A17 template shape "by at most 20%" and NLO EW shape "maximum size of 20%" (Sec. 8) | CONFIRMED | fulltext.txt ~L903, ~L910 | none |
| 2607.20246 | A18 interference among polarisation states ~2% (NLO EW), "effectively absorbed" (Sec. 3) | CONFIRMED | fulltext.txt ~L169-170 ("amounting to $2$ % according to NLO EW calculations [4]"; "effectively absorbed in the measured polarisation fractions") | none (paper also gives 1.5% for the non-resonant contribution at ~L167; not claimed, not an error) |
| 2607.20246 | A19 frame quote "fix the reference z-axis to the direction of the corresponding boson in the diboson centre-of-mass frame [19]"; ref [19] = Denner & Pelliccioli | CONFIRMED | fulltext.txt ~L131; reference list [19] "Ansgar Denner and Giovanni Pelliccioli" (~L1534) | none |
| 2607.20246 | A20 "f_00, f_0T, f_T0, f_TT ... composed of diagonal elements of the full spin density matrix" | CONFIRMED | fulltext.txt ~L125 | none (Q3 scope call is for the lead; see notes) |
| 2607.20246 | A21 non-measured proportions fixed to MC; floating-proportion fits "yield consistent results" | CONFIRMED | fulltext.txt ~L877-878 | none |
| 2607.20246 | A22 WZjj-EW ~13% and WZjj-QCD 67% of signal region (Sec. 6) | CONFIRMED | fulltext.txt ~L334 (Sec. 6 spans ~L310-553); "expected contribution of WZjj-EW ... about 13% ... 67% ... WZjj-QCD" | none |
| 2607.20246 | A23 mu_WZjj-EW 1.06 (stat 0.15, syst 0.11, lumi 0.01) | CONFIRMED | HEPData Table 5 row mu, Data = 1.06 with stat 0.15 / syst 0.11 / lumi 0.01; paper Table 5 "$1.06\pm 0.18$ $(\pm 0.15,\;\pm 0.11,\;\pm 0.01)$" | none |
| 2607.20246 | A24 Open issue 1: HEPData vs paper Table 5 uncertainties disagree (f_00, f_0X, f_X0) | CONFIRMED | HEPData asymerrors differ from paper parentheticals as the claim states (A1-A3 above) | none (correctly left open) |
| 2607.20246 | A25 bibliographic: arXiv 22 Jul 2026, CERN-EP-2026-213, STDM-2024-03, HEPData ins3182511 | CONFIRMED | fulltext.txt L35, L39-40; hepdata/record.json (ins3182511) | none |
| 2607.12879 | B1 f_LL 0.080 ±0.017 | CONFIRMED | paper.txt ~L281 "f_LL = 0.080 ± 0.017"; Table 4 ~L463 | none |
| 2607.12879 | B2 f_LL SM 0.061 ±0.002 | CONFIRMED | paper.txt ~L281; Table 4 third column ~L465 | none |
| 2607.12879 | B3 Table 4 second-column values 0.080±0.018 (inclusive), 0.110±0.030 (low m4l), 0.009±0.021 (high m4l) described as "column-ambiguous" | MISLABELED | paper.html Table 4 structure: header "Observed" with colspan 2 over "Scaled normalization for the interference term" | "Fixed normalization for the interference term" and a single "Expected" column; the second-column values are OBSERVED with FIXED interference normalization, and the third column (0.061±0.002, 0.094±0.002, 0.030±0.001) is the SM EXPECTED value. Relabel the rows in the claim note; remove the "column-ambiguous" caveat. |
| 2607.12879 | B4 f_LL low-m4l 0.108 ±0.028 | CONFIRMED | paper.txt ~L284 "$f_{LL}^{low-m_{4\ell}} = 0.108 \pm 0.028$" | none |
| 2607.12879 | B5 f_LL low SM 0.094 ±0.002 | CONFIRMED | paper.txt ~L285 "consistent with the SM predictions of 0.094 ± 0.002 and 0.030 ± 0.001, respectively" | none |
| 2607.12879 | B6 f_LL high-m4l 0.011 ±0.017 | CONFIRMED | paper.txt ~L284; "downward fluctuation of the data in the two most sensitive BDT bins" ~L287 | none |
| 2607.12879 | B7 f_LL high SM 0.030 ±0.001 | CONFIRMED | paper.txt ~L285 | none |
| 2607.12879 | B8 mu_LL Run 3 = 1.34 ±0.26 (stat) ±0.13 (syst) = ±0.29; obs 5.1σ, exp 4.1σ; SM 1.00 ±0.27 | CONFIRMED | paper.txt ~L190-192; Table 3 "Scaled normalization | Run 3 | 1.34±0.29 | 1.00±0.27 | 5.1 | 4.1" | none |
| 2607.12879 | B9 mu_LL Run 2 = 1.09 ±0.29; obs 4.3σ, exp 4.2σ | CONFIRMED | paper.txt ~L308-309; Table 3 Run 2 row | none |
| 2607.12879 | B10 mu_LL combined 1.22 ±0.21; obs 6.5σ, exp 5.6σ; SM 1.00 ±0.20 | CONFIRMED | paper.txt ~L316-317; Table 3 "Scaled | Combined | 1.22±0.21 | 1.00±0.20 | 6.5 | 5.6" | none |
| 2607.12879 | B11 mu_LL fixed-normalization combined 1.21 ±0.23; 5.5σ / 4.8σ; SM 1.00 ±0.22 | CONFIRMED | Table 3 "Fixed normalization ... Combined | 1.21±0.23 | 1.00±0.22 | 5.5 | 4.8" (paper.txt ~L453-456; HTML confirmed) | none |
| 2607.12879 | B12 mu_TX 1.00 ±0.10 | CONFIRMED | paper.txt ~L193 | none |
| 2607.12879 | B13 sigma(Z_L Z_L) obs 2.30 ±0.45 (stat) ±0.19 (syst) = ±0.49 fb; SM 1.71 ±0.11 fb | CONFIRMED | paper.txt ~L297-298 | none |
| 2607.12879 | B14 Table 2 (combined mu_LL): total 17, data stat 15, syst 8.1, MC stat 1.6, Sherpa-3 shape 4.4, QCD gg 3.4, NLO EW 2.9, PDF+as 1.9, shower 1.6, electrons 3.7, lumi 1.3, others | CONFIRMED | paper.txt Table 2 (~L325-360), each value as listed | none |
| 2607.12879 | B15 "can reach up to 11%" | CONFIRMED | paper.txt ~L172 | none (antecedent is not explicit in the source; the claim already says so) |
| 2607.12879 | B16 "total uncertainties increased by 6 ∼ 8 %" in fixed-normalization treatment | CONFIRMED | paper.txt ~L416 (End Matter) quotes this sentence | none to the claim as worded. Note for the lead: Table 3 itself gives mu_LL uncertainty increases of ~7% (Run 3, 0.29→0.31), ~10% (Run 2, 0.29→0.32) and ~10% (combined, 0.21→0.23). The paper's "6–8%" does not match its own Table 3 for mu_LL; if quoted, attribute it to the text. |
| 2607.12879 | B17 caveat quote "The normalization of the interference term is updated to be scaled with √(μLL μTX)" located at "Res-text, combination paragraph" | WRONG_LOCATION | paper.txt L303-306: the sentence follows "Some aspects of the Run 2 analysis are revised to ensure consistency with the Run 3 methodology" and precedes the Run 2 mu_LL = 1.09 result, so it is in the Run 2 re-analysis paragraph, not the combination paragraph | Change location to "Res-text, Run 2 re-analysis paragraph". |
| 2607.12879 | B18 gg→ZZ treated as background ("to be more conservative"); Run 2 reweighting showed "significant discrepancies" with fixed-order | CONFIRMED | paper.txt ~L107-110 | none |
| 2607.12879 | B19 quotes "The measurement is limited by statistical uncertainty of the data and the leading systematic uncertainty is from the theoretical modeling of the polarization templates" and "The statistical uncertainty of the data is the dominant source..." | CONFIRMED | paper.txt L301 and the combination paragraph (~L318-320) | none |
| 2607.12879 | B20 frame quote "defined in the center-of-mass frame of the two Z Z bosons"; cos theta_1 definition | CONFIRMED | paper.txt L54 (frame); L152 (theta_1 definition) | none (helicity vs Collins-Soper not stated, as claimed) |
| 2607.12879 | B21 Eq. 3 unity f_LL + f_TX + κ√(f_LL f_TX) = 1; κ SM-predicted | CONFIRMED | paper.txt End Matter, Eq. (3) | none |
| 2607.12879 | B22 event selection: two SFOC pairs, \|m_ll − m_Z\| < 10 GeV, m_4l > 180 GeV, m_ll > 5 GeV, ΔR_ll > 0.05; leading lepton p_T > 27, subleading > 20; electrons \|η\|<2.47 (p_T>7 dressed), muons \|η\|<2.5 (p_T>5) | CONFIRMED | paper.txt ~L286-300 (fiducial and on-shell paragraphs) | none |
| 2607.12879 | B23 SR split: low-mass 180 < m_4l < 240 GeV, high-mass m_4l > 240 GeV | CONFIRMED | paper.txt ~L141 | none |
| 2607.12879 | B24 bibliographic: arXiv 14 Jul 2026, CERN-EP-2026-191, STDM-2024-01, PRL field | CONFIRMED | paper.txt L22, L25-27 | none |
| 2607.12879 | B25 NLO EW prescription (additive vs multiplicative MoCaNLO); scale variation by factor 2 excluding factor-4; Pythia 8 vs Herwig 7 | CONFIRMED | paper.txt ~L165-170 | none |
| 2607.12879 | B26 HEPData: no record (NONE marker) | CONFIRMED | cache hepdata/NONE present; no table files | none |
| 2503.11317 | C1 expected SM share of W_L W_L jj ~10% and W_L W_T jj ~30% of EW W±W±jj (predicted) | CONFIRMED | text.txt Introduction ~L38 "are about 10% and 30% of the overall expected EW W± W± jj production cross section" (the source also says "defined using the W± W± center-of-mass reference frame"; the claim omits that qualifier) | optionally add "in the W±W± CM frame" |
| 2503.11317 | C2 measured sigma·B(W_L± W± jj) 0.88 ±0.30 fb (stat 0.28, mod 0.05, exp 0.08); 3.3σ observed | CONFIRMED | text.txt Table 1 row "W_L± W± jj" (~L76-78); Conclusion "significance ... is 3.3 standard deviations with a measured fiducial cross section of 0.88 ± 0.30 fb" | none |
| 2503.11317 | C3 predicted sigma·B(W_L± W± jj) 1.18 ±0.29 fb | CONFIRMED | text.txt Table 1 (~L76) | none |
| 2503.11317 | C4 observed (expected) 95% CL UL on sigma·B(W_L W_L jj) = 0.45 (0.70) fb | CONFIRMED | text.txt ~L60 and Conclusion ("An observed (expected) 95% CL upper limit of 0.45 (0.70) fb") | none (omission: see below) |
| 2503.11317 | C5 Table 1 W_L W_L jj: measured 0.01 ±0.21 (tot.) = ±0.20 stat, ±0.02 mod, ±0.05 exp; predicted 0.29 ±0.07 | CONFIRMED | text.txt ~L68-70 | none |
| 2503.11317 | C6 Table 4 breakdown (data stat 32.2, bkg stat 7.2, non-prompt 4.2, JES/MET 3.9, norm 2.5, EW+QCD model 4.7, exp+model 11.1, total 34.1) | CONFIRMED | text.txt Table 4 (~L255-282) | none (claim omits lepton calibration 0.2, pileup 1.2 etc.; not an error) |
| 2503.11317 | C7 quotes "none of the considered systematic uncertainties have a significant impact..." and "largest impact ... data-driven ... theory ... jet and E_T^miss" | CONFIRMED | text.txt ~L54 (both sentences present) | none |
| 2503.11317 | C8 polarization vectors in W±W± CM frame; appendix uses initial-state parton-parton CM frame | CONFIRMED | Fig. 2/3, Table 1 captions (~L38, ~L55-62); Appendix Table 5 caption "defined in the initial-state parton–parton reference frame" (~L283) | none |
| 2503.11317 | C9 fiducial/selection: lepton p_T>27 GeV, \|η\|<2.5 (µ), \|η\|<2.47 excl. 1.37–1.52 (e); jets \|η\|<4.5, p_T>65/35, m_jj>500, \|Δy_jj\|>2; m_ll>20, E_T^miss>30 | CONFIRMED | text.txt ~L44-48, ~L59 | none |
| 2503.11317 | C10 no polarization fraction (f_L, f_0, A_0, ρ_00) measured | CONFIRMED | absence checked in text.txt: all polarization observables are sigma·B or limits | none |
| 2503.11317 | C11 bibliographic: PRL 135 (2025) 111802, DOI 10.1103/bpln-ccql, CERN-EP-2025-048, STDM-2019-29, 16 Sep 2025, 140 fb^-1 | CONFIRMED | arxiv.html (Phys. Rev. Lett. 135 (2025) 111802; bpln-ccql; CERN-EP-2025-048; STDM-2019-29; 16 Sep 2025); text.txt Conclusion (140 fb^-1) | none |
| 2310.04350 | D1 mu_LL = 1.15 ±0.27 (stat) ±0.11 (syst) = ±0.29 (observed, inclusive, fiducial) | CONFIRMED | fulltext.txt ~L296 (Sec. 8.1) | none |
| 2310.04350 | D2 mu_LL SM expectation 1.00 ±0.27 | CONFIRMED | fulltext.txt ~L300 | none |
| 2310.04350 | D3 significance 4.3σ observed | CONFIRMED | fulltext.txt ~L298; abstract ~L51 | none |
| 2310.04350 | D4 expected significance 3.8σ | CONFIRMED | fulltext.txt ~L300 ("with an expected significance of 3.8σ") | none |
| 2310.04350 | D5 sigma_fid(Z_L Z_L) obs 2.45 ±0.56 (stat) ±0.21 (syst) = ±0.60 fb | CONFIRMED | fulltext.txt ~L373; abstract ~L52 | none |
| 2310.04350 | D6 sigma_fid SM 2.10 ±0.09 fb | CONFIRMED | fulltext.txt ~L374, ~L471-472 | none |
| 2310.04350 | D7 Table 2 (sigma_fid relative %): total 24, data stat 23, syst 8.8, MC stat 1.7, qq→ZZ interference 6.9, observable choice 3.7, PDF/αs/PS 2.2, non-closure 1.0, QCD scale 0.2, NLO EW 0.2, gg 1.4, lumi 0.8, muons 0.6, electrons 0.4, non-prompt 0.3, pile-up 0.3, triboson 0.1 | CONFIRMED | fulltext.txt Table 2 (~L380-420), every value read | none |
| 2310.04350 | D8 "the fraction of Z_L Z_L events" obtained via the fit | CONFIRMED | fulltext.txt ~L237 ("To extract the fraction of ZLZL events, a profile binned maximum-likelihood fit") | none |
| 2310.04350 | D9 luminosity 140 fb^-1 (text) vs 139 fb^-1 (HEPData qualifier) | CONFIRMED | text 140 fb^-1: fulltext.txt L49, L133; HEPData Table_1.json qualifier LUMINOSITY "139 fb$^{-1}$" | none (inconsistency correctly left open) |
| 2310.04350 | D10 Q3 HEPData Table 1: all 30 bins (observed, stat, syst, Sherpa, Powheg) | CONFIRMED | Programmatic comparison of every claim row with hepdata/tables/Table_1.json: 30/30 rows identical in bin edges and all values | none |
| 2310.04350 | D11 column assignment: observed = data; Sherpa and Powheg = predictions | CONFIRMED | Fig. 8 caption (fulltext.txt ~L424): "uncertainty bands represent ... systematic uncertainties in the measured unfolded cross-section and predicted particle-level cross-sections ... Sherpa or Powheg"; Sec. 8.2 (~L427) "measured cross-section from the data agrees ... with both sets of predicted cross-sections"; HEPData headers | none |
| 2310.04350 | D12 "The ZZ-boson polarisation is defined in the centre-of-mass (CM) frame of the two ZZ bosons" (Sec. 3) | CONFIRMED | fulltext.txt ~L147 | none |
| 2310.04350 | D13 dressed leptons: e p_T>7, \|η\|<2.47; μ p_T>5, \|η\|<2.7; dressing ΔR<0.1 | CONFIRMED | arxiv.html text (alttext): "pT>7 (5) and |η|<2.47 (2.7)"; "ΔR<0.1" | none |
| 2310.04350 | D14 reco jets anti-kt R=0.4, p_T>15 GeV | CONFIRMED | fulltext.txt ~L170-182 ("Candidate jets are required to satisfy pT>15") | none |
| 2310.04350 | D15 Z1 = pair with larger \|y_ll\| | CONFIRMED | fulltext.txt Sec. 4.3 ~L176-180 ("The SFOC lepton pair with the largest value of |yℓℓ| is defined as the leading Z") | none |
| 2310.04350 | D16 "numeric on-shell window |m_ll − m_Z| < X is not recoverable from the cached source text (math stripped), so it is not recorded" | MISMATCH | The cached arXiv HTML carries the math as alttext: Sec. 4.1 "on-shell with |mℓℓ−mZ|<10 GeV" and Sec. 4.3 "the invariant masses of both SFOC lepton pairs are required to be |mℓℓ−mZ|<10 GeV and ... m4ℓ>180 GeV" (.cache/2310.04350/arxiv.html, text extracted from alttext). The window is recoverable. | Replace the sentence with: "|m_ll − m_Z| < 10 GeV for each SFOC pair (fiducial Sec. 4.1 and reco Sec. 4.3); m_4l > 180 GeV". |
| 2310.04350 | D17 OO: T_yz,1(3) = sin φ × cos θ | CONFIRMED | fulltext.txt ~L248 | none |
| 2310.04350 | D18 unfolding: iterative Bayesian, two iterations, intrinsic bias < 1% per bin | CONFIRMED | fulltext.txt ~L260-263 | none |
| 2310.04350 | D19 interference template fixed (Step 2); only mu_LL and mu_TX float | CONFIRMED | fulltext.txt ~L227 (Step 2), ~L239 (floating normalisations) | none |
| 2310.04350 | D20 aNTGC limits "(Table 3, Sec. 9)" | WRONG_LOCATION | Table 3 and the aNTGC limits sit in Sec. 8.3 "BSM interpretation" (fulltext.txt ~L424-447). Sec. 9 is "Conclusion" (TOC, fulltext.txt L37). | Change "Sec. 9" to "Sec. 8.3". |
| 2310.04350 | D21 Sec. 8.1 quotes: "increase of the yield uncertainty for ZLZL is mainly due to the statistical uncertainty of the signal strength"; "measurement is limited by data statistical uncertainty ... leading contribution from the theoretical modelling" | CONFIRMED | fulltext.txt ~L295 and ~L372-374 | none |
| 2310.04350 | D22 bibliographic: JHEP 12 (2023) 107, DOI 10.1007/JHEP12(2023)107, INSPIRE 2709671, HEPData 143611 v1 | CONFIRMED | arxiv.html / fulltext.txt L43-45 (JHEP 12 (2023) 107; DOI); hepdata/record.json recid 143611, version 1 | none |
| 2009.09429 | E1 sigma·B W_L W_L (WW-CM) 0.32 +0.42/−0.40 fb | CONFIRMED | HEPData Table 6 (value 0.32, plus 0.42, minus −0.4); Table 6 description "helicity eigenstates defined in the WW center-of-mass frame"; paper text ~L773 caption | none |
| 2009.09429 | E2 theory 0.44 ±0.05 (WW-CM, W_L W_L) | CONFIRMED | HEPData Table 6 | none |
| 2009.09429 | E3 sigma·B W_X W_T (WW-CM) 3.06 +0.51/−0.48 | CONFIRMED | HEPData Table 6 | none |
| 2009.09429 | E4 theory 3.13 ±0.35 | CONFIRMED | HEPData Table 6 | none |
| 2009.09429 | E5 sigma·B W_L W_X (WW-CM) 1.20 +0.56/−0.53 | CONFIRMED | HEPData Table 6 | none |
| 2009.09429 | E6 theory 1.63 ±0.18 | CONFIRMED | HEPData Table 6 | none |
| 2009.09429 | E7 sigma·B W_T W_T (WW-CM) 2.11 +0.49/−0.47 | CONFIRMED | HEPData Table 6 | none |
| 2009.09429 | E8 theory 1.94 ±0.21 | CONFIRMED | HEPData Table 6 | none |
| 2009.09429 | E9 parton-frame W_L W_L 0.24 +0.40/−0.37; theory 0.28 ±0.03 | CONFIRMED | HEPData Table 7 (description: parton-parton frame, text caption ~L811) | none |
| 2009.09429 | E10 parton-frame W_X W_T 3.25 +0.50/−0.48; theory 3.32 ±0.37 | CONFIRMED | HEPData Table 7 | none |
| 2009.09429 | E11 parton-frame W_L W_X 1.40 +0.60/−0.57; theory 1.71 ±0.19 | CONFIRMED | HEPData Table 7 | none |
| 2009.09429 | E12 parton-frame W_T W_T 2.03 +0.51/−0.50; theory 1.89 ±0.21 | CONFIRMED | HEPData Table 7 | none |
| 2009.09429 | E13 95% CL UL sigma(W_L W_L), WW-CM: 1.17 obs (0.88 exp) fb | CONFIRMED | arxiv.html text ~L757-758 "observed (expected) upper limit at 95% CL is 1.17 (0.88) fb"; abstract ~L849 | none |
| 2009.09429 | E14 95% CL UL, parton-frame: 1.06 obs (0.85 exp) fb | CONFIRMED | arxiv.html text ~L805-808 | none |
| 2009.09429 | E15 significance W_L W_X (WW-CM): 2.3 σ obs, 3.1 σ exp (background-only, asymptotic / Asimov) | CONFIRMED | arxiv.html text ~L762 and abstract ~L850 | none |
| 2009.09429 | E16 significance W_L W_X (parton frame): 2.6 σ obs, 2.9 σ exp | CONFIRMED | arxiv.html text ~L808 | none |
| 2009.09429 | E17 Table 4 systematics (LL / XT / LX / TT): luminosity 3.2/1.8/1.9/1.8; lepton 3.6/1.9/2.5/1.8; JES 11.0/2.9/2.5/1.1; pileup 0.9/0.1/1.0/0.3; b-tag 1.1/1.2/1.4/1.1; non-prompt 17.0/2.7/9.3/1.6; trigger 1.9/1.1/1.6/0.9; limited sample 38.0/3.9/14.0/5.7; theory 6.8/2.3/4.0/2.3; total syst 44.0/6.6/18.0/7.0; stat 123/15/42/22; total 130/16/46/23 | CONFIRMED | HEPData Table_4.json (all 12 rows x 4 columns); column order matches the qualifier list of four processes | none |
| 2009.09429 | E18 Table 4 "units of percent"; caption does not name the frame | CONFIRMED | arxiv.html ~L564-565 caption text ("...cross section measurements in units of percent"); no frame named | none (the CM-frame attribution remains an inference, as the claim states) |
| 2009.09429 | E19 dominant systematics: LL limited sample 38%, non-prompt 17%, JES 11%; LX limited sample 14%, non-prompt 9.3%; theory 6.8% LL, 4.0% LX; quote "...limited numbers of simulated events and of data events ... latter being the dominant contribution" | CONFIRMED | Table 4 values as E17; quote in arxiv.html ~L558-564 | none |
| 2009.09429 | E20 LL SR yield 16.0 ±18.3 events; Interference-WW 8.4 ±0.6 events | CONFIRMED | HEPData Table_5.json (WW signal region yields: W_L W_L 16.0, total unc 18.3; Interference-WW 8.4, unc 0.6) | none |
| 2009.09429 | E21 quote "Ideally, we would measure all three contributions separately, but the current data sample size is too limited" | CONFIRMED | arxiv.html ~L187 | none |
| 2009.09429 | E22 signal modelling: MadGraph5_aMC@NLO 2.7.2 LO O(α^6); O(α_s α^6) and O(α^7) corrections; Phantom 1.5.1 cross-check; off-shell/non-resonant 1–2% not included | CONFIRMED | arxiv.html ~L219-220; Table 6 caption (~L773) for O(α^7) corrections | none |
| 2009.09429 | E23 fiducial definition: leptons p_T>20, \|η\|<2.5, m_ll>20; jets m_jj>500, \|Δη\|>2.5; generator dressed leptons ΔR=0.1; anti-kT R=0.4, p_T>50, \|η\|<4.7; jets ΔR<0.4 from leptons excluded | CONFIRMED | arxiv.html ~L751-753; HEPData Table_6.json description (same definition) | none |
| 2009.09429 | E24 SR selection: lead lepton p_T>25, sublead>20; m_ll>20; Z-veto 15 GeV (ee only); MET>30; m_jj>500; \|Δη\|>2.5; jets p_T>50; b-jet veto | CONFIRMED | arxiv.html ~L287-304; Table of selection (~L321-345) | none |
| 2009.09429 | E25 reference [68] = Ballestrero, Maina, Pelliccioli, PLB 811 (2020) 135856, "Different polarization definitions..." | CONFIRMED | arxiv.html reference list ~L1590-1593 (entry verified). The in-text numbering [68] was not independently mapped to this entry. | none |
| 2009.09429 | E26 journal year: INSPIRE "year 2021" vs free text "(2020)" for PLB 812, 136018 | CONFIRMED | inspire.json publication_info: year 2021, pubinfo_freetext "Phys. Lett. B 812 (2020) 136018" | none (discrepancy correctly left open) |
| 2009.09429 | E27 helicity-vector definitions in the two frames not stated; defers to Ref. [68] | CONFIRMED | arxiv.html ~L805 cites [68] for the frame-dependence discussion; no explicit formula found | none |

## Non-CONFIRMED rows (summary)

1. 2607.12879, B3 (Table 4 second-column values): MISLABELED. The second column is observed with fixed interference normalization; the third column is the SM expected value. See table.
2. 2607.12879, B17 (interference-scaling quote): WRONG_LOCATION. It is in the Run 2 re-analysis paragraph (paper.txt L303-306), not the combination paragraph.
3. 2310.04350, D16 (on-shell window): MISMATCH. The window is recoverable: |m_ll − m_Z| < 10 GeV (arxiv.html alttext, Sec. 4.1 and 4.3); m_4l > 180 GeV.
4. 2310.04350, D20 (aNTGC limits location): WRONG_LOCATION. Sec. 8.3, not Sec. 9.

## Verifier-noted omissions

Scope: Q1 (resonances), Q2 (W/Z longitudinal fractions), Q3 (multiple spin-density elements).

- 2607.20246: fiducial sigma(WZjj-EW) at 13.6 TeV = 0.374 ±0.077 (stat) ±0.053 (syst) ±0.009 (lumi) fb (HEPData Table 1; paper abstract, Sec. 9 ~L1278). Not a Q2/Q3 quantity; recorded in the claim file's "not extracted" list. Also in Sec. 9 (~L1272): individual Run 2 and Run 3 fits "yield consistent results ... but with a lower sensitivity" (not in the claim file; minor).
- 2503.11317: the expected 95% CL UL under the null hypothesis is 0.43 fb (text.txt ~L60), and the limits use the CL_s method (text.txt ~L60, refs [57,58]). Neither is in the claim file; the CL_s method is relevant to the "CL / obs-exp" column.
- 2310.04350: the on-shell window (see D16) is the only extractable omission in the claim file.
- 2009.09429: no omitted in-scope result found. No limit tables, no fraction measurement.
- 2607.12879: no omitted in-scope result found beyond the claim file's own list. mu_ZZ = 1.03 ±0.10 (inclusive ZZ normalisation, text ~L285) is not a fraction and is out of scope.

## Scope notes for the lead (not verdicts)

- Q3 applicability, claim-by-claim: 2607.20246 measures three diagonal-element fractions (f_00, f_0X, f_X0), which the paper calls "diagonal elements of the full spin density matrix" (A20). This is a plausible Q3 hit. 2607.12879 measures f_LL and the normalisation mu_TX only (B12, B21): borderline. 2310.04350 measures one CP-sensitive optimal observable plus mu_LL: borderline and arguably not "more than one element". 2009.09429 and 2503.11317 measure helicity cross sections only, with no fractions. The lead decides.
- Q2: 2503.11317 has no polarization fraction (C10). 2009.09429 has no fraction (E-rows describe cross sections and limits). 2310.04350 has mu_LL (signal strength) with no fraction (D8 notes the text phrase "fraction of Z_L Z_L events").
- Q1 (resonance limits, 10 GeV–1 TeV rule): none of the five papers is a resonance search. No Q1 result was checked.
- Verified HEPData column conventions: 2607.20246 Table 5 (Data column; MadGraph, Sherpa 3.0, MoCaNLO columns) and Table 3 (f_X0 vs mu columns, checked against the paper's Table 3 header); 2009.09429 Table 4 (LL, XT, LX, TT per the qualifier list and caption), Tables 6 and 7 (WW-CM vs parton-parton per the table descriptions and text captions); 2310.04350 Table 1 (observed vs Sherpa vs Powheg per the Fig. 8 caption).
