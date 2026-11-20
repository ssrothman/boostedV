# Signal-sensitivity study plan (2026-11-19; Phase A done; remaining ideas: E2C_NEXT_PLAN.md; results: SENSITIVITY_JOURNAL.md)

## Contents
- [Starting point](#starting-point)
- [Figure of merit and shape-distortion metric](#figure-of-merit-and-shape-distortion-metric)
- [Phase A: existing NANOs (offline)](#phase-a-existing-nanos-offline)
- [Phase B: needs a new production](#phase-b-needs-a-new-production)
- [Phase B2: jet-free EECs](#phase-b2-jet-free-eecs)
- [Phase C: theory shape for DY](#phase-c-theory-shape-for-dy)
- [Traps](#traps)
- [Open decisions](#open-decisions)

## Starting point
- Productions `20261116_zxb2b`, `20261117_zxb2bbkg`, `20261117_zh`; outputs `plots/20261119_zxall_xsec/` (1 pb^-1).
- `ZmumuBoostedReco`, E2Cn1 stacked: (DY + X)/DY is ~1.025 flat for ΔR < 0.3, rising to ~1.055 at ΔR ≈ 0.6-0.9 (all
  non-DY processes together); WZ and ZZ each ~1.01-1.02 at the peak.
- The NANOs hold the unbinned E2Cn1/E2Cn2 entries (charged constituents, pT weights, `ptMin 0`), E1C tables, jet
  substructure (`msoftdrop`, `tau1-4`, `n2b1`, `n3b1`), GloParT3 and ParticleNet scores, AK4 jets with b tags, MET.
- They hold **no** constituents (`writeConstituents` was not set) and **no** E3C (checked on `cutflow_20261118/`).

## Figure of merit and shape-distortion metric
Proposal (to confirm):
- Significance: Z = sqrt(s^T C^-1 s), s the signal E2C vector over (x, jet pT) bins and C the stat covariance of the
  total E2C built jet by jet (sum over jets of w_j w_j^T, x lumi), from the unbinned entries. EEC bins are correlated
  within a jet, so a per-bin Poisson Asimov formula overstates Z. Stat only; later a normalisation-free version
  (shape only) by profiling the total yield.
- Distortion: chi2/ndf of the unit-normalised DY E2C after vs before a cut, with the same jet-level covariance, plus the
  ratio plot. A cut "passes" if it does not create a DY local structure in the peak window.

## Phase A: existing NANOs (offline)
1. Selection scan (idea 1): boson pT and jet pT thresholds, |η_jet|, pT balance and Δφ(j, Z), m_ll window, MET upper
   cut and AK4 b-tag veto against ttbar (conflicts with ZH(bb): report per process), Zee + Zmumu combined.
2. Extra discriminants (idea 2), each as a cut scan with Z and distortion:
   - jet: mass-decorrelated GloParT3 (Xqq + Xcs + Xbb + Xcc) / (... + QCD), n2b1, tau21, charged multiplicity
     (q/g), `msoftdrop` (expected to sculpt, kept as a reference);
   - dilepton: |y_Z|, |y_Z - y_j|, the Z decay angle cos θ* of the lepton (ZV and Z+jet have different Z
     polarisation), number of extra AK4 jets.
3. E2C variants computable now (idea 3): n = 1 vs 2 and their combination; x = ΔR, pT_jet ΔR, pT_ll ΔR (peak alignment
   across pT bins); binning and fit window.
4. Per-jet E2C selection (idea 6): per-jet peak-window weight fraction, e.g. ∫_{0.6}^{1.5 · 2m/pT} E2C / ∫ E2C, or a
   per-jet likelihood ratio of the E2C entries; scan Z vs distortion.

## Phase B: needs a new production
On a reduced set of samples (DY 400-600 and 600, WZ, ZZ, ZH bb), with `writeConstituents=1`, so that ideas 3 to 5
become offline studies:
- other observables (idea 4): projected E3C, resolved E3C (shape variables), generalised energy weights n;
- constituent choice (idea 5): ptMin, charged + neutral, PUPPI-weight threshold. PV association (`fromPV`, dz) and
  displacement are not in the constituent table; adding them is a code change in the NANO producer.

## Phase B2: jet-free EECs
Requested 2026-11-19. Reference definition, arXiv:2608.14793 Eq. (6) and Sec. 2 (read verbatim): projected ENC over
**all final-state particles except the boson's decay products**, |η| < 2.4, weights ∏ p_T,i / p_T,V^N, angle
R_ij = sqrt(Δη² + Δφ²), all N-tuples of the event ("not partitioned by any jet boundary"). Prediction for γ+X only.
Why it may help: no AK8 boundary (the Z peak 2m/pT ≈ 0.6-0.9 at pT 200-300 sits at the jet edge), a direct theory
comparison (idea 7), and the boson pT as the hard scale.
Risks: pileup (the paper only argues insensitivity in general; ~60 PU vertices give large summed pT at |η| < 2.4),
UE/MPI and extra jets add background pairs exactly at large ΔR, where the low-pT peak is.
What exists: the EECs library takes any particle set and an external norm; `ReclusterEECJetProducer` clusters any
candidates but has no |η| cut, PV association or removal of the selected leptons. Needed (C++, Phase B):
- a candidate filter: |η| < 2.4, charged and PV-associated (or PUPPI-weighted all), minus the selected leptons (and
  their dressing photons); gen: stable visible particles minus the gen leptons;
- one event-level pseudo-jet per selected event, norm = boson pT, binned output (Dense/SparseMerged in ΔR up to ~5;
  O(10^4-10^5) pairs per event make Unbinned impractical);
- variants to compare: whole event vs recoil hemisphere (Δφ to Z > π/2); charged-PV vs PUPPI all.
Test on a reduced production (DY 400-600, 600, WZ, ZZ, ZH bb) against the AK8 E2C with the same metric.

## Phase C: theory shape for DY (idea 7)
arXiv:2608.14793 (Generet, Lee, Moult, Poncelet, Zhang, 14 Aug 2026): projected ENCs of **all** radiation recoiling
against γ (Z+X named as a future target), **no jet algorithm**, NLO+NNLL, p_T^γ > 500 GeV; no MC or data comparison and
no public code found (middle of the paper read only as a summary). It does not predict our AK8-jet E2C directly. Options:
(a) a jet-free variant of our observable that matches their definition (the V decay peak stays; more UE/pileup at
large angle); (b) use its collinear factorised form as a constrained functional form for the DY shape; (c) ask the authors
for Z+X grids.

## Traps
- E2C is tied to jet mass (∫ ΔR² E2C ∝ m²/pT² at small angle), so mass or mass-correlated tagger cuts sculpt a peak
  into DY at ΔR ≈ 2m/pT. Only mass-decorrelated variables are candidates.
- At jet pT 200-300 GeV the Z peak (2m/pT ≈ 0.6-0.9) sits at the AK8 edge; a larger-R or jet-free observable would
  recover it.

## Open decisions
See the questions put to the user on 2026-11-19 (signal definition, figure of merit and luminosity, scope of Phase B,
route for Phase C).
