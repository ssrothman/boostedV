# verify_w2_4 (transcribed by the lead from the verifier's returned message; the verifier did not write this file itself)

Claim files: ins355978, ins298412, ins356676, 1805.09299, 1901.10917.

Counts: CONFIRMED 242, MISLABELED 5, MISMATCH 2, UNSUPPORTED 2, WRONG_LOCATION 0, UNVERIFIABLE 0 (two omissions are UNVERIFIABLE).

| claim file | row/claim | verdict | evidence | suggested fix |
|---|---|---|---|---|
| ins298412 | sqrt(s) = 630 GeV "(HEPData Table 1 qualifier; abstract)" | MISLABELED | No "630" in the INSPIRE abstract or the Springer copy; it is in HEPData 15084 Table 1 qualifier "630.0 GeV" and its data_abstract | cite HEPData only |
| ins298412 | 5.8 nb expectation, energy "(abstract)" | MISLABELED | value and quote correct; energy not in the abstract | energy source = HEPData 15084 |
| ins356676 | Axigluon MT B2 N=10 "240 ≤ Ma ≤ 730", "Table 3, p. 17; text p. 11" | MISLABELED | Table 3 (PDF p.19) correct; text p.11 says 240–640 for N=10 with no structure function | drop "text p. 11" |
| ins356676 | Open issue "pdftotext returns nothing for pp. 16-17" | MISMATCH | pdftotext -layout returns the table text on PDF p.18/p.19 (OCR layer); values still correct | replace with: scan has an OCR text layer; values checked against page image |
| ins356676 | report number "CDF/ANAL/JET/CDF/2064" | MISMATCH | PDF p.1 "CDF/ANAL/.JET/CDFR/2064"; INSPIRE "CDF-ANAL-JET-CDFR-2064" | CDF/ANAL/JET/CDFR/2064 |
| ins356676 | "CDF Run 0 (1988-1989 run)" | UNSUPPORTED | paper says "1988-1989 run" (p.6), never "Run 0" | drop "Run 0" |
| 1901.10917 | "fit ranges 169–1100 GeV, Sec. 5" | MISLABELED | sentence occurs only after the "7 Conclusion" heading | Sec. 7 |
| 1901.10917 | BumpHunter "p > 0.5 for all distributions" | MISLABELED | source: "Without including systematic uncertainties, the BumpHunter p-value ... is p>0.5 for all distributions." | add the qualifier |
| 1901.10917 | Open issue: Sec. 7 fb values match HEPData "digit for digit" after ×1000 | UNSUPPORTED | no units in HEPData; agreement only to rounding (0.01205→12.05 vs 12; 0.02116→21.16 vs 21; 0.00505→5.05 vs 5.1; 0.00972→9.72 vs 9.7) | say units not stated; agreement to rounding if pb assumed |

Omissions:
- a. ins355978: excited-quark and W/Z σ limits vs mass (abstract only) — UNVERIFIABLE, no full text.
- b. ins298412: heavy vector boson → jj σ limit vs mass (abstract only) — UNVERIFIABLE, cached paper.pdf is an HTML landing page.
- c. ins356676: Table 2 limits computed with "QCD (MT-B2, μ = pT/2)" (text p.10) — add to the Table 2 row.
- d. 1805.09299: 389 of 475 out-of-window HEPData points not recorded (lead: intended under the Row-volume rule; all 69 in-window points present and match).

Checks passed (summary): 1805.09299 all 155 recorded HEPData rows and 54 band rows match, observed = group 0 / expected = group 1 consistent with caption; 1901.10917 all 44 rows of Tables 5–8 match (obs/exp from HEPData headers); ins356676 all 15 Table 2 rows match PDF p.18 page image, Table 3 matches p.19; ins355978 abstract quote verbatim; ins298412 9.6 nb (2.3 stat, 1.1 syst) matches HEPData 15084.
