# Questions and assumptions log (axes and polarimetry work, 2026-11-17)

Raised during the autonomous run. Each entry: the question, what the code does meanwhile, and where.

## Contents
- [Open questions](#open-questions)

## Open questions
1. **Soft-drop jets without MiniAOD subjets.** 57 of 2182 dev jets pass the MiniAOD soft-drop input cut (raw pt > 100,
   |y| < 2.4) but have no `SoftDropPuppi` subjets. All have raw pt < 170 GeV and fail our selection. Mechanism not
   found. Meanwhile: ignored (outside the selection). `JetSetup/test/validation/checkSoftDrop.py`.

***RESPONSE***: So long as they all are outside our selection, I think it's okay. 

2. **Subjet membership mismatches (0.6% of jets).** These are attributed to MiniAOD packing. The perturbation test
   flips all 12, but the perturbation sizes are estimates, not taken from the `PackedCandidate` code. Meanwhile:
   accepted.

***RESPONSE***: I think the diagnosis in terms of MiniAOD packing is convincing. Accepted

3. **Subjet JER details (my choices).**
   - Gen subjets: the MiniAOD `slimmedGenJetsAK8SoftDropSubJets` (central gen soft drop, which is also what NanoAOD
     calls `SubGenJetAK8`).
   - Match: dR < R/2 with R = 0.4 (the AK4 payload) and |Δpt| < 3σ, using our existing `jerMatch`.
   - JER after the JEC; seed per (event, jet srcIdx, subjet index), salt 11.
   - Not done: JES/JER subjet variations, and the JMS/JMR uncertainties (nominal only so far).

***RESPONSE***: Looks good

4. **Corrections on the other axes.** Only the production-like soft drop (`axisSoftDrop`) gets JEC and JER. The
   variants (β=1; z_cut=0.05), trimming and WTA use raw constituents. Should the variants also be corrected?

***RESPONSE***: Axes built from the raw constituents should not get JEC and JER. 

***REPLY (Claude)***: That is the current state, so nothing changes. Only `axisSoftDrop` (production parameters, validated against MiniAOD)
gets subjet JEC/JER. The soft-drop variants, trimming, WTA and recoil are built from the raw PUPPI-weighted
constituents.

***RESPONSE 2***: Good

5. **Recoil axis.** φ = φ(boson) + π of the first back-to-back channel that passes, in config order (Zmumu, then Zee);
   η = jet η. Events passing both channels use Zmumu.

***RESPONSE***: Is there not an `extra lepton` veto in the channel definitions that percludes overlap between Zmumu and Zee? If there is not, there should be.

***REPLY (Claude)***: No, there is none. The `dilepton` channel type has no `vetoes` field in the schema, and `DileptonSelector.cc` has no
veto. Only `leptonMET` and `singleObject` have one. Measured overlap: 0 of 429 selected events pass both Zmumu and Zee
(1000-event DY PTLL-400to600 dev file, reco and gen).

Proposed mechanism: a required `vetoes` list for `dilepton`, as for the other types. The event fails if any object in
those collections is not one of the two selected leptons. Before I implement it, **which objects should it veto?**
- ZX_test defines only `looseMuons` and `looseElectrons`, with kinematic cuts only (no ID, no isolation). Vetoing
  those would also reject non-prompt leptons inside the jet (semileptonic b/c decays), which biases the jet sample.
- I propose new veto objects with ID and isolation, like `default.yaml`'s `vetoMuons` (pt > 10, CutBasedIdLoose,
  PFIsoLoose) and `vetoElectrons` (pt > 10, cut-based veto ID).
- Then one of:
  (a) other flavour only. This is the minimum that precludes the overlap.
  (b) any lepton besides the pair ("exactly two leptons"). This also removes WZ → 3ℓ and ZZ → 4ℓ.

  My recommendation is (b).

***RESPONSE 2***: I agree with recommendation (b). Please implement it. Make sure that when we veto on the same species as the dilepton selection (e.g. third-muon veto) we don't accidentally self-veto with the selected pair. 

***REPLY 2 (Claude)***: Will do. I'll start once the running signal NANO production (Q19) has finished, about 13:00. The running jobs
read the EventSelection python and `ZX_test.yaml` when they start, so changing them now would mix two selections in
one sample.

Plan:
- A required `vetoes` list for `dilepton`.
- `DileptonSelector` rejects the event if any veto-collection candidate is not one of the two selected leptons. The
  selected pair is excluded by source identity (same PAT object, i.e. the same `edm::Ptr` key in the source
  collection), not by ΔR.
- New objects in ZX_test: `vetoMuons` and `vetoElectrons`, as in `default.yaml`. Zmumu and Zee both veto
  [vetoMuons, vetoElectrons]. Gen: the dressed-lepton equivalents.
