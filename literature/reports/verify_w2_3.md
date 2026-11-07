# Verification report: verify_w2_3 (five claim files)

Verdict: 62 rows checked. 55 CONFIRMED, 2 MISMATCH, 1 MISLABELED, 4 UNVERIFIABLE, 0 WRONG_LOCATION, 0 UNSUPPORTED. Two notes need a correction (1911.03761 Open issue on HEPData labels; 1806.00843 3.7 TeV spin-1 g_q value). Full table below.

Method: HEPData values were read from the cached JSON in `.cache/<id>/hepdata/tables/` (1911.03761, 1806.00843). Column assignment for 1911.03761 was checked against the JSON `headers` and the paper's Fig. 2/3 captions. For 1806.00843, all 87 observed text-table rows (21 low-mass, 66 high-mass) were parsed from `fulltext/paper.txt` and compared with HEPData t3 (261 values, max relative deviation 0.47%). Expected and RS text values for the in-window rows and the 1.5/1.6 TeV rows were compared the same way. Text quotes were re-grepped in the cached paper text. For 1302.0531, 1603.08791 and 1412.7706 there is no HEPData record (`hepdata/NONE`), so checks are against the paper text only.

## Table

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| notes/1911.03761.md | Fig. 2 σ×B×A observed, expected, ±1σ, ±2σ at 350–700 GeV (8 mass points) | CONFIRMED | HEPData `Figure_2.json`: 350 GeV obs 15.876, exp 23.125, +1σ 32.121, −1σ 16.689, +2σ 42.677, −2σ 12.546; all 8 rows match | none |
| notes/1911.03761.md | Fig. 3 g′_q limits at 350–700 GeV (8 rows) | CONFIRMED | `Figure_3.json`, e.g. 350 GeV obs 0.14901, exp 0.17984; all 8 rows match | none |
| notes/1911.03761.md | Table 1 acceptance (300, 400, 500, 600, 800 GeV) and paper percentages | CONFIRMED | `Table_1.json`: 0.040436 ±0.0040436 ... 0.13566; paper text line "(4.0 ± 0.4)% (6.7 ± 0.7)% (9.2 ± 0.9)% (10.9 ± 1.1)% (13.6 ± 1.4)%" | none |
| notes/1911.03761.md | Open issue 1: "the JSON tables ... carry no column labels for the six y-values (group indices 0–5)" | MISMATCH | `Figure_2.json` `headers`: "Observed limit [pb]", "Expected limit [pb]", "Expected limit + 1 sigma [pb]", "Expected limit - 1 sigma [pb]", "Expected limit + 2 sigma [pb]", "Expected limit - 2 sigma [pb]" (x-column first). `Figure_3.json` has the same six labels. The note's group 0→Obs, 1→Exp, 2→+1σ, 3→−1σ, 4→+2σ, 5→−2σ mapping is consistent with these headers. The mapping is confirmed; only the statement that labels are absent is wrong. | Replace the sentence with: "The JSON `headers` label the groups in this order: Observed, Expected, +1σ, −1σ, +2σ, −2σ (Figure_2.json, Figure_3.json)." Drop the request to check the CSV/YAML. |
| notes/1911.03761.md | Obs/exp column assignment | CONFIRMED | Confirmed by the JSON `headers` above and by the Sec. 7 text: "upper limits ... between 0.10 and 0.15" and Fig. 2/3 caption "The observed limits (solid curve), expected limits (dashed curve)". | none |
| notes/1911.03761.md | Trigger: L1 H_T>240, HLT H_T>250 GeV; jets pT>40, |η|<2.5; 2016 data scouting | CONFIRMED | paper.txt l.132–133 "HT > 240 GeV at the L1 trigger and HT > 250 GeV at the HLT ... pT > 40 GeV and |η| < 2.5"; l.143–144 (2016) | none |
| notes/1911.03761.md | Selection and fit: calo jets pT>30, |η|<2.5, ECAL/HCAL ≥5%; wide jets R=1.1; pT>72 GeV; |η1−η2|<1.1; fit 290<m_jj<1000; five parameters; signal-depleted |η1+η2|<1.1; KS>33%; 72 GeV threshold | CONFIRMED | paper.txt l.166–168, 170, 177, 183, 217, 271–272, 291–292, 304 | none |
| notes/1911.03761.md | "trigger efficiency is > 99% only for m_jj > 290 GeV" | MISLABELED | paper.txt l.146–147: "we measured a trigger efficiency larger than 99% for a dijet invariant mass greater than 290 GeV." The paper gives no efficiency below 290 GeV, so "only" is an added qualifier. | Delete "only": "trigger efficiency is > 99% for m_jj > 290 GeV (Sec. 3)." |
| notes/1911.03761.md | Systematics: JES 2% (±2% shift); JER ±10% width; ISR/FSR ×2 scale gives 10% normalization; lumi 2.5%; five background parameters dominant; pileup/PDF/UE/PS negligible | CONFIRMED | paper.txt l.304–305, 309–311, 315–317, 323–324. Minor-impact wording confirmed at l.307. | none |
| notes/1911.03761.md | Mass coverage 350–700 GeV; abstract "0.10 and 0.15"; "most stringent ... 350 and 450 GeV" | CONFIRMED | paper.txt l.331–334, 44–46, 457–459 | none |
| notes/1911.03761.md | Journal volume "Phys. Lett. B 805 (2020) 135448" | UNVERIFIABLE | DOI 10.1016/j.physletb.2020.135448 is in paper.txt l.50 (confirmed). The volume 805 does not appear anywhere in the cached paper text. | Keep the DOI as the verified identifier; mark the volume as "not verified". |
| notes/1806.00843.md | Q1a observed σ×B×A, 600–1000 GeV (9 rows, gg/gq/qq) from HEPData t3 | CONFIRMED | `Cross-section_limits.json`: 600 → 39.308 / 33.678 / 13.843; 1000 → 1.6586 / 0.96703 / 0.57163; all 9 rows checked | none |
| notes/1806.00843.md | Q1a expected gg/qg/qq and RS obs/exp text values, 600–1000 GeV, and 1500/1600 rows | CONFIRMED | Parsed from paper.txt "Limits from the low-mass search" table; every value in the note matches (e.g. 0.60: 2.10×10¹ / 1.90×10¹ / 1.05×10¹ / 2.59×10¹ / 1.46×10¹) | none |
| notes/1806.00843.md | Open issue 9: 87 HEPData observed rows agree with text observed values | CONFIRMED | Script over paper.txt and t3: 87 rows (21 low, 66 high), 261 values, max relative deviation 0.47%, zero above 0.6% | none |
| notes/1806.00843.md | Q1b out-of-window σ×B×A points: 1500, 1600 (two rows), 2000, 3000, 5000, 8000, 8100 | CONFIRMED | t3: 1500 → 0.41953/0.26561/0.14549; 1600 → 0.33655/… and 0.37191/…; 8100 → 0.0022577/0.00070466/0.00019665 | none (see omissions O1) |
| notes/1806.00843.md | Q1c leptophobic Z′ g′_q rows 600–1000 GeV, plus 1500–3700 GeV flagged | CONFIRMED | `Coupling_limits_Quark_only.json` rows checked, e.g. 600 → 0.12186 / 0.10612 (−0.018426, +0.025491) / (−0.030935, +0.060511); 3700 → 0.36891 / 0.34503 | none |
| notes/1806.00843.md | Q1d DM-mediator g_q rows at 1600, 2000, 3000, 4100 GeV; observed missing at 4100 | CONFIRMED | `Coupling_limits_DM_mediator.json`: 1600 → 0.22666 (−0.018485/+0.031454), 2 s.d. (−0.035795/+0.075753), obs 0.22021; 2000 obs 0.23743; 3000 obs 0.35411; 4100 obs "-" | none |
| notes/1806.00843.md | Q1f "width-corrected spin-1 g_q limit at 3.7 TeV: g_q > 0.53 ... 95% CL; observed" | MISMATCH | Paper text (Sec. 0.6.4, prose l.308–309): "the more accurate limit taking into account the width for the spin-1 resonance is g q > 0.53". HEPData t4 at 3700 GeV: observed g_q = 0.54659 (group 2, header "Observed g_q exclusion"); expected median = 0.47534. Neither column gives 0.53, and the paper sentence does not say "observed". The note's 0.53 vs HEPData 0.547 disagreement is not resolved in the cache. | Record the text value verbatim. Add the HEPData value at 3700 GeV (observed 0.54659, median 0.47534) and flag that 0.53 is not reproduced. Remove the "observed" label unless the source states it. |
| notes/1806.00843.md | Q1f "narrow-resonance g_q > 0.42 at 3.7 TeV; 95% CL; observed" | UNVERIFIABLE | Quote verified at prose l.308: "the narrow-resonance limit is g q > 0.42". The narrow-width curve is Fig. 19 blue, which the note itself says is figure-only, and it is not in t4. The source does not say "observed". | Keep the quote. Replace "observed" with "CL and observed/expected not stated in text". |
| notes/1806.00843.md | Q1e mass-limit table: string 7.7, diquark 7.2 (7.4), axigluon 6.1 (6.0), excited quark 6.0 (5.8), octet 3.4 (3.6), W′ 3.3 (3.6), Z′ 2.7 (2.9), RS 1.8 (2.3), DM 2.6 (2.5); 12.9 fb⁻¹ column; RS 1.9–2.5 TeV and Z′ ~3.1 TeV text | CONFIRMED | Prose table (prose2.txt l.61–110) and text l.51–53 | none |
| notes/1806.00843.md | Q1f other text values: DM mediator 0.6–2.6 TeV; g_q narrow valid to ~0.4 (10% width); 0.76 (30%); 4.1 TeV width-corrected | CONFIRMED | prose l.119–120, 310–312 | none |
| notes/1806.00843.md | Dominant systematics quotes: background "majority of the effect"; JES 2%; JER 10%; lumi 2.5%; gg largest, qq smallest | CONFIRMED | paper.txt l.436–450, 466–482 | none |
| notes/1806.00843.md | Caveats: A = A_Δ·A_η; m_jj acceptance corrected into the limit; "All upper limits ... without detector simulation"; interference not considered; diquark conservative; 150% truncation | CONFIRMED | prose l.38–39, 255; paper.txt l.406–410, 458–459, 1339 | none |
| notes/1806.00843.md | Open issues 2–5, 8: HEPData tables t1–t5 mapping; t4 4100 observed missing; duplicate 1600 rows; asymerror encoding | CONFIRMED | `record.json` data_tables DOIs 80166.v1/t1–t5 with names matching; t4 4100 observed "-"; t3 and t5 duplicate 1600 rows; t4/t5 use `asymerror` | none |
| notes/1806.00843.md | Bibliography: JHEP 08 (2018) 130; DOI 10.1007/JHEP08(2018)130; arXiv v2 01 Sep 2018; HEPData DOI 10.17182/hepdata.80166.v1 | CONFIRMED | `fulltext/inspire.json` contains "10.1007/JHEP08(2018)130" and arXiv 1806.00843; paper.txt contains "01 Sep 2018"; record.json uses hepdata.80166.v1 | none |
| notes/1302.0531.md | Observed σ×Br²×A "varies from 0.22 to 0.005 pb for resonance masses between 250 and 1200 GeV" | CONFIRMED | plain.txt l.24–25, 319–320 (quote verbatim). No mass attached to 0.22 or 0.005 in text, as the note says. | none |
| notes/1302.0531.md | Coloron exclusion 250 < m_C < 740 GeV (qq only); 250 < m_C < 580 GeV with C→S8S8, m_S8=150, tanθ=0.3 | CONFIRMED | plain.txt l.325–330; summary l.425–428 | none |
| notes/1302.0531.md | Table 1 acceptances: coloron 0.4, 2.2, 5.2, 8.0, 9.6, 10.6, 11.6, 11.8, 12.1% (200–1000 GeV); stop 0.9, 3.6, 7.9, 10.7, 12.9% (200–600 GeV) | CONFIRMED | plain.txt l.335–378 table; l.238–239 "0.4% ... 12.1%" | none |
| notes/1302.0531.md | Systematics: lumi 2.2%; signal acceptance 10% = JES 2.2% and JER 10%; PDF negligible; log-normal nuisances; CLs with one-sided profile likelihood | CONFIRMED | plain.txt l.311–315 (quotes verbatim) | none |
| notes/1302.0531.md | Selection and fit: trigger pT 70/80, |η|<3.0, 99.5% at 110 GeV; anti-kT R=0.5; pT>110, |η|<2.5; ΔR≥0.7; Δm<0.15 m_avg (≈3× 4.5% resolution); Δ>25 GeV; fit m_avg>220; limit m_avg≥250; 4.5% rms | CONFIRMED | plain.txt l.67–69, 72–73, 84–89, 101, 124, 244–245, 308 | none |
| notes/1302.0531.md | Largest local fluctuation 1130 GeV, 2.6σ local, 1.2σ global (flagged outside window) | CONFIRMED | plain.txt l.249–252 ("occurs for a hypothetical resonance mass of 1130 GeV and has a local statistical significance of 2.6σ") | none |
| notes/1302.0531.md | Open issues: no HEPData; expected and point values figure-only; S8 not sensitive; stop range not in text | CONFIRMED | `hepdata/NONE` = "no HEPData record"; plain.txt l.330–331 (S8); l.325–326; no stop range in text | none |
| notes/1603.08791.md | b* excluded 1.1–2.1 TeV at LO QCD, 95% credibility | CONFIRMED | paper.txt l.36 (abstract), l.152, l.180 (Sec. 8: "expected contribution ... excluded in the mass range 1.1–2.1 TeV") | none |
| notes/1603.08791.md | leptophobic Z′→bb̄ excluded 1.1–1.5 TeV; SSM Z′ not excluded | CONFIRMED | paper.txt l.36, 157, 181 | none |
| notes/1603.08791.md | Gaussian σ×A×BR 0.4 to 0.001 pb; 1.5–5.0 TeV (Abstract, Sec. 7); 1.1–5.0 TeV (Sec. 8) | CONFIRMED | paper.txt l.36, 161–162, 182 | none |
| notes/1603.08791.md | Sec. 3 signal parameters: 85% b*→bg; BR(Z′→bb̄)=13.8% (SSM) and 18.9% (leptophobic); Γ≈0.6% (b*), ≈3% (Z′); widths 15/10/7% | CONFIRMED | paper.txt l.86–88 (quotes verbatim); l.173 | none |
| notes/1603.08791.md | Selection: anti-kT R=0.4 from topo-clusters; jet pT>50; leading jet >440 GeV; |η|<2.4; m_jj>1.1 TeV; |y*|<0.6; b-tag WP 85% | CONFIRMED | paper.txt l.92–94, 98, 106 area, 103–104 (85%); y* at the m_jj/|y*| paragraph | none |
| notes/1603.08791.md | Lumi 3.2 fb⁻¹ with 5%; 2015 data; jet trigger pT≥360 GeV | CONFIRMED | paper.txt l.75 ("during 2015 ... at least one jet ... 360 GeV"); l.79 luminosity quote verbatim | none |
| notes/1603.08791.md | Acceptance: "around 20%" (b*, 1b); "9% at 1.5 TeV to 2% at 5.0 TeV" (Z′, 2b); 2b efficiency 2.5× lower at low mass, 10× at high mass | CONFIRMED | paper.txt l.104, 106 (quotes verbatim) | none |
| notes/1603.08791.md | Systematics: b-tag "largest systematic uncertainty"; reaches 50% above 2 TeV; b-jet JES 6%; untagged JES 1–5% (>200 GeV); r_trk 2.6% (200–800 GeV); JER <2% (pT>50); bkg parameter extra z^{p4 log z} | CONFIRMED | paper.txt l.134, 138–141, 134–144 (quotes verbatim), l.123–131 | none |
| notes/1603.08791.md | BumpHunter intervals 1493–1614 GeV (1b), 3596–3827 GeV (2b), probability >60%; "largest observed local excess is less than 2σ" | CONFIRMED | paper.txt l.125–128 (quotes verbatim); l.179 (Summary) | none |
| notes/1603.08791.md | Bayesian credibility limits; limit interpolated between mass points; LO QCD caveat; generic-Gaussian validity sentence | CONFIRMED | paper.txt l.146–150, 152, 163–164 | none |
| notes/1603.08791.md | Generator: Pythia8 with A14 tune and NNPDF2.3 (QCD and signals) | CONFIRMED | paper.txt l.80–81, 85; paper.html l.258–265 | none |
| notes/1603.08791.md | arXiv v2 23 Jun 2016; CERN-EP-2016-066; Phys. Lett. B from `\AtlasJournal` macro | CONFIRMED | paper.txt l.29 (v2 23 Jun 2016), l.30–31 (\AtlasJournal, Phys. Lett. B), l.32 (CERN-EP-2016-066) | none |
| notes/1603.08791.md | arXiv v1 "March 2016"; journal volume/pages "not verified" | UNVERIFIABLE | The cached paper text shows only v2 (l.29). v1 date is not in the cache. The note itself states volume/pages were not verified. | Keep "v1 date not checked" or drop it. |
| notes/1603.08791.md | HEPData: none (`hepdata/NONE`); figure-only Figs. 5–7 | CONFIRMED | `.cache/1603.08791/hepdata/NONE` present | none |
| notes/1412.7706.md | Coloron excluded 200–835 GeV (quote: "We exclude the production of colorons decaying into four jets at 95% CL for masses between 200 and 835 GeV") | CONFIRMED | paper.txt l.594–595 (quote verbatim) | none |
| notes/1412.7706.md | First coloron limits at 200–250 and 740–835 GeV | CONFIRMED | paper.txt l.677–679 | none |
| notes/1412.7706.md | λ″312 stops excluded 200–350 GeV | CONFIRMED | paper.txt l.591–592 (quote verbatim) | none |
| notes/1412.7706.md | λ″323 stops excluded 200–385 GeV | CONFIRMED | paper.txt l.592–594, 683–685 | none |
| notes/1412.7706.md | Figs. 6–7 limit curves, observed and expected, figure-only | CONFIRMED | Captions paper.txt l.627–629, 666–668; `hepdata/NONE` | none |
| notes/1412.7706.md | Lumi 19.4 fb⁻¹ ("as much as 19.4 ± 0.5 fb"); low-mass 12.4 fb⁻¹ | CONFIRMED | paper.txt l.57 (quote), l.121–126; Table 1 l.390 | none |
| notes/1412.7706.md | Selection: four-jet triggers, |η|<2.5, pT>80 / >120 GeV; anti-kT R=0.5; Table 1: 200–300 vs >300 GeV, Δm/m<0.15, Δη<1.0, Δ>70 / >100 GeV, fourth-jet pT >80 / >120; Eq. 2–3; Eq. 4 four-parameter fit from 200 / 300 GeV; ±10% window | CONFIRMED | paper.txt l.122, 143, 197–198, 218, 269 (Eq. 3), 390–394, 437–442 (Eq. 4), 450–451, 326 | none |
| notes/1412.7706.md | Heavy-flavor: CSV medium; 72% efficiency and 1.1% misid; ≥2 b-tags among four highest-pT jets | CONFIRMED | paper.txt l.156, 161–162, 348–352 | none |
| notes/1412.7706.md | Systematics: lumi 2.6%; ISR 5%; JEC 1–6.2%; JER 10%; b-tag 2%; pileup <1.5%; background 0.3–0.6% (low), 0.5–30% (high); "imperfect knowledge of the integrated luminosity (2.6%)" | CONFIRMED | paper.txt l.455–460 (quote verbatim, line break "im-perfect"), l.563–564 | none |
| notes/1412.7706.md | Method: Bayesian, uniform prior, posterior integrated to 0.95; stop mass = m_av in limit plots | CONFIRMED | paper.txt l.569, 581–589 | none |
| notes/1412.7706.md | Generators: MadGraph 5.1.5.12 (CTEQ6L1), Pythia 6.426; stop masses 100 GeV–1 TeV (50 GeV steps); coloron 100 GeV–2 TeV; NLO+NLL stops; NLO coloron | CONFIRMED | paper.txt l.166–186 (MADGRAPH and PYTHIA 6.426 quotes; spaced "M AD G RAPH" in the text layer) | none |
| notes/1412.7706.md | Introduction citations: CDF RPV stops 50–90 GeV and colorons 50–125 GeV; ATLAS scalar gluons 100–185 and 150–287 GeV; CMS coloron 250–740 GeV | CONFIRMED | paper.txt l.85–89 (values as stated in the paper; the cited papers themselves were not checked) | none |
| notes/1412.7706.md | arXiv v2 3 Jun 2015; DOI 10.1016/j.physletb.2015.04.045; CMS-EXO-12-052 | CONFIRMED | paper.txt l.10, 18 ("arXiv:1412.7706v2 [hep-ex] 3 Jun 2015"), l.43 (DOI) | none |
| notes/1412.7706.md | Phys. Lett. B 747 (2015) 98–119 | UNVERIFIABLE | DOI is in the paper text (l.43). Volume 747 and pages 98–119 do not appear in the cached paper text. The note cites INSPIRE, which is not cached for this paper. | Keep the DOI; mark volume/pages as not verified in cache. |
| notes/1412.7706.md | Mass-range attribution: "not explicitly labelled observed or expected in text" | CONFIRMED | Sec. 7 text (l.587–595) gives no observed/expected label; captions of Figs. 6–7 say both are drawn | none |

