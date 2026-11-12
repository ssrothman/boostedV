# Simulation journal (step A.2 onward)

## Contents
- 2026-11-11 A.2 setup and DataFormats
- 2026-11-11 EECs plugins and JetSetup
- 2026-11-11 EventSelection and end-to-end validation
- 2026-11-11 Placeholder constituent variations, selection overrides
- 2026-11-11 Single YAML analysis configuration
- 2026-11-11 Generator-level selections
- 2026-11-11 Reco lepton dressing and muon momentum corrections
- 2026-11-12 Batch production (CRAB and LPC condor)
- 2026-11-12 Production review fixes; corrections on cms-griddata latest

## 2026-11-11 A.2 setup and DataFormats
- Plan: `stepA2_plan.md`. New local repos (remotes pending): `EECDataFormats` (pkg `SRothman/DataFormats`),
  `JetSetup`, `EventSelection`; symlinked into `eecdev/CMSSW_15_0_22/src/SRothman/`.
- genreflex in 15_0 rejects explicit `std::array<double,N>` selections ("I/O is supported transparently").
- DataFormats tests: ROOT file round-trip of `EECJetCollection` and every EEC result vector. Mutations
  (eta→rapidity in `jetPseudoJet`, dropped charge, removed `UnbinnedResult<2>` dictionary) each fail the tests.

## 2026-11-11 EECs plugins and JetSetup
- EECs plugins and CovarianceAccumulator: see `EECs/JOURNAL.md` (2026-11-11 entries).
- Dev input: 2000 events of the DY MLM Summer22EE MiniAODv4 file, copied to
  `~/nobackup/boostedV/testdata/DYto2L-4Jets_MLL-50_MLM_Summer22EE_2000ev.root`.
- MiniAOD facts measured on that file:
  - Daughters of `slimmedJetsAK8`/`slimmedJetsPuppi` are unweighted packed candidates. Σ(puppiWeight·p) reproduces the raw jet pt (AK8 within 0.17%, 24 jets).
  - `slimmedJetsAK8` has no daughters for pt < 170 (`applySubstructure_cff.py: dropDaughters "pt < 170"`). The translator throws on such jets.
  - Gen-jet p4 vs the sum of its packed daughters differs by up to 2.7e-4 (packing precision; seen in double precision via FWLite).
  - Reclustering packedGenParticles without neutrinos (anti-kt 0.8) reproduces `slimmedGenJetsAK8` within 1.4e-4. PUPPI-weighted packedPFCandidates reproduce the `slimmedJetsAK8` raw pt with median 1.5e-4 and p95 7e-4.
  - ID names present: `cutBasedElectronID-RunIIIWinter22-V1-*`, `cutBasedPhotonID-RunIIIWinter22-122X-V1-*`. HLT paths present: IsoMu24_v15, Ele32_WPTight_Gsf_v17, AK8PFJet500_v18, PFHT1050_v20, Photon200_v15. All Run-3 `Flag_*` MET filters are present in the PAT TriggerResults.
- JME correctionlib keys (Summer22EE): `Summer22EE_22Sep2023_V2_MC_Total_AK8PFPuppi` and `..._JRV1_MC_{ScaleFactor,PtResolution}_AK8PFPuppi`. JME also ships `jetid.json.gz`; we use `PFJetIDSelectionFunctor` RUN3PUPPIruns2022FGruns2023CD instead.
- JetSetup mutations caught (6/6): JES sign, JER matching, lepton veto, chargedOnly, seed salt, JER systematic. A mutation that does not compile reuses the stale binary, so it must be redone.

## 2026-11-11 EventSelection and end-to-end validation
- EventSelection on 2000 inclusive DY events: Zmumu 217, Zee 102, Wmunu 44, Wenu 6, Hadronic 0 (trigger 0), GammaJets 0. The Z boson mass means are 90.5 (μμ) and 90.1 (ee).
  Z→μμ agrees event by event with an independent FWLite selection (217 = 217).
- Trap: in PyROOT, `m.passed(ROOT.reco.Muon.CutBasedIdTight)` passes the int 3 to the bitmask overload `passed(uint64_t)`, so it tests Loose|Medium. Use `1 << int(enum)`.
- EventSelection mutations caught: 6/6 (veto, OS, AND/OR, nMax, mT sign, closest mass).
- `configs/eecNano_cfg.py` end to end:
  - 1000 events of DY PTLL-400to600 (`~/nobackup/boostedV/testdata/DYto2L-4Jets_MLL-50_PTLL-400to600_MLM_Summer22EE_1000ev.root`): 17 s, 1.4 GB RSS (single thread, 5 reco variations + gen, 3 observables each).
  - Brute force from NANO constituents, about 600 jets per level: reco E2C/E3C/E1C ≤ 5e-8; gen E2C 5.6e-5, gen E3C 1.4e-4 (single-tuple bin-edge migrations from float-stored inputs).
  - Gen E1C: 2 of 609 jets each have exactly one particle in the adjacent bin.
  - Sum rules hold to 1e-6. The Zmumu aggregator H, C and Σw match the NANO recomputation (rtol 1e-4; Generator_weight is stored with 14 mantissa bits).