- Unit test: a pair plus a third same-flavour lepton must fail. A pair whose own legs pass the veto cuts must pass.
  This is the self-veto case, and I'll check that the test fails if the exclusion is removed.
- Also a cmsRun check that Zmumu ∩ Zee = 0, and the change in selected-event counts.

***Update (Claude, 18 Nov)***: Done, with one change from the plan above. The pair is excluded by ΔR < 0.01, not by
object identity. That is the existing rule of the `leptonMET` veto (`evsel::countExtra`). Identity across separately
selected PAT collections is not reliable, because the selectors copy the objects, while a lepton and its copy in the
veto collection have identical directions. Also changed: `default.yaml` (the schema now requires `vetoes`), the
schema, the cff, `NANO.md`.
- Module tests: 65 pass. Mutations: no pair exclusion → 2 failures; no veto → 4 failures.
- Config tests: 40 pass, including the new wiring and required-key checks.
- 1000 DY events: reco Zmumu 192 → 187, Zee 176 → 174; gen 214 → 214, 206 → 205; Zmumu ∩ Zee = 0; no event gained.
- Limitation: with reco dressing, each collection is dressed on its own (as for `leptonMET`); no configuration dresses.

6. **Truth axis.** The nearest last-copy W or Z (not H) with a quark or gluon daughter, ΔR < R (0.8), from
   `prunedGenParticles`. In data, and when there is no match, the axis is the jet (Status 2).

***RESPONSE***: Looks good.

7. **WTA recombination.** `WTA_pt_scheme` (boost-invariant), not `WTA_modp_scheme`.

***RESPONSE***: What is the difference?

***REPLY (Claude)***: From the fastjet 3.4.1 header (`JetDefinition.hh`, the version in CMSSW_15_0_22):
- `WTA_pt_scheme`: the merged object takes the rapidity, azimuth and mass of the input with the larger pT, and pT =
  pT1 + pT2.
- `WTA_modp_scheme`: it takes the 3-direction and mass of the input with the larger |p|, and |p| = |p1| + |p2|.

The pT version is boost-invariant along the beam, consistent with the (y, φ) clustering metric. The |p| version is the
natural choice in e+e−. At hadron colliders the convention is `WTA_pt_scheme`. In our central boosted jets the
"winner" is almost always the same in both schemes, so I expect a negligible difference, but I have not measured it.
No change, unless you want both.

***RESPONSE 2***: Makes sense. pt scheme is the correct choice. 

8. **Charge E2C weight.** `E2CChargePt` = Σ Q_i Q_j pT_i pT_j / pT_jet² is implemented, and `Charge` and
   `ChargeEnergy` modules also exist. Which variant(s) do you want?

***RESPONSE***: We want plain `Charge` NOT `ChargePt` or `ChargeEnergy`. Please fix. 

***REPLY (Claude)***: Done.
- Removed: the `ChargePt` and `ChargeEnergy` producer modules I had added (E1C and pENC). The library's weight
  policies were already there (committed, with their own tests), so they stay.
- Schema: `weight` is now `Energy | Pt | Charge`, and the config check uses `Charge` only.
- `polarimetryObservables.yaml`: `E2CCharge` (weight `Charge`, n = 1, `DeltaR`, norm `unity`) replaces `E2CChargePt`,
  and `E1CLabChargePt` is gone. `E1CLabCharge` stays (it was already plain charge).
- `NANO.md` is updated.

Tests:
- The config tests pass (40 tests; `ChargePt` now has a rejection test), and the merged held-back config loads.
- cmsRun on the 1000 DY events, 395 reco jets:
  - Σ(weight × symmetry factor) = (Σ Q)² exactly, so self-pairs are included at ΔR = 0 (library convention).
  - Σ(weight × sym × ΔR) equals Σ_{i≠j} Q_i Q_j ΔR_ij from the stored constituents to 1e-5. This would fail for any
    pT- or E-weighted variant.

***RESPONSE 2***: Good. 

9. **Held-back observables.** A and B live in `configs/polarimetryObservables.yaml` and are merged in by hand, so they
   don't run in the axis-study production. Tested on 300 DY events with sum rules.

***RESPONSE***: Good

10. **Axis observables and variations.** Axis E1C tables exist only for the nominal jets. The config rejects them in
    the aggregation.

***RESPONSE***: Good.

11. **Charged-hadron PUPPI weights are often not 0 or 1.** In 300 DY PTLL-400to600 reco jets, 555 of 3310 charged
    constituents (16.8%) have 0 < w < 1 (the zero-weight ones are already dropped). This contradicts the assumption
    behind "no PUPPI cut for charge observables". Charge weights count these fully.

***RESPONSE***: I think it's still okay --- these will overwhelmingly have weights which are very close to one. 

