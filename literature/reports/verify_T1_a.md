# Verification of limits.md rows R1–R36 and Sections 3–5 citing them

Verdict: 16 of 80 checked items are not CONFIRMED. Three are MISMATCH (R1 mass condition; two Section 3 statements), ten are MISLABELED (mostly "obs/exp inferred" flags where HEPData headers name Observed/Expected), three are MISSING_FLAG (R27 Bayesian, R33 expected-band conflict, Section 5 item 7). No row's numerical values disagree with HEPData or with the paper text, except R1 (incomplete mass condition).

Method: every value was matched against the note and against the cached HEPData JSON (group/header mapping read from qualifiers and headers) or the source text (`.cache/<id>/`). Scanned tables (ins356676 Tables 2–3) were re-read with `pdftotext -layout` on the cached PDF. No network access was used.

| row | item | verdict | evidence | suggested fix |
|---|---|---|---|---|
| R1 | value: √(g^A_b g^A_χ) ≤ 0.1 at m_R = 1 GeV | MISMATCH | `.cache/1805.02780/paper.txt` L1490–1493 (Sec. 5 Summary, which starts at L1438): "for m_{R}=1 GeV and m_{\chi} ≲ 20 GeV it requires \sqrt{g^{A}_{b}g^{A}_{\chi}}\leq 0.1, see Fig. 6". The bound holds only for m_χ ≲ 20 GeV, and the row drops this condition. | Add "for m_χ ≲ 20 GeV" to the coupling/mass column. |
| R1 | CL, obs/exp, RECAST, OUT, invisible-decay flags, Sec. 5 / Fig. 6 location | CONFIRMED | No CL in Sec. 3 recasts (note Open issues); Sec. 5 at L1438; invisible decay per note Sec. 3.1 | none |
| R2 | values: 0.3 excluded, 10–125 GeV, 35.9 fb⁻¹ | CONFIRMED | `.cache/1905.10331/paper.txt` L63 (35.9 fb⁻¹; "10 to 125 GeV"), L131 ("Values of g′_q greater than 0.3 are excluded at 95% CL for the entire mass range"); HEPData `hepdata/NONE` | none |
| R2 | "0.3 not assigned to obs or exp"; no HEPData; CLs | CONFIRMED | L131 has no obs/exp label; L131 "modified frequentist ... CLs" | none |
| R3 | values at 20, 60, 100, 200 GeV (observed / expected) | CONFIRMED | `.cache/2408.00049/hepdata/tables/95_CL_upper_limit_on_Z_-to-quarks_coupling.json` (script): 20 → 0.12239736526556165 / 0.1335872462766656; 60 → 0.09638965209812347 / 0.11755518677565452; 100 → 0.21489213938799076 / 0.15458101323463455; 200 → 0.26241837641285476 / 0.27839384835980946. All 13 points in the table match the note. | none |
| R3 | flag "obs/exp inferred from header order" | MISLABELED | Same JSON: headers are `["m_{Z'} [GeV]", "Observed", "Expected"]` and y-groups 0/1 are the named columns; the mapping is stated, not inferred. | Drop "inferred"; say "obs/exp from HEPData column headers". |
| R3 | text: "g q couplings as small as 0.1 are excluded" (m_Z′ < 100 GeV) | CONFIRMED | `.cache/2408.00049/text.txt` L303 | none |
| R4 | values at 20 and 200 GeV | CONFIRMED | `.cache/2408.00049/hepdata/tables/95_CL_upper_limit_on_XSEC_times_BF_times_A.json` (script): 20 → 0.0267312322536203 / 0.03184232977816885; 200 → 0.06817092982555772 / 0.07672378122066058 | none |
| R4 | flag "units not stated anywhere" | CONFIRMED | Table description and header carry no unit; `text.txt` gives fb only for production cross sections (L299–300) | none |
| R5 | values: g′_q > 0.25 excluded over 50–300 GeV; text 0.17 / 0.08 | CONFIRMED | `.cache/1710.00159/text.txt` L634–635 ("Coupling values of gq′>0.25 are excluded over the Z′ mass range from 50 to 300 GeV"); L580 ("0.17 or 0.08 that are close to our current sensitivity") | none |
| R5 | flags: obs/exp not stated; text 0.25 vs 0.17/0.08 unresolved; no HEPData | CONFIRMED | L634 has no obs/exp label; `hepdata/NONE` | none |
| R6 | values: 50–300 GeV mediator mass; 240 GeV bound when m_Med > 2 m_DM | CONFIRMED | `.cache/1710.00159/text.txt` L605–606 | none |
| R7 | values: g′_q > 0.4 over 50–450 GeV; > 0.2 below 250 GeV; 41.1 and 77.0 fb⁻¹; AK8 < 175, CA15 > 175 | CONFIRMED | `.cache/1909.04114/paper_text.txt` L77, L80 (luminosities), L153–154 (AK8/CA15 split), L455–456 ("g′_q>0.4 ... 50 to 450 GeV, ... most stringent constraints set for masses below 250 GeV where ... g′_q>0.2") | none |
| R8 | values: 79 pb (Φ), 86 pb (A) at 175 GeV; mass range 50–350 GeV | CONFIRMED | `.cache/1810.11822/paper.txt` L65 (50–350 GeV), L260 ("as low as 79 or 86 pb, respectively, at a resonance mass of 175 GeV"), L274 | none |
| R9 | values: g_q 3.9 / 2.5 at 175 GeV; 4.7 (Φ, AK8, 140 GeV); 4.6 (A, CA15, 260 GeV) | CONFIRMED | `.cache/1810.11822/paper.txt` L263 ("3.9 or 2.5, respectively"), L264 (4.7 at 140 GeV; 4.6 at 260 GeV) | none |
| R10 | values: 50 GeV 0.03567 / 0.038571; 55 GeV obs 0.031005 (table min); 300 GeV 0.13162 / 0.13189; text "0.03 to 0.13" | CONFIRMED | `.cache/2603.21965/hepdata/tables/Figure_2a.json` (script; 55 GeV is the observed minimum); `paper.txt` L246 and L264 ("range from 0.03 to 0.13") | none |
| R10 | flag "obs/exp inferred" | MISLABELED | Same JSON: headers `"Observed limit"`, `"Expected limit"` | Drop "inferred"; cite the headers. |
| R11 | values: g_qφ 50 GeV obs 1.3588; 55 GeV obs 1.3404; 300 GeV 5.6001 / 6.6097 | CONFIRMED | `.cache/2603.21965/hepdata/tables/Figure_2b.json` (script) | none |
| R11 | text "1.5 to 5.8 (1.0 to 3.8)" and the stated text-vs-HEPData mismatch | CONFIRMED | `paper.txt` L248 and L265 quote "1.5 to 5.8 (1.0 to 3.8)"; HEPData observed range is 1.3404–5.6001 (script), so the mismatch exists | none |
| R11 | flag "obs/exp inferred" | MISLABELED | `Figure_2b.json` headers `"Observed limit"`, `"Expected limit"` | Drop "inferred". |
| R12 | values: low-p_bb SR 50 GeV 9.6564 / 7.3346 fb; 300 GeV obs 0.88284; high-p_bb SR 50 GeV 2.8513 / 4.4746; 300 GeV obs 0.59295 | CONFIRMED | `.cache/2603.21965/hepdata/tables/Figure_A3a.json`, `Figure_A3b.json` (script) | none |
| R12 | definition: σ_vis, generator-level AK8, pT > 500 GeV, \|η\| < 2.5 | CONFIRMED | `paper.txt` L864–865 | none |
| R12 | flag "obs/exp inferred" | MISLABELED | A3a/A3b headers `"Observed limit [fb]"`, `"Expected limit [fb]"` | Drop "inferred". |
| R13 | values: 50 GeV 0.0092972 / 0.010271; 90 GeV obs 3.416e-05 (table min) | CONFIRMED | `.cache/2603.21965/hepdata/tables/Figure_A1a.json` (script; minimum over observed column is at 90 GeV) | none |
| R13 | RECAST; no unit in HEPData header | CONFIRMED | Header `"Observed limit"` has no unit; `paper.txt` L854 (recast of this search) | none |
| R14 | values: 50 GeV 1.2451e-05 / 1.6651e-05 GeV⁻¹; 300 GeV obs 4.9317e-05 GeV⁻¹ | CONFIRMED | `.cache/2603.21965/hepdata/tables/Figure_A1b.json` (script); top-loop assumption `paper.txt` L860 | none |
| R15 | values: g_q 0.17 (100 GeV), 0.21 (220 GeV), observed | CONFIRMED | `.cache/1801.08769/fulltext.txt` L286–287 ("The observed upper limits on the coupling g_q are 0.17 for m_Z′ = 100 GeV and 0.21 for m_Z′ = 220 GeV") | none |
| R16 | values: σ×A 0.50 / 0.04 pb (100 GeV), 0.35 / 0.03 pb (220 GeV); obs/exp not stated | CONFIRMED | `fulltext.txt` L284–285; no obs/exp label in the sentence | none |
| R17 | values: lowest excluded g_q 0.28 at 150 GeV (text); HEPData minimum 0.28048 (obs) / 0.53032 (exp) at 150.5 GeV; 135–185 GeV excluded at g_q = 0.6 | CONFIRMED | `.cache/2606.03222/paper.txt` L362 (135–185 GeV), L370 ("lowest value ... 0.28 for m = 150 GeV"); `hepdata/tables/Figure_5_Observed.json` min 0.28048 at 150.5 and `Figure_5_Expected.json` min 0.53032 at 150.5 (script) | none |
| R17 | labels: obs and exp; CLs; width non-negligible for g_q above ~0.2 | CONFIRMED | Fig. 5 tables carry Observed / Expected; `html_check.html` contains CL_s; `paper.txt` L145 | none |
| R18 | values: g_q = 0.6, 100 GeV 104310.0 / 52862.0; 250 GeV 12311.0 / 6974.7; g_q = 0.2, 150 GeV 4467.8 / 10731.0 | CONFIRMED | `hepdata/tables/Figure_4.json` (groups 0 = Expected, 1 = Observed; script) and `Figure_17_from_Auxiliary_material.json` (group 0 = Expected, 1 = Observed; script) | none |
| R18 | local 3.0σ (global 2.3σ) at 112 GeV | CONFIRMED | `paper.txt` L363–364 ("local significance of 3.0"; "global significance of 2.3"); mass 112 from `html_check.html` (annotation "m_{Z′}=112") | none |
| R19 | values: 100 GeV obs 16518.0 / exp 8317.4; 150 GeV obs 1383.8 / exp 3556.6 | CONFIRMED | `hepdata/tables/Figure_3.json` (script; group 4 = σ/m 0.10 Observed, group 0 = σ/m 0.10 Expected) | none |
| R19 | text "1.5 nb and 15 nb" vs HEPData in pb | CONFIRMED | `paper.txt` L382; HEPData range 1383.8–16518 pb (≈1.4–16.5 nb) does not reproduce the text; flag is accurate | none |
| R20 | values: g_B ≲ 0.6; "as large as 0.9"; "≈1.5"; "around 2.8 TeV" | CONFIRMED | `.cache/1306.2629/paper.txt` L808–812, L819–821 | none |
| R20 | "2.8 TeV antecedent inferred" flag | CONFIRMED | L819 "The plot is not extended above g_B=2.5 ... For that large coupling ..." (antecedent is inferred, as flagged) | none |
| R20 | range 140 GeV–5.3 TeV; UA2 140–200; √s list | CONFIRMED | `paper.txt` Table 2 (UA2 0.14–0.3 TeV; CMS 1.2–5.3 TeV) | none |
| R21 | values: tan θ dips below 0.15 only in 350–700 GeV and 0.9–1.6 TeV | CONFIRMED | `paper.txt` L845–847 | none |
| R21 | "95% C.L. per Fig. 2 caption" | CONFIRMED | `paper.txt` L826–828 ("Values of tan θ above each limit are excluded at the 95% C.L.") | none |
| R22 | values: excluded 200–835 GeV; first limits 200–250 and 740–835 GeV | CONFIRMED | `.cache/1412.7706/paper.txt` L594–595; L678 | none |
| R22 | 95% CL, Bayesian, uniform prior | CONFIRMED | `paper.txt` L569 ("Bayesian formalism with a uniform prior") | none |
| R23 | values: λ″312 excluded 200–350; λ″323 excluded 200–385 | CONFIRMED | `paper.txt` abstract L35–38; L591–593 | none |
| R24 | values: jbb 200 GeV 5%: 0.00559645 / 0.00597953; γjj 250 GeV 5%: 0.01340714 / 0.01614250; γjj 650 GeV 5%: 0.00803329 / 0.00577182 | CONFIRMED | `.cache/2403.08547/hepdata/tables/95_CL_xsec_upper_limit_gaussian_sig._jbb_channel.json` and `..._gamma_jj_channel.json` (script) | none |
| R24 | flag "obs/exp inferred ('Fit' label)"; t9 header malformed | CONFIRMED | Qualifiers name "Observed σ_G/M_G = 5%" and "Fit σ_G/M_G = 5%" (no explicit "Expected"); γjj Gaussian headers `['m_G', 'σ×A×BR', '$$ [pb]', 'σ×A×BR']` | none |
| R25 | values: 200 GeV 2603 / 3073 / 3628 pb; 900 GeV 2 / 5 / 7 pb; Table 2 | CONFIRMED | `.cache/ins356676/paper.pdf` p. 16 (pdftotext -layout): rows 200 and 900 match | none |
| R25 | "observed only from text ('CDF data exclude the region above')" | CONFIRMED | `.cache/ins356676/paper.pdf` text line "CDF data exclude the region above the listed cross sections at the 95% CL" | none |
| R26 | values: N=10 MT-B2 240–730, HMRS-B 220–640; N=20 MT-B2 260–280 and 420–580, HMRS-B 240–330 and 450–550 | CONFIRMED | `.cache/ins356676/paper.pdf` p. 17 (Table 3, pdftotext -layout) | none |
| R26 | flag: Table 3 vs text (240–640) conflict | CONFIRMED | Text: "axigluons of masses 240 ≤ Ma ≤ 640 GeV/c² are excluded for N=10" (paper.pdf text, abstract "between 240 and 640"); Table 3 HMRS-B N=10 is 220–640 | none |
| R27 | values: "g_q = 0.25 and above"; "near g_q = 0.15"; 225–1100 GeV; 1100 OUT | CONFIRMED | `.cache/1901.10917/fulltext.txt` L467–468 | none |
| R27 | CL type: row says "95% CL; obs/exp not stated" | MISSING_FLAG | `fulltext.txt` L417–420: "Limits are set ... using a Bayesian method ... 95% credibility-level (CL) upper limits". Row omits Bayesian/credibility (R28 carries it). | Write "95% credibility (Bayesian)". |
| R28 | values: Table 5 225 GeV Res obs 0.0340998809681 / exp 0.0294053878139; 400 GeV 0.07 obs 0.0120489943466; Table 6 1000 GeV Res 0.00457124000479 / 0.0041195745712; Table 7 225 GeV b-tagged Res obs 0.00231605585359 | CONFIRMED | `.cache/1901.10917/hepdata/tables/Table_5.json`, `Table_6.json`, `Table_7.json` (script; qualifiers: groups 0–3 Observed, 4–7 Expected) | none |
| R28 | text 12 fb (400 GeV, 7%), 5.1 fb (1050 GeV, 7%); HEPData units not stated | CONFIRMED | `fulltext.txt` L469; headers carry no unit | none |
| R29 | values: γjj 250 GeV 0.04310000 / 0.04205693; γjj 650 GeV 0.01816571 / 0.01606579; γbb 250 GeV 0.00514260 / 0.00705949; jjj 250 GeV 0.08787241 / 0.14522904; jbb 250 GeV 0.01301441 / 0.01112840 | CONFIRMED | `.cache/2403.08547/hepdata/tables/95_xsec_upper_limit_template_sig._*_channel.json` (script) | none |
| R29 | flag "obs/exp inferred"; x-axis labels inconsistent | CONFIRMED | Template qualifiers "Observed" / "Fit Z`" (inferred pairing); headers use m_jj in some tables and m_Z′ in others | none |
| R30 | quotes: "Both the expected and observed limits"; "down to 0.06–0.1" | CONFIRMED | `.cache/2403.08547/fulltext.txt` L374 and L388 | none |
| R30 | placement: Section 1 says rows with unstated lower edge go at the end; R30 is at row 52 | MISLABELED | limits.md Section 1 rule vs row position; the note states the mass range is "not stated in text" yet HEPData tables cover 250–650 GeV | Move R30 to the end, or give 250–650 GeV (tables) and drop "not stated". |
| R31 | values: 0.22 to 0.005 pb over 250–1200 GeV; CLs; observed | CONFIRMED | `.cache/1302.0531/fulltext/plain.txt` L25 and L320–321 | none |
| R32 | values: 250 < m_C < 740 GeV; 250 < m_C < 580 GeV with S8S8 | CONFIRMED | `plain.txt` L325–330 | none |
| R33 | values: σ/m = 0: 250 GeV 2.06E-02 / 2.94E-02; 1000 GeV 3.74E-03 / 4.34E-03; 2000 GeV 1.08E-03 / 1.31E-03; 6000 GeV 3.49E-05 / 3.88E-05 | CONFIRMED | `.cache/2002.11325/hepdata/tables/Table_5_95_CL_upper_limit_on_XSEC_times_BR.json` (script; qualifiers: group 0 Observed, 1 Expected) | none |
| R33 | Bayesian / credibility | CONFIRMED | Table 5 description: "95% credibility-level upper limits" | none |
| R33 | expected-band conflict not flagged (σ/m = 0.15 is in Table 8) | MISSING_FLAG | Table 8 description: expected limits and bands "used in Figure 04"; `.cache/2002.11325/paper.txt` L573–574 and L601–603 (Fig. 4 caption: "The 95% CL observed limits"). Row covers σ/m = 0.15 but flags only the grid mismatch. | Add: "Table 8 says Fig. 4 shows expected bands; Fig. 4 caption says observed only (unresolved)". |
| R34 | values: 300 GeV 1.70E-01 / 2.46E-01; 1000 GeV 1.88E-02 / 2.83E-02; 2000 GeV 7.23E-03 / 6.44E-03 | CONFIRMED | `.cache/2002.11325/hepdata/tables/Table_1_95_CL_upper_limit_on_XSEC_times_BR.json` (script; qualifiers: group 0 Observed, 1 Expected) | none |
| R34 | quote "technipion masses below 350 GeV are excluded" | CONFIRMED | `.cache/2002.11325/paper.txt` L735 | none |
| R34 | flag "mass axis not labelled in HEPData" | MISLABELED | Table 1 header is `"Mass [GeV]"`, so the axis is labelled; what is unstated is which particle's mass it is | Replace with "particle whose mass is the axis not stated". |
| R34 | limit form σ×B vs HEPData description σ×A×BR | CONFIRMED | Table 1 description: "cross-section times acceptance times branching ratio"; row carries the unresolved flag | none |
| R35 | values: 350 GeV obs 15.876 / exp 23.125; 700 GeV obs 1.4504 / exp 1.8906 | CONFIRMED | `.cache/1911.03761/hepdata/tables/Figure_2.json` (script) | none |
| R35 | "obs and exp" mapping (note says "inferred column map") | CONFIRMED | Headers `"Observed limit [pb]"`, `"Expected limit [pb]"`; the row itself does not carry the "inferred" flag, so only the note is affected | none (note wording only) |
| R36 | values: 350 GeV 0.14901 / 0.17984; 700 GeV 0.1017 / 0.11611; text "between 0.10 and 0.15" | CONFIRMED | `.cache/1911.03761/hepdata/tables/Figure_3.json` (script); `paper.txt` abstract L43–45 | none |
| S3 | "All are boosted ISR-γ or ISR-jet single-jet searches" after "Edge at 100 GeV: R15–R19" | MISMATCH | R17–R19 are resolved-dijet pile-up searches (`.cache/2606.03222/paper.txt` L48, L141; no ISR tag), so the sentence is false for them | Exclude R17–R19 from that sentence. |
| S3 | "R17–R19 ... are the only resolved-dijet (non-ISR-tagged) limits below 200 GeV" | MISLABELED | R20 (Dobrescu–Yu mapping of UA2 dijet searches, 140–200 GeV) is resolved-dijet and below 200 GeV; it is excluded only because it is a theory mapping | Say "the only experimental resolved-dijet limits below 200 GeV". |
| S3 | "Edge at 200 GeV: R22–R26" | MISMATCH | R26 row range is 220–730 GeV (`ins356676` Table 3 at 220) | Change to R22–R25 at 200 GeV, or move R26 to the 200–500 list. |
| S3 | ">1 TeV (all OUT)" list includes R20, R21, R27, R28, R31, R33, R34 | MISLABELED | Each has in-window values (R20 140 GeV–5.3 TeV; R21 350–700 GeV; R27 225–1000 GeV; R28 225–1000 GeV; R31 250–1000 GeV; R33 250–1000 GeV; R34 300–1000 GeV) | Split into "entirely above 1 TeV" and "has OUT values". |
| S3 | "R2 (g′_q, 10–125 GeV) ... 10–20 GeV has only R2" | CONFIRMED | R2 range 10–125 GeV; R3/R4 start at 20 GeV | none |
| S4 | Section 4 rows: g_B (1306.2629), tan θ (1306.2629), g′_q (1710.00159, 1909.04114, 1905.10331, 1911.03761), g_q (1801.08769, 2408.00049, 2606.03222, 2403.08547, 1901.10917), g_q, g_qφ, g_qA (2603.21965), g_q (1810.11822), g^V, g^A (1805.02780) | CONFIRMED | Spot checks: 2408.00049 "vector resonance Z′" (`text.txt` L137); 2606.03222 "u,d,s,c,b" and g_χ=1 (`html_check.html`); 1901.10917 width 3.6–4.2% at g_q = 0.3 (`fulltext.txt` L410–412); 2603.21965 "coupled equally to all quark flavors", ×1.2 NLO (`paper.txt` L72, L110); 2403.08547 non-top coupling 0.2 (`fulltext.txt` L140) | none |
| S4 | "The ATLAS 2408.00049 benchmark and the CMS models are vector" | CONFIRMED | 2408.00049 vector (see above); CMS 1710.00159 and 2603.21965 vector | none |
| S5 | item 1: "observed/expected mapping inferred ... 2603.21965, 2408.00049 (header order)" | MISLABELED | 2603.21965 Figure_2a/2b headers "Observed limit"/"Expected limit"; 2408.00049 t5 headers "Observed"/"Expected" | Move these two out of "inferred" list. |
| S5 | item 7: figure-only results list | MISSING_FLAG | `.cache/ins356676` Fig. 1 is figure-only (note Open issue 7) and R26 depends on it, but item 7 omits it | Add "ins356676 Fig. 1". |
| S5 | item 10: "2002.11325 Tables 1–4 do not label the mass axis" | MISLABELED | Table 1 and Table 5 headers read "Mass [GeV]" | Say "do not state which particle's mass is on the axis". |
| S5 | item 11: local excesses (1710.00159 2.9σ/2.2σ at 115 GeV; 2606.03222 3.0σ/2.3σ at 112 GeV; 1909.04114 2.2σ at 115 GeV, 2017 local 2.9σ at 200 GeV) | CONFIRMED | `.cache/1710.00159/text.txt` L583–587; `.cache/2606.03222/paper.txt` L363–364; `.cache/1909.04114/paper_text.txt` L433 | none |
| S5 | item 3: 2603.21965 g_qφ text vs HEPData; 2606.03222 0.28 vs 0.28048 and nb vs pb | CONFIRMED | Verified under R11, R17, R19 | none |

