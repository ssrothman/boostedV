# Sensitivity study journal

Plan: `SENSITIVITY_PLAN.md`. Newest entries at the end.

## Contents
- [2026-11-19 Decisions and starting point](#2026-11-19-decisions-and-starting-point)
- [2026-11-19 Tools: per-jet tables and the significance](#2026-11-19-tools-per-jet-tables-and-the-significance)
- [2026-11-19 Jet-free EECs requested](#2026-11-19-jet-free-eecs-requested)
- [2026-11-19 Jet-free collections: code, validation, test production](#2026-11-19-jet-free-collections-code-validation-test-production)
- [2026-11-19 Storage options and MiniAOD completeness](#2026-11-19-storage-options-and-miniaod-completeness)
- [2026-11-19 Phase A results (existing NANOs)](#2026-11-19-phase-a-results-existing-nanos)
- [2026-11-19 Constituents-only production, lostTracks, Python bindings](#2026-11-19-constituents-only-production-losttracks-python-bindings)
- [2026-11-19 Tagger working points and per-pT-slice thresholds](#2026-11-19-tagger-working-points-and-per-pt-slice-thresholds)
- [2026-11-19 Half-sample stability; VV with the bb score, ZH with the V score](#2026-11-19-half-sample-stability-vv-with-the-bb-score-zh-with-the-v-score)

## 2026-11-19 Decisions and starting point
User decisions:
- Signal: VV (WZ + ZZ) and ZH optimised separately, each with the other in the background.
- Figure of merit: stat-only Z of the E2C with the jet-by-jet covariance; DY distortion as the chi2 of the normalised
  DY shape against the baseline. Luminosity 326.03 fb^-1 ("full Run 3", user-given).
- Phase A (existing NANOs) first; a constituent production is decided afterwards.
- arXiv:2608.14793 deferred until the user has read it. Read so far (abstract and the first ~40% verbatim, rest from a
  summary): projected ENCs of all radiation recoiling against a photon, no jet algorithm, NLO+NNLL, p_T^γ > 500 GeV;
  Z+X a future target; no MC/data comparison or public code found.
- Added later: study the E2C binning; document plan, tests and conclusions.

Starting point (`plots/20261119_zxall_xsec/vv/boosted/e2c/E2Cn1_ZmumuBoostedReco.png`): (DY + all others)/DY is ~1.025
for ΔR < 0.3 and ~1.055 at ΔR 0.6-0.9. The NANOs have no constituents and no E3C (checked on `cutflow_20261118/`).
DY is produced only with p_T^ll > 200 (B2B NANOs), so looser Z pT cuts cannot be studied.

## 2026-11-19 Tools: per-jet tables and the significance
- `bvana/tables.py` + config key `tables:`; `configs/sensitivity.yaml` (40 log ΔR bins 1e-3-1.6, E2Cn1 and E2Cn2, jet
  substructure, GloParT3/ParticleNet, Z and negative-lepton kinematics, MET, AK4). Condor `work/sens_20261119`, 80 jobs,
  `--lumi 326030`. The B2B NANOs have exactly one jet per event (checked on one DY file: nJets = 1 for 14194/14194),
  so the per-jet covariance is the per-event one.
- `bvana/sensitivity.py`: C = Σ w v vᵀ (data covariance at the luminosity), Z_tot² = sᵀC⁺s, Z_shape profiles the
  background normalisation; Cmc = Σ w² v vᵀ adds the MC statistical covariance.
- Tests (`tests/test_tables.py`, `tests/test_sensitivity.py`), each verified discriminating by mutation:
  - tables: rows/columns/EEC rows on synthetic events; event-weighted row sum equals the bvana EEC histogram (flow
    included); processor accumulation; AK4 cleaning. Mutations caught 6/6 (no symfactor, cuts OR-ed, ΔR(AK8) flipped,
    no lepton cleaning, bin index shifted, weight ignored).
  - significance: Stats vs explicit block vectors (incl. a jet at a slice edge); one bin per jet reproduces Σ s²/b;
    identical rows reduce to counting S/√N and dropping correlations overstates by √3; shape chi2 for two Poisson bins
    and invariance under a pure normalisation term with correlated bins; merging bins never increases Z;
    cos θ* of a boosted lepton; peak window. Mutations caught 8/8 (Cmc weight power, slice edge side, profile term,
    normalisation Jacobian, boost sign, window factor 2, ...); the Jacobian and slice-edge mutations needed the
    correlated-covariance and edge cases added for that purpose.
- Smoke run (one file per sample, unnormalised): Z without the MC covariance is not monotonic under bin merging
  (40 → 20 bins: 88.7 → 303.8), i.e. near-singular directions of the MC-estimated C inflate it; with the MC
  covariance it decreases as it must (13.1, 12.1, 11.7, 10.9). To be checked on full statistics before choosing the
  headline number.

## 2026-11-19 Jet-free EECs requested
User: consider jet-free EEC observables. arXiv:2608.14793 Sec. 2, Eq. (6) verbatim: all final-state particles but the
boson's decay products, |η| < 2.4, ∏ p_T,i / p_T,V^N, R_ij in (η, φ), all tuples, no jet boundary; γ+X results only
(Sec. 3.3: "we take V=γ"); Z+X named as a future target. Sec. 4-5 not read verbatim (numbers there unverified).
Pileup/UE: only a general insensitivity statement (intro); no treatment found. Our code lacks the |η| cut, PV
association and lepton removal for such a set, so it is a C++ addition (plan, Phase B2).

## 2026-11-19 Jet-free collections: code, validation, test production
Design and decisions: `simulation/jetFreeEEC_plan.md`. Code: `EventEECJetProducer`, `EECConstituentPackedTableProducer`,
`jetsetup::selectEventParticles`/`matchPacked`, `DileptonSelector` `leptonPtrs`, `setupJets` mode `event`, observable
`collections:`, manifest `writeConstituents`; config `simulation/configs/ZX_jetfree.yaml` (`make_jetfree_config.py`);
manifest `simulation/production/samples_jetfree.yaml` (prepared, not submitted).
Dev MiniAOD (DY PTLL-400to600):
- First version (100 events): ΔR + charge removal missed a selected electron (PF candidate of opposite charge, ΔR 5e-5,
  same pT); fromPV ≥ 1 kept 293 charged/event (519 GeV) vs gen 105 (409 GeV); fromPV ≥ 2: 90 (378), PUPPI charged 91
  (395), ≥ 3: 66 (271). Unbinned pair tables ~935 kB per written event.
- Gen dressing daughters do not match packedGenParticles exactly (muon 6.7e-5 relative; a 17 keV photon 1.6e-3):
  MiniAOD packs pt as float16 and y, φ as truncated int16, and the merged collection keeps the full-precision pruned
  copies. Matching within 1.5 packing quanta, unique, same pdgId; Rivet ghost τ tags (status 2) skipped.
- Final version, 1000 events (427 written): no failure (every dressing daughter matched uniquely); no same-flavour
  constituent within ΔR < 0.02 of any selected lepton (reco 420 μ, 366 e; gen 430 μ, 416 e); hemisphere and |η| cuts
  exact; Σ(w × symfactor) = 1.000000 per event (n = 1, sumPt) in all four unbinned collections; particles/event
  RecoEvtCh 94, RecoEvtPuppi 135, RecoEvtAll 1171, GenEvtCh 110, GenEvtAll 243; 507 kB per written event
  (GenEvtAll pairs 242, RecoEvtPuppi 75, GenEvtCh 50, RecoEvtCh 37, RecoEvtAll constituents 30, AK8 E3C 24 + 19 kB).
- Selected-lepton PF candidates (FWLite, Z-candidate tight leptons, same file): muons 440/440 exactly one (the PF muon);
  electrons 304/310 exactly one (the PF electron), 6 with 2-8 (π± 9, γ 8, μ 1; up to 100% / 93% of the electron pT)
  whose own PF candidate is then a π± or μ. All of them are removed (user: correct, 2026-11-19).
Tests (each verified discriminating by mutation): `test_jettools.cc` selectEventParticles (6/6) and matchPacked
(pdgId, uniqueness, each of pt/y/φ; 5/5 after adding per-component cases); `test_modules.cc` DileptonSelector
leptonPtrs (order swap caught); `test_analysisConfig.py` EventCollections checks and wiring (12/12 after renaming the
test collections so they sort after the AK8 ones: `writeTmp` sorts keys, which hid the back-to-back-flag guard);
`test_production.py` writeConstituents (schema, default, CRAB, condor); `job.sh` argument handling simulated for the
four mask/constituents combinations.

## 2026-11-19 Storage options and MiniAOD completeness
Same 1000 DY PTLL-400to600 dev events (427 written), kB per written event:
- unbinned jet-free E2C (4 collections) 404; SparseMerged 100 log ΔR bins (1e-3-6) 1.2, 200 bins 2.1. Binned vs
  unbinned histogram (RecoEvtCh, 100 bins + flow): max relative difference 9e-9.
- constituents: RecoEvtAll (all PF candidates in |η| < 2.4 with details) 30.0, GenEvtAll 3.7, RecoEvtCh 1.4,
  RecoEvtPuppi 2.2, GenEvtCh 1.7, AK8 reco/gen 0.4 each; AK8 unbinned E3C 42.9. Totals 507 (unbinned), 104 (100 bins).
MiniAOD (CMSSW_15_0_22 sources): `PATPackedCandidateProducer` packs every `particleFlow` candidate (pt float16,
η and φ int16 rounded: quanta 1.8e-4 and 9.8e-5); tracks not used by PF are in `lostTracks` (highPurity pt > 0.95 or
pt > 2, ≥ 8 hits, ≥ 1 pixel hit), which we do not read. `packedGenParticles`: every status-1 gen particle with
|y| < 6. Track details exist for every charged candidate in the dev events (below 0.95 GeV the low-quality properties,
`minPtForLowQualityTrackProperties = 0`).

## 2026-11-19 Phase A results (existing NANOs)
`sensitivity.py` on `work/sens_tables_20261119.coffea` (20261116_zxb2b, 20261117_zxb2bbkg, 20261117_zh; both
channels), 326.03 fb^-1, stat only. Output `~/nobackup/boostedV/sensitivity_20261119b/scan.md` (corrected distortion
metric: each jet-pT slice normalised on its own; the first run, `sensitivity_20261119/`, normalised over all slices,
which turned any change of the jet-pT spectrum into "distortion"; its Z columns are identical). Z_shape below is
the version with the MC-statistics covariance (Z_shape MC).
- Baseline (Z pT, jet pT > 200, |η| < 2, medium muons): VV S/B in the peak window 2.9%, Z_shape 9.2 (Z_tot 14.6).
  ZH: S/B 0.14%, Z_shape 0.5; at best 1.1-1.4 with a tagger (pnXbbVsQCD or gpV at 3% DY efficiency).
- Event-level cuts (Z pT, jet pT, |η|, pT balance, m_ll, MET, AK4 b-tag veto, AK4 multiplicity, |y_Z|, |Δy|, Z decay
  angle |cos θ*|) never raise Z_shape by more than 2% (MET < 100: 9.4): no VV/DY separation in these variables.
- Mass-decorrelated GloParT V score gpV = (Xqq+Xcs+Xbb+Xcc)/(+QCD) is the only large gain: at DY efficiency 10% / 3%,
  S/B 10% / 19.6%, Z_shape 11.6 / 13.5 (+26% / +47%); DY shape χ²/ndf 22 / 12 at 326 fb^-1 (largest per-bin
  |ratio - 1| 46% / 61%), so a residual sculpting visible at this luminosity. Tighter working points not scanned yet.
- Mass-correlated cuts sculpt and lose Z_shape: msd window (6.8, χ²/ndf 1.8e3), withMass taggers, τ21, N2, ParticleNet
  Xqq (χ²/ndf 10²-10³). Per-jet E2C selections (peak-window fraction, per-jet log-likelihood ratio; idea 6) lose
  Z_shape (≤ 8.2) and sculpt most (χ²/ndf 10³-10⁴): they cut on the information the shape fit already uses.
- Observable: E2C n = 1 beats n = 2 (9.2 vs 6.4); both jointly 9.5. Binning: Z only falls when bins are merged (as it
  must); 5/10/20/40 ΔR bins 7.5/8.0/8.8/9.2; 1/5/10 pT slices 7.1/9.2/9.6; both n with 10 slices 10.0.
- Artifacts: `n2b1 < -1` (n2b1 = -1 marks undefined values, ≥ 3% of DY jets); one χ²/ndf of 7e17 (lrVV at 3%) from a
  near-singular covariance.

## 2026-11-19 Constituents-only production, lostTracks, Python bindings
User decisions: constituents only; pybind11 bindings of the EEC library; lostTracks in the loose collection.
- `ZX_jetfree.yaml` now adds `RecoEvtAll` (packed PF candidates + lostTracks, details incl. `source`) and `GenEvtAll`,
  constituents only; no unbinned jet-free E2C, no AK8 E3C. 1000 dev events: 55.7 kB per written event; 30 lost tracks
  per event (all charged, 78% with |dxy| > 0.1 cm); srcIdx unique.
- ~7% of selected electrons (27/366 on the dev events) left a prompt same-charge lost track at ΔR < 0.002 with
  30-100% of the electron pT: the electron's CTF track (the PF electron uses the GSF track). `closestCtfTrackRef()` is
  available for 374/382 slimmedElectrons (pT > 25) and matches a lost track within packing precision for 35
  (|Δpt|/pt ≤ 4.4e-4). User: remove it. `EventEECJetProducer` now removes the candidate uniquely matching each
  excluded electron's CTF track (charge, pt, η, φ within packing precision): 23 -> 2 such lost tracks; the two left are
  other collinear tracks (pt 138 and 82 GeV vs CTF 101 and 21 GeV, ΔR ~ 1e-3), kept by the exact rule.
- Bindings: `simulation/EECs/pybind/eecs_py.cc` (`projected_enc`: PENCProducer's calculator, norm External, Dense, Pt
  or Energy weight, DeltaR or Angle3D, N 2-6) built by `analysis/build_eecs_py.sh` with gcc 11.4 and fastjet 3.4.1
  (gcc 11) from cvmfs, so it needs at most GLIBCXX_3.4.29 (the coffea container's libstdc++; CMSSW_15 gcc 12 needs
  3.4.30); one module per Python (dev 3.14, container 3.13) in `analysis/bvana/_ext/` with libfastjet beside it;
  `bvana/eecext.py` wraps it. Tests `tests/test_eecext.py`: brute-force N = 2, 3, 4 and n = 2 (incl. φ wrap), empty
  jets, argument errors, `byJet`; closure against the production tables of the dev NANO (AK8 E2Cn1, E2Cn2, E3Cn1,
  jet-free RecoEvtCh E2C) within 1e-4. All pass in the dev env and in the container (apptainer); 4/4 mutations caught.

## 2026-11-19 Tagger working points and per-pT-slice thresholds
`sensitivity.py --scan tagger` (`~/nobackup/boostedV/sensitivity_20261119c_tagger/scan.md`): VV with gpV, ZH with
pnXbbVsQCD, at DY efficiency 10%-0.1%, one global threshold or one per jet-pT slice (10 slices, flat DY efficiency;
`slicedThresholdMask`, tested), evaluated with E2C n = 1 or both n, 5 or 10 pT slices. Z_shape with MC statistics:
- VV peaks at DY efficiency ~1%: S/B in the peak window 34%; Z_shape 14.0 (n = 1, 5 slices), 15.0 (10 slices), 15.3
  per-slice threshold, 15.9 per-slice with both n (baseline 9.2-10.0); tighter than 0.3% falls (0.1%: 10.4-14.0).
  DY distortion at 1%, n = 1: χ²/ndf 7.2 / 4.5 (global / per-slice threshold, 5 / 10 slices), max |ratio - 1| ~27%,
  lower than at 3% (12, 61%). Per-slice thresholds add 1-3%.
- ZH: Z_shape 1.9-2.4 at 0.3%-0.1% (n = 1, 5 slices); 3.7-5.9 with both n and 10 slices at 0.1%.
- Not trusted: points at ≤ 0.3% DY efficiency with 10 slices or both n (≥ 400-800 bins from ≤ 12k DY MC jets):
  χ²/ndf jumps to 10²-10³ between neighbouring settings and the significance rises with the bin count, the signature
  of a noisy covariance estimate. The ZH 5.9 is one of these. A stability check (bootstrap of the MC jets, or fewer
  bins) is needed before using any tight-point number.

## 2026-11-19 Half-sample stability; VV with the bb score, ZH with the V score
`~/nobackup/boostedV/sensitivity_20261119d_tagger/scan.md`. Each point also gets Z_shape (no MC term) from two random
halves of the MC (weights x 2) and Z_corr = sqrt(2 Z^2 - mean Z_half^2), which removes at first order the upward bias
of sᵀĈ⁻¹s from an estimated covariance (bias ∝ bins / MC jets). Toy check (200 bins, known covariance): 2000 MC jets
give Z 294 vs true 277, Z_corr 275; 20000 give 278.8 / 277.3 vs 277.4.
Stable means Z_half ≈ Z ≈ Z_corr. Quoted: Z_shape with MC term (Z_corr without it).
- VV, gpV: stable down to 1% DY efficiency with n = 1 and 5 slices (14.0; Z_corr 16.2) and down to 3% with 10 slices
  or both n (14.4-15.3; Z_corr 16.0-17.4). Tighter or finer settings are unstable (one half jumps to 35-300): too
  few DY MC jets (≤ 40k at 1%) for 400-800 bins. Reliable best VV ≈ 14-15 (baseline 9.2-10.0).
- VV, gpHbb (asked): worse than no cut at every stable point: 5.7 / 4.8 at 10%, 3.2 / 2.7 at 3%, 3.1 / 2.6 at 1%,
  5.5 / 4.6 at 0.3% (Z_shape / with MC; n = 1, 5 slices; baseline 10.7 / 9.2). The bb score keeps only Z → bb and
  removes W → qq'.
- ZH, gpV (asked): 1.1 / 1.0 at 3%, 1.4 / 1.2 at 1%, 1.7 / 1.5 at 0.3% (stable), ~3x the baseline 0.5;
  with both n 1.6-1.9. Comparable but below pnXbbVsQCD (2.1 / 1.9 at 0.3%) and gpHbb (2.2 / 1.8 at 0.3%).
- ZH tops out at ≈ 2 at the stable points; the larger values (3.5-37) are all at unstable points.
- Tight working points need either more DY MC or fewer bins / a regularised covariance before they can be judged.
