# Verification report: w1_2 (five claim notes)

Verdict: 4 non-CONFIRMED rows in total: 2 among the 158 quoted-result rows (1 WRONG_LOCATION, 1 MISLABELED) and 2 among the other checked items (1 UNVERIFIABLE, 1 MISLABELED). The 2606.03222 note is the most reliable (101 HEPData rows match exactly). The 1909.04114 note has one wrong location; the 2606.03222 note has one text range that the HEPData tables do not reproduce.

## Non-CONFIRMED rows

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| notes/1909.04114.md | Quoted results row 1: "Coupling g′_q > 0.4 excluded", location "Sec. 0.7 Summary; also Abstract" | WRONG_LOCATION | Value confirmed in Summary (`.cache/1909.04114/paper_text.txt` line 455): "Coupling values of g′_q>0.4 are excluded over the signal mass range from 50 to 450 GeV". The abstract (line 42) gives no numeric limit: "Upper limits at the 95% confidence level are set on the coupling of narrow resonances to quarks, as a function of the resonance mass." | Delete "also Abstract" from the location. |
| notes/1909.04114.md | Open issues / HEPData: "HEPData record: none found" for ins1753375 (the job lists ins1753375 as an existing source record) | UNVERIFIABLE | Cache `.cache/1909.04114/hepdata/NONE` reads "no HEPData record"; no HEPData tables exist in cache. Per the job, hepdata.net was not contacted. The note's "none found" matches the cache, but the job's ID claim cannot be checked. No HEPData-sourced number is used in this note, so no value is affected. | Confirm directly that ins1753375 exists or correct the job's source list. |
| notes/2606.03222.md | Quoted results: "Gaussian σ×A×B, 10% relative width, range: 1.5 nb to 15 nb (text)" | MISLABELED | The text is verbatim (paper_text `.cache/2606.03222/paper3.txt` line 354: "upper limits on σ×A×B range between 1.5 nb and 15 nb, depending on the mass, for resonances with a 10% relative width"). The HEPData tables do not reproduce it. Figure 3 (10% width, `hepdata/tables/Figure_3.json`): observed (group 4) spans 1383.8 pb (150 GeV) to 16518 pb (100 GeV); expected (group 0) spans 1820.4 pb (232 GeV) to 8317.4 pb (100 GeV). | Keep the text quote, label it "text only", and add the HEPData obs and exp ranges with units (pb). State that the text range does not match the tabulated curves. |
| notes/2603.21965.md | Selection: "ρ = 2 ln(m_SD/pT) restricted to −5.5 < ρ < −2.1 (203 bins)" | MISLABELED | The source typesets the window as "−5.5>ρ>−2.1" (`.cache/2603.21965/paper.txt` line 164). As printed, the inequality is reversed. The note silently uses the physically sensible order. | Note that the printed inequality is reversed and that the note uses the intended window. |

## Checked and CONFIRMED with flags (no verdict change)

- 2603.21965, spin-0 g_qφ text range "1.5 to 5.8 (1.0 to 3.8)" (paper.txt lines 248, 265): verbatim. It is not reproduced by Figure 2b. Observed (group 0) spans 1.3404 (55 GeV) to 5.6001 (300 GeV). Expected (group 1) spans 1.7287 (55 GeV) to 6.6097 (300 GeV). The note's Open issue 1 is correct that this is unreconciled.
- 2603.21965, g_qA range "1.0 to 3.8": text only, no table. Confirmed as a quote.
- 2606.03222, lowest excluded g_q "0.28 for m=150 GeV" (text, paper3.txt line 342) vs Figure 5 observed minimum 0.28048 at 150.5 GeV. Both values are correct as stated, as the note says.

## Counts per verdict

Quoted-results rows (158 total, 5 notes):
- CONFIRMED: 156 (2603.21965: 23; 1909.04114: 9; 1810.11822: 10; 1801.08769: 9; 2606.03222: 105)
- WRONG_LOCATION: 1 (1909.04114)
- MISLABELED: 1 (2606.03222)
- UNSUPPORTED: 0
- MISMATCH: 0
- UNVERIFIABLE: 0 among quoted rows