***REPLY (Claude)***: Agreed, the data support this. On the 1000 DY events (10574 charged constituents in 395 reco jets):
- 83.5% have w = 1 and 16.5% have 0 < w < 1.
- Among the fractional ones, the median is 0.996 (probably MiniAOD's 8-bit weight packing, 254/255) and 90% are
  above 0.82.
- Only 2.5% of all charged constituents have w < 0.9 and 0.3% have w < 0.5. These are soft (median stored pT
  0.9 GeV vs 3.2 GeV for w = 1).
- Per-jet charge: mean |Σ Q − Σ wQ| = 0.15, against an rms of Σ Q of 3.4.

No cut.

***RESPONSE 2***: Good. we can revisit as needed.

12. **PUPPI-scaled candidates in the rest-frame boost.** The C++ scales the whole four-vector by w (mass w·m_π). bvana
    assigns m_π to the scaled momentum. The boost closes to 1e-4 rad only for w = 1 pions with p* > 0.5 GeV. Particles
    nearly at rest in the boson frame (p* → 0) have ill-defined angles but small weights. 7 of 2737 unit-weight
    charged pions carry a stored mass that is not m_π beyond float precision (unexplained).

***RESPONSE***: I think it's okay. 

13. **Spin-density conventions.** The decay matrix uses Wigner D-functions (Condon–Shortley) with λ ordered (+1, 0, −1).
    The fermion is the decay product with pdgId > 0. The frame is z = V direction, x toward the beam on the V side. The
    diagonal shapes are tested (sin²θ; (1+cosθ)² for λ = −1 with a left-handed fermion). A geometric test fixes the
    off-diagonal phases: the m = −1 state rotated to +x (Wigner R(0, π/2, 0)) gives a fermion distribution peaked along
    +x (`tests/test_spin.py`). Not yet compared with the paper's convention (App. D: "up to a sign convention for x")
    or a published extraction. A theory reference or colleague is needed before quoting off-diagonal values.

***RESPONSE***: I need more detail about what you have done in order to assess it.

***REPLY (Claude)***: What the code does (`analysis/bvana/spin.py`):

*Frame.* For each LHE W/Z (status 2) with exactly two status-1 daughters, both are boosted to the V rest frame (pure
boost from the lab). z is the V lab direction. x lies in the (V, beam) plane, pointing toward the beam on the V's side
(sign of V pz), so y = z × x. "The fermion" is the daughter with pdgId > 0 (the quark, the charged lepton ℓ−, or the neutrino). (θ, φ) is its direction in that frame. This is the same convention as our jet
frames (`frames.axisKinematics`), and it is tested with hand-computed kinematics (`tests/test_spin.py`).

*Decay distribution.* For massless fermions only σ = λ_f − λ_f̄ = ±1 contributes. P(σ = −1) = (1 + A_f)/2 with
A_f = 2g_V g_A/(g_V² + g_A²); A_f = 1 for W and neutrinos. With D_{λσ} = e^{−iλφ} d¹_{λσ}(θ) (Wigner d,
Condon–Shortley), λ ordered (+1, 0, −1):

  W(θ,φ) = (3/4π) Σ_σ P_σ Σ_{λλ'} ρ_{λλ'} D*_{λσ} D_{λ'σ}.

Expanded symbolically (sympy, from exactly this definition), W = (3/16π) × [
  (1 + cos²θ)(ρ++ + ρ−−) − 2 A_f cosθ (ρ++ − ρ−−) + 2 sin²θ ρ00
  + 2 sin²θ (cos2φ Re ρ+− − sin2φ Im ρ+−)
  + 2√2 sinθ cosθ [cosφ Re(ρ+0 − ρ0−) − sinφ Im(ρ+0 − ρ0−)]
  − 2√2 A_f sinθ [cosφ Re(ρ+0 + ρ0−) − sinφ Im(ρ+0 + ρ0−)] ].
For A_f = 1 and ρ−− = 1 this gives (1 + cosθ)², i.e. the fermion follows a helicity −1 boson's spin.

*Extraction.* There is no fit. W contains only spherical harmonics with l ≤ 2, so the nine weighted moments
⟨Y_lm⟩ fix the nine real parameters linearly. In closed form:
- ρ00 = (1 − 10⟨P₂(cosθ)⟩)/3, and ρ++ + ρ−− = 1 − ρ00.
- ρ++ − ρ−− = −2⟨cosθ⟩/A_f.
- Re ρ+− = (5/2)⟨sin²θ cos2φ⟩, and Im ρ+− = −(5/2)⟨sin²θ sin2φ⟩.
- Re(ρ+0 − ρ0−) = 5√2⟨sinθcosθ cosφ⟩, and Im(ρ+0 − ρ0−) = −5√2⟨sinθcosθ sinφ⟩.
- Re(ρ+0 + ρ0−) = −(√2/A_f)⟨sinθ cosφ⟩, and Im(ρ+0 + ρ0−) = (√2/A_f)⟨sinθ sinφ⟩.

The code builds this inverse numerically (exact Gauss–Legendre quadrature of W per unit parameter). I checked
today that the closed forms above equal the code's matrix to 7e-15. The statistical covariance is the sample
covariance of the moments (signed event weights), propagated linearly.

*What is tested.*
- Shapes: L gives sin²θ, and helicity −1 with A_f = 1 gives (1 + cosθ)².
- Closure: decays sampled from random valid density matrices are recovered within errors, for two values of A_f. A
  wrong A_f fails the test.
- Swapping fermion and antifermion (θ → π − θ, φ → φ + π, A_f → −A_f) gives the identical ρ.
- Off-diagonal phases: the helicity −1 state rotated by +90° about y (into +x) must give a fermion distribution
  peaked along +x, i.e. Re ρ+0 < 0 in this convention.

*What is not verified.* Whether this convention (the sign of x, the phase convention of the states) matches the
paper's App. D or any published extraction. The diagonal entries and ρ+− are convention-independent up to the
direction of x. The signs of Re/Im ρ+0 and ρ0− flip with x → −x (and Im parts with y → −y).

*Relevance.* Only for quoting truth off-diagonal values next to a reference. ρ00 is not affected.

***RESPONSE 2***: This looks good to me :). 

14. **Z couplings.** A_f uses tree-level couplings at the generator's sin²θ_W (`truthRho.py --sin2`, default 0.2229;
    see 16). γ*/Z interference inside the LHE "Z" is ignored.