## Counts

| verdict | count |
|---|---|
| CONFIRMED | 64 |
| MISMATCH | 3 |
| MISLABELED | 10 |
| MISSING_FLAG | 3 |
| UNSUPPORTED | 0 |
| UNVERIFIABLE | 0 |
| Total items | 80 |

## Non-CONFIRMED items

- MISMATCH: R1 value (missing "m_χ ≲ 20 GeV"); Section 3 "All are boosted ISR" sentence (R17–R19); Section 3 "Edge at 200 GeV: R22–R26" (R26 starts at 220 GeV).
- MISLABELED: R3, R10, R11, R12 ("obs/exp inferred" although HEPData headers name the columns); R30 placement (Section 1 end-of-table rule); R34 "mass axis not labelled"; Section 3 "only resolved-dijet limits below 200 GeV" (R20 omitted); Section 3 ">1 TeV (all OUT)" list; Section 5 item 1 (2603.21965, 2408.00049); Section 5 item 10 (2002.11325 mass axis).
- MISSING_FLAG: R27 (Bayesian/credibility not stated); R33 (Table 8 vs Fig. 4 expected-band conflict); Section 5 item 7 (ins356676 Fig. 1 figure-only).
- Not checked: the journal versions of 1801.08769 and 1901.10917 (as the note states); HEPData record for ins356676 (only Table 1 present, per note). Rows R37 and later, and sentences citing only rows R37+, are out of scope.