- E1C rest-frame angles are badly conditioned for boosted light jets. Perturbing the jet four-vector by 6e-8 (relative) moved one jet's E1C by 0.19 (L1), so recomputing E1C downstream from float NANO jets is not reliable. Computing the reference in float32 numpy gave a 0.19 false alarm.
- `GenWeightsTableProducer` warns at beginRun about reading `LHERunInfoProduct` before endRun. The Runs tree still has `genEventCount` = processed events and `genEventSumw`.

## 2026-11-11 Placeholder constituent variations, selection overrides
- At the user's request, the constituent-variation sizes are invented placeholders (`JetSetup` `CONSTITUENT_VARIATIONS`): charged-hadron drop 2%; charged, neutral and photon scales ±1%, ±5%, ±2%. The selection defaults stay as proposed.
- The drop uses `seedSalt=1`. With salt 0, its first draw would come from the same seed as the JER stochastic smearing of the same jet.
- `addAllChannels` now forwards `objectCuts`, `metFilters`, `triggers` and `channelCuts`; unknown names raise.
- On 1000 PTLL-400to600 events: each scale variation changes only its category, by exactly its factor. TrkDrop removed 1.91% of 15356 charged hadrons (expected 2.0 ± 0.11%) and nothing else. All end-to-end checks pass. Wall time is 21 s (17 s before) with 7 more reco chains.
- `testdata/` is gitignored in boostedV; `~/nobackup/boostedV` is the repo itself.

## 2026-11-11 Single YAML analysis configuration
- `configs/default.yaml` is the only source of physics settings, with `config=` on the `cmsRun` line. Schema in `analysis.schema.yaml` (jsonschema 4.22 and PyYAML 6.0.1 are in CMSSW_15_0_22; there is no `tomllib` on Python 3.9).
- The package helpers no longer have defaults. They take dicts: `addSelection`/`addChannel` (generic channel types), `setupJets(spec)`, `addObservable`/`addAggregator`.
- Regression: `default.yaml` reproduces the previous hard-coded setup exactly. 1000 PTLL-400to600 events give an identical output: 1309 Events branches, 192 Runs branches and 572 histogram objects compared value by value.
- `test_analysisConfig.py` (9 tests) checks that no tracked parameter of any SRothman module falls back to `fillDescriptions`: 200+ modules in MC, 45 in data. Omitting `rhoMax`, `idMask` or `maxBins` in a helper fails it.
- Traps:
  - `edmConfigDump` does not define `__file__`; use `inspect.currentframe().f_code.co_filename`.
  - Generated cfis carry the untracked `mightGet`.
  - `cms.InputTag('').value()` is `'""'`.
  - `__pycache__/*.pyc` from `scram b python` had been committed to EECs, JetSetup and EventSelection; they are now untracked and ignored.
- The validation configs in JetSetup and EventSelection take `config=` too. Their checks pass with the same numbers, except the 50% drop test, whose `seedSalt` changed (0.514 kept).

## 2026-11-11 Generator-level selections
- Design choices made with the user:
  - Gen objects come from the Rivet particle level (`ParticleLevelProducer`, as in NanoAOD): dressed prompt leptons (ΔR 0.1), isolated prompt photons, MET from prompt neutrinos.
  - Gen cuts mirror the reco kinematics.
  - Jets are cleaned against their own level's objects.
  - Aggregation is per channel and level, for all jet collections.
- `selection.levels` = [reco] | [gen] | [reco, gen] picks which levels define written and aggregated events. Both levels are always evaluated in MC.
- Trap: `GenParticles2HepMCConverter` needs `PDTRecord`. `addGenCommon` loads `SimGeneral.HepPDTESSource.pythiapdt_cfi`.
- 1000 PTLL-400to600 events:
  - reco-only writes 466 events, gen-only 677 and OR 727, with 416 in both. OR = reco ∪ gen exactly.
  - Zmumu: reco and gen 198, reco only 0, gen only 49. Zee: 153 / 0 / 95.
  - Gen Z→μμ vs bare prompt muons (FWLite): 247 vs 243 selected, with 996 of 1000 events agreeing.
  - The Rivet chain adds about 10 s per 1000 events (25 s → 35 s).
- Regression: reco-only reproduces the previous run's 466 events. All 1254 non-gen branches and all 144 reco histograms are identical (the histogram directories are now `<ch>_reco_…`). Gen observables change because gen jets are now cleaned against gen objects.
- End-to-end checks pass in OR mode (36 checks, including aggregation at both levels). The config tests (13) cover the levels, data behaviour, gen schema and per-level cleaning.