***RESPONSE***: What is the impact of this? On the spin analyzing power? Is there anything more precise we can do?

***REPLY (Claude)***: A_f enters only the three l = 1 combinations: ρ++ − ρ−− and Re/Im(ρ+0 + ρ0−). Each scales as 1/A_f (see the closed
forms in 13). The other six (ρ00, ρ+−, ρ+0 − ρ0−, and the trace) do not depend on A_f or sin²θ.

*Impact on the measurement.* A jet does not tell the quark from the antiquark. Our jet observables are therefore
symmetric under θ → π − θ, φ → φ + π, so they see only the parity-even part. The coupling choice does not affect
ρ00 or anything measured from the jet. It matters for:
(i) the truth parity-odd entries;
(ii) the leptonic-vs-hadronic cross-check;
(iii) later, the charge-weighted observables, where the l = 1 sensitivity is ∝ A_q × charge-tagging power.

*Sizes.* sin²θ_W 0.22263 (Powheg) vs 0.23154 (MadGraph DY) changes A_ℓ = 0.2164 vs 0.1469 (47%), A_u = 0.698 vs
0.667 (4.5%), and A_d = 0.941 vs 0.936 (0.6%). So only the leptonic parity-odd entries are sensitive.

*γ*/Z interference.* It is present in both samples: Powheg ZZ is generated with `mllmin 4d0`, so γ* is included, and
MadGraph DY ℓℓ includes γ*. Within the mass window, the pure γ* part has A = 0 and the interference term changes
sign across the pole. The effective analysing power therefore depends on m_ℓℓ and differs from the tree-level Z
value. I have not quantified this.

*More precise options.*
(a) Use each generator's own sin²θ_W. Done; see 16.
(b) Measure the effective A_ℓ(m_ℓℓ) from the sample itself. In ZZ with both Z on shell, the leptonic and hadronic Z
    have the same ρ, so the ratio of their l = 1 moments in m_ℓℓ bins gives A_ℓ,eff/A_q with no theory input.
(c) For the truth of the hadronic measurement, use the hadronic decay. A_q barely depends on sin²θ, and the γ*
    fraction is the same physics there.

I recommend (c) as the truth definition, with (b) as a cross-check if the leptonic parity-odd entries are ever
needed.

***RESPONSE 2***: Okay what you say makes sense. A few follow-up questions:

 - What is the physical intuition for why the sin^2 theta_w matters so much more for leptons than quarks? 
 - How hard would it be to quantify the impact of gamma interference? If we can, it would be nice to do. 
 - I agree, we should use the hadronic truth as the benchmark for the hadronic measurement. 

***REPLY 2 (Claude)***: 
*Why leptons are so sensitive.* A_f = 2g_V g_A/(g_V² + g_A²) with g_A = T₃ and g_V = T₃ − 2Q sin²θ_W.
- Charged leptons: g_V = −1/2 + 2 sin²θ_W ≈ −0.055. That is an almost exact cancellation, so A_ℓ ≈ 2g_V/g_A ∝
  (1 − 4 sin²θ_W), a small difference of two numbers near 1. A shift of 0.009 in sin²θ_W changes 1 − 4 sin²θ_W from
  0.110 to 0.074, i.e. 47%.
- Quarks, smaller charge, no cancellation: g_V(u) = 1/2 − (4/3) sin²θ_W ≈ 0.20 and g_V(d) ≈ −0.35. The same shift
  moves A_u by 4.5%. A_d ≈ 0.94 sits near its maximum, where it is flat (0.6%).
