# verify_w2_6 (transcribed by the lead from the verifier's returned message; the verifier did not write this file itself)

Claim files: 2604.25678, 1103.5699, 2203.01602, 2509.13759.

Counts: CONFIRMED 422 table rows (2604: 144/144 vs HEPData; 1103: 26/26 vs PDF; 2203: 72/72 vs arXiv tables; 2509: 180/180 values vs HEPData). Non-CONFIRMED: MISMATCH 1, WRONG_LOCATION 4, MISLABELED 5, UNSUPPORTED 1, UNVERIFIABLE 2.

| claim file | row/claim | verdict | evidence | suggested fix |
|---|---|---|---|---|
| 2604.25678 | "Jet algorithm and R: none stated" | MISLABELED | Sec 0.2 FxFx merging with up to two partons; Sec 0.6 merging scale 30 GeV | state MC uses FxFx, 30 GeV |
| 2604.25678 | open issue: 97% sentence "does not parse" | MISLABELED | Sec 0.5: MC sample size reaches 97% of total syst on A6 at pT 120–200 GeV | keep as systematics caveat |
| 1103.5699 | CS-frame quote "Footnote 3 (p.4)" | WRONG_LOCATION | bibliography ref [3], p.7 | cite ref. [3], p.7 |
| 1103.5699 | "Footnote 11 (p.7)" GJ frame A0−A2 ≈ −2 | WRONG_LOCATION | ref. [11], p.7 (citation of Arteaga-Romero et al.) | cite ref. [11] |
| 1103.5699 | "no fraction is quoted" for Compton | MISMATCH | p.4: "significant (≈ 30%) contribution of the Compton process" | add quote |
| 1103.5699 | "dominated by" annihilation/Compton (abstract, p.6) | MISLABELED | "dominated" absent; abstract printed p.3 | "both contribute" |
| 1103.5699 | "Q2 is not met" | MISLABELED | Q2 scope names A_0; A0 measured (Table I) | Q2: A_0 measured |
| 1103.5699 | plug 1.2<|η|<2.8 (p.4) | WRONG_LOCATION | selection on p.5; p.4 gives calorimeter coverage | p.4–5 |
| 1103.5699 | journal ref PRL 106, 241801 | UNVERIFIABLE | local PDF arXiv v3 has no journal line | keep flag |
| 2203.01602 | "Total" row = central value | UNVERIFIABLE | not defined; A0−A2 consistency holds in 9/10 bins, 80–100 GeV: 0.0385 vs 0.0371 | keep as inference |
| 2509.13759 | figure column "Figs. 12, 14"/"13, 15" on 160 rows | WRONG_LOCATION | Fig 12/13 = A0,A2–A4; Fig 14/15 = A1,A5–A7 (W−/W+) | per-coefficient figure |
| 2509.13759 | "W− channel more sensitive" to folding threshold | UNSUPPORTED | Sec 5 gives one set of numbers | delete |
| 2509.13759 | "ρ_λλ′ map not stated" | MISLABELED | Sec 1: nine helicity density matrix elements; A_i = helicity cross-section ratios to σ^{U+L} | qualitative only |

Omissions: 2509.13759 Sec 6 "slight deviation from zero ... intermediate pT"; 2203.01602 Sec 6 A0 tension at highest yZ (ResBos); leads 2509 refs [13]–[15], 2604 refs [8],[9] (lead: all already in corpus: 1203.2165, 1104.3829, 2005.03799, 1504.03512, 1606.00689); 2203.01602 yZ 3.6–4.5 bin absent from HTML.

Confirmed notes: 2604 HEPData "Figure 4 ($A_{1}$)" holds A5 (header/caption); 1103 "×10⁻¹" header genuine; 2203 selection and yields confirmed.
