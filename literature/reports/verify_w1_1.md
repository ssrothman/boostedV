# Verification report: w1_1 (five claim files)

Verdict summary: 96 rows checked. 90 CONFIRMED, 3 MISLABELED, 2 WRONG_LOCATION, 1 MISMATCH, 0 UNSUPPORTED, 0 UNVERIFIABLE.

Source locations: `.cache/<id>/text.txt` (1710, 2408), `paper.txt` (1306), `paper_math.txt` (1905, 2605, with `arxiv.html` alttext where math was garbled). Line numbers below refer to those files. HEPData values for 2408 were read from `.cache/2408.00049/hd_gq_limit.json` and `hd_xsec_limit.json`. Live HEPData was not contacted.

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| 1710.00159 | Summary: g_q' > 0.25 excluded, 50–300 GeV, 95% CL | CONFIRMED | "Coupling values of gq′>0.25 are excluded over the \PZpr mass range from 50 to 300\GeV" (text.txt:634–635, Sec 0.7). Obs/exp not labelled in this sentence. | none |
| 1710.00159 | Fig. 7 right, mass-dependent g_q' limit (figure-only) | CONFIRMED | "Coupling values above the solid curves are excluded." (text.txt:591); Fig. 7 caption "observed limits (solid)" (text.txt:598) | none |
| 1710.00159 | Fig. 7 left, cross-section limit (figure-only) | CONFIRMED | Fig. 7 caption (text.txt:596–598) | none |
| 1710.00159 | Mediator mass excluded 50–300 GeV, g_q=0.25, g_DM=1.0 | CONFIRMED | "The excluded range of mediator mass (red) is between 50 and 300\GeV." (text.txt:605); g_q=0.25, g_DM=1 (text.txt:603, 620) | none |
| 1710.00159 | 240 GeV upper bound when m_Med > 2 m_DM | CONFIRMED | "The upper bound decreases to 240\GeVwhen mMed>2mDM" (text.txt:606) | none |
| 1710.00159 | Local 2.9 sigma, global 2.2 sigma at 115 GeV (not a limit) | CONFIRMED | "corresponds to 2.9 standard deviations ... at a \PZprboson mass of 115\GeV" and "global ... approximately 2.2 standard deviations" (text.txt:584–586) | none |
| 1710.00159 | Coupling 0.17 / 0.08 "close to our current sensitivity" (non-limit) | CONFIRMED | text.txt:579–581 | none |
| 1710.00159 | Selection, trigger, lepton veto, AK8 R=0.8, zcut=0.1, beta=0, rho range, N21,DDT, five pT bins (Sec 0.3.2, 0.6) | CONFIRMED | AK8 pT>500, |eta|<2.5 (text.txt:210); leptons pT>10, |eta|<2.5/2.4/2.3 (216–217); zcut=0.1, beta=0 (225); −5.5<rho<−2.0 (261); five pT bins 500–1000 (555); X(5%) quantile (Fig. 2 caption). Section numbers 0.3.2, 0.6 match the TOC. | none |
| 1710.00159 | Fit and limit method: binned ML, CLs, profile LR, asymptotic, log-normal nuisances | CONFIRMED | text.txt:573–577, 593 | none |
| 1710.00159 | Conversion g_q' = g_B/6 per Ref. [37] (1306.2629) | CONFIRMED | Paper: "related to the Z′ coupling convention of Ref. [37] by gq′=gB/6" (text.txt:588–590). Checked against the cited conversion source 1306.2629 Eq. (6): "(g_B/6) Z′_Bμ q̄γ^μ q", generator normalised to 1/2 (paper.txt:357–363). Consistent. | none |
| 1710.00159 | Z' systematics table, Z' column: N21 9%, JER 10%, NLO QCD 10%, lumi 2.5%, trigger 2%, JMS 0.5%, JMS pT-dep 0.5–2%, lepton veto 0.5%, multijet 1–3% | CONFIRMED | Table rows in text.txt:475–530; column order Multijet / Z' / W/Z / ttbar | none |
| 1710.00159 | "Top normalization 10% and N21,DDT mistag 2%" | MISLABELED | Table row is "Top quark mistag rate", 2% in the ttbar column only (text.txt ~ line 495–500, Table in Sec 0.5). The paper does not call it an N21,DDT mistag. | Replace "N21,DDT mistag 2%" with "top quark mistag rate 2% (ttbar column)". |
| 1710.00159 | Scale factors N21 0.88±0.10, mass scale 1.10±0.05, mass resolution 1.14±0.06 | CONFIRMED | text.txt:444–447 | none |
| 1710.00159 | "first direct limits ... 50 to 100 GeV" (paper's own claim) | CONFIRMED | text.txt:636–638, Sec 0.7 | none |
| 1710.00159 | HEPData: none | CONFIRMED | Cache `hepdata/` holds a 404 page; `hepdata_search.json` total = 0. Live HEPData not re-queried (job rule). | none |
| 1710.00159 | Ref. [37] = Dobrescu & Yu, arXiv:1306.2629 | CONFIRMED | Reference list text.txt:851–853 (PRD 88 035021, "Coupling-mass mapping of dijet peak searches") | none |
| 1710.00159 | Topology: Z' → qq̄ merged AK8 jet recoiling against high-pT ISR jet; 50–300 GeV | CONFIRMED | "recoils against another high-pT ISR jet" (text.txt:204); "satisfy ... 50 to 300 GeV" (text.txt:552) | none |
| 1710.00159 | Identifiers: CMS-EXO-17-001, CERN-EP-2017-235, JHEP 01 (2018) 097, arXiv v2 Jan 2018 | CONFIRMED | "arXiv:1710.00159v2 ... 30 Jan 2018"; EXO-17-001 (text.txt header); CERN-EP-2017-235 and JHEP 01 (2018) 097 in inspire.json | none |
| 1306.2629 | Z'_B: g_B <~ 0.6 unconstrained | CONFIRMED | "unconstrained for a gauge coupling gB≲0.6" (paper.txt:808–809, Sec III.2) | none |
| 1306.2629 | Z'_B: g_B up to 0.9 over sub-TeV region | CONFIRMED | "for the entire sub-TeV region ... gB couplings as large as 0.9" (paper.txt:810–811) | none |
| 1306.2629 | Z'_B: locally ~1.5 | CONFIRMED | "locally, gB couplings can reach ≈1.5" (paper.txt:811–812) | none |
| 1306.2629 | Z'_B: mass reach ~2.8 TeV for "that large coupling" | CONFIRMED | "For that large coupling, the current mass reach is around 2.8 TeV" (paper.txt:820–821), after "plot is not extended above gB=2.5" (819). The antecedent g_B≈2.5 is the most natural reading. | none |
| 1306.2629 | Coloron: experimental tan θ limit dips below 0.15 only at 350–700 GeV and 0.9–1.6 TeV | CONFIRMED | paper.txt:846–847 | none |
| 1306.2629 | Coloron perturbative range 0.15 <~ tan θ <~ 6.7 (ref [44]) | CONFIRMED | paper.txt:411–412 | none |
| 1306.2629 | Coloron width 15% corresponds to tan θ ≈ 1.3 | CONFIRMED | paper.txt:861 | none |
| 1306.2629 | Z'_B NLO effect O(10%) | CONFIRMED | paper.txt:801–802 | none |
| 1306.2629 | Table 2, CMS [23]: 0.13 fb⁻¹, 0.6–1 TeV | CONFIRMED | Table 2 row "[23] 0.13 0.6 – 1" (paper.txt ~ 655–668). Operative 260–900 GeV window in text (paper.txt:733–735). Both are in the paper. | none |
| 1306.2629 | Table 2, CDF Run II [10]: 1.1 fb⁻¹, 0.26–1.4 TeV | CONFIRMED | Table 2 row (paper.txt ~ 655–668) | none |
| 1306.2629 | Table 2, CMS [25]: 20 fb⁻¹, 1.2–5.3 TeV | CONFIRMED | Table 2 row "20 1.2 – 5.3". Text says "CMS 19.6 fb-1" (paper.txt:757–758); the claim's 20 is the table value. | none |
| 1306.2629 | Table 2, ATLAS [16]: 1.0 fb⁻¹, 0.9–4 TeV | CONFIRMED | Table 2 row "1.0 0.9 – 4" | none |
| 1306.2629 | Tevatron: CDF Run I [9] and D0 [11] (≈110 pb⁻¹) for 200–260 GeV | MISLABELED | "The CDF [9] and D0 [11] searches ... compete for the best limit ... We choose to extract a limit from the CDF analysis" (paper.txt:722–725). Only CDF is used. | State that CDF [9] is adopted; D0 [11] is not used. |
| 1306.2629 | Fig. 1 and Fig. 2 caption confidence level 95% CL; figure-only values | CONFIRMED | "Values of gB above each line are excluded at the 95% C.L." (Fig. 1 caption); "Values of tan θ above each limit are excluded at the 95% C.L." (Fig. 2 caption) | none |
| 1306.2629 | Systematics/inputs: dijet resolution ~5–10%; coloron NLO −30%/+20%; Eq. (6) and Eq. (9) | CONFIRMED | "∼5−10%, depending on mass [2] as well as experiment" (paper.txt:466–468); "roughly −30% and +20%" (paper.txt:839); Eq. (6) (paper.txt:357–363); Eq. (9) (paper.txt:401–403) | none |
| 1306.2629 | ATLAS Gaussian-core fit ranges (alpha 0.05–3.5, n 0.5–5, x̄ 70–105%, sigma 0.5–30%) | CONFIRMED | Appendix text (paper.txt ~ 940–950) | none |
| 1306.2629 | MC setup: MadGraph 5 v1.5.7, CTEQ6L1, Pythia 6.4.20, PGS v4; LO only; "somewhat model dependent" (Sec IV) | CONFIRMED | paper.txt:674–677 (tools); paper.txt:881 ("somewhat model dependent") | none |
| 1306.2629 | Wide-resonance line: limits "not reliable if set by narrow resonance searches" | CONFIRMED | paper.txt:865 | none |
| 1306.2629 | Erratum note: acknowledgement mentions earlier error in Eq. (3) | CONFIRMED | paper.txt:937 | none |
| 1905.10331 | Limit: g'_q > 0.3 excluded at 95% CL, entire 10–125 GeV range | CONFIRMED | "Values of $g^{\prime}_{\cPq}$ greater than 0.3 are excluded at 95% CL for the entire mass range." (paper_math.txt, Results paragraph after Table 1). The sentence does not label obs or exp. The Fig. 2 caption and text "Coupling values above the solid curves are excluded" make the solid (observed) curve the reference. | none (the claim already flags the obs/exp gap) |
| 1905.10331 | Fig. 2 curves, observed solid, expected dashed, bands (figure-only) | CONFIRMED | Fig. 2 caption (paper_math.txt) | none |
| 1905.10331 | Signal masses 10–125 GeV; simulated 10, 25, 50, 75, 100, 125; 5 GeV steps | CONFIRMED | "(10, 25, 50, 75, 100 and 125 GeV)" and "in steps of 5 GeV from 10 to 125 GeV" (paper_math.txt, signal-fit paragraph) | none |
| 1905.10331 | ttbar efficiency scale factor 0.909±0.046 (stat+sys) | CONFIRMED | "data-to-simulation efficiency scale factor is found to be $0.909\pm 0.046$ (stat+sys)" (paper_math.txt, ttbar control region paragraph) | none |
| 1905.10331 | Lumi 35.9 fb⁻¹ (2016); abstract "10 to 125 GeV" | CONFIRMED | paper_math.txt:64 (abstract) | none |
| 1905.10331 | Table 1 systematics (12 rows: 54, 45, 11, 5, 6, 6, 3, 2.5, 2, 0.7, 0.5, 0.5, polynomial 1–5) | CONFIRMED | Table 1 rows, paper_math.txt (Table 1 block) | none |
| 1905.10331 | Selection: trigger γ pT>175 |η|<3.0; offline γ pT>200 |η|<2.4; γ>14 / lepton>10 veto; AK8 pT>200; ΔR(J,γ)>2.2; AK4 pT>30 CSVv2 or pTmiss>75 discard; soft drop β=0 zcut=0.1; |η_γ|<2.1 signal region; fit up to 201 GeV; N²_DDT<0 retains 10% | CONFIRMED | paper_math.txt (selection paragraph, "The trigger strategy ..."; "Events with photon |η|<2.1 ..."; "masses up to 201 GeV"; "retain 10%" from Eq. 1 text) | none |
| 1905.10331 | Benchmark g'_q = 1/6 for signal generation; no SM Z–Z' interaction | CONFIRMED | "coupling constant to quarks set to g′q=1/6" and "The model assumes no interaction between the SM Z and the Z′" (paper_math.txt, benchmark paragraph) | none |
| 1905.10331 | CL method: modified frequentist CLs, profile LR, asymptotic | CONFIRMED | paper_math.txt, Results paragraph | none |
| 1905.10331 | "more stringent than the indirect limits ... Z and Upsilon decay widths [18]" below 50 GeV | CONFIRMED | Results paragraph (paper_math.txt); Fig. 2 caption also cites [18] | none |
| 1905.10331 | "first direct constraints ... below 50 GeV obtained at a hadron collider" | CONFIRMED | Abstract (paper_math.txt:64) | none |
| 1905.10331 | Identifiers: CMS-EXO-17-027; PRL 123 (2019) 231803; arXiv v2, 03 Dec 2019 | CONFIRMED | "EXO-17-027" (paper_math.txt); "arXiv:1905.10331v2 ... 03 Dec 2019" (line 43); PhysRevLett.123.231803 and artid 231803 (inspire.json) | none |
| 1905.10331 | "reference [28] only (Dobrescu & Yu)" for the g'_q Lagrangian and normalisation | MISLABELED | Ref. [28] is "B. A. Dobrescu and F. Yu, 'Erratum: Coupling-mass mapping of dijet peak searches', Phys. Rev. D 90 (2014) 079901" (paper_math.txt reference [28]). The erratum is to arXiv:1306.2629. The normalisation itself is in 1306.2629 Eq. (6). | Cite as "[28] erratum to Dobrescu & Yu, PRD 90 079901 (erratum to arXiv:1306.2629)". |
| 1905.10331 | Refs [16] = arXiv:1901.10917 (ATLAS), [17] = arXiv:1710.00159 (CMS) | CONFIRMED | paper_math.txt reference list [16], [17] | none |
| 1905.10331 | HEPData: none (ins1736729) | CONFIRMED | Cache `hepdata.json` / `hepdata_rec.json` are 404 pages | none |
| 1905.10331 | Anti-kT jet radii: AK4 0.4, AK8 0.8 | CONFIRMED | "a distance parameter of 0.4 and 0.8 for AK4 and AK8 jets" (paper_math.txt, reconstruction paragraph) | none |
| 2408.00049 | 52 HEPData values, g_q limit and sigma×B×A limit, 13 mass points (20–200 GeV), observed and expected | CONFIRMED | Scripted check of all 52 claim values against `hd_gq_limit.json` (26 values) and `hd_xsec_limit.json` (26 values): 0 mismatches | none |
| 2408.00049 | Observed = group 0, expected = group 1 | CONFIRMED | Caption "Observed (expected) upper exclusion limits at 95% CL" (text.txt:309); "expected ±1σ (±2σ) interval around the expected limit" (text.txt:310); HEPData header order "Observed, Expected" (hd_gq_limit.json, hd_xsec_limit.json) | none |
| 2408.00049 | σ×B×A units not stated; t6 description | CONFIRMED | No units in hd_xsec_limit.json; text.txt does not mention σ×B×A. HEPData description defines it as σ_Z′ × B(Z′→qq̄) × A. | Optionally quote the HEPData definition in the claim. |
| 2408.00049 | HEPData table locations: t5 "Figure 5", t6 "Figure 2 in the publication auxiliary material" | CONFIRMED | `location` fields in hd_gq_limit.json and hd_xsec_limit.json. Cache note: `hepdata/tables/95_CL_*.json` are "HEPData Error" HTML pages, not data. The values come from the root `hd_*.json` files. | Change cited cache path to `hd_gq_limit.json` / `hd_xsec_limit.json`. |
| 2408.00049 | Mass range 20–200 GeV cited as "(Sec. 4, Abstract)" | WRONG_LOCATION | "The mass of the hypothesised Z′ resonance ranged between 20 GeV and 200 GeV" is at text.txt:141, inside Sec 3 (Sec 4 starts at text.txt:142). Abstract at text.txt:41 is correct. | Change "Sec. 4" to "Sec. 3". Also applies to the "Fit range" row. |
| 2408.00049 | Z' width "well below the detector resolution" cited as Sec. 4 | WRONG_LOCATION | "which results in a Z′ width well below the detector resolution" at text.txt:137, Sec 3 | Change "Sec. 4" to "Sec. 3". |
| 2408.00049 | Search range 20–100 GeV in the Conclusion (Sec. 8) | CONFIRMED | text.txt:319 (Sec 8 starts text.txt:311) | none |
| 2408.00049 | "g_q couplings as small as 0.1 for m_Z′ < 100 GeV" (Sec. 7); Conclusion "down to 0.1" | CONFIRMED | text.txt:303, 324; consistent with observed g_q at 60 GeV (0.0964) and 70 GeV (0.0985) in hd_gq_limit.json | none |
| 2408.00049 | Non-resonant background is 80–90% of systematics; >90% from data/MC stats (Sec. 6) | CONFIRMED | text.txt:255, 259 | none |
| 2408.00049 | Calibration R_D2DDT = 0.971 ± 0.026 (Sec. 5) | CONFIRMED | text.txt:237 (Sec 5 spans text.txt:176–238) | none |
| 2408.00049 | Statistical uncertainties 20–50% of theory cross section (Sec. 6) | CONFIRMED | text.txt:276 | none |
| 2408.00049 | Selection: photon pT>150 (Sec 5); TAR jets R=1.0, |eta|<2, pT>150, 2m/pT<1, Δφ>π/2, ΔR≥1.2 with pTγ/pTJ>0.1 (Sec 4); ρ≤−5.4 rejected; veto; D2_DDT<0 at 13%; central |η_γ|≤1.3 is the SR | CONFIRMED | text.txt:169–173 (Sec 4), 178 (Sec 5), 180–182, 193–194, 218–222 (Sec 5 region definitions) | none |
| 2408.00049 | "Bernstein order 5" cited to Sec. 6 | CONFIRMED | Paper says "six Bernstein coefficients" (text.txt:218, Sec 5). Order 5 is equivalent. The Sec 6 citation covers only the 80–90% sentence. | Optional: cite Sec 5 for the Bernstein detail. |
| 2408.00049 | MC: MadGraph5_aMC@NLO v2.9.2 + Pythia 8.244, LO; Z' decays to qq̄ only, Z'–Z interference neglected | CONFIRMED | text.txt:137–139 (Sec 3) | none |
| 2408.00049 | Translation to other g_q via Ref. [73] (not tabulated) | CONFIRMED | "The translation of the results to other g q values is done following Ref. [73]" (text.txt:140) | none |
| 2408.00049 | Expected ±1σ/±2σ bands figure-only | CONFIRMED | text.txt:310 | none |
| 2605.28934 | Authors, arXiv:2605.28934 (v1, 27 May 2026), CERN-TH-2026-116; INSPIRE 3162400 | CONFIRMED | Author list and "arXiv:2605.28934v1 ... 27 May 2026", "Preprint: CERN-TH-2026-116" (paper_math.txt:24–34). Cache `hepdata.json` for ins3162400 is a 404 page. | none |
| 2605.28934 | Dijet channel: AK4 R=0.4, p_T>97 GeV, |η|<2.0, seven pT bins, 0.002≤x_L≤0.35 | MISMATCH | Eq. (3.6) in arxiv.html alttext: "p_{T}>97~GeV, |η|<2.1, |Δφ(j_1,j_2)|>2.0 rad". The paper_math.txt rendering "|η|2.0 rad" lost the symbols. Correct value: |η| < 2.1, plus |Δφ(j1,j2)| > 2.0 rad (Event selection, App. 3, Eq. 3.6). Seven pT bins (paper_math.txt:622) and x_L range (paper_math.txt:641) are correct. | Replace "|η|<2.0" with "|η|<2.1, |Δφ(j1,j2)|>2.0 rad". |
| 2605.28934 | Photon channel |η_γ| cut (claim left it open, "garbled") | CONFIRMED | Event selection alttext in arxiv.html: "exactly one photon with p_Tγ>200 GeV and |η_γ|<2.4 (2.1)". The meaning of the parenthetical 2.1 is not stated in that sentence. | Transcribe as "|η_γ|<2.4 (2.1)" and note the parenthetical is unexplained in the text. |
| 2605.28934 | Model Eq. (3): L_int = Σ_q g'_q q̄ Z̸' q, couplings to quarks only | CONFIRMED | paper_math.txt:148–151, "(3)" | none |
| 2605.28934 | "transverse production fixes the spinning coefficient to c^(2)=1/2 with all higher coefficients vanishing" | CONFIRMED | Verbatim, paper_math.txt:159 | none |
| 2605.28934 | Observable z_* ≡ m_X²/E²; helicity eigenstates: boost axis = spin quantisation axis | CONFIRMED | Verbatim, paper_math.txt:139 | none |
| 2605.28934 | "current bounds of order g'_q ~ O(0.1)" (no source, CL, mass) | CONFIRMED | Verbatim, paper_math.txt:161–162; no citation in that sentence | none |
| 2605.28934 | CMS expected limit (solid red) taken from [49]; recast dashed blue "slightly stronger" | CONFIRMED | paper_math.txt:191 | none |
| 2605.28934 | Inclusive EEC in jet-mass window "enhances the sensitivity" (Fig. 3 long-dashed pink) | CONFIRMED | paper_math.txt:195–196 | none |
| 2605.28934 | Fig. 4 caption: projected limits, extrapolation of CMS EEC measurement in dijet events [26] | CONFIRMED | paper_math.txt:212 | none |
| 2605.28934 | Target mass up to ~100 GeV requires pTj harder than ~250 GeV | CONFIRMED | paper_math.txt:188 | none |
| 2605.28934 | Z'γ: "we don't include any systematic uncertainty"; sensitivity "currently limited by statistics" | CONFIRMED | paper_math.txt:190 | none |
| 2605.28934 | Z'j: CMS 9 experimental and 6 theory sources; "comparable in size to the statistical uncertainties" | CONFIRMED | paper_math.txt:205–207 (quote matches) | none |
| 2605.28934 | Systematics fully correlated, Σ^ab = σ^a σ^b | CONFIRMED | paper_math.txt:206 | none |
| 2605.28934 | App. 3: nine experimental and six theory source names | CONFIRMED | Named lists at paper_math.txt:662–663 (after Eq. 3.13) | none |
| 2605.28934 | Each asymmetric uncertainty symmetrised, σ=(σ⁺+σ⁻)/2 | CONFIRMED | paper_math.txt:654 | none |
| 2605.28934 | Photon channel: one photon pT>200; AK8 R=0.8; leading jet pTj>200; EEC in 100 GeV pT bins to 600 GeV + overflow | CONFIRMED | paper_math.txt:171–189; arxiv.html alttext for R_j=0.8 | none |
| 2605.28934 | CMS alpha_s range 20 GeV/pTj ≲ x_L ≲ 0.2 vs 0.002–0.35 used; "at the cost of a less controlled theoretical description" | CONFIRMED | paper_math.txt:641 | none |
| 2605.28934 | Jet-mass window ±20% of m_Z′ | CONFIRMED | paper_math.txt:195–203 ("±20 % of a Z′ mass") | none |
| 2605.28934 | Luminosity: 36.3 fb⁻¹ baseline (Z'j); 300 fb⁻¹ and 3 ab⁻¹ projections; photon-channel luminosity not stated | CONFIRMED | 36.3 fb⁻¹ (paper_math.txt:206); 300 fb⁻¹ and 3 ab⁻¹ (paper_math.txt:661); no luminosity in the photon section | none |
| 2605.28934 | Asimov dataset, SM = data; simulation only | CONFIRMED | "we take the data to coincide with the central SM prediction (Asimov dataset)" (paper_math.txt:654) | none |
| 2605.28934 | "not directly optimized for new physics searches"; "particle level"; CMS shape cut "artificial violation of the scaling" | CONFIRMED | paper_math.txt:199, 211, 181 | none |
| 2605.28934 | References: [49] = CMS 1905.10331, [48] = CMS 1710.00159, [1] = ATLAS 2408.00049 | CONFIRMED | paper_math.txt reference list ([48], [49], [1]) | none |
| 2605.28934 | HEPData: none (ins3162400, 404) | CONFIRMED | Cache `hepdata.json` is a 404 page | none |

## Counts

| verdict | count |
|---|---|
| CONFIRMED | 90 |
| MISMATCH | 1 |
| MISLABELED | 3 |
| WRONG_LOCATION | 2 |
| UNSUPPORTED | 0 |
| UNVERIFIABLE | 0 |
| total rows | 96 |

Non-CONFIRMED rows: 2605.28934 dijet |η| (MISMATCH); 1710.00159 top/N21 mistag label, 1306.2629 Tevatron CDF/D0 choice, 1905.10331 ref [28] erratum (MISLABELED); 2408.00049 "Sec. 4" mass range and width (WRONG_LOCATION).

## Omissions

1. 1306.2629, Sec. III.1.3 (paper.txt ~763–766): "upward fluctuations in the CMS 20 fb-1 limit actually leave some small gaps where the ATLAS [19] 13.0 fb-1 limit and the CMS 5.0 fb-1 limits are more stringent (see Figures 1 and 2)." Above 1.2 TeV, so outside the 10 GeV–1 TeV window. Flagged, not extracted.
2. 1306.2629, Sec. III.1.2 (paper.txt ~742–744): "the CDF limits on spin-1 resonances are the most stringent ones, even though they are based on only a tenth of the Run II data." This is in-window (200–900 GeV) and relevant to the Tevatron row. Not extracted.
3. 2605.28934: photon-channel |η_γ|<2.4 (2.1) cut was not transcribed (see the CONFIRMED row above). Selection detail, not a result.
4. 2408.00049: no omitted limit in window. All 13 mass points of both HEPData tables were checked.
5. 1710.00159 and 1905.10331: no omitted in-window limits beyond the figure-only curves already flagged by each claim file. No NLO EW systematic row applies to Z' (W/Z column only).

## Cache notes (not verdicts)

- `.cache/2408.00049/hepdata/tables/95_CL_*.json` are "HEPData Error" HTML pages. The 52 values were read from the root files `hd_gq_limit.json` and `hd_xsec_limit.json`, which carry the same metadata and values.
- `hepdata/NONE` or 404 pages for 1710.00159, 1306.2629, 1905.10331 and 2605.28934 are consistent with the claim files' "no HEPData record" statements. Those checks are cache-based only.
