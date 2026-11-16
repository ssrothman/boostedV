# ZX_test against the JME recommendations (2026-11-15)

Source: local mirror `~/nobackup/cms-wikis/jme-docs/md/` of the six cms-jme*.docs.cern.ch sites, fetched 2026-11-15
(pages cited by path below). Implementation: `simulation/configs/ZX_test.yaml`, JetSetup, EventSelection at the
working tree of 2026-11-15. Era: Summer22EE MiniAODv4 (2022 EFG).

## Deviations (need a decision)

1. **Jet veto map not applied.** Mandatory in Run 3 (`cms-jme-jerc/recommendations/jet-veto-maps`, FAQ "When are
   jet veto maps required"): reject the event if any jet with corrected pT > 15 GeV, `tightLepVeto` ID and
   chEmEF + neEmEF < 0.9 has its axis in a vetoed bin of `jetvetomap`; for AK8 analyses use the corrected **AK4**
   jets (FAQ "Which jet collection should an AK8-based analysis use"); same map for data and MC
   (2022 postEE: `Summer22EE_23Sep2023_RunEFG_V1` in CAT `jetvetomaps.json.gz`; "affected by EE+ leak"). It also
   covers an extra 2022 ECAL crystal (noise-filter page). We read no AK4 jets at all.
2. **Jet ID: CMSSW functor differs from the JME definition.** In CMSSW_15_0_22 `PFJetIDSelectionFunctor.h`
   (TIGHTLEPVETO block, ~line 1030) `if (RUN3...) set("CHF", 0.01); else if (RUN3...FG...) set("NHF", 0.99);` —
   the `else if` is unreachable, so `RUN3PUPPIruns2022FGruns2023CD` TightLepVeto keeps NHF < 0.90 while Tight and
   the JME table (`cms-jme-jmar/recommendations/jet-identification`) use NHF < 0.99. Compared with CAT
   `jetid.json.gz` on all RecoJet of the seven v3 cutflow samples (69 298 jets): Tight 1 mismatch (chHEF stored as
   0.0100, at the 0.01 boundary, 10-bit precision); TightLeptonVeto 8 mismatches: 2 at |eta| < 2.4 (neHEF 0.986 and
   0.903, rejected by us, accepted by JME), 6 at 2.6 < |eta| < 3.0 (functor applies no lepton veto or neHEF cut there;
   outside our |eta| <= 2.4). Recommended for MiniAOD: the jet fraction accessors with the table criteria; for NANO
   v13+: `jetid.json.gz`.
3. **ECAL bad-calibration filter, 2022 prompt-reco era.** For 2022-2023 prompt-reco MiniAOD, JME says rerun
   `EcalBadCalibFilter` with crystal 838871812 added, "to data and simulation" (runs 362433-367144, i.e. part of
   2022G; `noise_filters`). We use the stored `Flag_ecalBadCalibFilter`.
4. **Payload versions not pinned.** We read `.../latest/*.json.gz`; the FAQ ("Is an unversioned CVMFS JME JSON path
   sufficient") says record exact tags and dated release. `latest` = `2026-06-05` today.
5. **Before enabling jet systematics:** we configure only `..._Total_AK8PFPuppi` (single-source, Case III, needs JME
   approval). Default is the regrouped set (Case II); the AK8 JSON has 11 `Regrouped_*` keys.
6. **Soft-drop mass** (`RecoJet_msoftdrop`, histogrammed by bvana, not used in selections): taken from MiniAOD
   (production JEC on the subjets, no JER). JME: re-apply AK4 JEC and JER to both subjets and recompute; then no
   JMS/JMR correction, residual uncertainties JMS ±1 %, JMR ±2 % (`jet-mass`).
7. **MET** (`slimmedMETsPuppi`, stored; used only by leptonMET channels, not in ZX_test): Type-1 PUPPI MET from
   MiniAOD carries the production AK4 JEC, not V4; JME: recompute Type-1 with the recommended JEC
   (`application/type1_met`, `met/corrections`).

## Compliant (with evidence)

- Collection AK8PFPuppi from `slimmedJetsAK8`; PUPPI tune v17 for Summer22EE MiniAODv4, stored `puppiWeight()` used.
- JEC: `Summer22EE_22Sep2023_V4` compound `L1L2L3Res` from raw pT (recommended tag; FAQ "Which JEC levels");
  validated against FWLite/correctionlib (note, Validation). Known-issue `rawFactor > 0.9`: none in the v3 samples
  (max JEC factor 1.29).
- JER: `Summer22EE_22Sep2023_JRV2`, hybrid, after nominal JEC, MC only, dR < R/2 = 0.4 and |dpt| < 3 sigma pT;
  agrees with `SmearedPATJetProducer` (2124 matched jets to 1.3e-7). Variations reuse the nominal seed (correlated
  draws, as recommended). Up/down = SF (1 ± SFUncertainty): the FAQ calls `SFUncertainty` fractional, which answers
  OPEN_QUESTIONS JME 1. Differences: floor at 1e-2 GeV energy (as `SmearedJetProducerT`) instead of truncation to
  0; seed from (run, lumi, event, jet index) instead of hashPRNG(pT, eta, rho, event) — both deterministic.
  The 2.5 < |eta| < 3 JER issue does not apply (|eta| <= 2.4).
- Jet ID on raw energy fractions (unchanged by JEC/JER, verified on MiniAOD); TightLepVeto plus our own lepton
  cleaning is allowed (Tight alone would also be allowed with dedicated cleaning).
- MET filters: our eight flags are exactly the Run 3 list (HBHE filters not required in Run 3); read from the PAT
  process `TriggerResults`.

## Status (2026-11-15, after the user's decisions)

- Items 1-4 implemented: jet veto map flag `jetVetoMap` (AK4 PUPPI, V4 JEC, correctionlib TightLeptonVeto, EM < 0.9,
  pt > 15, in `<c>`); jet ID from `jetid.json.gz` (`JetSetup/plugins/JetId.h`) in the translator and
  `PATJetJECProducer`; `ecalBadCalib` rerun flag; all CAT paths pinned (JME 2026-06-05, MUO 2026-06-18,
  LUM 2024-01-31). The process now uses `inputs.eras: [Run3, run3_nanoAOD_pre142X]` (central NANO for 13_0_X MiniAOD).
- Items 6 (soft-drop mass) and 7 (MET): future developments (TODO.md). Item 5: before systematics.