## Counts

| verdict | count |
|---|---|
| CONFIRMED | 55 |
| MISMATCH | 2 |
| MISLABELED | 1 |
| UNVERIFIABLE | 4 |
| WRONG_LOCATION | 0 |
| UNSUPPORTED | 0 |
| Total rows | 62 |

Non-CONFIRMED rows: 1911.03761 Open issue 1 (MISMATCH); 1911.03761 trigger efficiency "only" (MISLABELED); 1911.03761 journal volume 805 (UNVERIFIABLE); 1806.00843 Q1f 3.7 TeV spin-1 g_q = 0.53 "observed" (MISMATCH); 1806.00843 Q1f 3.7 TeV narrow g_q = 0.42 "observed" (UNVERIFIABLE); 1603.08791 arXiv v1 date and volume/pages (UNVERIFIABLE); 1412.7706 PLB volume 747 and pages 98–119 (UNVERIFIABLE).

## Omissions

- O1 (1806.00843, Q1b–Q1d, scope "record the full mass range"): out-of-window HEPData rows are only partly transcribed. Missing: σ×B×A t3 rows 1050–1450, 1550, 1700–1900, 2100–2900, 3100–3900, 4000–8100 GeV; Z′ g′_q t5 rows 1050–1550, 1700–2900, 3100–3600 GeV; DM-mediator t4 rows 1700–3500 and 3700–4000 GeV. All are above 1 TeV, so the in-window record is complete. Priority is low.
- O2 (1302.0531, plain.txt l.321–322): "The limits are generally applicable for pair-produced resonances, each decaying to dijets." This is a general applicability statement relevant to the Q1 scope and is not recorded.
- No in-window omissions found for 1911.03761, 1603.08791 or 1412.7706. For 1412.7706 the cited prior limits (Sec. 1) were recorded as cited only and not checked, as the note says.
