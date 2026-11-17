# Question for JME/PAT: `slimmedJetsAK8` jets with a corrupted corrected pt

Dataset `/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM`
(MiniAOD made in CMSSW_13_0_13, GT `130X_mcRun3_2022_realistic_postEE_v6`). Found 2026-11-16 (`20261113_zxtest` crashes, TODO.md).

## What is seen
A `slimmedJetsAK8` jet whose stored p4 is a fraction of the true jet, with the "Uncorrected" pt (p4 x `jecFactor("Uncorrected")`) sensible:

| event (run:lumi:event), file | stored pt | raw pt | stored/raw | eta | gen AK8 pt | soft-drop subjets (corr. pt) |
|---|---|---|---|---|---|---|
| 1:87440:61994860, `/store/mc/Run3Summer22EEMiniAODv4/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/2530000/b47331c0-22b3-4b9b-adad-150cb89cbe66.root` | 88.28 | 326.79 | 0.270 | 0.52 | 337 | 217 + 51 |
| 1:48407:34320277, `.../40000/1034c3b7-2f5a-4415-b5a2-1a22fb14fdf6.root` | 165.15 | 326.78 | 0.505 | 0.46 | 362 | 239 + 52 |

- Normal jets have stored/raw = 1.03-1.14 (171 jets with raw 326-327.6 GeV in 6 files, none abnormal). The AK4 jet matching event 1 has pt 343 (raw 322.7).
- The corrupted jets have no daughters and no PF specific (`isPFJet()` false): the pt < 170 slimming cut acted on the corrupted pt.
  Mass scales with pt, so the whole p4 is scaled by 0.27 / 0.51.
- A third jet (job 223 of `20261113_zxtest`, lumi 112543, event 79792614) behaves the same: V4 JEC on its raw pt gives 348.45 GeV.
- Rate: none in ~1.5M AK8 jets of 13 other files of the dataset, one in ~43k in the first file.

## Ruled out here
- Not a JEC value: V4 (and the production) AK8PFPuppi L2Relative x L3Absolute is >= 1.06 at every pt and |eta| 0.5; a factor of 0.27 cannot come from any pt.
- Not copied from another jet (nearest AK4 pt 88.27 is at a different eta); raw pt 326.8 is not special.
- `edmProvDump`: `slimmedJetsAK8` = `PATJetSelector` (`pt > 10`) on `updatedPatJetsTransientCorrectedSlimmedAK8DeepTags`; the upstream
  updater and the transient jet-correction producer are not stored in the file, so the cause cannot be seen from the MiniAOD.

## Questions
1. Is this a known issue of the MiniAODv4 (13_0_13) AK8 update / transient JEC step (`updateJetCollection`, ParticleNet tags)?
2. Is the stored p4 meant to be raw x JEC? Should analyses trust the "Uncorrected" pt for these jets?
3. Are these jets present in data and in other Run 3 campaigns?

## Our handling
`JetSetup` re-applies V4 JEC from the raw pt, so the pt is right; the jet has no PF specific, so it fails the ID (bit 2, `kNoPFSpecific`) like any
other daughterless jet. Neither jet would have passed the analysis anyway (soft-drop mass 5.9 / 21.6 GeV, tau2/tau1 0.92 / 0.63; mass window not checked).