- The same smallness of g_V(ℓ) makes the leptons sensitive to γ*/Z interference. The Z-only parity-odd term carries
  the small g_V(ℓ), but the γ*–Z interference term carries Q_ℓ g_A(ℓ), which is not suppressed.

*γ*/Z interference, measured.* Data: 24 unselected ZZ LHE files, 538809 events with a Z → ee/μμ and an in-window
hadronic Z. In bins of m_ℓℓ, I compare the leptonic ρ++ − ρ−− (tree A_ℓ) with that of the hadronic Z in the same
events. The ratio is A_ℓ,eff(m)/A_ℓ,tree × A_q,tree/A_q,eff, and without interference it would be flat.
File: `~/nobackup/boostedV/axisStudy_20261118/gammaInterference.md`.

| m_ℓℓ (GeV) | 4–40 | 40–66 | 66–81 | 81–87 | 87–90 | 90–92 | 92–95 | 95–101 | 101–116 |
|---|---|---|---|---|---|---|---|---|---|
| ratio | 0.00 ± 0.04 | −1.7 ± 0.3 | −3.0 ± 0.5 | 0.14 ± 0.27 | 0.43 ± 0.15 | 0.96 ± 0.10 | 1.33 ± 0.15 | 2.1 ± 0.3 | 3.9 ± 0.6 |