## 2026-11-11 Reco lepton dressing and muon momentum corrections
- **Dressing** (`selection.reco.dressing.mode`, default none):
  - Modes: `fsr` (CMSSW `LeptonFSRProducer`) and `cone` (Rivet-like, ΔR 0.1, outside electron footprints, PUPPI-weighted).
  - The PAT selectors produce copies, so `fsr` matches each copy to its `slimmed*` original by identical pt/η/φ.
  - Validation, 2000 inclusive DY events (761 tight μ, 577 tight e): `fsr` matches the FSR producer's photons and `cone` matches an independent FWLite recomputation, both to ≤ 1.3e-7 of E. Dressed: fsr 18 μ and 2 e; cone 29 μ and 16 e.
  - Mutations caught: no footprint veto (electron E doubled), PUPPI ignored (80 μ dressed instead of 29, up to +78% E: pileup photons matter), cone ×2, FSR photon not added.
  - With pt moved to `dressedCut`, reco − gen Z→μμ mass over 216 events:

    | Mode | Mean | RMS |
    |---|---|---|
    | none | −0.34 GeV | 1.64 GeV |
    | fsr | −0.10 GeV | 1.74 GeV |
    | cone | −0.18 GeV | 1.47 GeV |

    Z→ee mean −0.65 / −0.61 / −0.59 GeV, i.e. barely changed (the supercluster energy is already dressed).
  - Isolation is not recomputed for dressed leptons.
- **Muon corrections** (`selection.reco.muonCorrections`, default off): a port of the MUO POG MuonScaRe (Run-3 Summer22EE `muon_scalesmearing.json.gz`). `correctedMuons` feeds every muon consumer.
  - It matches the POG `MuonScaRe.py` to ≤ 2.2e-16 on 5248 muons for MC and data nominal, scale up/down, and resolution up/down with `python` k. The `cpp` k is checked against the written-out `MuonScaRe.cc` formula.
  - Trap: the reference `MuonScaRe.py` non-nested path is broken; call it with jagged arrays (nested=True).
  - Mutations caught: upper threshold ignored, k switch ignored, lumi in the seed, smearing in data.
  - With the corrections on (2000 inclusive DY, 216 Z→μμ in both levels), the reco − gen mass mean is −0.25 GeV (none −0.34). With cone dressing as well it is −0.09 GeV. The RMS grows slightly (+0.08 GeV) because the MC smearing targets the data resolution, not gen.
  - With everything off, the output is identical to before (1357 branches, 1144 histograms).
  - **Open with the MUO POG** (also in EventSelection/README.md):
    1. The scale above 200 GeV: C++ corrects, Python leaves unchanged. We use highPtThreshold 200, configurable.
    2. The k in the resolution variation: C++ √(k_data²−k_mc²), Python k_mc, differing by up to 0.6% in pT. Default `cpp`, provisional.
    3. Only the event number enters the smearing seed: the length-one seed sequence uses only its first input.
  - The muon POG pt-correction wiki needs CERN SSO, so it could not be consulted from here.
- Integration (1000 PTLL-400to600 events):
  - With all options off, the output is identical to the previous run (1357 / 192 / 1144 objects).
  - With muon corrections and cone dressing (pt moved to `dressedCut`), all three level modes run, and `checkLevels` and `checkEndToEnd` pass.
  - Z→μμ reco − gen mass: mean −0.58 → −0.23 GeV, RMS 3.08 → 2.80 GeV (about 200 events).
- Muon-correction mutations caught (4/4): no 200 GeV cut, k switch ignored, lumi in the seed, smearing in data.

## 2026-11-12 Batch production (CRAB and LPC condor)
- `production/`: manifest `samples.yaml` → `submit.py` (CRAB or condor) → `status.py` → `merge.py`. See `production/README.md`. Choices made with the user:
  - both backends behind one manifest;
  - MC and data;
  - merge the histograms per sample and keep the per-job NANO;
  - tags `YYYYMMDD_desc`;
  - the GlobalTag is a per-sample manifest field.
- **cfg**: `globalTag=` is now required, and there is an optional `lumiMask=`.
  - No module reads conditions yet. With the GT set, the 1000-event output is identical to before (all NANO trees and histogram objects).
  - Loading the GT costs about 40–140 s of Frontier start-up interactively and about 2.5 min on an LPC worker.
- **GTs from the MiniAOD provenance** (`edmProvDump`):
  - Summer22EE MC: `130X_mcRun3_2022_realistic_postEE_v6`, as in the dataset name.
  - `/Muon/Run2022F-22Sep2023-v2/MINIAOD`: `130X_dataRun3_PromptAnalysis_v1`. It is a re-MINI of PromptReco AOD; `Run2022F-19Dec2023-v1` also exists.
  - DAS `config` queries return no GT.
