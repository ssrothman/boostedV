# Verification report: verify_w3_1 (notes 2209.14903, 2005.03799, 1410.1154, 1202.5272)

Sources: 2209.14903 and 2005.03799 read from the arXiv HTML text in `.cache/<id>/` (`paper.txt`, `fulltext.txt`); 1202.5272 and 1410.1154 read from the cached PDFs via `pdftotext -layout`; 1410.1154 HEPData values read from the local `hepdata/tables/Table_{1,2,3}.json`. The other three HEPData records are `hepdata/NONE` (no record). HEPData was not contacted. Verdicts are per table row; grouped rows (e.g. a 6-entry covariance matrix) count as one row.

## Verdict table

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| 2209.14903 | f0 = 0.684 ± 0.005 (stat) ± 0.014 (syst) | CONFIRMED | Abstract: "f0=0.684±0.005(stat.)±0.014(syst.)"; Sec. 9 display; Table 3 totals 0.005/0.014 | — |
| 2209.14903 | fL = 0.318 ± 0.003 ± 0.008 | CONFIRMED | Abstract: "fL=0.318±0.003(stat.)±0.008(syst.)" | — |
| 2209.14903 | fR = −0.002 ± 0.002 ± 0.014 | CONFIRMED | Abstract: "fR=-0.002±0.002(stat.)±0.014(syst.)" | — |
| 2209.14903 | Covariance matrix (Table 2, 6 entries) | CONFIRMED | Table 2: 2.125e-4, −3.665e-5, −1.758e-4, 6.651e-5, −2.986e-5, 2.057e-4 | — |
| 2209.14903 | Correlation matrix (Table 2, 3 entries) | CONFIRMED | Table 2: −0.308, −0.841, −0.255. Recomputed f0-fL from Table 2: −3.665e-5/sqrt(2.125e-4·6.651e-5) = −0.308 | — |
| 2209.14903 | χ²/ndf = 0.267 | CONFIRMED | Sec. 9: "divided by the number of degrees of freedom of the fit is 0.267" | — |
| 2209.14903 | Unfolded cos θ* distribution, figure-only | CONFIRMED | Sec. 9 "shown ... Figure 3(b)"; no table of per-bin values in text | — |
| 2209.14903 | NNLO reference f0 0.687±0.005, fL 0.311±0.005, fR 0.0017±0.0001 (mt 172.8 GeV) | CONFIRMED | Sec. 1: "f0=0.687±0.005, fL=0.311±0.005 and fR=0.0017±0.0001 assuming a top-quark mass mtop=172.8 GeV" | — |
| 2209.14903 | Table 3 category rows (jet reco 0.008/0.004/0.010; tt̄ generator 0.009/0.004/0.004; tt̄ radiation 0.007/0.002/0.007; top mass 0.005/0.003/0.007; electron, muon, b-tag, parton shower, pile-up) | CONFIRMED | Sec. 9 Table 3 rows, values match the claim exactly | — |
| 2209.14903 | Table 3 totals: systematic 0.014/0.008/0.014; stat 0.005/0.003/0.002; total 0.015/0.008/0.014 | CONFIRMED | Sec. 9 Table 3 last rows | — |
| 2209.14903 | Text: largest syst. in all three fractions from tt̄ modelling, dominated by generator choice | CONFIRMED | Sec. 9: "The largest systematic uncertainty in all three helicity fractions arises from the modelling of t t̄ production, and is dominated by the uncertainty from the choice of matrix-element generator." Note: for fR, Table 3 single row jet reconstruction (0.010) exceeds tt̄ generator (0.004); the claim's open issue on this is correct | — |
| 2209.14903 | ATLAS 8 TeV inputs (f0 0.709, fL 0.299, fR −0.008, with stat+bkg/syst) | CONFIRMED | Sec. 1: "f0=0.709±0.012(stat. + bkg.) −0.014+0.015(syst.)", "fL=0.299±0.008 ... −0.012+0.013", "fR=−0.008±0.006 ... ±0.012" | — |
| 2209.14903 | ATLAS+CMS 8 TeV combination f0 0.693±0.014, fL 0.315±0.011, fR −0.008±0.007 | CONFIRMED | Sec. 1: "f0=0.693±0.014, fL=0.315±0.011 and fR=−0.008±0.007"; "total uncertainties are quoted" | — |
| 2209.14903 | Data/selection: 13 TeV, 139 fb⁻¹, 2015–2018; lepton pT >25 (2015) / >27 GeV (2016–18); ≥2 jets pT>25, anti-kt R=0.4; ≥2 b-tags at 60% (DL1r); Z-veto 80–100 GeV and ETmiss>60 for SF; mll>15; e |η|<2.47, μ |η|<2.5 | CONFIRMED | Sec. 3: "integrated luminosity of 139 fb⁻¹"; Sec. 4: "pT>25 GeV or pT>27 GeV ... 2015 and 2016–2018"; "60%-efficiency operating point"; "outside of the ZZ-boson mass window of 80–100 GeV"; "mℓℓ>15 GeV"; electron |η|<2.47 and jets |η|<2.5, R=0.4 | — |
| 2209.14903 | Generators: Powheg Box v2 + Pythia 8.230 (tt̄), Sherpa (V+jets) | CONFIRMED | Sec. 3: "Powheg Box v2 ... Pythia 8.230 [33]"; "Sherpa 2.2.1" for V+jets | — |
| 2209.14903 | Neutrino weighting solution for ~90% of tt̄; RooUnfold IBU with regularisation 180 | CONFIRMED | Sec. 5: "A solution is found for about 90% of the t t̄ events"; Sec. 6: "The optimal value is found to be 180" | — |
| 2209.14903 | Observable definition: θ* between lepton and reversed b direction in W rest frame; frame not named (not "helicity" or "Collins–Soper") | CONFIRMED | Sec. 1 and Abstract: "both calculated in the WW boson rest frame"; no occurrence of "helicity angle", "helicity frame" or "Collins" in paper.txt | — |
| 2209.14903 | Parton level: leptons before FSR, τ before decay; both tops decay leptonically | CONFIRMED | Sec. 6: "The leptons are taken from the MC generator's 'truth' record before final-state photon radiation, and in the case of τ-leptons, also before decay" | — |
| 2209.14903 | Fit parameters unrestricted, may be outside [0,1] | CONFIRMED | Sec. 7: "are allowed to take unphysical values outside of the [0,1] interval" | — |
| 2209.14903 | MC-truth reweighted; parton-shower reshuffling distorts at "a few per mille level" | CONFIRMED | Sec. 6: "distorts the distribution at a few per mille level" | — |
| 2209.14903 | Non-closure "negligible", does not change Table 3 totals | CONFIRMED | Sec. 9: "A small degree of non-closure is observed but the corresponding uncertainty is negligible and does not change the total uncertainties listed in Table 3." Sec. 7: "Any non-closure seen is included as a systematic uncertainty" (the claim's open issue on this is correct) | — |
| 2209.14903 | Citation: PLB 843 (2023) 137829; CERN-EP-2022-197; arXiv v2 16 Jun 2023 | CONFIRMED | Paper text: "CERN-EP-2022-197", "Phys. Lett. B. 843 (2023) 137829", "arXiv:2209.14903v2 [hep-ex] 16 Jun 2023" | — |
| 2209.14903 | HEPData: none | CONFIRMED | `.cache/2209.14903/hepdata/NONE` = "no HEPData record" | — |
| 2005.03799 | ATLAS (ℓ+jets) inputs: F0 0.709±0.012±0.015; FL 0.299±0.008±0.013; FR −0.008±0.006±0.012 | CONFIRMED | Sec. 0.2.3 input table (Table 0.2.3): "0.709±0.012±0.015", "0.299±0.008±0.013", "−0.008±0.006±0.012" | — |
| 2005.03799 | CMS (e+jets) inputs: 0.705±0.013±0.037; 0.304±0.009±0.020; −0.009±0.005±0.021 | CONFIRMED | Sec. 0.2.3 input table, same rows | — |
| 2005.03799 | CMS (μ+jets) inputs: 0.685±0.013±0.024; 0.328±0.009±0.014; −0.013±0.005±0.017 | CONFIRMED | Sec. 0.2.3 input table | — |
| 2005.03799 | CMS (single top) inputs: 0.720±0.039±0.037; 0.298±0.028±0.032; −0.018±0.019±0.011 | CONFIRMED | Sec. 0.2.3 input table | — |
| 2005.03799 | Combined F0 = 0.693 ± 0.009 (stat+bkg) ± 0.011 (syst); FL = 0.315 ± 0.006 ± 0.009 | CONFIRMED | Sec. 0.5: "0.693±0.009 (stat+bkg)±0.011 (syst)", "0.315±0.006 (stat+bkg)±0.009 (syst)" | — |
| 2005.03799 | F0–FL total correlation −0.85 | CONFIRMED | Sec. 0.5: "with a total correlation of −0.85"; Table 0.5 caption "ρ=−0.85" | — |
| 2005.03799 | FR = −0.008 ± 0.005 (stat+bkg) ± 0.006 (syst), from unitarity | CONFIRMED | Sec. 0.5: "FR=−0.008 ±0.005(stat+bkg)±0.006(syst)" | — |
| 2005.03799 | FR < 0.007 at 95% CL, Feldman–Cousins with FR ≥ 0 | CONFIRMED | Sec. 0.5: "an upper limit of FR<0.007 at 95% confidence level (CL) is set. The limit is set using the Feldman–Cousins method ... FR≥0" | — |
| 2005.03799 | Relative uncertainty F0 2.0%, FL 3.5% | CONFIRMED | Sec. 0.5: "The relative uncertainty on F0 and FL is 2.0 and 3.5%, respectively" | — |
| 2005.03799 | Precision improvement 25% (F0), 29% (FL) | CONFIRMED | Sec. 0.5: "Improvements of 25 and 29% relative to the most precise single measurement" | — |
| 2005.03799 | χ² = 4.3, probability 64% | CONFIRMED | Sec. 0.5: "The χ2 and upper tail probability of the combination are 4.3 and 64% respectively" | — |
| 2005.03799 | Stability, ρ in [0.0, 0.6]: F0 0.693→0.687, FL 0.314→0.319 | CONFIRMED | Sec. 0.5.1: "In the interval between 0.0 and 0.6, ... F0 going from 0.693 to 0.687, and FL from 0.314 to 0.319" | — |
| 2005.03799 | Stability at ρ = 0.7: F0 = 0.684 ± 0.014 | CONFIRMED | Sec. 0.5.1: "At 0.7, the combination yields F0=0.684±0.014". The same sentence gives FL = 0.321 ± 0.010 and fit probability 28%; see Omissions | Add FL and the 28% probability to the row (see Omissions) |
| 2005.03799 | Table 0.5 breakdown (stat+bkg 0.009/0.006; sample size 0.005/0.003; JES 0.004/0.002; JER 0.004/0.002; JVF 0.001/0.001; jet reco <0.001; lepton 0.002/0.001; b-tag 0.001/0.001; pileup <0.001; top mass 0.003/0.004; sim model 0.006/0.005; radiation 0.005/0.004; top pT 0.001/0.002; PDF 0.001/0.001; single top 0.001/<0.001; total 0.014/0.011) | CONFIRMED | Sec. 0.5 Table 0.5, all 16 rows match | — |
| 2005.03799 | Dominant uncertainties: stat+bkg, then radiation and scales, sample size, simulation model choice | CONFIRMED | Sec. 0.5: "The dominant uncertainties are those arising from the statistical uncertainty on data and background estimation (stat+bkg), followed by the uncertainties in the radiation and scales modelling, the limited size of the simulated samples, and simulation model choice." | — |
| 2005.03799 | ATLAS selection: exactly one e/μ, ≥4 jets, ≥2 b-tags | CONFIRMED | Sec. 0.2.1: "exactly one reconstructed electron or muon and at least four jets, of which at least two were tagged as b jets" | — |
| 2005.03799 | CMS e/μ+jets selection: one lepton, ≥4 jets, ≥2 b-tags | CONFIRMED | Sec. 0.2.2: "one lepton and four or more jets, of which at least two were tagged as b jets" | — |
| 2005.03799 | CMS single top selection: one e/μ, exactly two jets, one b-tag | CONFIRMED | Sec. 0.2.2: "exactly one electron or muon, and exactly two jets, one of which was tagged as a b jet" | — |
| 2005.03799 | Jet radius R = 0.4 (ATLAS, calorimeter) and 0.5 (CMS, particle-flow) | CONFIRMED | Sec. 0.3.2: "radius parameter R of 0.4 and 0.5 for the ATLAS and CMS experiments"; "built from energy deposits in the calorimeter" / "particle-flow" | — |
| 2005.03799 | Eq. (1) and unitarity F0+FL+FR=1 | CONFIRMED | Sec. 0.1 Eq. (1) matches; "F0+FL+FR=1" stated | — |
| 2005.03799 | θ* frame not named | CONFIRMED | Sec. 0.1 defines θ* "both in the rest frame of the W boson"; no "helicity" or "Collins" in fulltext.txt | — |
| 2005.03799 | Journal ref JHEP 08 (2020) 051; DOI 10.1007/JHEP08(2020)051 | CONFIRMED | `inspire.json`: "journal_title":"JHEP", "journal_volume":"08", "artid":"051", year 2020; DOI "10.1007/JHEP08(2020)051" | — |
| 2005.03799 | 8 TeV; 20.2 fb⁻¹ (ATLAS), 19.7 fb⁻¹ (CMS) | CONFIRMED | Sec. 0.2: "integrated luminosities of 20.2 and 19.7 fb-1 for the ATLAS and CMS experiments" | — |
| 2005.03799 | HEPData: none | CONFIRMED | `hepdata/NONE` = "no HEPData record" | — |
| 2005.03799 | Caveat: "NNLO QCD predictions are shown in Fig. 2 (Sec. 0.5) ...; their central values are figure-only, not tabulated, and are not extracted here" | MISMATCH | The central values are in the text, Sec. 0.1: "Theoretical calculations at next-to-next-to-leading order (NNLO) ... predict the fractions to be F0=0.687±0.005, FL=0.311±0.005, and FR=0.0017±0.0001 [1], assuming a top quark mass of 172.8±1.3 GeV." | Replace with: NNLO values F0 0.687±0.005, FL 0.311±0.005, FR 0.0017±0.0001 for mtop = 172.8±1.3 GeV, Sec. 0.1 (text, not figure-only); Fig. 2 shows them graphically |
| 2005.03799 | Open issue: "The NNLO prediction values are figure-only (Fig. 2); not extracted." | MISMATCH | Same quote as above, Sec. 0.1 | Delete the open issue; the values are in Sec. 0.1 |
| 2005.03799 | ATLAS top-mass uncertainty changed from ±0.7 to ±1.0 GeV for the combination | CONFIRMED | Sec. 0.3 modifications list: "increased from a variation of ±0.7 GeV to ±1.0 GeV" | — |
| 2005.03799 | CMS first uncertainty statistical; second total systematic incl. background; ATLAS first = stat+bkg | CONFIRMED | Sec. 0.2.3: "For CMS measurements, the first uncertainty is statistical, while the second is the total systematic uncertainty, including that on background determination." | — |
| 2005.03799 | FR allowed to be negative | CONFIRMED | Sec. 0.5: "The combined FR value is negative, as this is not explicitly forbidden in the combination" | — |
| 2005.03799 | ATLAS has the highest impact on F0; CMS (μ+jets) dominates FL | CONFIRMED | Sec. 0.5: "The measurement with the highest impact in the determination of F0 is ATLAS, while CMS (μμ+jets) dominates the combined FL determination" | — |
| 2005.03799 | No pT-binned fractions | CONFIRMED | Inclusive results only throughout; no pT-binned fraction table or text found in fulltext.txt | — |
| 2005.03799 | CMS fit uses reconstructed cos θ* (Eq. (3)) | CONFIRMED | Eq. (3) text: "the number of observed events in each bin k of the reconstructed cos θ* distribution" | — |
| 2005.03799 | Table numbering: input table "Table 0.2.3", combination breakdown "Table 0.5" | CONFIRMED | Sec. 0.2.3 text: "summarized in Table 0.2.3"; Sec. 0.5: "presented in Table 0.5" | — |
| 1410.1154 | F_L muon 0.316 (stat 0.033, sys 0.03) | CONFIRMED | HEPData Table_1.json group 0 "0.316", errors stat 0.033 / sys 0.03 (header order FL, F0, FR); PDF p.11: "FL = 0.316 ± 0.033 (stat) ± 0.030 (syst)" | — |
| 1410.1154 | F_0 muon 0.715 (0.045 / 0.041) | CONFIRMED | Table_1.json group 1; PDF: "F0 = 0.715 ± 0.045 (stat) ± 0.041 (syst)" | — |
| 1410.1154 | F_R muon −0.031 (0.022 / 0.022) | CONFIRMED | Table_1.json group 2; PDF: "FR = −0.031 ± 0.022 (stat) ± 0.022 (syst)" | — |
| 1410.1154 | F_L electron 0.272 (0.057 / 0.036) | CONFIRMED | Table_2.json group 0; PDF: "FL = 0.272 ± 0.057 (stat) ± 0.036 (syst)" | — |
| 1410.1154 | F_0 electron 0.753 (0.087 / 0.04) | CONFIRMED | Table_2.json group 1; PDF: "F0 = 0.753 ± 0.087 (stat) ± 0.040 (syst)" | — |
| 1410.1154 | F_R electron −0.025 (0.042 / 0.025) | CONFIRMED | Table_2.json group 2; PDF: "FR = −0.025 ± 0.042 (stat) ± 0.025 (syst)" | — |
| 1410.1154 | Combined F_L 0.298 (0.028 / 0.032) | CONFIRMED | Table_3.json group 0; PDF p.12: "FL = 0.298 ± 0.028 (stat) ± 0.032 (syst)" (also abstract) | — |
| 1410.1154 | Combined F_0 0.72 (0.039 / 0.037) | CONFIRMED | Table_3.json group 1 "0.72"; abstract "F0 = 0.720 ± 0.039 (stat) ± 0.037 (syst)" | — |
| 1410.1154 | Combined F_R −0.018 (0.019 / 0.011) | CONFIRMED | Table_3.json group 2; abstract "FR = −0.018 ± 0.019 (stat) ± 0.011 (syst)" | — |
| 1410.1154 | Stat correlation F_L–F_0 ≈ −0.90 (muon and electron) | CONFIRMED | Table_1/2 description: "The statistical correlation between the fit parameters is about -0.90."; PDF: "about −0.90 in both channels" | — |
| 1410.1154 | Total correlation −0.80 (combined) | CONFIRMED | Table_3 description: "The total correlation between the fit parameters is about -0.80"; PDF p.12: "with a total correlation of −0.80" | — |
| 1410.1154 | SM reference FL 0.311±0.005, F0 0.687±0.005, FR 0.0017±0.0001 (mb 4.8, mt 172.8±1.3) | CONFIRMED | PDF p.3: "FL = 0.311 ± 0.005, F0 = 0.687 ± 0.005, and FR = 0.0017 ± 0.0001 [10] for a bottom quark mass mb = 4.8 GeV and a top quark mass mt = 172.8 ± 1.3 GeV" (page label: see WRONG_LOCATION row) | — |
| 1410.1154 | Page labels for the cited values: "PDF Sec. 8 (p.10)" (muon/electron), "(p.11)" (combined), "PDF p.2" (SM reference), "Table 2 ... p.10" | WRONG_LOCATION | Using the PDF page index (`pdftotext -f N`): muon and electron results and Table 2 are on PDF p.11; combined results on p.12; SM reference on p.3. The claim's labels are each one less | Use PDF page indices: muon/electron and Table 2 p.11; combined p.12; SM reference p.3 (or state explicitly if printed JHEP page numbers are meant) |
| 1410.1154 | Table 2 combined column: Experimental 0.010/0.010; Modeling 0.025/0.020; Normalization 0.011/0.012; SM W helicities 0.007/0.004; MC sample size 0.020/0.012; tWb 0.011/0.014; Total 0.037/0.032 | CONFIRMED | PDF p.11 Table 2, last column pair ΔF0 ΔFL; values match | — |
| 1410.1154 | Table 2 per-channel totals: muon ΔF0 0.041, ΔFL 0.030; electron ΔF0 0.040, ΔFL 0.036 | CONFIRMED | PDF Table 2 "Total 0.041 0.030 0.040 0.036" | — |
| 1410.1154 | Column order within channel blocks is ΔF0 then ΔFL | CONFIRMED | Table 2 header: "∆F0 ∆FL" per block | — |
| 1410.1154 | Paper does not rank systematics in prose | CONFIRMED | No ranking sentence in Sec. 7 text | — |
| 1410.1154 | Group contents: m_t 172.5 ± 0.7 GeV; luminosity 2.6%; QCD multijet 50% (μ) / 100% (e); EW backgrounds ~17% | CONFIRMED | PDF: "mt = 172.5 ± 0.7 GeV"; "varied by 2.6%"; "a 50% (100%) uncertainty for the muon (electron)"; "an uncertainty of about 17%" | — |
| 1410.1154 | Eq. (1) ρ(cos θ*) = (3/8)(1−cos)²FL + (3/4)sin²θ* F0 + (3/8)(1+cos)²FR; F_i = Γ_i/Γ | CONFIRMED | PDF Eq. (1) and Sec. 1 text, "Fi = Γi / Γ" | — |
| 1410.1154 | θ* definition: W momentum in top rest frame vs down-type fermion in W rest frame | CONFIRMED | PDF Sec. 1: "the angle between the W boson momentum in the top quark rest frame and the momentum of the down-type decay fermion in the rest frame of the W boson" | — |
| 1410.1154 | Frame: "The paper does not name this frame (helicity, Collins–Soper, other): 'not stated'" | MISMATCH | PDF Sec. 1: "The helicity angle θ`∗ is defined as the angle between the W boson momentum in the top quark rest frame and ..." (paper names the angle "helicity angle"; it does not name a frame) | Record that the paper calls θ* the "helicity angle" (Sec. 1); the frame is defined by the stated momenta, no frame name is given |
| 1410.1154 | Muon trigger pT>24 (|η|<2.1); electron trigger pT>27; muon pT>26, |η|<2.1, I_rel<0.12; electron pT>30, |η|<2.5, I<0.1; extra leptons vetoed | CONFIRMED | PDF Sec. 3: "isolated muon (electron) with pT > 24 (27) GeV ... |η| < 2.1"; "pT > 26 GeV"; "less than 0.12"; "pT > 30 GeV and |η| < 2.5 ... less than 0.1"; "Events with additional leptons" | — |
| 1410.1154 | Jets anti-kT R=0.5; exactly 2 jets pT>40, |η|<4.7, ΔR(jet,lepton)>0.3; exactly 1 b-tag | CONFIRMED | PDF Sec. 3: "anti-kT algorithm ... distance parameter of 0.5"; "exactly two jets with |η| < 4.7 and pT > 40 GeV ... ∆R > 0.3"; "exactly one of the selected jets is identified as likely originating from ... b" | — |
| 1410.1154 | m_T(W) > 50 GeV; complex pz,ν solutions discarded (40% single top, ~50% other); mW = 80.4 GeV constraint | CONFIRMED | PDF: "T > 50 GeV"; Table 1 caption "This rejects 40% of the single top quark events and about 50% of"; "mW = 80.4 GeV" | — |
| 1410.1154 | Sample includes tt̄ with one leptonic top decay | CONFIRMED | PDF Sec. 3: "The tt events with the µ(e)+τ decay mode ... contribute about 16%"; "The tt events in the current sample are rejected by the standard lepton+jets tt selection" | — |
| 1410.1154 | Reconstructed-level fit with transfer matrix (Eq. 7); no particle-level unfolding | CONFIRMED | PDF Eq. (7): "ρ(cos θ`∗, rec |~F ) ∝ ∑ w(...) R(...)" | — |
| 1410.1154 | W+jets normalization β_jets floated | CONFIRMED | PDF: "The ~F components, as well as β W jets , are treated as free parameters in the likelihood fit" | — |
| 1410.1154 | Combined F_R outside muon/electron interval: consequence of ΣF=1 and channel weighting | CONFIRMED | PDF p.12: "a consequence of the ∑ Fi = 1 constraint together with the different contributions of the two channels in the combination" | — |
| 1410.1154 | Citation: arXiv v2 14 Jan 2015; JHEP 01 (2015) 053; INSPIRE 1320561; HEPData 66567 | CONFIRMED | PDF header "arXiv:1410.1154v2 [hep-ex] 14 Jan 2015"; "doi:10.1007/JHEP01(2015)053"; `hepdata/record.json`: "inspire_id":1320561, "id":66567 | — |
| 1410.1154 | Point measurements, one x-value each, no pT or mass binning | CONFIRMED | Table_1/2/3.json: `"x": [{"value": "Measurement"}]`, x_count 1 | — |
| 1410.1154 | Anomalous couplings g_L = −0.017, g_R = −0.008 (out of scope, not extracted) | CONFIRMED | PDF: "are −0.017 and −0.008, respectively" (not extracted into the note; out of scope) | — |
| 1202.5272 | f0 (2D) = 0.722 ± 0.081 [± 0.062 stat ± 0.052 syst] | CONFIRMED | Abstract: "f0=0.722±0.081 [± 0.062 (stat.)±0.052 (syst.)]"; Eq. (3)/(5) | — |
| 1202.5272 | f+ (2D) = −0.033 ± 0.046 [± 0.034 ± 0.031] | CONFIRMED | Abstract; Eq. (3) "f+ = −0.033 ± 0.046 [± 0.034 (stat.) ± 0.031 (syst.)]" | — |
| 1202.5272 | f0 (1D, f+ fixed) = 0.682 ± 0.057 [± 0.035 ± 0.046] | CONFIRMED | Abstract; Eq. (4): "f0 = 0.682 ± 0.057 [± 0.035 (stat.) ± 0.046 (syst.)]" | — |
| 1202.5272 | f+ (1D, f0 fixed) = −0.015 ± 0.035 [± 0.018 ± 0.030] | CONFIRMED | Abstract and Eq. (4): "f+ = −0.015 ± 0.035 [± 0.018 (stat.) ± 0.030 (syst.)]" | — |
| 1202.5272 | f+ 1D systematic ±0.031 in Eq. (6)/Summary | CONFIRMED | Sec. VI Eq. (6): "f+ = −0.015 ± 0.035 [± 0.018 (stat.) ± 0.031 (syst.)]" (PDF text) | — |
| 1202.5272 | CDF lepton+jets inputs: f0 0.903 ± 0.123 [0.106 ± 0.063]; f+ −0.195 ± 0.090 [0.067 ± 0.060]; f0 0.674 ± 0.081 [0.069 ± 0.042]; f+ −0.044 ± 0.053 [0.019 ± 0.050] | CONFIRMED | Table I (PDF p. TABLE I): values as in claim | — |
| 1202.5272 | CDF dilepton inputs: f0 0.702 ± 0.186 [0.175 ± 0.062]; f+ −0.085 ± 0.096 [0.089 ± 0.035]; f0 0.556 ± 0.106 [0.088 ± 0.060]; f+ −0.089 ± 0.052 [0.041 ± 0.032] | CONFIRMED | Table I | — |
| 1202.5272 | D0 inputs: f0 0.669 ± 0.102 [0.078 ± 0.065]; f+ 0.023 ± 0.053 [0.041 ± 0.034]; f0 0.708 ± 0.065 [0.044 ± 0.048]; f+ 0.010 ± 0.037 [0.022 ± 0.030] | CONFIRMED | Table I | — |
| 1202.5272 | 2D χ² = 8.86 for 4 dof, p = 6%; f0–f+ correlation −0.86 | CONFIRMED | Sec. V: "a χ2 value of 8.86 for four degrees of freedom, corresponding to a p-value of 6%"; "correlation coefficient of −0.86" | — |
| 1202.5272 | 1D χ²: f0 2.12 (2 dof, p 35%); f+ 4.44 (2 dof, p 11%) | CONFIRMED | Sec. V: "The combination for f0 (f+) has a χ2 of 2.12 (4.44) for two degrees of freedom, corresponding to a p-value of 35% (11%)" | — |
| 1202.5272 | Table VIII 2D: f0 SIG 0.038, BGD 0.028, DET 0.016, MTD 0.014, JES 0.007, MTOP 0.007, MHI 0.001; f+ SIG 0.022, BGD 0.013, JES 0.012, MTOP 0.010, MTD 0.008, DET 0.003, MHI 0.0004 | CONFIRMED | Table VIII (PDF text) | — |
| 1202.5272 | Table VIII 1D: f0 SIG 0.036, JES 0.018, BGD 0.012, MTOP 0.012, DET 0.011, MTD 0.007, MHI 0.002; f+ SIG 0.021, JES 0.014, MTOP 0.010, BGD 0.009, DET 0.007, MTD 0.006, MHI 0.002 | CONFIRMED | Table VIII (PDF text) | — |
| 1202.5272 | Table IX weights: D0 f+ input f0 weight −22.0%; CDF l+jets f0 input f+ weight −15.4% | CONFIRMED | Table IX: f+,D0 row "−22.0 / 75.9"; f0,CDF(ℓ+j) row "44.4 / −15.4" | — |
| 1202.5272 | Frame: θ* is the "helicity angle", defined in the W rest frame between the direction opposite to the top quark and the down-type fermion; frame name not stated | CONFIRMED | Sec. II: "the distribution of the helicity angle θ⋆ ... θ⋆ is the angle in the WW boson rest frame between the direction opposite to the top quark and the direction of the down-type fermion" | — |
| 1202.5272 | Eq. (1): ω(cos θ*) ∝ 2(1−cos²θ*)f0 + (1−cosθ*)²f− + (1+cosθ*)²f+ | CONFIRMED | Sec. II Eq. (1), layout text | — |
| 1202.5272 | f0, f−, f+ are fractions of W+ from top decay; "hermitian conjugation will be assumed throughout the paper" | CONFIRMED | Intro: "we denote the fractions of W+ bosons produced in these states as f0 ... f− ... and f+ ... (hermitian conjugation will be assumed throughout the paper)" | — |
| 1202.5272 | m_t shift: CDF shifted to 172.5 GeV; D0 assumes 172.5 GeV; 1.4 GeV uncertainty | CONFIRMED | Sec. II: "the CDF helicity fractions are shifted to mt of 172.5 GeV/c2"; "D0 assumes a value of mt=172.5 GeV/c2 ... This uncertainty corresponds to a 1.4 GeV/c2 uncertainty on mt" | — |
| 1202.5272 | SM reference f0 = 0.688 ± 0.004, f− = 0.310 ± 0.004, f+ = 0.0017 ± 0.0001 (Ref. [4]) | CONFIRMED | Intro: "the expected SM values are f0=0.688±0.004, f−=0.310±0.004, and f+=0.0017±0.0001 [4]" (omission: see Omissions) | — |
| 1202.5272 | Integrated luminosities: CDF l+jets 2.7 fb⁻¹, CDF dilepton 5.1 fb⁻¹, D0 5.4 fb⁻¹ | CONFIRMED | Intro/Sec. II: "2.7 fb-1 of CDF data", "5.1 fb-1 of CDF data in the dilepton", "5.4 fb-1 of D0 data" | — |
| 1202.5272 | √s not stated | CONFIRMED | No "TeV" energy value in the paper; only "Tevatron proton-antiproton Collider" | — |
| 1202.5272 | Open issue: f+ 1D systematic ±0.030 (Abstract, Eq. 4) vs ±0.031 (Eq. 6, Summary) | CONFIRMED | Abstract "[± 0.018 (stat.) ± 0.030 (syst.)]"; Eq. (6) "[± 0.018 (stat.) ± 0.031 (syst.)]" | — |
| 1202.5272 | "In some cases, the weights have negative values"; "The SM values ... lie within the 68% C.L. contour" | CONFIRMED | Sec. V: "In some cases, the weights have negative values"; "The SM values for the helicity fractions lie within the 68% C.L. contour of probability." | — |
| 1202.5272 | f_L / A_0 / ρ00 not used | CONFIRMED | No A0, A_0 or ρ00 symbols in the PDF text (grep = 0) | — |
| 1202.5272 | Journal ref PRD 85, 071106 (2012); INSPIRE recid 1090176 | CONFIRMED | `inspire.json`: "journal_title":"Phys.Rev.D", "journal_volume":"85", "artid":"071106", year 2012; "control_number":1090176; DOI 10.1103/PhysRevD.85.071106 | — |
| 1202.5272 | HEPData: none | CONFIRMED | `hepdata/NONE` = "no HEPData record" | — |

## Verdict counts (per table row)

| claim file | rows | CONFIRMED | MISMATCH | WRONG_LOCATION | MISLABELED | UNSUPPORTED | UNVERIFIABLE |
|---|---|---|---|---|---|---|---|
| 2209.14903 | 23 | 23 | 0 | 0 | 0 | 0 | 0 |
| 2005.03799 | 33 | 31 | 2 | 0 | 0 | 0 | 0 |
| 1410.1154 | 31 | 29 | 1 | 1 | 0 | 0 | 0 |
| 1202.5272 | 25 | 25 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **112** | **108** | **3** | **1** | **0** | **0** | **0** |

## Omissions (scope Q2, Q3 as relevant; Q1 not applicable to these four papers)

- 2005.03799, Sec. 0.5.1 (stability at ρ = 0.7): the paper gives FL = 0.321 ± 0.010 alongside F0 = 0.684 ± 0.014, and states the fit probability drops to 28% and that this is "the maximum variation observed in all tests performed in this study". The note gives only F0 and omits the FL value and the probability caveat.
- 1202.5272, Intro and ref. [4]: the SM reference values assume m_t = 173.3 ± 1.1 GeV and M_W = 80.399 ± 0.023 GeV, and the paper says they were "obtained via private communication with the authors" (ref. [4]). The note omits the assumptions and the provenance.
- 1410.1154, Sec. 1: the paper calls θ* the "helicity angle" (already the MISMATCH row above).
- Scope note for Q3: all four papers measure only diagonal W spin-density elements (f0, fL, fR or f0, f+ with unitarity). None measures off-diagonal terms or angular coefficients A0–A7, and none is a theory map. No Q3 item beyond these diagonal fractions is present in these sources.
- Scope note for Q1: none of the four is a direct search for a hadronically decaying resonance, so Q1 has no content here.
- Wording note (not a verdict): the 2209.14903 topology bullet calls θ* the "W helicity angle", while its own frame bullet says the paper does not name the frame. The angle is the standard helicity angle, but the paper does not use that name; the claim should match its own frame bullet.

## Non-CONFIRMED rows, with fixes

1. 2005.03799, Caveat "NNLO central values figure-only" — MISMATCH. The values are in the text, Sec. 0.1: "predict the fractions to be F0=0.687±0.005, FL=0.311±0.005, and FR=0.0017±0.0001 [1], assuming a top quark mass of 172.8±1.3 GeV." Fix: state the values and location (Sec. 0.1); Fig. 2 is the graphical display only.
2. 2005.03799, Open issue "NNLO prediction values are figure-only" — MISMATCH. Same source. Fix: delete.
3. 1410.1154, frame row — MISMATCH. Sec. 1 says "The helicity angle θ`∗ is defined as the angle between the W boson momentum in the top quark rest frame and the momentum of the down-type decay fermion in the rest frame of the W boson." Fix: record that the paper calls θ* the "helicity angle" and gives no frame name.
4. 1410.1154, page labels — WRONG_LOCATION. Muon/electron results and Table 2 are on PDF p.11; combined results p.12; SM reference p.3. Fix: correct the page labels, or say which pagination is used.
