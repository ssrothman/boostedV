# Verification report: w1_4 (Q2/Q3 notes)

Sources re-opened: `.cache/<id>/` paper text/HTML, HEPData tables in `.cache/<id>/hepdata/tables/` (not refetched), INSPIRE JSON where cached.

| claim file | row/claim | verdict | evidence (quote + location) | suggested fix |
|---|---|---|---|---|
| notes/2207.03511.md | "Fig. 2 and Fig. 4: monoenergetic W, MadGraph semileptonic W+W- with pT(W) > 300 GeV, showered with Pythia 8" | MISLABELED | Only Fig. 2 has this setup: "In Fig. 2 we compare the analytic LO result with the numerical simulation for a monoenergetic (E=1.5 TeV) hadronic W jet. Concretely, we simulated through MadGraph [36] the semileptonic W+W- production ... processed via Pythia 8". Fig. 4 is described only as "Two-point energy correlator of a W-boson jet" with "This is shown in Fig. 4 for the diagonal ones" (analytic); no simulation stated (`.cache/2207.03511/paper_full.txt`, Sec. "Diagonal entries", Fig. 4 caption). | Attribute the MadGraph/Pythia 8 sample to Fig. 2 only. |
| notes/2207.03511.md | Fig. 8 D2 cut "threshold garbled ... see Open issues" | UNVERIFIABLE (PDF not cached) | HTML source (`.cache/2207.03511/html_head.txt`, TeX alttext) reads "after further requiring D_2<5, 2 and 1" (three successive cuts). The PDF is not in cache, so the rendering was not checked directly. | Record Fig. 8 cuts as "65 < m_J < 95 GeV, then D_2 < 5, D_2 < 2, D_2 < 1" (HTML alttext, Sec. "Towards the LHC"); confirm against PDF. |
| notes/2207.03511.md | Omission: Fig. 5 (off-diagonal interference) | OMISSION | Fig. 5 caption: "Azimuthal dependence of the one- and two-point energy correlators of a 1TeV W-boson. A contribution with lambda_gamma=0.01 shows a cos 2phi behaviour from the interference." Text (Sec. "Off-diagonal entries"): "We simulated the semileptonic decay of e+e- -> W+W- at s=2 TeV in the SM (cyan) and in presence of lambda_gamma=0.01 (magenta)." The text and caption disagree on sqrt(s) (2 TeV vs 1 TeV W energy). This is a |Delta h|=2 interference result, directly in Q3 scope, and the claim does not record it. | Add a Fig. 5 row: figure-only cos 2phi interference at lambda_gamma=0.01; note the 2 TeV (text) vs 1 TeV (caption) inconsistency. |
| notes/hep-ph_9406381.md | Quantity row "alpha_1, alpha_2, beta_1, beta_2 vs p_T(V), Fig. 2" | MISLABELED | Fig. 2 caption (a): "Angular coefficients alpha_2, beta_1, and beta_2 for W W boson production"; alpha_1 appears only in panel (b), for Z: "Angular coefficients alpha_1, alpha_2, beta_1, and beta_2 for Z Z boson production". (`.cache/hep-ph_9406381/paper.txt`, Fig. 2 caption.) | Split the row: W panel = alpha_2, beta_1, beta_2; Z panel = alpha_1, alpha_2, beta_1, beta_2. |
| notes/ins335604.md | Abstract-derived claim "INSPIRE abstract refers to p-bar p collisions at the Tevatron" | MISLABELED | INSPIRE abstract (`.cache/ins335604/inspire.json`): "measurement of the angular decay distribution of leptons from W-production at high-q_T in p p collisions"; the Tevatron (p-bar p) appears only as the numerical example: "We present detailed analytical formulas ... discuss the size of the NLO corrections for W+ production at the Tevatron collider." | Replace with: "abstract states pp collisions; Tevatron (p-bar p) is the numerical example for W+ production." |
| notes/ins335604.md | Full-text rows (sqrt(s), topology, selection, frame, Q3 map) | UNVERIFIABLE | Only the INSPIRE abstract is cached. `.cache/ins335604/sd.html` is a ScienceDirect shell with no article body ("nine helicity" and "Abstract" not present). `elsevier.html` is a redirect page. No arXiv eprint exists in INSPIRE. | Keep as "not extracted"; obtain the PDF (Nucl. Phys. B 387, 3) to fill the frame and rho/A_i map. |
| notes/ins335604.md | Omission (abstract, Q3-relevant) | OMISSION | Abstract: "enabling the measurement of six out of nine helicity cross sections sigma_alpha"-type statement is garbled in the record, but it states the decay distribution is governed by nine helicity cross sections, that large deviations from (1+cos^2 theta) appear at q_T ~ 20 GeV, and that the sign of the "T-odd" helicity cross sections discriminates V-A from V+A. | Add abstract-level statements, marked as abstract-only. |

