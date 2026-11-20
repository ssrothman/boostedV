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
- [2026-11-19 Bug: signal-only bins in the MC-statistics significance](#2026-11-19-bug-signal-only-bins-in-the-mc-statistics-significance)
- [2026-11-19 Corrected scans: binning, pT x dR, |eta|, m_SD](#2026-11-19-corrected-scans-binning-pt-x-dr-eta-m_sd)
- [2026-11-19 E2C kept; plan for the remaining ideas](#2026-11-19-e2c-kept-plan-for-the-remaining-ideas)
- [2026-11-19 Data products: tables and scan outputs](#2026-11-19-data-products-tables-and-scan-outputs)
- [2026-11-19 Truth match and jet-pT vs Z-pT resolution](#2026-11-19-truth-match-and-jet-pt-vs-z-pt-resolution)
- [2026-11-19 Constituent correlator tables (ceec)](#2026-11-19-constituent-correlator-tables-ceec)

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

## 2026-11-19 Bug: signal-only bins in the MC-statistics significance
- Z_tot/Z_shape "+MC" used C_bkg + Cmc_bkg + Cmc_sig. A bin with signal MC but no background MC then has positive
  variance (signal MC only) and enters the pseudo-inverse with s^2 / sigma^2(signal MC). Found on the m_SD templates:
  ZH, 10 pT slices, baseline Z_shape 0.7 without the MC term but 2.0 with it (adding covariance cannot raise Z).
- Fix: the MC-term significance uses only bins with background MC (`significance(..., support=diag(C_bkg) > 0)`),
  like the plain one. Test `SignalOnlyBins` (a signal-only bin: 5/sqrt(101.5) with the support, > 10 without) fails
  when the support is ignored.
- Every earlier "+MC" number (Phase A, tagger and stability tables) is affected wherever such bins exist (tight cuts,
  fine binning, one-hot m_SD); the Z without the MC term and the half-sample numbers are not. All scans are being rerun
  into the same directories; the entries above are superseded by the next one.

## 2026-11-19 Corrected scans: binning, pT x dR, |eta|, m_SD
All scans rerun with the support fix on condor (`scanCondor.py`, `configs/scans_20261119.yaml`, 48 jobs; outputs in
the same `~/nobackup/boostedV/sensitivity_20261119*/`). Condor vs a local run of the m_SD scan: Z values agree to
<= 2e-7 relative (DY chi2/ndf to 3.5e-3, an ill-conditioned pseudo-inverse). The ptdR tables' plain e2cn1 rows
reproduce the ΔR scan exactly (consistency of `sens_tables_20261119b`).
Numbers: Z_shape with MC stat. at the best *stable* working point (both half-sample Z_shape within 10% of the full one;
the tagger thresholds of `taggerScans`); baseline in brackets. "x/y": pT slices / ΔR bins.
| config | VV gpV | ZH pnXbb | ZH gpV |
|---|---|---|---|
| E2C n=1, 5/40 (reference) | 14.2 (9.2) | 1.2 (0.46) | 1.6 (0.46) |
| E2C n=1, 10/40 | 14.9 (9.6) | 1.6 | 1.1 |
| both orders, 10/40 | 15.3 (10.0) | 1.5 | 1.2 |
| n=1, 5 slices, 20 / 10 / 5 ΔR bins | 13.6 / 11.9 / 10.7 | 1.4 / 1.9 / 1.6 | 1.4 / 1.0 / 0.8 |
| n=1, 1 slice, 40 ΔR bins | 10.0 (7.1) | 1.2 | 1.0 |
| n=1 in pT·ΔR, 1 / 5 / 10 slices | 14.0 / 14.7 / 15.4 | 1.8 / 1.8 / 1.6 | 1.7 / 1.7 / 1.4 |
| n=1, 5 slices x 2 / 4 abs(eta) slices | 14.3 / 12.4 | 1.2 / 0.9 | 1.1 / 0.7 |
| n=1, 10 slices x 2 / 4 abs(eta) slices | 15.5 / 10.0 (base only) | 0.9 / 0.9 | 1.5 / 2.3 (9/11 unstable) |
| m_SD (5 GeV bins), 1 / 5 / 10 slices | 18.6 / 19.1 / 19.6 (10.5-11.3) | 3.4 / 4.9 / 5.5 (0.6) | 2.8 / 2.0 / 2.1 |
| E2C n=1 + m_SD, 5 / 10 slices | 19.5 / 20.2 | 5.1 / 2.0 | 2.1 / 2.2 |
- Fewer ΔR bins lower Z at every stable point; they make tighter working points stable only for ZH (pnXbb 0.3%:
  1.9-2.5 with 10 bins), not for VV.
- pT·ΔR: with one pT slice it matches the ΔR binning with 5-10 slices (VV 14.0 vs 10.0 for ΔR with one slice); with
  slices, the same as ΔR within ~0.5. It removes the need for pT slicing, not more.
- |eta| slices: no consistent gain; the doubled bin count makes more working points unstable.
- m_SD: the stat-only m_SD template fit beats the E2C: VV 19-20 vs 14-15, ZH(pnXbb) 4.9-5.5 vs 1.2-1.6; adding the E2C
  to m_SD changes VV by < 1 and does not help ZH. ZH gpHbb with m_SD: 4.8-5.3 (1 and 5 slices).
- Superseded numbers of the previous entries: the VV E2C results moved by < 0.1 (few signal-only bins); VV with the bb
  score now has no stable point below baseline at the 10% criterion (earlier quoted 2.6-4.8 with a looser one). ZH
  m_SD baseline at 10 slices 2.0 -> 0.59 (the bug).

## 2026-11-19 E2C kept; plan for the remaining ideas
- User: keep the E2C as the search observable and pursue the remaining ideas despite the stronger m_SD fit.
- Draft plan for discussion: `E2C_NEXT_PLAN.md` (boson-pT x dR; projected E3C and energy weights n; constituent
  choice; jet-free EECs; theory shape deferred; tight working points). Facts it rests on: the `20261119_jetfree` AK8
  constituents are charged only (`ZX_jetfree.yaml`), its DY is p_T^ll > 400 with ~10% of the files, and the
  bindings take a real n (`eecs_py.cc`).
- Production status: `simulation/JOURNAL.md`, entry "`20261119_jetfree` status".

## 2026-11-19 Data products: tables and scan outputs
Tables (`run.py configs/sensitivity.yaml --tag 20261116_zxb2b 20261117_zxb2bbkg 20261117_zh --lumi 326030
--backend condor`, 80 jobs, provenance in `work/<condor dir>/state.json`); local copies in `analysis/work/`
(git-ignored), masters on EOS `/store/user/srothman/boostedV/analysis_tables/`:
| file | condor dir | code | size, adler32 | content |
|---|---|---|---|---|
| `sens_tables_20261119.coffea` | `work/sens_20261119` | 260b1a0 + the uncommitted tables code, committed in d63894a | 1979056787 B, 9cded72e | ΔR columns |
| `sens_tables_20261119b.coffea` | `work/sens_20261119b` | bd4445a + the pT·ΔR columns, committed in 94970f8 (`configs/sensitivity.yaml` identical) | 2762999036 B, 75cab58d | + `e2cn{1,2}ptdR` |
Validation of `b`: same row sums and mean log as the first on one DY file; its ΔR rows reproduce the ΔR scans exactly.

Scan outputs (`scan.md`, `scan.json`, `run.log`) in `~/nobackup/boostedV/` (not backed up); current ones are those of
`configs/scans_20261119.yaml` (condor `work/scans_20261119`, 48 jobs, code 94970f8), rerun after the MC-term fix:
`sensitivity_20261119b` (cut scan), `_d_tagger`, `_e_fewbins`, `_f_eta2`, `_g_eta4`, `_h_msd`, `_i_ptdR`.
Stale (before the fix, not rerun; superseded): `sensitivity_20261119` (old distortion normalisation) and
`sensitivity_20261119c_tagger` (no half-sample check; superseded by `_d_tagger`).

## 2026-11-19 Truth match and jet-pT vs Z-pT resolution
Plan item 1 (`E2C_NEXT_PLAN.md`). Tables `sens_tables_20261119c.coffea` (condor `work/sens_20261119c`, code 83ec19e;
EOS copy adler32 fef6bfc0, 3604752306 B) = the `b` tables plus `e2cn{1,2}ptlldR` (x = Z pT x dR) and the truth match
(`bvana/truth.py`). Every shared column equals the `b` tables (row counts and weighted sums, 60 samples).
- Truth match: the rules of the production `axisTruth` applied offline to GenPart. Same status and particle as
  `RecoJet/GenJet_axisTruth*` for all 8329 jets of one DY (dev), one WZ and one ZH file (pt, eta, phi within 0.19%,
  the GenPart float precision). The existing productions (zxb2b, zh) predate `axisTruth`, hence the offline version.
- Matched fractions at the sensitivity baseline (weighted): VV 54% of jets are the hadronic boson (WZ ~45%, ZZ ~76% of
  table rows); the rest are mostly a hard-process parton (status 3). qq->ZH and gg->ZH: 87%. DY: 100% status 3.
- Resolution r = (pT_true - pT_reco)/pT_true (`ptResolution.py`, `~/nobackup/boostedV/ptResolution_20261119c/`),
  median / 68% half-width at pT_true 200-300 and 400-600 GeV:
  | | jet pT | Z pT |
  |---|---|---|
  | VV (boson) | -0.035 / 0.105, -0.020 / 0.081 | -0.004 / 0.119, 0.029 / 0.141 |
  | ZH (boson) | 0.017 / 0.146, 0.027 / 0.097 | -0.008 / 0.142, 0.015 / 0.109 |
  | DY (parton) | -0.068 / 0.118, -0.040 / 0.095 | -0.015 / 0.132, 0.025 / 0.187 |
  The jet pT is the better estimate of the boson pT for VV and DY (narrower at all pT_true, tails |r| > 0.3 half as
  frequent); for ZH (b decays with neutrinos) the two are equal. The Z-pT residual of DY has a shoulder up to
  r = 0.5, where the baseline Z pT > 200 GeV cuts for a parton at 400 GeV (extra radiation shares the recoil).
- Open observation: 26% of the boson-matched ZH jets (13% for VV) have pT_true < 200 GeV with a reco jet above 200
  (median r -0.8): the jet then contains more than the boson. Not investigated further.

## 2026-11-19 Constituent correlator tables (ceec)
Table key `ceec` (`bvana/ceec.py`, design in `E2C_NEXT_PLAN.md`): per-jet rows from the stored constituents of the
jet-free productions, for plan items 2-4. Checked on the dev DY NANO (per-channel layout, 500 events) and one
`20261119_jetfree` WZ file (old layout):
- AK8 E2C recomputed from the constituents (n = 1, jetPt) equals the production E2C table row by row: max relative
  difference 7e-8 (4.7e-4 in one table, float rounding at a bin edge).
- AK8 approximated by the all-particle collection within dR < 0.8 of the jet (charged, PUPPI-weighted, no lost tracks;
  plan item 3 option b) vs the real AK8 charged E2C: summed weights within 1%, single bins of single jets up to 25%
  apart (cone vs anti-kT boundary).
- The resolved E3C (R_L, xi) projection sums to the projected E3C; the recoil hemisphere keeps 65-80% of the
  charged-PV jet-free E2C weight.
- Unit tests `tests/test_ceec.py` (filters, srcIdx join, spec checks). Mutation tests rerun with bytecode caching off
  (a stale `.pyc` had hidden a mutant): all 27 mutations of this session's Python code caught, and 4 earlier ones
  (support mask, m_SD rows, cell index, scan merge) rechecked.