- The effective analysing power changes sign below the pole and grows above it, the A_FB(m) pattern.
- At 4–40 GeV the ratio is 0, as a pure photon (vector coupling) must give. This validates the method.
- ρ00 (parity-even) agrees between leptonic and hadronic Z in every bin.
- Window-averaged ratio: 0.950 ± 0.067 (66–116), 0.959 ± 0.067 (the channel's 61.2–121.2) and 0.982 ± 0.068
  (±10 GeV). The odd interference term largely cancels across the peak, so the window-integrated leptonic
  parity-odd truth is unaffected within the 7% statistical precision. The unselected-LHE production (15) would bring
  that to about 2–3%.
- Any m_ℓℓ-dependent weighting, e.g. acceptance varying across the window, would not cancel.
- Hadronic side: by the same argument it is much less affected (larger g_V(q), smaller |Q|). It is not separately
  measured here, since it is the reference.

15. **Truth ρ from unselected LHE.** `simulation/configs/lheNano_cfg.py` writes LHE tables for every event, because the
    selected ZX_test NANOs bias the decay angles through the acceptance. High-pT statistics need many inclusive ZZ files
    (most of ZZto2L2Q is at low pT). Should this become a CRAB/condor production?

***RESPONSE***: Yes, I agree this is a valuable to-do. In the meantime: how large is the bias? Can we learn anything from the events which pass the selection? 

***REPLY (Claude)***: The bias is large at low pT.

Method:
- Hadronic Z (66–116 GeV) in ZZto2L2Q.
- "Selected": all 149 NANO files of the `20261116_zxb2b` production. The event passes reco Zmumu or Zee, and a
  table jet (pT > 200, |η| < 2.4, ID) lies within ΔR < 0.4 of the LHE Z.
- "Unselected": the 24 unselected LHE NANOs, which are independent events, so the errors add.
- In bins of LHE V pT; script `~/nobackup/boostedV/axisStudy_20261118/selectionBias2.py`.

| V pT | ρ00 unselected | ρ00 selected | difference | acceptance in \|cos θ*\| (0–0.2 … 0.8–1), mean 1 |
|---|---|---|---|---|
| 200–300 | 0.085 ± 0.016 | −0.061 ± 0.009 | **−0.145 ± 0.019** | 0.95 0.96 0.90 1.03 1.16 |
| 300–400 | 0.106 ± 0.035 | 0.035 ± 0.013 | −0.071 ± 0.037 | 0.94 1.00 0.97 1.01 1.08 |
| 400–600 | 0.101 ± 0.053 | 0.030 ± 0.019 | −0.070 ± 0.057 | 0.97 0.97 0.97 0.98 1.11 |
| > 600 | 0.02 ± 0.12 | 0.02 ± 0.04 | 0.00 ± 0.13 | 1.02 1.10 0.95 0.95 0.99 |

What we learn from the selected events:
1. The selection favours |cos θ*| → 1, i.e. asymmetric q q̄ energy sharing along the boost, by about 15% at
   200–300 GeV, fading above 600. That alone pulls the moment estimate of ρ00 down. At 200–300 the result is even
   negative, so the sculpted distribution is no longer a valid density matrix. The truth must come from unselected
   (or fiducially defined) events, and the bias is far larger than the statistical precision we are after.
2. I have not identified the mechanism. A plausible candidate is the jet-pT threshold and the back-to-back pT
   balance cut acting on LHE-V-pT bins (migration), but this is a hypothesis, not tested.
3. The acceptance is a smooth function of cos θ* per pT bin. It is measurable from selected events plus an
   unselected denominator, so in principle the selected moments can be acceptance-corrected (weight 1/A). In the
   measurement that is part of the response/unfolding anyway.

Statistics: the unselected denominator now limits this (805 events at 400–600). That is the case for the
unselected-LHE production. Selected events are 8× more numerous.

***RESPONSE 2***: This is reported on the hadronic decay right? I'm surprised the bias is so large for boosted decays --- I expected the quarks would just be inside the boosted jet. Can we assess the source of the bias? If it is from some aspect of the selection that can be easily tweaked, that would be important to know. 

***REPLY 2 (Claude)***: Yes, it is the hadronic Z (quark angles in its helicity frame). The source is found: the quarks are often *not*
inside the jet at these pT.

*Geometry.* ΔR(q, q̄) ≈ 2m/(pT sin θ*). That is about 0.73 for a symmetric decay at pT = 250 GeV, and larger for
asymmetric ones. Fraction of unselected decays with ΔR(q, q̄) < 0.8, per |cos θ*| bin (0–0.2 … 0.8–1):

| V pT (GeV) | 0–0.2 | 0.2–0.4 | 0.4–0.6 | 0.6–0.8 | 0.8–1 |
|---|---|---|---|---|---|
| 200–300 | 0.56 | 0.46 | 0.27 | 0.07 | 0.00 |
| 300–400 | 1.00 | 1.00 | 0.96 | 0.65 | 0.09 |
| 400–600 | 1.00 | 1.00 | 1.00 | 0.97 | 0.36 |

Full containment needs pT ≳ 2m/R ≈ 230 GeV (Z) or 200 GeV (W) even for symmetric decays.

*Mechanism.* My label "channel" was misleading: `Selection_Zmumu` already includes the back-to-back requirement
(leading AK8 jet with pT > 200, Δφ > 2.8, pT balance < 0.3). That is why adding the matched jet changed nothing.
An uncontained symmetric decay gives two jets of about pT/2 each, which fail pT > 200. An asymmetric decay survives
as a single hard-quark jet. So the acceptance rises toward |cos θ*| = 1, and ρ00 drops. Only 48% of the selected
jets at 200–300 contain both quarks.

*Confirmed by emulation.* The selection is emulated on unselected LHE events: quarks merged into one jet when
ΔR < R, other partons as jets, plus lepton cuts. Script:
`~/nobackup/boostedV/axisStudy_20261118/emulateSelection.py`.

| V pT 200–300 | ρ00 |
|---|---|
| unselected | 0.098 ± 0.020 |
| leptons only | 0.033 ± 0.036 |
| full emulation | −0.25 ± 0.05 |
| without the balance cut / without the Δφ cut | −0.24 / −0.25 |
| jet pT > 150 | −0.10 ± 0.04 |
| quarks merged at R = 1.2 (containment restored) | 0.073 ± 0.040 |

The jet-pT threshold acting on uncontained decays is the cause; the balance and Δφ cuts don't matter. At
300–400 and 400–600 the emulation shows no bias. In the production, 300–400 shows −0.07 ± 0.04 (2σ), which more
statistics would settle. The emulation exaggerates the 200–300 effect (no hadronisation, no ISR, LHE pT bins).

*Possible tweaks.*
(a) Measure polarimetry only for V pT ≳ 300 GeV, either via the binning or by raising `pairPtMin` or the jet pT to
    300. That is a decision for you.
(b) Larger-R jets would restore containment, but there is no standard calibrated collection.
(c) Lowering the jet pT threshold only halves the bias.

*A bigger warning, from the same study.* Requiring a two-prong jet sculpts far more:
- Both quarks inside the jet: ρ00 = 1.24 / 0.80 / 0.49 / 0.20 at 200–300 / 300–400 / 400–600 / > 600, against a
  truth of about 0.1.
- m_SD in 70–110: ρ00 ≈ 0.8 at every pT, including above 600.

Soft drop with z_cut = 0.1 removes decays whose softer quark carries < 10%. Since z ≈ (1 + cos θ*)/2, that is
|cos θ*| > 0.8: the acceptance in the last |cos θ*| bin drops to 0.2. So any groomed-mass window, or a tagger that
relies on it, cuts directly into the polarisation-sensitive region. This is inherent to such a selection, not to our
thresholds. It matters for how the signal region is defined (we currently bin in m_SD). It needs a decision before
the measurement design is fixed: avoid mass/tagger cuts, or unfold through them with the full angular response.

16. **sin²θ_W per generator.** The Powheg ZZ/WZ header says "using mW, mZ. gmu scheme". On-shell 0.2229 (assumed
    mW = 80.385) makes the ZZ leptonic and hadronic ρ agree (χ² 6.3/8 vs 40/8 at 0.2315). The actual mW/mZ are not in
    the header (defaults in ZZ/smcouplings.f). The MadGraph DY value is not checked: the leptonic parity-odd entries
    of DY are uncertain until it is.

***RESPONSE***: Again I need more detail about how rho is extracted to understand what we need and assess what to do about it. 

***REPLY (Claude)***: The extraction is described in 13. sin²θ_W enters only through A_f, and only in the three parity-odd combinations
(14). Both generator values are now pinned down from the generators themselves:
- **Powheg ZZ and WZ**: `ZZ/smcouplings.f` and `WZ/smcouplings.f` (POWHEG-BOX-V2 svn trunk, last changed r2479 in
  2013) set mZ = 91.1876 and mW = 80.399, with G_μ = 1.166364e-5 and sin²θ_W = 1 − mW²/mZ². That gives
  **sin²θ_W = 0.22263**. My earlier 0.2229 assumed mW = 80.385 (A_ℓ 0.2143 vs 0.2164, 1%).
  - The `truthRho.py` and `axisStudy.py` defaults are now 0.22263.
  - Caveat: the gridpack header says "no svn repository found", so the revision used is not recorded. The file has
    not changed since 2013.
- **MadGraph DY** (`sm-ckm_no_b_mass`, from the LHE header of the DY PTLL-400to600 sample): aEWM1 = 128.8253,
  Gf = 1.166379e-5, MZ = 91.15351. That gives MW = 79.907 (also printed in the header) and **sin²θ_W = 0.23154**. DY
  must be run with `--sin2 0.23154`. With the old default, the DY leptonic parity-odd entries were too small by a
  factor 0.147/0.214; ρ00 and the other parity-even entries are unaffected.

*Re-check on 24 freshly processed ZZ files (both Z on shell), leptonic vs hadronic Z, all 9 entries:*
- At 0.22263: χ²/8 = 16.8 (pT < 100), 6.0 (100–200) and 7.4 (> 200). The ρ++ − ρ−− pulls are −1.0, +1.5 and +1.1.
- At 0.23154: χ²/8 = 71.5 at pT < 100, with a ρ++ − ρ−− pull of −6.6. This still clearly rejects the MadGraph
  value for Powheg.
- The pT < 100 value (p ≈ 0.03) is new; the earlier, different file set gave 6.3/8. It comes from 1.5–2.4σ shifts
  spread over several entries (ρ00, Re ρ0−, ρ−−), not from the parity-odd entry. The leptonic and hadronic Z come
  from the same events, which this χ² treats as independent. Above 100 GeV, our region, there is no tension.

I'll note it and not chase it further unless you want me to.

***RESPONSE 2***: Makes sense, and sounds good. 

17. **Diboson truth ρ needs both bosons on shell** for a leptonic-vs-hadronic comparison. Which definition should the
    "truth" for the measurement use? Only the measured boson in the window, or both?

***RESPONSE***: In order to compare apples-to-apples we need to apply the same selections on both leptonic and hadronic channels. This comparison is just a cross-check anyway. For the final measurement I think we have to accept off-shell hadronic states (just because we have no way to controll the hadronic mass). I imagine the cross-section is dominated by on-shell production anyway? 

***REPLY (Claude)***: Agreed. Since the hadronic mass can't be controlled, the measurement truth should follow the selection: the leptonic Z
in the channel's m_ℓℓ window, and the hadronic boson unrestricted. The lep/had cross-check keeps both in the window.

Unselected LHE (24 ZZto2L2Q files), weighted (i.e. cross-section) fractions for the hadronic Z:

| V pT | hadronic Z in 66–116 | partner also on shell, given hadronic on shell | both on shell |
|---|---|---|---|
| all | 0.61 | 0.52 | 0.32 |
| > 200 GeV | 0.935 | 0.83 | 0.77 |
| > 400 GeV | 0.91 | 0.83 | 0.75 |

So yes, at our pT the hadronic Z is about 93% on shell. The low inclusive numbers come from γ* down to
m_ℓℓ = 4 GeV at low pT.

ρ00 of the hadronic Z for the three definitions (none / hadronic in window / both in window):

| V pT | none | hadronic in window | both in window |
|---|---|---|---|
| 100–200 | 0.157 ± 0.006 | 0.159 ± 0.006 | 0.157 ± 0.007 |
| 200–300 | 0.082 ± 0.016 | 0.085 ± 0.017 | 0.088 ± 0.018 |
| 400–600 | 0.09 ± 0.05 | 0.10 ± 0.05 | 0.14 ± 0.06 |

The definitions agree within the statistics above 100 GeV. Below 100 GeV they differ strongly (0.25 / 0.22 / 0.34),
which is the population effect seen before.

***RESPONSE 2***: Looks good. 

18. **L/T reweighting in `analysis/axisStudy.py`.** It reweights by the LHE quark polar angle only, relative to the
    unselected truth ρ00 in each LHE V pT bin, so the jet acceptance cancels. Validated on unselected LHE: ρ00 → 1.005 ±
    0.005 (L) and 0.008 ± 0.008 (T). Parity-odd and off-diagonal terms are not removed, so ρ++ − ρ−− = −0.12 remains in
    "pure L". Fine for an axis-bias comparison, not a pure-state sample. Proper polarised samples are still to be
    generated (plan.tex).

***RESPONSE***: Is the only way to get "pure" samples a dedicated production? 

***REPLY (Claude)***: No. In order of exactness:
- (1) **Dedicated polarised generation.** MadGraph5_aMC@NLO generates helicity-selected intermediate W/Z (Buarque
   Franzosi, Mattelaer, Ruiz, Shil, JHEP 04 (2020) 082, arXiv:1912.01725). This is exact, including the correlations
   with the rest of the event. Powheg has no such option. Costs: a new LO MadGraph sample, a different generator
   from our nominal one, and a production.
- (2) **Per-event matrix-element reweighting** of the existing events. Compute |M_λ|² per helicity from the LHE
   kinematics with a standalone helicity-amplitude code (e.g. MadGraph standalone output), and weight by
   |M_λ|²/Σ|M|². This is exact per event (up to interference between helicities, which a pure state drops by
   definition) and needs no new events. It is substantial work: the processes, γ* diagrams, and a per-event
   evaluation.
- (3) **Full-matrix angular reweighting** (a cheap upgrade of today's method). Weight = W_pure(θ,φ)/W_true(θ,φ), using
   all 9 truth ρ entries per bin and A_f per flavour, not only ρ00. That removes the parity-odd and off-diagonal
   residuals (e.g. ρ++ − ρ−− = −0.12 in "pure L") in the bin average. It stays approximate because ρ varies within a
   bin and with the rest of the event, which finer pT × |y| bins reduce. The weights stay finite, since W_true > 0
   for a valid ρ.

For the axis comparison, (3) is enough and is about an hour's work: shall I do it? For templates and closure of the
real measurement, (1) is the standard.

***RESPONSE 2***: I think we can leave it for now, but we may need to return to this point. 

19. **Axis study, 24 signal files (16 ZZ + 8 WZ; 2127 reco / 2263 gen truth-matched jets).** ρ00 sensitivity
    ⟨P₂⟩_T − ⟨P₂⟩_L of the rest-frame-energy-weighted E1C, paired differences (same jets) against the truth axis:
    - jet, soft drop (all three) and trimming are consistent with truth (|Δ| ≤ 0.016 ± 0.011–0.017, reco and gen).
      Against the jet axis, the soft-drop and trimming axes gain +0.012 to +0.018 ± 0.002 (reco).
    - WTA (C/A and kT alike) loses −0.070 ± 0.009 against truth, about half the sensitivity; recoil loses −0.09 ±
      0.02. WTA follows the harder prong (median ΔR to truth 0.155 vs 0.044 for the jet axis).
    So WTA and recoil can be dropped. Between jet, soft drop and trimming the sample cannot decide (truth-axis
    sensitivity is 0.13 ± 0.01). Should I submit a full signal production to settle it, or choose on other grounds
    (pileup and grooming robustness, available systematics)? Files: scratchpad `sig/axes_full_{Reco,Gen}.md`.

***RESPONSE***: I think we need a bunch of histograms of Delta R(axis, truth) plus the relevant summary statistics. 

***REPLY (Claude, 18 Nov)***: Done. The histograms, median and quantile plots and the summary table are in the AN,
Appendix B.6, and in `~/nobackup/boostedV/axisStudy_20261118/dR/`. The NANOs were regenerated (23 files; a 24th has no
selected event).

**Correction to the numbers in 19 above.** The study did not require the matched truth boson to be in its mass
window. A few low-mass γ* → qq̄ "bosons" (4–6 GeV, Powheg generates down to 4 GeV) got boosts with γ ≈ 100 and
dominated the weights. `axisStudy.py` and `axisDeltaR.py` now apply the truth windows. The errors shrink by more than
10×. Reco, sensitivity relative to the truth axis (0.149 ± 0.007):
- WTA: −0.060 ± 0.005. Recoil: −0.053 ± 0.007. Both are excluded.
- Jet: +0.008 ± 0.005.
- Soft drop and trimming: +0.020 to +0.022 ± 0.005, which is +0.012 to +0.014 ± 0.001 above the jet axis.

Exceeding the truth axis can't come from knowing the boson direction better. A plausible but untested cause is that
the axis is built from the same particles as the energy flow. So the choice among jet, soft drop and trimming needs
more than sensitivity: the bias of the moments, pileup, and the soft-drop systematics.