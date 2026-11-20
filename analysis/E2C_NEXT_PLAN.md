# E2C sensitivity: remaining ideas (agreed with the user, 2026-11-19)

Context: `SENSITIVITY_PLAN.md` (ideas 1-7), results in `SENSITIVITY_JOURNAL.md`. User, 2026-11-19: keep pursuing the
E2C as the search observable although the m_SD template fit is stronger (VV 19-20 vs 14-15, ZH 4.9-5.5 vs 1.2-1.6).
Figure of merit unchanged: Z_shape with MC statistics, 326.03 fb^-1, stat only, at stable points (both half-sample Z
within 10%), plus the DY shape chi2/ndf.

## Contents
- [Common inputs](#common-inputs)
- [1. Boson-pT x dR](#1-boson-pt-x-dr)
- [2. Other observables (idea 4)](#2-other-observables-idea-4)
- [3. Constituent choice (idea 5)](#3-constituent-choice-idea-5)
- [4. Jet-free EECs (Phase B2)](#4-jet-free-eecs-phase-b2)
- [5. Theory shape for DY (idea 7)](#5-theory-shape-for-dy-idea-7)
- [Open technical issue: tight working points](#open-technical-issue-tight-working-points)
- [Proposed order](#proposed-order)
- [Questions](#questions)

## Common inputs
- Items 1 and 5 use the existing tables (`sens_tables_20261119{,b}.coffea`; DY p_T^ll > 200, full statistics).
- Items 2-4 need `20261119_jetfree` (CRAB, not yet complete; merge with `--allow-missing`, see
  `simulation/JOURNAL.md`). What it holds (`simulation/configs/ZX_jetfree.yaml`):
  - AK8 reco and gen jets with their constituents, **charged only** (`constituentCuts.chargedOnly: true`), PUPPI
    weights applied, no PV details;
  - `RecoEvtAllJet`: all packed PF candidates + lostTracks, |η| < 2.4, no PV cut, no PUPPI weighting, with `fromPV`,
    `dz`, `dxy`, `puppiWeightRaw`, `puppiWeightNoLep`, `source`; `GenEvtAllJet`: all stable gen particles but
    neutrinos, |η| < 2.4. Both without the selected leptons of every passing channel (old single-collection layout).
  - Samples: DY p_T^ll 400-600 and 600+ (~10% of the files each), WZ, ZZ, ZH(bb) in full. So DY starts at
    p_T^ll = 400 and has ~10x fewer MC jets than the existing tables.
- Consequence: every comparison in items 2-4 must be made **within this production**, against the AK8 charged E2C
  recomputed there from the constituents (the bindings close on the production tables within 1e-4, journal
  2026-11-19), not against the numbers above.
- Tool: E2C/E3C from constituents with `bvana/eecext.py` (`projected_enc`, N = 2-6, energy-weight power n, ΔR), then
  the same `bvana/sensitivity.py` statistics. New: a table processor that builds per-jet E(N)C vectors from the
  constituent tables (offline, condor).

## 1. Boson-pT x dR
- x = p_T^ll · ΔR instead of p_T^jet · ΔR (idea 3; the Z pT as the hard scale).
- Needs: table columns `e2cn1ptlldR`, `e2cn2ptlldR` in `configs/sensitivity.yaml` (to check: whether a dilepton pT can
  appear in `var`), table rerun on condor, scans as in `scans_20261119.yaml` (1/5/10 slices, gpV / pnXbb / gpV).
- Expected: like jet-pT·ΔR (removes the need for pT slicing); the question is whether it beats it.
- We should also try binning in the boson pT
  - Decided: the 1/5/10 pT slices defined in p_T^ll instead of jet pT, with x = ΔR and x = p_T^ll · ΔR.
- We should also make some plots which compare the resolution with which either the boson pT or the jet pT reconstructs the pT of the true hadronically decaying boson. (ie histograms of (pT^true - pT^reco)/pT^true).
  - Default unless told otherwise: truth = the AK8 `axisTruth` hadronic boson (status 0), signal samples (WZ, ZZ, ZH)
    only, per jet-pT and Z-pT bin. Decided: also DY, with truth = the recoiling hard-process parton (`axisTruth`
    status 3).

## 2. Other observables (idea 4)
- Projected E3C (N = 3) and its ratio to the E2C; generalised energy weights, e.g. n = 1/2, 2 (the bindings take any real n).
- Resolved E3C shape variables (triangle shapes) are **not** in the bindings (`projected_enc` only): a C++/pybind
  addition, only if the projected E3C shows promise.
- Resolved E3C can be straightforwardly implemented with the `Extra` machinery in the EECs library.
  - Decided: coordinates (R_L, ξ = R_S/R_M, φ); in the C++ library, the bindings and the NANO producer, but not
    enabled in any production yet: computed offline until the details are settled.
- Each alone and jointly with the E2C (as for n = 1 + n = 2).

## 3. Constituent choice (idea 5)
- Charged constituent ptMin (e.g. 0, 0.5, 1, 2 GeV): directly from the AK8 constituents.
- PV association (`fromPV`, |dz|) and PUPPI-weight threshold: the AK8 constituents have no details; join them to
  `RecoEvtAllJet` by `srcIdx` (to verify: both index `packedPFCandidates` the same way).
- Charged + neutral: not stored for AK8 in this production. Options: (a) recluster AK8 from `RecoEvtAllJet` with
  fastjet (PUPPI-weighted) and match to the stored jets; (b) take all candidates within ΔR < 0.8 of the jet axis
  (approximate); (c) wait for a production with `chargedOnly: false`.
      - Lets take option (b). It should be close enough

## 4. Jet-free EECs (Phase B2)
- E2C of all particles in |η| < 2.4 except the Z leptons, norm p_T^Z, no jet boundary (arXiv:2608.14793 Eq. (6)),
  from `RecoEvtAllJet` (reco) and `GenEvtAllJet` (gen).
- Variants: 
    - whole event vs recoil hemisphere (|Δφ| > π/2 to the Z); 
    - charged with `fromPV` cut vs all PUPPI-weighted
    - charged with minimum pT 0.2, 0.5, 1, 2 GeV
    - charged with maximum dz and dxy
    - charged with ***minimum*** dxy (including Lost Tracks?) and maximum dz
      - Decided: with and without lostTracks (`source`), compared.
    - Decided cut values: max |dz| 0.1, 0.2 cm; max |dxy| 0.05, 0.1 cm; displaced: min |dxy| 0.02, 0.05, 0.1 cm.
- ΔR range up to ~5 (log bins).
- Compare with the AK8 charged E2C in the same events (Z_shape and DY distortion), and the gen vs reco shape (pileup).
- Trap: the 6/132822 DY 600+ reco events where both channels pass lose all four leptons (old layout); drop them.

## 5. Theory shape for DY (idea 7)
Deferred until the user has read arXiv:2608.14793. Options (a) jet-free observable matching their definition
(item 4 is the prerequisite), (b) their factorised form as a constrained DY shape, (c) ask the authors for Z+X grids.

Still defer for now ...

## Open technical issue: tight working points
Points at ≤ 1% DY efficiency are unstable: ≤ 40k DY MC jets for 400-800 bins. Options: more DY MC (a production),
a regularised covariance (shrinkage, or an eigenvalue cut-off), or a fixed coarse binning at tight points. Worse in
the jet-free production (10% of DY).

## Decisions on the production and implementation details (2026-11-19)
- `20261119_jetfree` WZ (and later failures of the same kind): merge with `--allow-missing`.
- Resolved E3C binning, a starting point: R_L in the 40 log ΔR bins, ξ in [0, 1] and φ in [0, π/2] in 5 bins
  each; the sensitivity starts from coarser projections (e.g. R_L x ξ) because of the bin count.
- Item 3 option (b): neutrals weighted with `puppiWeightRaw` (the AK8 PUPPI weight), lostTracks excluded.

## Proposed order
1. Item 1 now (existing tables).
2. Implementation of resolved E3C in c++ and python bindings
3. Submission of additional crab jobs to cover the rest of the DY MC (including all pT bins)
   - Decided: current code (zero-pT fix, per-channel layout), new tag, DY only: all of DY 200-400 (286 files) and the
     files of 400-600 (162 of 180) and 600+ (167 of 186) not in `20261119_jetfree`. The analysis reads both layouts.
     Estimate from the `20261119_jetfree` sizes per DY file: 400-600 ~46 GB, 600+ ~73 GB, 200-400 ~60-95 GB (not
     produced with this config yet); total ~180-215 GB of ~330 GB free (EOS quota 1.67 of 2.00 TB used, 2026-11-19).
     Decided: default EOS `outputBase`; a larger area is available from the user if later productions need it.
   - Decided: DY 400-600 and 600+ rerun in full (CRAB cannot skip files: `maxJobs` takes the first N), +~13 GB;
     the 10% DY of `20261119_jetfree` is not used. Open: also rerun WZ, ZZ, ZH (~11 GB) for one layout.
4. When crab jobs are done: run the merging
5. The constituent table processor, closure against the production E2C,
6. Items 4, 3, 2 (continue to defer item 5)

## Questions
- Order and priorities above? Checked and updated
- Item 3, charged + neutral: option (a), (b) or (c)? Inline
- Items 2-4 working points: only baseline and loose (≥ 3% DY efficiency) because of the DY statistics, or a regularised
  covariance first? Submission of more crab jobs. For now stick with only baseline and loose
- Item 4: pileup is in the reco sample; is the gen-level comparison enough for now, or should a pileup study
  (e.g. `fromPV` / PUPPI variants vs gen) be part of it? For now comparison with gen is good enough