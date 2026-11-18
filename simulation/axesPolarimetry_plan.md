# Plan: jet-axis study, charge and energy correlators, rest-frame conversion, truth density matrix

Status 2026-11-17 (end of the autonomous run): steps 1-5 implemented and tested; step 6 (axis comparison) has a
first small-sample run (`analysis/axisStudy.py`). Questions: `axesPolarimetry_questions.md`. Context: comparison with arXiv:2610.38688 (Sec. V, App. D).

## Contents
- [1. Goal](#1-goal)
- [2. Jet axes](#2-jet-axes)
- [3. A: charge correlators](#3-a-charge-correlators)
- [4. B: energy-weighted correlators](#4-b-energy-weighted-correlators)
- [5. C: lab to rest-frame conversion in bvana](#5-c-lab-to-rest-frame-conversion-in-bvana)
- [6. D: truth spin-density matrix from LHE](#6-d-truth-spin-density-matrix-from-lhe)
- [7. Decisions needed](#7-decisions-needed)
- [8. Order of work and runs](#8-order-of-work-and-runs)

## 1. Goal
Choose the helicity axis for the one-point correlators, and prepare the observables and truth references for
polarimetry. Lab frame first: per App. D (Eq. D8), the boost acts pointwise and keeps Φ, so the lab E1C plus a per-jet
axis and γ give every frame offline.

Key design point: an unbinned lab E1C (`E1CLab`, θ′ and φ about the jet axis) plus the jet four-vector reconstructs each
particle's direction exactly. With pT weights, E_i = w_i · pT_jet · cosh η_i. So **re-axing (to any axis stored per jet,
or computed offline) and boosting can both be done in bvana**, on existing productions too. The C++ only has to provide
the alternative axes.

## 2. Jet axes
Computed in the translators (`PATJetToEECJetProducer`, `GenJetToEECJetProducer`) from the **full** PUPPI-weighted
constituents, before `constituentCuts` (which are charged-only in `ZX_test`). Stored as four-vectors on `EECJet`, and
written as jet-table columns `axis<Name>_{pt,eta,phi,mass}`. Missing axis: NaN, plus a status column.

| # | Axis | Definition | Where |
|---|---|---|---|
| 1 | `jet` (current) | jet p4 after JEC/JER (sum of constituent momenta) | exists |
| 2 | `softDrop` | sum of the two soft-drop subjets (β=0, z_cut=0.1, R0=0.8, C/A declustering) | translator (fjcontrib `SoftDrop`), reco and gen alike; MiniAOD `SoftDropPuppi` subjets as a cross-check (reco only) |
| 3 | light grooming, a few variants | e.g. SD β=1 z_cut=0.1; SD β=0 z_cut=0.05; trimming (R_sub, f_cut to be taken from a cited CMS reference) | translator |
| 4 | `wta` | constituents reclustered with C/A and `WTA_pt_scheme` (fastjet 3.4.1 in CMSSW_15_0_22), axis = the jet's WTA direction | translator |
| 6 | `recoil` | Z(ℓℓ) channels: φ = φ(ℓℓ) + π, η = jet η | bvana, offline |
| 7 | `truth` | LHE V (status 2, pre-shower) and the GenPart last-copy V, matched to the jet by ΔR | bvana, offline |

Axis 5 (charged-only momentum sum) is dropped (user, 2026-11-17).

Metrics (signal: ZZto2L2Q, WZto2L2Q; background: DY PTLL bins), in bins of pT and `PV.npvsGood`:
- ΔR(axis, truth V).
- E1C moments ⟨P₂(cos ϑ)⟩, ⟨cos 2Φ⟩, ⟨sin 2ϑ cos Φ⟩ (Eq. D5) about each axis, minus the same moments about the truth axis.
- The same moments after reweighting signal to pure L or pure T with the LHE quark decay angle (§6). An axis whose bias
  differs between L and T sculpts ρ00.
- For gen-level observables, the truth axis is the reference itself.

## 3. A: charge correlators
- Schema: allow `weight: Charge | ChargeEnergy | ChargePt` (the library already has them; `EECConversion` attaches
  `EECParticleInfo`).
- The App. D charge flux F (Eq. D1) is E1C with `weight: Charge`, `norm: unity`, in the lab frame (`jetAxis`).
- Charge weights get no PUPPI suppression: a pileup charged hadron with a small nonzero PUPPI weight counts fully.
  Zero-weight candidates are already dropped (`ConstituentFill.h:26`). A `minPuppiWeight` cut is needed for charge
  observables (value: decision).
- Config entries added, but **not run** until the axis is settled.

## 4. B: energy-weighted correlators
In addition to the pT ones, **not run** until the axis is settled:
- `E1CLabE`: `weight: Energy`, `norm: jetE`, frame `jetAxis` (App. D Eq. D8 normalisation, 4π/E_V).
- `E2CEn1`: `weight: Energy`, `norm: jetE`; angle `Angle3D` (z′ of the paper) or `DeltaR` (decision).

## 5. C: lab to rest-frame conversion in bvana
New module `bvana/frames.py`, exposed as derived EEC fields chosen per histogram in the YAML, e.g.
`frame: {axis: softDrop, boost: none | mJet | mV | mSoftDrop}`:
1. Particle directions from (θ′, φ) of `E1CLab` and the jet p4 (the exact inverse of `makeFrame(JetAxis)`).
2. Re-axis: θ′, φ about the chosen axis, x toward the beam on the axis side (the `jetAxis` convention).
3. Boost along the axis with β and γ of the axis momentum and the chosen boson mass. Every constituent is assigned the
   charged-pion mass (user, 2026-11-17), at reco and gen level alike, so the observable is defined identically at both
   levels. Reco PF charged hadrons already carry m_π±.
   - p from the weight (p = pT cosh η, or p = √(E² − m²)), and E = √(p² + m_π²).
   - Boost: p∥* = γ[(1−β)E − m_π²/(p+E) − 2p sin²(θ′/2)] (cancellation-free form), p⊥* = p sin θ′,
     E* = γ(E − β p cos θ′). Then ϑ = atan2(p⊥*, p∥*), Φ unchanged, weight E*/M.
   - 1−β = m²/(E_axis(E_axis + p_axis)).
4. Collins–Soper: a fixed per-jet rotation of the rest-frame axes (optional).

Tests:
- Closure against the C++ `E1CHelicity` and `E1CCS` on the same jets (axis `jet`, boost `mJet`). This should agree up
  to the massless approximation; measure and report the size of the difference.
- Re-axing to the original axis is the identity.
- Mutation check: perturbing β or the x-axis sign must fail the closure.

## 6. D: truth spin-density matrix from LHE
Verified on `20261116_zxb2b` ZZto2L2Q (2000 events): `LHEPart` has the intermediate V (pdgId 23, status 2), the decay
products (status 1) and `firstMotherIdx`/`lastMotherIdx`. This resolves the extra parton (a gluon in the events
checked, but it can be a quark of the decay flavour).
- Per V: the fermion's (ϑ, Φ) in the helicity frame. z is the V lab direction; x lies in the (V, beam) plane on the
  beam side of sign(V pz), the same convention as our jet frames. The CS frame is also computed, to compare with the
  literature.
- A₀–A₇ by moments (e.g. A₀ = 4 − 10⟨cos²ϑ⟩, A₄ = 4⟨cos ϑ⟩), then ρ via the fermion analysing power
  A_f = 2g_V g_A/(g_V² + g_A²). The mapping and the moment formulas are taken from a verified reference in
  `literature/notes/` (to be cited in the code; `CS_to_helicity_mapping.md` is not yet sufficient).
- Consistency:
  - ZZ: leptonic Z vs hadronic Z in the same bins of V pT and |y|. The parity-even entries (ρ00, Re ρ+−,
    Re(ρ+0 − ρ0−)) should agree directly. The parity-odd entries should agree after dividing by A_ℓ or A_q, per quark
    flavour.
  - Expected differences: γ*/Z interference, singly-resonant diagrams, finite width. Mass windows 66–116 GeV (Z) and
    60–100 GeV (W), as in the paper.
  - Also: DY (leptonic Z) vs ZZ leptonic Z, WZ hadronic W, and the paper's ρ00(γ) (Fig. 4, figure only: qualitative).
- Tests:
  - Synthetic decays sampled from known A₀–A₇ recover them within statistical uncertainty.
  - A frame test with hand-computed kinematics.
  - Mutation: swapping the fermion and antifermion must flip the parity-odd coefficients.

## 7. Decisions (user, 2026-11-17)
1. Soft drop: recomputed in our translators, reco and gen.
   - Validation: with the production parameters and the GT AK4PFPuppi L2L3 JEC, the subjets and the soft-drop mass
     must match MiniAOD `SoftDropPuppi` / `groomedMass('SoftDropPuppi')` jet by jet.
   - Then V4 AK4PFPuppi JEC on the subjets, and recompute `msoftdrop` with them (closes the `TODO.md` soft-drop item).
   - Jets with 1 subjet: axis = that subjet, flagged. Jets with 0 subjets: axis = the jet axis, with a separate flag.
   - On the 1000 DY PTLL-400to600 dev events (2088 MiniAOD AK8 jets, pT > 200 GeV): 86.5% have 2 subjets, 11.8% have
     1, 1.6% have 0.
2. Light-grooming variants as proposed in §2.
3. WTA: both C/A and kT.
4. Charge: both E1C and E2C, no PUPPI cut for now (the user says charged-hadron PUPPI weights are almost all exactly 0
   or 1).
5. Energy E2C: `DeltaR`.
6. Truth ρ: helicity frame only, no CS. The density-matrix elements are computed directly, not through A₀–A₇. Formulae
   to be researched (candidate: Aguilar-Saavedra & Bernabéu, arXiv:1508.04592, not yet read) or asked of theory
   colleagues.
7. The rest-frame conversion lives in bvana.

8. Re-axing in C++: one lab E1C table per axis (and per weight), written for the **nominal jets only**. bvana does only
   the boost (§5).

## 8. Order of work and runs
1. Soft drop in the translators. Validate it against MiniAOD (production parameters and GT JEC), then switch to V4 JEC
   and recompute `msoftdrop`.
2. The other axes (trimming and soft-drop variants, WTA C/A and kT; recoil and truth from event inputs) and the
   per-axis lab E1C tables (nominal jets only).
3. C: the boost in bvana, with a closure test against `E1CHelicity`.
4. D: the truth ρ from LHE, after the formulae are verified.
5. A and B: config and schema now, production after the axis decision.
6. One production of signal plus DY. Compare the axes; decide.
