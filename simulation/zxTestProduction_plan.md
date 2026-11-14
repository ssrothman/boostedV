# Plan: first ZX_test production on four MC samples

## Contents
- [Samples](#samples)
- [Steps](#steps)
- [Decisions (user, 2026-11-13)](#decisions-user-2026-11-13)

## Samples
All Run3Summer22EEMiniAODv4, GT `130X_mcRun3_2022_realistic_postEE_v6`, config `configs/ZX_test.yaml` (DAS, 2026-11-13).

| Name | Dataset (primary / processed) | Events | Files |
|---|---|---|---|
| DY (Z→ll + jets) | `DYto2L-4Jets_MLL-50_TuneCP5_13p6TeV_madgraphMLM-pythia8` / `..._postEE_v6-v3` | 264.4M | 6114 |
| ZZ | `ZZ_TuneCP5_13p6TeV_pythia8` / `..._postEE_v6-v2` | 4.04M | 82 |
| WZ | `WZ_TuneCP5_13p6TeV_pythia8` / `..._postEE_v6-v2` | 26.7M | 391 |
| ttbar | `TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8` / `..._postEE_v6-v2` | 74.3M | 1388 |

ZZ and WZ are the inclusive pythia8 LO samples (all decays: Z→ll with Z→qq or W→qq is a subset).
No LO inclusive ttbar exists in this campaign; the user chose powheg (NLO) dileptonic.

## Steps
1. ZX_test: EECs `Unbinned` (coordinates `dR` / `theta, phi`, full precision); `aggregation.observables: []`.
2. Local test, one file per sample: runs, selection rates, tables present, unbinned EECs vs a brute-force
   recomputation from the constituents (`writeConstituents=1`), CPU time and NANO size per event → job splitting.
   Check that empty histogram files do not break job completion and `merge.py`.
3. Manifest `production/samples_zxtest.yaml` (CRAB, `T3_US_FNALLPC`), `submit.py --dryrun`, a `maxJobs` pilot.
4. **Check in with the user before the full submission.**
5. Columnar scaffolding (`simulation/analysis/`, coffea from the mambaforge `dev` env): NanoEvents schema for this
   NANO, sample registry from `merged/sample.json` (normalisation by genEventSumw; cross sections supplied by the
   user, none invented), example processor and checks.

## Decisions (user, 2026-11-13)
- ttbar: powheg `TTto2L2Nu`; DY: v3 only (not ext1); aggregation dropped; coffea.
