# Verification report: W2_2 notes (five claim files)

Scope: Q1 (hadronic resonance limits), Q2 (W/Z f_L measurements), Q3 (W/Z spin density matrix elements). Five files checked by five independent verifiers, one per file. Four spot checks by the assembling agent are marked "spot-checked".

## Non-CONFIRMED rows

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| 1911.03947.md | "Width-dependent limits (Figs. 6, 7, 10)" for spin-1 qq, spin-2 qq, gg | MISLABELED | Sec 0.6.1: "Figures 6 and 7 show the model-independent observed upper limits ... for narrow resonances." Width-dependent limits appear only in Fig. 10 (caption: "shown for various values of intrinsic width"). | Cite Fig. 10 for width dependence; Figs. 6-7 are narrow-resonance limits (Sec 0.6.1). |
| 1911.03947.md | Open issue: "paper does not say which curve or Gamma/M row gives the 4.8 TeV point" (g_q = 0.9) | MISMATCH | Sec 0.6.2: "for Gamma/M=0.45, this search excludes DM mediators with mass less than 4.8 TeV." Eq. (6) at Gamma/M = 0.45 gives g_q = sqrt((0.45 x 12 pi - 1)/18) = 0.942 (verifier arithmetic; spot-checked). HEPData DM observed g_q at 4800 GeV = 0.94069. | Replace the open issue with: "Eq. (6) at Gamma/M=0.45 gives g_q ~ 0.94, consistent with HEPData 0.94069 at 4800 GeV and with the paper's rounded 0.9." |
| 1911.03947.md | "Cloudflare HTML files hepdata_505215.json ... 505224.json at top level of cache" | UNVERIFIABLE | Files absent from .cache/ and .cache/1911.03947/ (listing checked by the verifier). | Delete the line. |
| 2510.21641.md | Q3: "the 1050 and 1800 GeV endpoints and the 1500 GeV reference point" | MISLABELED | Line 21 of the note. 1050 GeV is not an endpoint of the 600-1800 GeV table range; no source text calls 1500 GeV a reference point. | "The 1050, 1500 and 1800 GeV points lie outside the primary window and are listed separately and flagged." |
| 2510.21641.md | O1: "HEPData labels all four tables as 'Data from Figure 4' or 'Figure 6'" | MISMATCH (verifier verdict) | Spot-checked in .cache/2510.21641/hepdata/hepdata_record.json: "Data from Figure 4 (left).", "Data from Figure 4 (middle).", "Data from Figure 4 (right).", "Data from Figure 6." The note's wording is imprecise rather than false; severity is minor. | Replace with the four exact HEPData labels; note that they do not follow the caption positions (caption: qq upper left, qg upper right, gg lower). |
| 2509.01219.md | INSPIRE recid 2966134 | UNVERIFIABLE | No INSPIRE record in cache. HEPData key "ins2966134" is present, which supports the id only by convention. | Cite the ins key, or fetch the INSPIRE record into a fresh /tmp directory. |
| 2507.17884.md | Header: "X = vector-like quark (charm or omega)" | MISLABELED | Sec 0.1: "The dijet resonance is a vector-like quark, \PGc or \PGo" (chi and omega macros). HEPData t20 description: "pairs of vector-like quarks, $y_{\chi}$ and $y_{\omega}$". "charm" does not occur in the cached arXiv HTML (spot-checked: count 0). | "X = vector-like quark chi or omega, decaying at one loop to g + q." |
| 2507.17884.md | Printed paper table number ("Table 0.5") | UNVERIFIABLE | Only the LaTeXML label "Table 0.5" appears in the cache; no printed number. | Drop the printed number or cite the label as it appears. |
| 2307.14944.md | BumpHunter bullet: "3200 GeV ... 0.53 sd" and "800 GeV ... 1.98 sd"; "no significant excess is observed" | MISLABELED | Sec 4.1: the 3200 GeV excess is in m_4j, alpha 0.24-0.26, global 0.53 sd; the 800 GeV excess is in <m_2j>, alpha 0.26-0.28, global 1.98 sd. "No significant excess" is not in Sec 4.1; Sec 4.2 says "As no signal is observed." | State spectrum and alpha for each excess; cite Sec 4.2 for "no signal observed." |

