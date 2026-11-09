# Step 1 check-in: literature (2026-11-06)

Answers to the three step-1 questions in `planning/plan.tex`, a proposal for the mass and pT ranges, and the decisions needed from you.

Every number below is copied from `limits.md`, `polarization_fL.md` or `spin_density_matrix.md`. Those tables were built only from the verified per-paper notes in `notes/`. Row labels (R#) refer to `limits.md`.

The proposals in Section 4 are my judgement and are marked as proposals.

## Contents
1. Q1: current limits on hadronic resonances
2. Q2: longitudinal fractions vs pT
3. Q3: full spin density matrix vs pT
4. Proposed mass and pT ranges (proposal)
5. Competitiveness
6. Decisions needed and open issues
7. Process summary

## 1. Q1: current limits on hadronic resonances (`limits.md`)

The table has 71 rows from 32 papers. Limits above 1 TeV are kept and flagged `OUT`.

- **10–20 GeV.** One number only: CMS γ + boosted jet (R2), which states "g′_q greater than 0.3" excluded over 10–125 GeV. There are no per-mass values and no observed/expected label. There is no σ×B limit at these masses.
- **20–100 GeV.** The only per-mass tabulated limits are:
  - ATLAS γ + large-R jet (R3). Observed / expected g_q are 0.122 / 0.134 at 20 GeV and 0.096 / 0.118 at 60 GeV, for a vector Z′.
  - CMS ISR + two-prong jet (R10, R11). R10 gives g_q 0.0357 / 0.0386 at 50 GeV and 0.132 / 0.132 at 300 GeV, for a spin-1 Z′ with equal couplings to all quark flavours. R11 covers spin-0.

  The other results in this range are text statements whose curves are figure-only (R5, R7, R8, R9).
- **Spin-0 / ALP.** There is no limit below 50 GeV. For 50–300 GeV there are only the CMS boosted results R8, R9, R11 and R14 (R14 is the paper's own ALP recast).
- **Analysis method below 200 GeV.** Every LHC limit uses a hard ISR photon or jet, with one exception: R17–R19 (ATLAS pile-up dijets, 1.30 pb⁻¹ effective), whose best g_q is 0.28 at 150 GeV. Boosted single-jet ISR searches stop at 450 GeV (R7). Above that, coverage is resolved dijets.
- **500 GeV–1 TeV.** Couplings from resolved dijets:
  - ATLAS trigger-level dijets (R37): g_q 0.040 / 0.054 at 850 GeV.
  - CMS wide-jet dijets (R47, R50): g′_q 0.0373 / 0.0572 at 1 TeV (R50).
- **Caveat: coupling conventions differ.** CMS g′_q = g_B/6 (Dobrescu–Yu, 1306.2629 Eq. 6), ATLAS axial-vector g_q, and R10's flavour-universal g_q are different conventions. No note gives a conversion between them. The values above are therefore not ranked against each other.

## 2. Q2: longitudinal fractions vs pT (`polarization_fL.md`)

- **Hadronic W measurements exist only at LEP.** L3 measured hadronic-W f_0 = 0.215 ± 0.042 ± 0.039 (hep-ex/0301027, Table 3). No hadronic or boosted W/Z measurement exists at hadron colliders; the only entries in that class are theory (2610.38688; 2207.03511).
- **The highest-pT longitudinal quantities are leptonic Drell–Yan angular coefficients A0, not fractions.** All are in the Collins–Soper frame. Values are A0 ± stat ± syst.
  - Z, ATLAS 8 TeV (1606.00689): pT^Z 253–600 GeV, A0 = 0.964667 ± 0.0235584 ± 0.0100706. A separate regularisation-bias uncertainty of 0.0216611 is reported.
  - Z, CMS 13 TeV (2604.25678): 200–400 GeV, A0 = 0.92154 ± 0.01507 (stat) −0.00555/+0.0056 (syst), |y| < 1.
  - Z, CMS 8 TeV (1504.03512): open last bin 200–9999 GeV, A0 = 0.928 ± 0.035 ± 0.015.
  - W, ATLAS 13 TeV low-pileup (2509.13759): 210–600 GeV, A0(W⁻) = 1.856 with stat 0.4725, and A0(W⁺) = 1.143 with stat 0.2530.
- **W+jets helicity fractions stop at p_T^W > 50 GeV.** They are in the helicity frame (1203.2165; 1104.3829), e.g. ATLAS f_0 = 12.7 ± 3.0 ± 10.8 %.
- **Diboson (WZ).** The only pT-binned result is ATLAS f_00 at p_T^Z > 200 GeV: 0.13 +0.09/−0.08 (stat) ± 0.02 (syst) (2402.16365). It is a joint fraction, not a single-boson one. All other diboson and VBS results are inclusive, such as:
  - WZ f_00 = 0.067 ± 0.010 (2211.09435);
  - ZZ f_LL = 0.080 ± 0.017 (2607.12879);
  - VBS polarized cross sections and limits.
- **Top decays and LEP have no pT binning.** Top-decay W has F_0 between 0.684 and 0.722, with total uncertainties of about 0.015 (ATLAS 13 TeV) to 0.081 (Tevatron). LEP has longitudinal fractions of 21.8 % (L3) and 23.9 % (OPAL).
- **"f_L" means two different things in the corpus.** In the LHC and top papers it is the left-handed fraction. In OPAL it is the longitudinal fraction. Each row says which.

## 3. Q3: full spin density matrix vs pT (`spin_density_matrix.md`)

- **pT-differential multi-element results exist only for leptonic Drell–Yan.**
  - Z A0–A7: up to 600 GeV (ATLAS 8 TeV) and 400 GeV (CMS 13 TeV); CMS 8 TeV and LHCb give A0–A4 or subsets.
  - W A0–A7: up to 600 GeV (ATLAS 13 TeV), with large uncertainties.
  - These are angular coefficients. They are not normalised ρ_λλ′.
- **Off-diagonal elements have been measured only inclusively.**
  - LEP WW: Im ρ CP/CPT combinations from OPAL, binned in cos θ_W.
  - ATLAS H→ZZ* (2603.26463): two tensor-basis coefficients, C₂,₁,₂,₋₁ = −0.71 ± 0.45 and C₂,₂,₂,₋₂ = 0.08 ± 0.44, and rejection of the separable |00⟩ hypothesis at 4.7σ.
- **Hadronic decays lose information that leptonic decays keep.**
  - At LEP, hadronic W decays fold ρ_++ and ρ_−−. Off-diagonal elements were measured with leptonic decays only (OPAL hep-ex/0312047; L3 hep-ex/0301027, where the quark charge is not reconstructed).
  - Theory (2610.38688, App. D): the hadronic energy flow probes ρ_00, ρ_+− (via cos 2Φ and sin 2Φ) and ρ_+0 − ρ_0− (via cos Φ and sin Φ).
  - So a jet-substructure measurement can in principle reach ρ_00 and some interference terms, but not ρ_++ and ρ_−− separately. This is a source statement for leptonic vs hadronic decays at LEP and a theory statement for jets. It has not been demonstrated for jets.
- **Complete map from A_i to helicity-basis fractions f_λ.** The exact conversion is given in 1203.2165 Eq. 4-5:
  - f_0 = (1/2)A_0
  - f_L = (1/4)(2 − A_0 ∓ A_4), f_R = (1/4)(2 − A_0 ± A_4)
  - f_L − f_R = ∓A_4/2
  - Upper sign for W⁺, lower sign for W⁻.
  - This maps CS-frame A_i to helicity-frame fractions directly.
- **Partial maps stated elsewhere:**
  - A_i ↔ unnormalised H_mm′ (1606.00689 App. A);
  - α/γ ↔ tensor-basis A, C (2409.16731);
  - helicity ρ ↔ energy-correlator structure functions (2610.38688).

## 4. Proposed mass and pT ranges (proposal, for you to decide)

**Mass, physics case.** Target **10–450 GeV**, emphasising **10–50 GeV and spin-0**. The literature is thinnest below 50 GeV: only one text value in 10–20 GeV, and no spin-0 limit below 50 GeV. Above 450 GeV, boosted single-jet ISR searches stop and resolved dijets give couplings of about 0.04.

**Containment.** I take ΔR ≃ 2m/pT from `planning/plan.tex` (citing 2610.38688) and require the decay to fit in an AK8 jet, 2m/pT < 0.8, so pT ≳ 2.5 m. This is my own application of the plan's formula, not a literature result. It gives:

| mass | minimum jet pT for AK8 containment |
|---|---|
| 10 GeV | 25 GeV |
| 50 GeV | 125 GeV |
| 91 GeV (Z) | 228 GeV |
| 450 GeV | 1.1 TeV |

At the low end, the trigger rather than containment will set the reach. Current searches below 200 GeV all need a hard ISR photon or jet, or scouting/trigger-level data.

**pT for polarization.** Target hadronic W/Z with **pT ≳ 200 GeV up to ~1 TeV**, about 200 GeV being the AK8 containment threshold for W/Z from the same formula. That region has no measurement of any kind. The leptonic reference points there are:
- Drell–Yan A0 for Z up to 600 GeV with an uncertainty of about 0.02–0.03;
- W A0 up to 600 GeV with an uncertainty of about 0.25–0.47;
- the WZ joint f_00 above 200 GeV with about ±0.09.

## 5. Competitiveness

- **Resonances.** A new search would compete most directly below 50 GeV, especially for spin-0, and in 10–20 GeV. There the existing constraints are a single text number or nothing. At 50–300 GeV, CMS R10 already gives g_q ≈ 0.03–0.13. Whether we can beat that needs a sensitivity study (step 2 onwards). The convention issue in Section 1 must be settled before any number is compared.
- **Polarization.** Any hadronic or boosted measurement of ρ_00 or of interference terms would be the first of its kind. A hadronic-V measurement is not directly comparable with leptonic A0 precision until a map (2610.38688 / 2409.16731 / 1606.00689 conventions) is fixed for our observable.

## 6. Decisions needed and open issues

1. **Ranges.** Accept, change or reject the proposal in Section 4.
2. **Coupling conventions.** I propose to obtain a stated conversion between CMS g′_q, ATLAS axial-vector g_q and the flavour-universal g_q (from the original model papers) before quoting any "we beat X" number. Nothing in the corpus states one.
3. **Missing full texts.** Three papers have abstract and HEPData only: ins335604 (Mirkes 1992, Nucl. Phys. B 387, 3), ins355978 (UA2 1993 dijets, NPB 400, 3), and ins298412 (UA2 1991 W/Z → jj, Z. Phys. C 49, 17). If you can provide PDFs, I will extract them.
4. **Unresolved source disagreements**, kept as flags in the tables:
   - 1606.00689: HEPData A0−A2 vs the paper; the paper is consistent with A0 and A2 separately.
   - 1806.00843: g_q at 3.7 TeV, text vs HEPData.
   - 2607.20246: uncertainties in HEPData vs the paper's Table 5.
   - 2603.21965 and 2606.03222: text ranges vs HEPData.
   - Several HEPData tables give no units, or don't say which particle's mass is on the axis.
5. **Not done from the plan.** I did not extract published high-pT V+jets cross sections, which are needed to set a Run-3 event-count scale (item (d) of Phase 7 in `PLAN.md`). I propose doing this at the start of step 2.
6. **Proposed edit to step 4 of `plan.tex`** (text only; the file is not changed). Add explicit sensitivity targets for ρ_+− and ρ_+0 − ρ_0−, not only the longitudinal fraction. The energy flow is stated to probe these (2610.38688 App. D), while hadronic decays fold ρ_++ and ρ_−−.
7. **No LHCb resonance limit is among the deep-read papers.** The LHCb entries are Z angular coefficients only.

## 7. Process summary

- **Corpus.** 414 candidates, 64 of them deep-read, including 2008.04174, which a verifier found late.
- **Extraction.** Every note was extracted by a Haiku agent and checked by at least one independent verifier. Fixed rows were then re-checked.
- **Summary tables.** All three were checked row-by-row against the notes and the sources. Results are recorded in `reports/` and in each table's verification record.
- **Two pipeline bugs found and fixed:**
  - HEPData error pages saved as tables;
  - double-encoded table URLs.

  Both bugs are covered by tests (11 pass).
- **Logs.** Full history in `progress.log.md`, findings in `journal.md`, and BibTeX for all deep papers in `refs.bib`.
