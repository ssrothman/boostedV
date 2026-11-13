# Plan: latest JEC on the AK8 EEC jets, and a jet-axis lab frame for the E1C

Status 2026-11-13: implemented (see `JOURNAL.md`). Decisions: x in the jet–beam plane; θ log 1e-3–1, 20 bins; `jec` in both configs.

## Contents
- [1. AK8 JEC re-application](#1-ak8-jec-re-application)
- [2. Jet-axis lab frame](#2-jet-axis-lab-frame)
- [3. Tests](#3-tests)
- [4. Open points](#4-open-points)

## 1. AK8 JEC re-application
Now: the AK8 EEC jets keep the MiniAOD JEC (`NANO.md:351`); only the AK4 table re-applies V4 (`PATJetJECProducer`).
Available: `fatJet_jerc.json.gz` compound keys `Summer22EE_22Sep2023_V4_{MC,DATA}_L1L2L3Res_AK8PFPuppi` (DATA takes the run).

Chain (reco `pat` collections): `src -> PATJetJECProducer -> translator -> JER -> ...` (unchanged after the translator).
- **YAML/schema:** new required collection block `jec: {correctionFile, mcKey, dataKey, rho}` for reco `pat` jets
  (cross-check: only there), as `output.ak4Jets.jec`. Added to `default.yaml` and `ZX_test.yaml`.
- **PATJetJECProducer:** new parameter `sortByPt` (AK4: true, as now; AK8: false). Keeping the source order keeps
  `srcIdx` valid for `jets[srcIdx]` and for the re-tagged copy (`taggedJets[srcIdx]`, built from the same `src` in
  source order; the extension table errors on an η/φ mismatch, and JEC does not change η/φ).
- **Extension table:** `jets` = the JEC'd copies, so `extraVariables` see the new p4. `pat::Jet::setP4` does not update
  the stored JEC levels, so `jecFactor('Uncorrected')` stays the MiniAOD one: change the YAML columns
  `jecPt` (doc: re-applied V4 JEC, before JER) and `rawFactor` → `1 - userFloat('rawPt')/pt`; add `jecFactor`.
- **Translator `ptMin` trap:** MiniAOD drops AK8 daughters below MiniAOD-JEC pt 170, and the translator throws for a jet
  above `ptMin` (180) without daughters. A jet with MiniAOD pt < 170 and V4 pt > 180 (> +6%) would kill the job.
  Measured V4/MiniAOD pt (test files, MiniAOD pt > 170): MC mean 1.001, range 0.984–1.011; data (Run2022F) mean 0.991,
  range 0.983–1.018. For MiniAOD pt in [140, 170) the largest ratio is 1.017 (data) and 1.006 (MC), far below 1.06, so
  `ptMin: 180` stays; a crossing would stop the job with an exception, not drop data silently.
- JES variations use the V4 `Total` key already; unchanged.
- Docs: `NANO.md` (RecoJet corrections), `configs/README.md`, `JetSetup/README.md`.

## 2. Jet-axis lab frame
New `frame` value (name TBD, e.g. `jetAxis`): no boost; z along the jet direction; x in the plane of the jet and the
beam (as `jetHelicity`), i.e. `frame::BoostRotate(PseudoJet(0,0,0,1), jet direction, beam)`.
Code: `EECs/interface/Config.h` (`FrameKind`), `EECs/src/Config.cc` (`parseFrame`, `makeFrame`), schema enum,
`NANO.md`. `E1CLab` in `ZX_test.yaml` switches to it.
θ is then the 3D angle to the jet axis, about ΔR/cosh(η) ≲ 0.8: the current 20 regular θ bins on [0, π] put almost
everything in the first bin, so the θ axis needs new binning (open point 2).

## 3. Tests
- `test_config.cc`: the jet-axis frame maps the jet direction to θ = 0, a particle in the jet–beam plane on the
  +z side to φ = 0, and leaves energies unboosted (compare with `lab` for a jet along z).
- `test_modules.cc`: `PATJetJECProducer` with `sortByPt: false` keeps the source order (discriminating input: source
  not pt-ordered after JEC).
- Real-file check: EEC jet `jecPt` = raw pt × V4 factor from an independent correctionlib evaluation (MC and data
  test files); extension and retag columns still attach to the right jets (η/φ match passes).
- Mutation checks for the new frame axes and the sort flag.

## 4. Open points
1. x axis of the jet-axis frame: jet–beam plane (as helicity)? φ sign convention as helicity?
2. θ binning for that frame (e.g. log, 1e-3 to 1, 20 bins?).
3. ~~Translator `ptMin`~~: resolved, stays 180 (section 1).
4. Apply the V4 AK8 JEC in `default.yaml` too (proposed: yes, the schema makes the block required).
