# Verification report: verify_w4_1

Sources re-opened: `.cache/2603.26463/paper.txt` and `arxiv_2603.26463.html`; `.cache/2507.03500/fulltext.txt` and `hepdata/tables/*.json`; `.cache/2409.16731/paper.txt` and `arxiv_2409.16731.html`; `.cache/2008.04174/fulltext.txt`, `arxiv_html.html` and `hepdata/tables/*.json`. HEPData values for 2008.04174 were compared programmatically (Figure 9a/9b, A1a/A1b, Impacts A16a/A16b: 40 + 40 + 140 values, all match). Line numbers below refer to the cached text files.

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| 2603.26463 | Abstract: C(2,1,2,-1) = -0.71 +/- 0.45; C(2,2,2,-2) = 0.08 +/- 0.44 | CONFIRMED | "yield coefficients C 2,1,2,−1 = −0.71 ± 0.45 and C 2,2,2,−2 = 0.08 ± 0.44" (paper.txt:32) | none |
| 2603.26463 | Table 1 observed values, 2e2mu / 4e+4mu / combined, both coefficients | CONFIRMED | Table 1 rows "−0.98±0.64, −0.44±0.63, −0.71±0.45, 0.00±0.64, 0.15±0.61, 0.08±0.44" (paper.txt:180–188; arXiv HTML table S0.T1.5) | none |
| 2603.26463 | Table 1 uncertainty rows (fake-lepton, irreducible, interference, EW NLO, migration, statistical) | CONFIRMED | paper.txt:190–220; HTML rows match all listed values | none |
| 2603.26463 | SM expected -0.97 / 0.64, labelled "inclusive" (open issue on which column) | CONFIRMED | Table 1 "SM expected | −0.97 | 0.64"; HTML cells for "SM expected" carry colspan=3 under each coefficient, i.e. one value spanning 2e2mu, 4e+4mu and combined | Close the open issue: the value spans all three columns per coefficient |
| 2603.26463 | Hypothesis test: 4.7 sigma observed, expected 4.9 sigma; rejection of |00> | CONFIRMED | "rejected with a significance of 4.7 σ (expected 4.9 σ)" (paper.txt:240; abstract) | none |
| 2603.26463 | Delta C_interf = -0.07 (C1) and 0.06 (C2), same-flavour channels | CONFIRMED | "Δ C 2,1,2,−1 interf = −0.07" and "Δ C 2,2,2,−2 interf = 0.06" (paper.txt:296–298) | none |
| 2603.26463 | 50% of the correction as symmetric systematic | CONFIRMED | "A conservative symmetrical systematic uncertainty equal to 50 % of this correction is assigned to the same-flavour channels" (paper.txt App. B) | none |
| 2603.26463 | EW NLO multiplicative uncertainty 1.1% (C1), 1.4% (C2) | CONFIRMED | "corresponding to multiplicative uncertainties of 1.1 % for C 2,1,2,−1 and 1.4 % for C 2,2,2,−2" (paper.txt:300) | none |
| 2603.26463 | Reducible background uncertainty 39% (Run 2), 46% (Run 3) | CONFIRMED | "39% for the Run 2 data and 46% for the Run 3 data" (paper.txt:289) | none |
| 2603.26463 | Hypothesis-test systematics: ~10% QCD higher order; 3% experimental | CONFIRMED | "approximately 10% of the predicted yield"; "conservative overall 3% uncertainty" (paper.txt:304) | none |
| 2603.26463 | Sensitivity gains: "about 20%" (full distribution vs c_2,1,2,-1), "about 15%" (mZ2 split) | CONFIRMED | "about 20% higher expected sensitivity"; "about 15% in the rejection of the purely longitudinal configuration" (paper.txt:~150–152) | none |
| 2603.26463 | Selection: lepton pT/eta, 20/15/10 GeV, mZ1, mZ2, m4l windows, mu eta < 2.7 (2.5 Run 3) | CONFIRMED | paper.txt:109–117 | none |
| 2603.26463 | Estimator c = 40 pi Re(Y Y), M1 = -M2 in {1,2}; SDM map 1/3 factors, nine of 81 elements, cited to ref. 11 | CONFIRMED | paper.txt:125–131; reference [11] = Aguilar-Saavedra, Bernal, Casas, Moreno, PRD 107.1 (2023) 016012 (paper.txt:358–360) | none |
| 2603.26463 | "Higher-order EW effects are <2% (Introduction)" | MISLABELED | Introduction says the dedicated observables "have small (<2%) higher-order corrections [42]" (paper.txt:82). It does not say EW; the EW-specific numbers are 1.1% and 1.4% (App. B) | Write "higher-order corrections (<2%, ref. 42)" and give the EW numbers from App. B separately |
| 2603.26463 | Metadata: PRL 137 (2026) 111804; DOI 10.1103/y1nh-1b82; arXiv v2 05 Oct 2026 | CONFIRMED | paper.txt:4–12 header | none |
| 2603.26463 | HEPData: no record | CONFIRMED | cache marker `hepdata/NONE` present, `tables/` empty | none |
| 2507.03500 | No measured f_L, f_0, A_i, rho or other SDM element (Q2/Q3 negative scope) | CONFIRMED | Full-text search finds polarisation only in the intro (line 94) and an EFT-discriminant remark (line 944); HEPData Tables 23–29 are cross sections | none |
| 2507.03500 | Sec. 1 quote "The latest ATLAS analyses [16, 17], focused on polarisation measurements..." | CONFIRMED | fulltext.txt:94 | none |
| 2507.03500 | Sec. 9.2 quote "polarisation-related observables, as well as various multivariate combinations of them" | CONFIRMED | fulltext.txt:944 | none |
| 2507.03500 | phi*_W, phi*_Z definition following Ref. [113] (Panico, Riva, Wulzer) | CONFIRMED | fulltext.txt:862; reference [113] at 1748–1751 | none |
| 2507.03500 | Triple product proposed in Ref. [114] (Degrande, Touchèque) | CONFIRMED | fulltext.txt:864; reference [114] at 1753–1756 | none |
| 2507.03500 | "two triple product observables are measured differentially" | CONFIRMED | fulltext.txt:869 | none |
| 2507.03500 | "Any asymmetry observed around pi/2 ..." quote | CONFIRMED | fulltext.txt:871 | none |
| 2507.03500 | HEPData Tables 23, 25 (phi*_W, phi*_Z) and 27, 29 (triple products) | CONFIRMED | hepdata/tables/Table_23/25/27/29.json: first header column is phi*_W, phi*_Z, p_perp(sum pz,Z,l^W), p_perp(l+,z,l-,l^W); values are fiducial cross sections [fb] | none |
| 2507.03500 | cos theta* decay-angle definition, BDT input only (Table 7) | CONFIRMED | fulltext.txt:1044, 1042 | none |
| 2507.03500 | Refs [15]–[17]: EPJC 79 (2019) 535; PLB 843 (2023) 137895; PRL 133 (2024) 101802 | CONFIRMED | fulltext.txt:1266–1279 | none |
| 2507.03500 | Selection: mu pT>15, abs(eta)<2.5; e pT>15; W-lepton pT>20 tight; mT>30; anti-kt R=0.4, pT>25, abs(eta)<4.5; 4th-lepton veto pT>5 | CONFIRMED | fulltext.txt:217, 222, 235–237, 250–253, 260–262 | none |
| 2507.03500 | Metadata: JHEP 11 (2025) 006; HEPData 166315, 38 tables | CONFIRMED | fulltext.txt "JHEP 11 (2025) 006"; hepdata/record.json has 38 data_tables | none |
| 2409.16731 | Table 3, ZZ LO / NLO QCD / NLO EW coefficients (alpha_1,0 and alpha_2,0 for both bosons, gamma_1,0,1,0, gamma_2,0,2,0, alpha_2,-2) | CONFIRMED | Table 3 (arXiv HTML table #29): e.g. "α2,0(1) 0.03009(11) 0.02794(13) 0.02960(11)"; all 24 values match | none |
| 2409.16731 | Table 5, ZZ NLO QCD inclusive vs ATLAS fiducial | CONFIRMED | Table 5: "α2,0(1) 0.02807(5) 0.02075(7)", "α2,−2(1) −0.01000(2) −0.02614(3)"; the source prints the second-boson coefficient as "α2,−2(2)" | keep "as printed" note |
| 2409.16731 | Table 7, W+Z NLO QCD, MC-truth vs nu-reco | CONFIRMED | Table 7: "α2,0(1) 0.0283(3) 0.0147(3)", "γ2,0,2,0 0.0013(1) −0.0013(1)" etc.; all 16 values match | none |
| 2409.16731 | Table 4, H->4l default setup (LO / NLO EW 4l-CM / NLO EW H-rest) | CONFIRMED | Table 4 (HTML #34): "α2,0(1) −0.04792(4) −0.04498(6) −0.04215(6)"; "γ2,1,2,−1 −0.00776(1) −0.00779(2) −0.00715(2)" etc. | none |
| 2409.16731 | Table 4, second setup 81 < M_ee < 101 GeV | CONFIRMED | Table 4 lower block: "α2,0(1) −0.04395(8) −0.0435(1) −0.0430(1)"; "γ2,1,2,−1 −0.00794(3) −0.00798(4) −0.00773(4)" | none |
| 2409.16731 | Table 6, finite-pT H, NLO EW, columns 25 GeV no cuts / 25 GeV Eq. 38 / 200 GeV Eq. 38 | CONFIRMED | Table 6 (HTML #41): "α2,0(1) −0.04511(7) −0.07312(8) −0.05518(8)"; "γ2,2,2,−2 0.00488(2) 0.00549(3) 0.00523(3)" etc. | none |
| 2409.16731 | Table 6 gamma_{2,-1,2,1} = −0.00592(2) at 25 GeV with Eq. 38 cuts, "as printed" | CONFIRMED | Table 6 prints "−0.00592(2)" in that cell, neighbours −0.00845(3) and −0.00724(2) for gamma_{2,1,2,−1} | value stands as printed (see next row) |
| 2409.16731 | Open issue: the −0.00592 entry "could be a typo" | UNSUPPORTED | Table 6 caption: "Owing to different selections for different lepton flavours, the symmetry relations of Eq. 30 are also violated." (paper.txt Table 6 caption, Sec. 4.4). The paper attributes the asymmetry to the cuts | Replace "could be a typo" with that caption sentence; keep the value as printed |
| 2409.16731 | R_c (ZZ): LO 1.89(3), NLO QCD 1.73(2); fiducial NLO QCD 1.87(2) | CONFIRMED | Eq. 28: "R_c(LO) = 1.89(3), R_c(NLO QCD) = 1.73(2)" (paper.txt:460–462); "R_c^fid = 1.87(2)" in Table 5 caption text (Sec. 4.4) | none |
| 2409.16731 | R_c (W+Z): LO 2.39(3), NLO QCD 1.31(2) | CONFIRMED | Eq. 29 (paper.txt:464) | none |
| 2409.16731 | I_3 (CGLMP) LO 2.671(2), NLO EW 4l-CM 2.682(4), H-rest 2.571(4); bound <= 2 (Eq. 18) | CONFIRMED | Eq. 34 (HTML #35) "I3 = 2.671(2), 2.682(4), 2.571(4)"; Eq. 18 "I3 ≤ 2" | none |
| 2409.16731 | Table 2, ZZ off-shell vs DPA: sigma and alpha_2,0(1) incl. delta, LO +0.16%, NLO QCD −0.04%, NLO EW 0.02932(5)/0.02944(5)/+0.41% | CONFIRMED | Table 2 (HTML #27) | none |
| 2409.16731 | Eq. 11 map of alpha_{1,0}, alpha_{2,0}, gamma_{1,0,1,0}, gamma_{2,0,2,0} to f_lambda-lambda' | CONFIRMED | Eq. 11 (HTML #10): (1/4)sqrt(3/pi) eta (f+ − f−); (1 − 3 fL)/(4 sqrt(5 pi)); 3 eta1 eta3 (…)/(16 pi); (1 − 3fL(1) − 3fL(3) + 9 fLL)/(80 pi) | none |
| 2409.16731 | eta_l ≈ 0.219 (Eq. 9), (G_mu, M_W, M_Z) scheme, massless leptons | CONFIRMED | Eq. 9 "≈ 0.219" (HTML #8); paper.txt:153 | none |
| 2409.16731 | Eq. 14 rho = (1/9)[...] in irreducible-tensor basis T of Ref. [44]; A, C complex | CONFIRMED | Eq. 14 (HTML #13); paper.txt:197–199 | none |
| 2409.16731 | Eq. 16 as printed: sqrt(40 pi) alpha = A; 40 pi gamma = C; 8 pi gamma/eta^2 = C | CONFIRMED | arXiv HTML alttext: `\sqrt{40\pi}\alpha^{(i)}_{2,m_{i}}=A^{(i)}_{2,m_{i}}`, `40\pi\gamma_{2,m_{1},2,m_{3}}=C_{2,m_{1},2,m_{3}}`, `8\pi\gamma_{1,m_{1},1,m_{3}}/\eta_{\ell}^{2}=C_{1,m_{1},1,m_{3}}` | none (as printed) |
| 2409.16731 | Eq. 16 factors against the basis source Ref. [44] (arXiv 2209.13441) | UNVERIFIABLE | Ref. [44] is correctly identified: "J.A. Aguilar-Saavedra, A. Bernal, J.A. Casas, J.M. Moreno, PRD 107 (2023) 016012, [2209.13441]" (reference list). Its text is not in the cache and was not fetched, so the normalisations sqrt(40 pi), 40 pi, 8 pi/eta^2 are not checked against it | Fetch 2209.13441 into an empty directory and check the tensor-basis normalisation, or state Eq. 16 only as the paper's convention |
| 2409.16731 | Eq. 17: entangled iff gamma_{2,1,2,-1} != 0 or gamma_{2,2,2,-2} != 0, "sufficient and necessary" | CONFIRMED | "sufficient and necessary conditions for the two bosons to be entangled are" (paper.txt:209) | none |
| 2409.16731 | Eq. 20 CGLMP expression | CONFIRMED | Eq. 20 (HTML #19): I3 = 1/2 + 4√3/9 − √(5π)(1 − 8√3/9) α2,0 − 40π(2/3 + 4√3/9) γ2,1,2,−1 + (20π/3) γ2,2,2,−2 | none |
| 2409.16731 | "Tree-level H->ZZ* relations at LO (Eqs. 30–32), confirmed numerically at LO in both setups" | MISLABELED | Table 4 caption: "The relations of Eq. 30 are confirmed numerically at LO in both setups." Eq. 31 is discussed only at NLO EW ("mildly violated"), and Eq. 32 only at NLO EW ("A mild modification ... is found at NLO EW") | Restrict the LO confirmation to Eq. 30 |
| 2409.16731 | Open issue: Table 1 vs Table 3 alpha_2,0(1) 0.02807(5) vs 0.02794(13); "Both captions say the same setup" | CONFIRMED | Table 1 caption: "computed according to Eq.4"; Table 3: "according to Eq. 7". For ZZ the scale (M_V1+M_V2)/2 equals M_Z, so the scales agree. Values 0.02807(5) and 0.02794(13) are as printed | Optionally name the Eq. 4 vs Eq. 7 difference as the only textual difference |
| 2409.16731 | Selection: Eq. 22 (81–101 GeV, opposite-sign same-flavour), Eq. 23, Eq. 24, Eq. 26, Eq. 38; p_T,H 25 and 200 GeV | CONFIRMED | Eq. 22 lead-in "charged-lepton pairs with opposite charge and same flavour" (paper.txt:253–256); Eqs. 23–24 (HTML #22–23); Eq. 26 (HTML #25); Eq. 38 (HTML #40); p_T,H values in Table 5 caption text | none |
| 2409.16731 | Dressing R_lgamma = 0.1 "(Sec. 3.1, 3.2)" | CONFIRMED | paper.txt:262 (Sec. 3.1) and paper.txt:273 (Sec. 3.2) | none |
| 2409.16731 | Frame: "we will employ the di-boson CM frame as Lorentz frame for the helicity-state definition ..." (Sec. 2.1) | CONFIRMED | paper.txt:117 | none |
| 2409.16731 | Decay angles for positive leptons (Sec. 2.1); Ref. [44] uses negative leptons (Sec. 2.3) | CONFIRMED | paper.txt:84 and paper.txt:207 ("associated to the negatively charged leptons") | none |
| 2409.16731 | Off-shell effects "< 2% in most of phase-space regions" (Sec. 4.1); alpha_2,0 DPA effect largest 0.4% at NLO EW | CONFIRMED | paper.txt:284; Table 2 caption "the largest one (0.4%) found at NLO EW" | none |
| 2409.16731 | NLO QCD effect on R_c "not covered by the LO-uncertainty estimate" (Sec. 4.2, after Eq. 29) | CONFIRMED | paper.txt:465–466 | none |
| 2409.16731 | H-rest vs 4l-CM: radiative effect 6.5% vs 14% on alpha_2,0; I_3 "−4%" in H-rest (Sec. 4.3) | CONFIRMED | Table 4 caption text "6.5% level ... while 14% corrections"; paper.txt:607 "slightly larger effects (−4%) are found in the H-rest frame" | none |
| 2409.16731 | Tree-level Eq. 6 "is no longer valid" at NLO EW (Sec. 4.3) | CONFIRMED | paper.txt:490 | none |
| 2409.16731 | Table 6: "large, unphysical modifications to all considered coefficients" (Sec. 4.4) | CONFIRMED | Table 6 caption text | none |
| 2409.16731 | Table 8: "up to 30% discrepancies for polar coefficients, and even a wrong sign for alpha_2,2" (Sec. 4.5) | CONFIRMED | Table 8 text (paper.txt ~l.817–826) | none |
| 2409.16731 | sqrt(s) of the paper's own predictions not stated | CONFIRMED | No sqrt(s) in the body; "TeV" occurs only in the intro and in cited ATLAS/CMS references | none |
| 2409.16731 | Preprint: arXiv v1 25 Sep 2024; COMETA-2024-24, MPP-2024-183, TIF-UNIMI-2024-15; authors Grossi, Pelliccioli, Vicini | CONFIRMED | paper.txt:36–39. INSPIRE recid 2833094 not checked (not in the source) | none |
| 2409.16731 | R_c defined "as in ATLAS 2211.09435" | CONFIRMED | paper.txt:170 "proposed by ATLAS [3]", and reference [3] is ATLAS 2211.09435 (PLB 843 (2023) 137895) | none |
| 2409.16731 | Table 6 label printed "gamma_{1,1,1-1}" (comma missing) | CONFIRMED | Table 6 (HTML #41) prints "γ1,1,1−1" | none |
| 2008.04174 | Selection: muon pT>26, abs(eta)<2.4; electron pT>30 | CONFIRMED | fulltext.txt:256–257, 274 | none |
| 2008.04174 | m_T > 40 GeV | CONFIRMED | fulltext.txt:323 | none |
| 2008.04174 | Extra-lepton veto: loose leptons with pT > 10 GeV | CONFIRMED | fulltext.txt:328–330 | none |
| 2008.04174 | |y_W| bins of width 0.25 up to 2.5 (10 per charge); |y_W| > 2.5 fixed to MC | CONFIRMED | fulltext.txt:579–583 | none |
| 2008.04174 | Template binning: pT^l up to 45 GeV in 1 GeV bins; eta^l in 0.1 bins | CONFIRMED | fulltext.txt:572–575 | none |
| 2008.04174 | Collins–Soper frame quote; Eq. 2 keeps A0 and A4 after phi* integration | CONFIRMED | fulltext.txt:465 (frame); fulltext.txt:476 (A0 and A4 terms) | none |
| 2008.04174 | Eq. 3: A0 ∝ f0, A4 ∝ ∓(fL − fR); f_i > 0, fL+fR+f0 = 1; no constant stated | CONFIRMED | fulltext.txt:490 | none |
| 2008.04174 | f_i depend strongly on pT^W, |y_W|, charge | CONFIRMED | fulltext.txt:497–498 | none |
| 2008.04174 | f_0 fixed to MC; longitudinal component with 30% normalization uncertainty | CONFIRMED | fulltext.txt:586 ("longitudinally polarized states are fixed to the MC prediction"); fulltext.txt:1324 ("30% normalization uncertainty") | none |
| 2008.04174 | Fig. 9: helicity cross sections normalized to total; 9a = W+, 9b = W− | CONFIRMED (caption); charge-to-file mapping inferred | Caption: "Measured normalized W+ → ℓ+ν (left plot) or W− → ℓ−ν (right plot) ... normalized to the total cross section" (fulltext.txt:1343–1349). That 9a is the left plot is an inference from file naming | none beyond the caveat already in the claim file |
| 2008.04174 | Table A: 40 normalized W_L/W_R values, HEPData Figure 9a/9b | CONFIRMED | Programmatic check against hepdata/tables/Figure_9a.json and Figure_9b.json (groups 0 and 3) gives 0 mismatches | none |
| 2008.04174 | Table A uncertainty label "Measurement uncertainty (total; no stat/syst split in HEPData)" | UNSUPPORTED | HEPData label is only "Measurement uncertainty" (Figure_9a.json, group 0, asymerror). The claim file's own open issue says the type is not stated | Delete "total"; write "Measurement uncertainty (type not stated)" |
| 2008.04174 | Table B: 40 absolute W_L/W_R values [pb], HEPData Figure A1a (W+) / A1b (W−) | CONFIRMED | Programmatic check against Figure_A1a.json and Figure_A1b.json gives 0 mismatches; charge mapping matches the Fig. 10.1 caption "W+ (left) and W− (right)" (fulltext.txt:1995–1998) | none |
| 2008.04174 | Table C: 20 rows x 7 A4 uncertainty components, Impacts A16a/A16b | CONFIRMED | Programmatic check against Impacts_Figure_A16a.json and A16b.json gives 0 mismatches; column order matches the HEPData headers; group k maps to header k+1 (total = 0.017 in A16a, 0–0.25) | none |
| 2008.04174 | HEPData A16a and A16b both labelled W+ while caption says upper W+ and lower W− | CONFIRMED | Both Impacts_Figure_A16a/b.json descriptions read "for $W^{+}$"; caption (fulltext.txt:2138) "for W+ (upper) and W− (lower)" | none (already flagged in claim file) |
| 2008.04174 | A4 central values figure-only (Fig. 10.5 W+, 10.6 W−); no A4-coefficient table in HEPData | CONFIRMED | fulltext.txt:2044–2060; HEPData Figure_A4 is the charge asymmetry, not A4 | PRD numbering not checked (already flagged) |
| 2008.04174 | "A4 is negative in this case, and the plotted quantity is −A4" (W+ only) | CONFIRMED | fulltext.txt:2050–2051 | none |
| 2008.04174 | Intro fractions W_L ~65 (60)%, W_R ~28 (33)%, W_0 ~7 (7)% (background statement, not a measurement) | CONFIRMED | fulltext.txt:110–112 | none |
| 2008.04174 | Correlations "in the range 50–80% for adjacent W boson rapidity bins" | CONFIRMED | fulltext.txt:1369–1371 | none |
| 2008.04174 | 2.5% luminosity "fully correlated across all the rapidity bins ... cancels out" in ratio | CONFIRMED | fulltext.txt:1352–1354 | none |
| 2008.04174 | Impacts: "mostly cancel when considering either the cross section normalized to the total cross section or in the charge asymmetry" (Sec. 0.7.3) | CONFIRMED | fulltext.txt:1191–1193 | none |
| 2008.04174 | Systematic groups (Sec. 0.7.3), PDFs with 60 Hessian variations of NNPDF3.0 | CONFIRMED | fulltext.txt:1163–1175; NNPDF3.0 at fulltext.txt:219 and 60 Hessian at fulltext.txt:997 | none |
| 2008.04174 | Dressing with dR < 0.1 used only in the double-differential measurement (Sec. 0.6.3) | CONFIRMED | fulltext.txt:616 | none |
| 2008.04174 | Pre-FSR generated leptons for helicity templates | CONFIRMED | fulltext.txt:491 ("considered before any final-state radiation") | none |
| 2008.04174 | Metadata: PRD 102 (2020) 092012; DOI 10.1103/PhysRevD.102.092012; INSPIRE 1810913; HEPData recid 94180 | CONFIRMED | arXiv HTML journal ref "Phys.Rev.D 102 (2020) 092012"; hepdata/record.json (recid 94180, inspire ins1810913, DOI in journal_info) | none |
| 2008.04174 | sqrt(s) = 13 TeV; integrated luminosity 35.9 fb^-1 | CONFIRMED | fulltext.txt:196 | none |
| 2008.04174 | Q2: no measured f_L, f_0, A0 or rho00 (f_0 fixed; L and R not converted to f_L) | CONFIRMED | fulltext.txt:586, 1324; fit has 40 floating cross sections (fulltext.txt:586–590) | none |

## Counts

| verdict | count |
|---|---|
| CONFIRMED | 88 |
| MISMATCH | 0 |
| WRONG_LOCATION | 0 |
| MISLABELED | 2 |
| UNSUPPORTED | 2 |
| UNVERIFIABLE | 1 |
| Total rows | 93 |

Per file: 2603.26463, 17 rows (16 CONFIRMED, 1 MISLABELED); 2507.03500, 12 rows (12 CONFIRMED); 2409.16731, 37 rows (34 CONFIRMED, 1 MISLABELED, 1 UNSUPPORTED, 1 UNVERIFIABLE); 2008.04174, 27 rows (26 CONFIRMED, 1 UNSUPPORTED).

## Verifier-noted omissions

No file in the claim set has a "Verifier-noted omissions" heading, so there were no bullets to check.

Omissions found by the verifier (in scope, more relevant than what was extracted):

- 2409.16731 (Q2/Q3, theory): Table 1 gives full off-shell vs DPA at NLO QCD for W+Z, which the claim file does not extract. The W+Z full off-shell column equals Table 7 MC-truth. The DPA column is alpha_1,0(1) −0.0472(3), alpha_2,0(1) 0.0289(3), alpha_1,0(3) 0.0041(3), alpha_2,0(3) 0.0294(3), gamma_1,0,1,0 −0.0053(1), gamma_2,0,2,0 0.0014(1), alpha_2,-2(1) −0.0118(3), alpha_2,-2(3) −0.0078(4) (paper.txt Table 1, arXiv HTML #26). This is the only W+Z DPA comparison in the paper.
- 2409.16731 (Q3 caveat): Sec. 2.3 says the rho of Eq. 14 "is either incomplete or not even well defined" when used for entanglement and Bell quantities (paper.txt:233–235). The claim file does not record this caveat.
- 2409.16731 (lower priority): Table 8 gives the SM-extrapolation numbers (e.g. SMEFT truth alpha_2,0(1) 0.0313(1) vs extrapolated with nu-reco 0.041(2)). The claim file quotes only the "30%" sentence.
- 2008.04174: none in scope. Figures 11, 13 and 14–16 are polarisation-integrated (Fig. 11 caption: "integrated over the W polarization states"; Sec. 0.6.3 fits unpolarised processes), so they are not helicity results.
- 2603.26463: none. 2507.03500: none (no polarisation or SDM content exists in the paper).

## Notes

- 2008.04174, Fig. 9 and Fig. A1 consistency: sum(value x 0.25) over bins gives W+ W_L 0.341 and W_R 0.255 (Fig. 9a), and W− W_L 0.402 and W_R 0.277 (Fig. 9b). The ratio L/(L+R) agrees with the Fig. A1 absolute tables within each charge (W+ 0.571 both, W− 0.592 both). This supports per-charge normalisation. It does not reproduce the intro fractions 65% and 60%, which are of the total cross section including f_0. The claim file's refusal to convert to f_L is correct.
- 2409.16731, Table 1 vs Table 3: the claim file's open issue is accurate. The two captions cite different projection equations (Eq. 4 and Eq. 7), and the values differ at about 1 sigma. Neither the paper nor the cache explains the difference.