## Counts per verdict (per verifier tallies, summed)

| claim file | CONFIRMED | MISLABELED | MISMATCH | WRONG_LOCATION | UNSUPPORTED | UNVERIFIABLE |
|---|---|---|---|---|---|---|
| 1911.03947.md | 132 | 1 | 1 | 0 | 0 | 1 |
| 2510.21641.md | 57 | 1 | 1 | 0 | 0 | 0 |
| 2509.01219.md | 54 | 0 | 0 | 0 | 0 | 1 |
| 2507.17884.md | 71 | 1 | 0 | 0 | 0 | 1 |
| 2307.14944.md | 332 (34 narrative + 298 HEPData rows) | 1 | 0 | 0 | 0 | 0 |
| **Total** | **646** | **4** | **2** | **0** | **0** | **3** |

Note on 2509.01219.md: the verifier's enumeration sums to 55 rows while its stated total is 56. The per-verdict counts are reported as stated.

## CONFIRMED rows with a fix (not a verdict change)

- 1911.03947.md: DM benchmark (g_q = 0.25, g_DM = 1.0) is missing from the Table-1 benchmark list (Sec 0.1). Add it.
- 2510.21641.md: S5 H_T definition omits "|eta| < 3.0" (Sec 0.2).
- 2307.14944.md: mass-asymmetry requirement omits the "< 0.1" threshold (Sec 3.2 equation).
- 2507.17884.md: the "-" entries list is partial (43 "-" cells exist). Replace with the full list or state it is partial. Also, the level of A (generator) and eps (reconstructed m4j > 1.6 TeV) should be stated.

## Omissions (in scope, more relevant than what was extracted)

1. **2509.01219.md (confirmed by the assembler against JSON):** Z' J100 table has 25 mass points from 600 to 1800 GeV. The note extracts only 1050, 1500, 1600 and 1800 GeV in the 1050-1800 range. Missing: 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1550, 1650, 1700, 1750 GeV (Z_limits_J100.json). Gaussian J100 table has the same gap (1100-1450, 1550, 1600, 1650, 1700, 1750 GeV missing). These are outside 1 TeV and must be flagged, not skipped.
2. **2507.17884.md (confirmed by the assembler against JSON):** the 8.6 TeV row, at the mass of the 3.9 sd local excess, is absent from every limit table extract. Example: t20 (1.5%, alpha 0.25) at 8.6 TeV, sigma x B x A observed 0.0000476421 pb, expected 0.0000268968 pb; observed exceeds expected. Also in the abstract: 10%-width significance at 8.6 TeV is 3.6 (local) / 1.4 (global) sd.
3. **2510.21641.md (verifier):** Sec 0.6 states that benchmark W', Z', diquarks, colorons, axigluons, excited quarks and DM mediators are excluded over 0.6-1.8 TeV (figure-only, Fig. 4). Sec 0.7 compares sensitivity to ATLAS [56] (132 fb^-1) and states ATLAS [36] was more sensitive below ~1 TeV for Z'. Pointers only; ATLAS values not verified.
4. **1911.03947.md (verifier):** abstract DM endpoint 1.8 TeV at 1% width is not extracted. HEPData theory cross-section columns (Fig. 6 tables) are unused.
5. **2307.14944.md (verifier):** Fig. 7 (observed limit summary) is figure-only and not verified. Section B records endpoints and reference masses only; full rows are in the cache JSON.

## Method and limits

- HEPData-sourced rows were compared programmatically by each verifier against the cached JSON (with mutation tests reported by the 2307 and 2507 verifiers). The assembler did not rerun those comparisons.
- Figure-only values (Fig. 1, Fig. 4 axes, Fig. 5 p-values, Fig. 6 curves, Fig. 7, Fig. 8 significance) were not checked against figures; the cache does not contain them.
- Spot checks by the assembler: 2509.01219 omissions (JSON mass-point lists); 2510.21641 O1 HEPData labels and Q3 wording; 2507.17884 "charm" absence and 8.6 TeV row values; 1911.03947 Eq. (6) arithmetic at Gamma/M = 0.45.
- No file was edited except this report.