- **Golden JSONs**: `/cvmfs/cms-griddata.cern.ch/cat/metadata/DC/Collisions22/<date>/`; `latest/` moves.
- **Data skim** `testdata/Muon_Run2022F-22Sep2023_8lumis_2000ev.root`: 250 events from each of 8 lumis; 225 and 226 of run 360458 are not golden. With the mask, exactly the 6 golden lumis are processed (285 → 207 events written).
- **Merge test** (`test_merge`): two half-jobs merged against one job over both halves.
  - It matches at 1e-12 for every histogram object (values, covariance, axes, `sumW`, `sumW2`, `nEvents`, `axisTypes`), the Runs sums, the Events count and the processed lumis.
  - `hadd` sums the TParameters and keeps the TNamed.
  - Mutations caught: 6/6 in merge plus 5/5 in the comparator; unit tests 16/16.
- **Condor end-to-end** (2 DY PTLL-400to600 files): genEventCount 3010 = 731 + 2279 (DAS). The job-0 output is identical to a local cmsRun on the same file.
- **Condor data end-to-end** (1 Run2022F file, 67391 events): it took 9.4 ms per event, and the processed lumis equal DAS file lumis ∩ golden.
  - Deleting `nano_0` and running `status.py --resubmit` reran the job.
  - The re-merged histograms are identical to the first merge, with 9127 events written both times.
- **Traps**:
  - The LPC `condor_*` wrappers have no shebang line (run them via `sh`). `condor_rm -constraint` needs `-name <schedd>`. In `condor_q`, the cluster ids must precede `-af`.
  - The LPC schedds do not mount `/cvmfs/cms-griddata`, and condor transfers inputs only when a job starts, so `submit.py` snapshots the cfg, YAML, mask and `job.sh` into `work/<tag>/<sample>/inputs/`.
  - CMSSW's uproot has no `fsspec-xrootd`; use `handler=uproot.source.xrootd.XRootDSource`.
  - `EECs/build` contains symlink loops; the tarball skips `build/`.
  - CRAB's sandbox walks `src/` without following symlinks, so the symlinked packages' `interface/` dirs are not shipped. The cfg itself is evaluated at submission.
  - CRAB needs a MyProxy delegation (`crab createmyproxy`), which asks for the grid pass phrase.
- **Sizes**: 56 MB histogram file per job with `default.yaml`. About 20k events per Summer22EE DY MLM file, but individual files vary (731 and 2279 seen).

## 2026-11-12 Production review fixes; corrections on cms-griddata latest
- **Review fixes** (`production/`, details in its README):
  - `merge.py --tag` refuses without a job list.
  - The condor tarball is tied to the code state it was built from (`cmssw.tgz.state`) and to its EOS adler32.
  - `condor.json` stores `{cluster, schedd}`.
  - The committed test outputs were removed.
  - Tags submitted before this change (`20261112_e2etest`) are not readable by the new `status.py`/`submit.py`.
- **CRAB without the packages' `interface/` headers works**: cmsRun on an unpacked sandbox with every `SRothman/*/interface`
  deleted ran, and strace showed no SRothman header opened. The previous entry's sandbox concern is not a problem.
- **Lumis**: NanoAODOutputModule writes every processed lumi (also with no selected events). In Run2022F run 360458
  (53 files, 246 lumis) no lumi spans two files.
- **Corrections** now come from `/cvmfs/cms-griddata.cern.ch/cat/metadata/{JME,MUO}/Run3-22EFGSep23-Summer22EE-NanoAODv12/latest/`
  (user's choice: `latest`, read directly by the jobs).
  - The old `/cvmfs/cms.cern.ch/rsync/.../jsonpog-integration/POG/` copies stopped updating on 2025-09-23. Its JME file equals the dated 2025-07-15 copy.
  - JME: JES V2 → V4, JER JRV1 → JRV2. JRV2 has no up/down input: the SF and its uncertainty are separate keys (new YAML
    field `jerScaleFactorUncertaintyKey`). Up/down = SF·(1 ± unc), as in cms-cat nanoAOD-tools-modules PR #32 (user's choice).
  - The JRV2 uncertainty matches JRV1's absolute `up − nom` instead, so this may be a JME bug: `JME_JRV2_SFUncertainty.md`
    (to report).
  - MUO `latest` has the same keys and inputs, plus a new `RandomSmearing` correction (evtNr, lumiNr, phi) that is not used here.
  - LPC workers read both files (3 jobs, one node). CRAB grid sites are not checked.
  - Tests: all 8 C++ suites, `test_analysisConfig`, `test_production`. The JER test now covers nominal/up/down; the absolute form and swapped
    up/down both fail it.