Other checked items (not counted above):
- Dominant-systematics items: all CONFIRMED (2603.21965: 9; 1909.04114: 10; 1810.11822: 13; 1801.08769: 7 table rows; 2606.03222: 6)
- Caveat and selection items: CONFIRMED except 1 MISLABELED (2603.21965 ρ window)
- 1909.04114 HEPData existence: 1 UNVERIFIABLE
- Journal refs (arXiv abs pages fetched into /tmp/vh/fetch): 1909.04114 = PRD 100, 112007 (2019), CONFIRMED; 1810.11822 = PRD 99, 012005 (2019), CONFIRMED; 2603.21965 = preprint, CONFIRMED; 1801.08769 = PLB 788 (2019) 316, CONFIRMED against INSPIRE in cache; 2606.03222 = INSPIRE 2863 authors, CONFIRMED.

## Method

- HEPData: cache tables used, not refetched. For 2606.03222 I checked all 101 HEPData-sourced rows by script against `Figure_*.json`: value, x, group, and band signs and sizes (88 band strings). Zero mismatches. Group mapping for 2606 Figures 3, 4, 17, 18 is explicit in the JSON `qualifiers.Type`. For 2603.21965 the mapping was checked against the caption (solid = observed, which has no bands; bands belong to expected) and against the `hide` flag on group 0.
- 2603.21965: extrema computed over the full tables (observed min/max and expected min/max for Figures 2a, 2b, A1a). All cited values confirmed.
- Text quotes were checked against the cache text (paper_text / paper.txt / fulltext.txt / paper3.txt), and against `html_check.html` where the LaTeX conversion truncated a passage (2606 Δz < 2 mm, |η| < 2.0 → 2.4, |y*| < 0.8).
- 1810.11822 HEPData cache is empty ("no HEPData record"); its numbers are text-only and were checked against text and figure captions (Fig. 3 mass 140 GeV, Fig. 4 mass 260 GeV).
- 1801.08769 and 1909.04114: no HEPData in cache; text and table values checked against text.

## Omissions (in scope, clearly more relevant than what was extracted)

1. 1909.04114 (paper_text.txt line 435): "Above 300 GeV the most sensitive limits are set by the searches for dijet resonances in the resolved regime produced in association with a jet [63] or with a photon [23]." The note's caveats do not state this. It is directly relevant to the 300–450 GeV coupling limits, and [23] (ATLAS dijet + photon, 225–450 GeV) is in Q1 scope (associated production with ISR photon).
2. 1810.11822 (paper.txt line 261): "The abrupt loss in sensitivity to the coupling constants for resonance masses greater than 2 m_t is because the branching fraction to bb̄ falls steeply as the decay to tt̄ becomes kinematically allowed." The note's caveats omit this. It bears on the top end of the 50–350 GeV coupling curves (2 m_t ≈ 346 GeV).
3. 1810.11822 (paper.txt line 274): "This constitutes the first LHC constraint on exotic bottom quark-antiquark resonances below 325 GeV." Not recorded. The source also cites bb̄ searches with masses down to 325 GeV (trigger-level b-tag, refs [10, 11]) and to 450 GeV (refs [6–9], line 84). These are in Q1 scope but are not extracted from this source.
4. 2606.03222 (HEPData Figure 5, `Figure_5_Observed.json`, 119 points, x = 129.96–188.33 GeV; `Figure_5_Expected.json`, 139 points, x = 100.5–188.16 GeV): only the minimum is recorded. The full g_q-vs-mass limit curve is the Q1 coupling result and is not recorded. The note's Open issue 3 flags it as contour-like.
5. 2606.03222 (HEPData Figures 3 groups 1–3 and 5–7; Figures 13–16): Gaussian limits at 15, 20, 25% relative width are not recorded. Generic hadronic resonances are borderline in scope. Figures 17 and 18 theory lines (g_q = 0.2, 1.0) are also not recorded.
6. 2603.21965: no clearly more relevant omission found. The Z′ and scalar results, the ALP and dark-photon recasts, and the ATLAS comparison above 250 GeV are recorded.
7. 1801.08769: no clearly more relevant omission found. The mass range is 100–220 GeV only, as the note states.

## Notes on out-of-scope items

- The cited CMS g_q range "0.1 to 0.25 over 50–300 GeV" in 1801.08769 (Sec. 1) is a cross-reference. It was not checked and the note says so. It is not directly comparable to 1909.04114's own 0.2/0.4 statements, which are for 2016+2017 combined data.