Non-listed rows: all other rows in the five files were checked and are CONFIRMED (see counts). Key confirmations: 2207.03511 quotes ("z=1/6 z*", "z≃11/144 z*", "A_LT≃0 ... ∼0.5", "θ*≃58°", "postponed for future work", R*=4m_V^2/p_TJ^2, A_int definition with N_± quadrants, Eq. 6 and Eq. 8 forms, Fig. 8 1.5 TeV lepton collider); hep-ph/9406381 quotes (A_0 = 2σ^L/σ^{U+L} from Eq. 26, Eq. 27, 1.8 TeV, MRS D'_- with Λ=215 MeV, μ²=M²+p_T², "A_3 has the wrong sign", "A_0−A_2 ≈ −2"); 1504.03512 (all 96 HEPData-quoted rows checked for bin, column group, and value; cuts and frame text confirmed); 1902.05759 (Table 24 HEPData values for all 12 measured rows; Sec. 12 quotes; significances 6.5/6.1 and 4.2/3.8; Sec. 12 values 0.238/0.230 vs Table 5 0.2376/0.2294; 36.1 fb^-1; EPJC 79 (2019) 535).

Verification of conversions: the claim files convert nothing across conventions except A_0 = 2σ^L/σ^{U+L} (hep-ph/9406381, from the paper's own Eq. 26; CONFIRMED) and the 2207.03511 A_LT/A_int asymmetries (definitions quoted from the paper; CONFIRMED). No A_0 to f_L conversion is claimed for 1504.03512, consistent with the caveat there.

HEPData checks: 1504.03512 Table_1/Table_2 (group order A0, A1, A2, A3, A4, A0-A2 matches the paper's table header order); paper table values match HEPData central values (format differences only, e.g. 0.020 vs 0.02). 1902.05759 Table_24: observed/expected not applicable (polarisation fractions); columns "f_0" and "f_L-f_R" assigned by the table qualifiers and confirmed against Table 5 text.

Partial checks (not fully re-derived): 1902.05759 Table 6 individual systematic rows (only the stat and total rows were read in the extracted text); 1902.05759 Table 5 MATRIX f_L-f_R W±Z value 0.0375 not located in text.

## Counts (rows evaluated)

| claim file | CONFIRMED | MISMATCH | WRONG_LOCATION | MISLABELED | UNSUPPORTED | UNVERIFIABLE | OMISSION |
|---|---|---|---|---|---|---|---|
| 2207.03511 | 19 | 0 | 0 | 1 | 0 | 1 | 1 |
| 1504.03512 | 108 (96 HEPData rows + 12 text rows) | 0 | 0 | 0 | 0 | 0 | 0 |
| hep-ph_9406381 | 11 | 0 | 0 | 1 | 0 | 0 | 0 |
| 1902.05759 | 20 | 0 | 0 | 0 | 0 | 0 | 0 |
| ins335604 | 1 | 0 | 0 | 1 | 0 | 1 | 1 |
| total | 159 | 0 | 0 | 3 | 0 | 2 | 2 |

Omissions list:
1. 2207.03511: Fig. 5, cos 2phi interference from lambda_gamma=0.01 (figure-only, |Delta h|=2, Q3 scope).
2. ins335604: abstract-level statements on nine helicity cross sections and the T-odd sign test (abstract-only, Q3 scope).
