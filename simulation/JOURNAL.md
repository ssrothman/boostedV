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
- 2026-11-12 MUO POG Run-3 compliance: high-pT muons and muon SFs
- 2026-11-12 LHE tables in the NANO
- 2026-11-12 Selected leptons and MET in the NANO
- 2026-11-12 NANO documentation
- 2026-11-13 NANO additions: event tables, AK8/AK4 jets, lepton details, GloParT
- 2026-11-13 Jets flagged, not removed, near selected objects
- 2026-11-13 V4 JEC on the AK8 EEC jets; jet-axis E1C frame; ZX_test config
- 2026-11-13 First ZX_test production: unbinned EECs, four MC samples
- 2026-11-14 ZX_test production `20261113_zxtest`: CRAB outcome, merge, sample plots
- 2026-11-14 Dilepton pT cut and back-to-back jet selection
- 2026-11-15 Second-production manifest, ZX_test note, bvana back-to-back regions
- 2026-11-15 Human review 1 of the ZX_test note: flags, JER order, frames, gen-jet flavour

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

## 2026-11-12 MUO POG Run-3 compliance: high-pT muons and muon SFs
- Source: MUO POG wiki git source (`~/nobackup/cms-wikis/muo-wiki`, guidelines/{recommendations,corrections}.md). Plan: `muonPOG_plan.md`.
- PTLL-400to600 test file: 347/697 muons (Tight or HighPt ID, pT > 15) above 200 GeV; leading muon > 200 GeV in 263/275
  dimuon events; only 7 of the 347 HighPt-ID muons above 200 GeV fail Tight ID. HLT_Mu50, HLT_CascadeMu100,
  HLT_HighPtTkMu100 exist in Summer22EE MiniAOD.
- Summer22EE MUO files: trigger keys have `nominal` = DATAeff/MCeff (≤ 7e-8); `stat`/`syst` are absolute SF
  uncertainties (for ID keys systup = nominal + hypot(stat, syst)); out-of-range errors contain "bounds".
  `muon_HighPt.json.gz` HLT keys have no DATAeff/MCeff, so the high-regime trigger term uses the `muon_Z` key
  `..._DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose`.
- Built (user decisions): momentum pf | tuneP | hybrid (per muon, PF pT ≥ 200), GE κ_b (q/pT + κ_b on MC by default,
  `kappaTarget`) and high-pT smearing for 2022–2023, `MuonSFProducer` with nominal SF in reco aggregators.
- Validation:
  - wiki tables transcribed exactly (`checkHighPtTables.py`; 3/3 injected wiki edits caught).
  - high-pT producer vs independent numpy: κ_b shifts exact (≤ 4.4e-16), smearing pulls mean 0.06, std 1.02 (n=387).
  - medium-pT output bit-identical to the previous producer (8 variants, 5248 muons).
  - SF weights vs independent Python correctionlib: ≤ 4e-8 (float storage) for 13 (default) and 29 (hybrid) columns.
  - Mutations caught by unit tests: lepton pt instead of matched muon, ε_data = ε_MC, regime ignored, charge-blind
    matching, η-major κ index, κ in c/GeV, aggregator ignoring weights.
- End to end (PTLL-400to600, 1000 events): `checkEndToEnd` 36/36 PASS with the default config and with the hybrid
  recipe (`EventSelection/test/validation/muonRecipes.py`); reco Zmumu Σw now includes the muon SF (1070.31 vs NANO
  1070.32). On the 2000-event inclusive file the brute-force checks fail only their ≥ 20-jet guard (9 jets). Data runs.
- User: the smearing and its systematics (medium, high, hybrid) and the PUPPI MET correction for TuneP muons are
  marked "ask the POG" (README, plan, default.yaml). Trigger-key `systup` = nominal + syst only (stat excluded).
- Trigger SFs now use HLT matching (user): only the triggering muon gets the trigger SF, i.e. the highest-pT selected
  muon within ΔR 0.1 of a `slimmedPatTrigger` object from the last filter of a fired path of its regime's trigger term
  (term field `paths`). If a path fired but no muon matches: warning, no trigger SF. Both rules are provisional (ask the
  POG; `OPEN_QUESTIONS.md`). The SF producer now only computes for events passing the full channel flag: Sel leptons
  exist also when the trigger fails, which first threw on PTLL event 1:1002:11473109.
  - FWLite on the test files (Tight+PFIsoTight, IsoMu24): Zmumu-like 0/528 events without a matched selected muon;
    exactly-one-tight-muon 2/~730, both fired by a muon failing Tight PF iso but passing the loose veto.
  - Unit test: 8/8 mutations caught (selection gate, leading choice, fired check, last filter, ΔR, term paths, SF for all
    muons, SF without match). Config checks: 3/3 mutations caught.
  - `checkMuonSF.py` redoes the HLT matching from MiniAOD with FWLite: ≤ 4.3e-8 on PTLL and inclusive DY, default and
    hybrid (the inclusive hybrid check fails only its ≥ 10 high-regime-events guard: there are none); no warnings.
- New `OPEN_QUESTIONS.md` (repo root): all open questions (MUO, JME, our decisions, unverified, literature).

## 2026-11-12 LHE tables in the NANO
- `output.lheTables` (default true, MC only): CMSSW `LHETablesProducer` with the standard NanoAOD settings
  (`precision 14`, `storeLHEParticles`), on the first of `inputs.lheInfo` = [externalLHEProducer, source] present.
  Writes `LHEPart` (pt, eta, phi, mass, incomingpz, pdgId, status, spin, firstMotherIdx, lastMotherIdx) and `LHE`
  (HT, HTIncoming, Vpt, AlphaS, Njets, Nb, Nc, Nuds, Nglu, NpLO, NpNLO).
- On 300 PTLL-400to600 events: all 222 written events match the LHEEventProduct HEPEUP read with FWLite (pdgId and
  status lists exact, pt / incoming pz within 3e-5, the 14-bit mantissa); 6–9 LHE particles per event. Data: no LHE
  branches. Config test: 3/3 mutations caught (MC-only guard, storeLHEParticles, scheduling).

## 2026-11-12 Selected leptons and MET in the NANO
- `<ch>Leptons` / `Gen<ch>Leptons` for every dilepton and leptonMET channel (pt, eta, phi, mass, charge, pdgId of the
  `<ch>Sel:leptons` copies, i.e. after dressing and muon corrections; filled whenever `<ch>Sel` passes, which does not
  include the trigger). `MET` / `GenMET` singleton (pt, phi) of the MET the leptonMET selectors use, only if such a
  channel exists at that level. Trap: singleton SimpleCandidateFlatTableProducer rejects a `cut` parameter.
- 300 PTLL-400to600 events (default and hybrid): multiplicity 2/1 exactly when `<ch>Sel` passes, |pdgId| as the
  channel, Z mass and W pt (lepton + MET) rebuilt from the tables match the boson tables (≤ 3.3e-7); MET equals
  slimmedMETsPuppi read with FWLite in all 222 events. Gen W channels select nothing in DY (no W sample locally), so
  their lepton content is untested on events. Data: tables present, no gen tables. Config test: 4/4 mutations caught.

## 2026-11-12 NANO documentation
- `NANO.md`: every table family, which configuration keys create, name and fill it, conventions, per-table columns, a
  worked `default.yaml` inventory and pitfalls. The inventory is measured from a 300-event PTLL MC file and a data file
  (39 EEC per-jet tables in MC: 12 Reco chains × 3 observables + Gen × 3).
- Checked on the file: EEC per-jet rows = jet rows (nominal, variation, gen); `nEntries` sums to the Entries count;
  `iJet` sorted; bins below the flow-inclusive extent; dilepton leptons leading first; jets in source order; gen jetId 0;
  LHE incoming pt 0; every written event passes some channel flag.

## 2026-11-13 NANO additions: event tables, AK8/AK4 jets, lepton details, GloParT
- Plan and user decisions: `nanoAdditions_plan.md`; reference: `NANO.md` §4.3, 4.5, 4.10–4.13.
- Added (all YAML-controlled):
  - `SelectionMET` (renamed from `MET`); `MET`/`RawMET` (PF), `PuppiMET`/`RawPuppiMET` (with the JES/JER/unclustered
    shifts), `GenMET`;
  - `PV`, `OtherPV`, `SV`, `Rho`, `GenVtx`, `GenPart` (standard pruning), and `Pileup_weight{,Up,Down}` (LUM
    correctionlib);
  - AK8: 42 NanoAODv12-style columns from `slimmedJetsAK8[srcIdx]`, `jerFactor` (new `EECJet` field), and the 23
    GloParT columns from an in-job re-tag;
  - lepton/photon detail columns with `undressedPt` and `triggerMatched`;
  - `AK4Jet` with the V4 JEC re-applied from raw (MC and run-dependent data keys) and `jesUncTotal`.
- Validation:
  - Unit tests: 16 mutations caught (pileup 2, jet extension and jerFactor 5, object extension 4, JEC 3, re-tagged
    columns 2). The JEC mutation that corrects the MiniAOD-corrected p4 survives the unit test (bare jets) and is caught
    by the real-MiniAOD check.
  - Every table against FWLite/correctionlib in Python on MC and data, within the storage precision. AK4: 1100 MC and
    546 data jets, including the selected set and order.
  - GloParT equals the standard NanoAOD `nanoAOD_addDeepInfoAK8` result exactly (1056 jets × 23 columns). All 1703 MC
    and 963 data pre-existing branches are bit-identical with re-tagging on.
  - `checkEndToEnd` 36/36 for default and hybrid; production and merge tests pass. Wall time 81 s / 1000 MC events.
- Traps:
  - The data JEC compound key has a `run` input.
  - `reco::Muon::Selector` values are bit indices: in PyROOT `passed(enum)` resolves to `passed(uint64_t)`, so use
    `selectors() & (1 << enum)`. My first ID check was wrong because of this.
  - `updateJetCollection` refuses `jetCorrections=None` with taggers.
  - The GloParT tag infos need GeometryRecoDB, MagneticField and TransientTrackBuilder.
  - `PFJetIDSelectionFunctor::operator()` is not const, so stream modules only.
  - Singleton tables take no `cut`.
- GloParT class scores do not sum to 1 per jet (NanoAOD's are identical).
- Not covered on real events: the photon columns (no GammaJets events in the DY file) and gen-level W leptons.

## 2026-11-13 Jets flagged, not removed, near selected objects
- User decisions: one bool column per cleaning channel; channel X's aggregators skip X's vetoed jets only.
- `EECJetOverlapProducer` (JetSetup) gives a `veto<ch>` extension on every jet table and a per-channel `vector<bool>`.
  `EECAggregator` has a `jetMask`. `EECJetSelector` no longer gets veto sources from `setupJets`.
- 1000 PTLL events:
  - `RecoJet` rows 1056 → 1283 and `GenJet` 1011 → 1510; e.g. 111 reco jets with `vetoZmumu`.
  - `checkEndToEnd` (updated to apply `veto<ch>`) 36/36 for default and hybrid, with 109 (reco) / 248 (gen) Zmumu-vetoed
    jets skipped in the recomputation.
  - Data: 11 jets (was 10), one with `vetoWmunu`.
  - Unit tests: 4/4 mutations caught (mask inverted/ignored, channel mix-up, ΔR threshold).
- Exposed: a one-electron gen jet whose E1C angles are undefined (rest-frame direction of a single particle). The check
  skips one-particle jets for E1C; question in `OPEN_QUESTIONS.md`.
- Answered (user): every jet needs >= 2 constituents. `jetCuts.minConstituents` is 2 in `default.yaml`; the schema
  minimum is 2 and `analysisConfig` rejects `cuts` variations below 2 (test fails without that check).
  `checkEndToEnd` again compares E1C for every jet and reports any jet with < 2 constituents. Per the user, the full
  regression was not rerun for this configuration change; only the config tests were (33 OK).

## 2026-11-13 V4 JEC on the AK8 EEC jets; jet-axis E1C frame; ZX_test config
- Plan: `ak8JEC_jetAxisFrame_plan.md`. AK8 jets: `PATJetJECProducer` (V4 `L1L2L3Res_AK8PFPuppi`, source order) before
  the translator, from a required-for-reco-pat `jec` block (default.yaml and ZX_test.yaml).
- V4/MiniAOD AK8 pt (MiniAOD pt > 170): MC mean 1.001 (0.984–1.011), Run2022F data mean 0.991 (0.983–1.018); below
  170 at most 1.017 (data), so translator `ptMin: 180` is safe against daughterless jets.
- `setP4` on a pat::Jet copy leaves the MiniAOD JEC levels: `correctedP4("Uncorrected")`, `jecFactor('Uncorrected')`
  and the energy fractions were wrong (300 PTLL events: 802/802 raw pts, 615/651 PF-jet fractions). Fixed with
  `correctedJet("Uncorrected")` + `scaleEnergy(c, "Uncorrected")`: 0 mismatches in MC (802 jets) and data (428). This
  also fixes the AK4 table's energy-fraction columns, which used the `setP4` copies.
- `frame: jetAxis` (EECs): lab frame, z = jet, x toward +z beam. Unit test vs lab-built (θ, φ); mutations (x flipped,
  boost added) caught.
- Unit/config tests: EECs 55, EECsPlugins 12, JetSetupModules 15 (sortByPt mutation caught), config 35 OK.

## 2026-11-13 First ZX_test production: unbinned EECs, four MC samples
- Plan and samples: `zxTestProduction_plan.md`; manifest `production/samples_zxtest.yaml`, tag `20261113_zxtest`.
- ZX_test: five observables `Unbinned` (coords `dR` / `theta, phi`), `aggregation.observables: []` (hist files empty;
  `hadd` of them works).
- Local, 4000 events per sample (one DAS file each, `writeConstituents=1`): written 1007 (DY), 309 (ZZ), 147 (WZ),
  390 (TT); reco AK8 jets 11, 18, 14, 65. CPU 14 ms/event (DY), 18 ms/event (TT) after 13 s start-up; max RSS 2.34 GB
  (CRAB `maxMemoryMB` raised to 3000). NANO about 1 kB per input event with constituents.
- `configs/checkUnbinned.py`: every unbinned entry (reco and gen, 5 observables, 4 samples) matches a numpy
  recomputation from the constituents (max |dcoord| 9e-5, |dw/w| 3e-7); `--mutate` fails every table.
- CRAB dry run: splitting as planned (613/17/79/232 jobs). Its runtime estimates (e.g. 8542 min per TT job) come from
  an 11-event test (16.5 s CPU, mostly start-up) and are not meaningful.
- Columnar framework moved to top-level `analysis/` (coffea; plan `analysis/PLAN.md`).

## 2026-11-14 ZX_test production `20261113_zxtest`: CRAB outcome, merge, sample plots
- Merged (`merge.py`; MC sums from the Runs trees): ZZ 17/17 jobs (genEventCount 4,043,040 = DAS), WZ 79/79
  (26,722,782 = DAS), TT 229/232 (73.3M of 74.3M), DY 589/613 (253.9M of 264.4M). TT and DY merged with
  `--allow-missing` (user decision).
- TT 17, 112, 223 fail deterministically: an AK8 jet with MiniAOD pt < 170 (daughters dropped) whose raw pt (326.8 in
  two inspected events) gives V4 pt ≈ 348.45, so `PATJetToEECJetProducer` throws. Open item in `TODO.md`.
- Grid traps seen with this task:
  - Stage-out to T3_US_FNALLPC from T2_CH_CSCS never succeeded (FTS HTTP 500, exit 60328; 0 of 613 DY jobs finished
    there), while 565 finished at T1_US_FNAL. Blacklisting T1_US_FNAL for an input problem pushes DY jobs to CSCS, the
    only other disk replica, so they cannot finish.
  - Some DY input files fail to open at FNAL (`cmsdcadisk.fnal.gov`, exit 8028) on every retry (up to 15).
  - Jobs at T3_US_FNALLPC ran 18-21 h (about 45% CPU efficiency) and hit the wall limit (exit 50664); about 2 h at T1.
  - CRAB caps `--maxmemory` at 5000 MB per core; TT 176 (4.7 GB peak, killed at 3000) finished at 5000.
  - A second `crab resubmit` on a task right after one still being processed returns HTTP 500.
- Sample plots (area-normalised, no cross sections yet): `~/nobackup/boostedV/plots/20261113_zxtest/` via its
  `make_plots.sh` (60 plots: kinematics, E2C by jet pT, E1C θ/φ/maps in the lab, helicity and CS frames). m_SD shows the
  W/Z peaks in WZ/ZZ and none in DY; the E2C peak moves to smaller ΔR with jet pT.

## 2026-11-14 Dilepton pT cut and back-to-back jet selection
- `pairPtMin` (dilepton channels): the chosen pair (closest to m_Z) must have pt >= pairPtMin, no fallback to another
  pair. ZX_test: 150 GeV at reco and gen. 2000 inclusive DY events: 8 written instead of 513, exactly those with a reco or
  gen Z above 150 GeV. Expected kept fractions (from `20261113_zxtest`): DY 0.5%, TT 2.5%, WZ/ZZ about 5%.
- `backToBack` (per channel; plan and user decisions: `backToBack_plan.md`): leading non-vetoed jet with Δφ > 2.8 and
  pt asymmetry < 0.3 against the channel's object, else the channel fails; only selected jets are written. Nominal jets
  only: validation rejects it with jet variations, for leptonMET channels and for singleObject with nMin 0.
- Validation: core and module unit tests (8 mutations caught), config tests (3 wiring mutations caught); disabled gives
  a byte-identical process dump to before (default MC and data, ZX_test). `JetSetup/test/validation/checkBackToBack.py`
  on enabled vs disabled runs: PTLL-400to600 431/517 events kept, 809 jets and 4045 (jet, EEC table) pairs identical to
  the recomputation, 903 other columns unchanged; inclusive DY 3/8. `--mutate` (dPhiMin + 0.1) fails it.
- Size: the PTLL-400to600 NANO goes from 13.4 to 9.4 MB. Every NANO carries a fixed 2.5 MB ParameterSets tree.

## 2026-11-15 Second-production manifest, ZX_test note, bvana back-to-back regions
- Manifest `production/samples_zxb2b.yaml` (ZZ/WZ -> 2l2q powheg, DY MLM PTLL-200to400/400to600/600; ~360 jobs), not
  submitted. Local timing with ZX_test: 28 s start-up, 5 ms/event (inclusive DY), 42 ms/event (PTLL-400to600), peak RSS
  1.9 GB; back-to-back adds ~0.5 ms/event although the jet chain now feeds the event filter.
- Note `notes/zxtest_AN/zxtest_AN.tex` (CMS-AN style) on every step of ZX_test. Cutflow on one file per sample from a
  loose variant (pairPtMin 0, backToBack off) plus `make_cutflow.py`, which reproduces the B2B flags exactly. Written
  fractions: ZZto2L2Q 0.30%, WZto2L2Q 0.51%, PTLL-binned DY 30-48%. ZZto2L2Q passes the reco Zmumu/Zee flags in only
  7.5%/5.6% of events: "2L" probably includes taus (to check in the generator cards).
- bvana regions: with B2B columns, step `backToBack` (B2B<ch>) after `channel`, and the jets are those with b2b<ch>.
  On the PTLL-400to600 test NANO it removes 2-3 events per region (written for another channel or level) and matches the
  B2B counts exactly. Synthetic test with mutations (flag ignored, veto jets used) caught; the uproot comparison now
  sums float32 genWeights in float64 (it failed by 5e-4 on weighted samples).
- 2026-11-15 (later): ZX_test note second pass. Citations: 16 papers checked against the arXiv API; MUO and EGM POG pages
  read on local copies (`~/nobackup/cms-wikis`); JME/LUM/XPOG pages only checked to exist (SSO). CMS-DP-2024-065 (quoted
  in our MuonScaRe comments) is not found on CDS and not cited. New facts from the POG pages: MuonScaRe was derived for
  tight, isolated muons in [26, 200] GeV (we apply it to all muons); Run-3 MiniAOD noIso MVA electron IDs include isolation
  in the barrel (our columns are affected); EGM recommends Run-3 electron scale/smearing (not applied). High-pT smearing
  factor for 2022 postEE is 0.32 (|eta| < 1.2) / 0.46, as implemented. The note now has an explicit order-of-operations
  section (muons, electrons, gen leptons, reco and gen jets) with a table of what each cut sees.

## 2026-11-15 Human review 1 of the ZX_test note: flags, JER order, frames, gen-jet flavour
Plan and decisions: `notes/zxtest_AN/review1_plan.md`.
- Flags: `<ch>B2B` = `<ch>Sel` AND a back-to-back jet; `<ch>` now ANDs it (the old `B2B<ch>` column and `<ch>B2BFilter`
  are gone). bvana: the region's `channel` step is the whole selection (no `backToBack` step).
- ZX_test: pairPtMin 200 (= jet pt cut), jet ID tight + lepton veto (idMask 3), translator ptMin 200, new E1C
  `jetProjective`. bvana boosted region: jet pt > 200, no dR(jet, Z) cut. The cross sections first given by the
  analysts were 13 TeV values and were withdrawn the same day; `analysis/xsec.yaml` is all null until 13.6 TeV values
  are collected.
- JER now on the pat::Jet (`PATJetJERCProducer`, POG JSON, per-srcIdx seed) before the translator and every jet cut;
  JES variations likewise. `pat::Jet::scaleEnergy` adds a level, so the translator takes the raw pt from
  `correctedP4(0)` (the "Uncorrected" level is no longer level 0). Central `SmearedPATJetProducer` (needs JRDatabase text
  files: AK8PFPuppi JRV2 = links to AK4PFPuppi files, resolution from JRV1) vs ours on 1000 PTLL-400to600 events
  (`JetSetup/test/validation/compareCentralJER*.py`): text and JSON payloads identical at all 2180 jets; 2124 gen-matched
  factors equal to 1.3e-7; 56 unmatched jets with z widths 1.09 (ours) / 1.04 (central). The central output is pt-sorted.
- GT 130X_mcRun3_2022_realistic_postEE_v6 has AK8PFPuppi JEC `Summer22EE_AK8PFPuppi_offline_v2` and JER
  `..._offline_v1`, not V4/JRV2, so central MiniAOD tools would need sqlite/text payloads. V4 MC AK8PFPuppi: L1FastJet,
  L3Absolute and L2L3Residual are 1 (2000 random points); only L2Relative acts. JME also ships `jetid.json.gz`
  (AK8PUPPI_Tight/TightLeptonVeto), not yet compared with `PFJetIDSelectionFunctor`.
- JER before the 180 cut made jobs fail: MiniAOD jets without daughters (pt < 170) smeared above 180 in 14/10508
  PTLL-200to400 events (1 above 200). User decision: translator at 200, such jets kept without constituents with a
  LogWarning, and they block the back-to-back selection when they would lead (`leadingEmptyJetPt`).
- Regression against HEAD (separate CMSSW area) on 1000 PTLL-400to600 events: 388 reco / 420 gen jets in both; all 75/8
  columns identical except rawPt (64 jets, <= 1 float ulp, from the float JEC factors of the extra level); E2C and E1C
  entries identical except jetAxis/jetHelicity of the jets with pz < 0 (182 reco, 199 gen), as intended.
  `checkUnbinned.py`: helicity/CS have 4-18 entries per table above the 1e-4 coordinate tolerance (max 6e-4), the same
  entries with HEAD code and HEAD checker, so pre-existing (probably float32 inputs boosted into the rest frame).
- Frames: jetAxis/jetHelicity x now toward the beam on the jet side (as CS); jetProjective: theta = dR,
  phi = atan2(-s dphi, s deta), s = sign(pz), equal to jetAxis phi near the axis (unit test both signs).
- Gen jets: NanoAOD-style flavour (HadronAndPartonSelector + JetFlavourClustering R 0.8) and the closest hadronic W/Z/H
  within 0.8 with its quark/gluon daughters in the jet (`EECGenJetMCTableProducer`).
- ZZto2L2Q / WZto2L2Q: the leptonic Z is ee/mumu/tautau in thirds; 54% of Z->ee/mumu have m_ll < 40 GeV (gamma*).
- Other analyses' back-to-back (read in the PDFs): CMS JES (1607.03663 Sec. 3.2) |dphi(Z, jet1)| > 2.8 and
  alpha = pt2/ptZ < 0.3; CMS SMP-20-010 (2109.03340 Sec. 4) leading jet with dphi > 2 and asymmetry < 0.3.
- validateJets_cfg.py: recluster specs copied the reco jec/retag blocks; now dropped (retag needs a GlobalTag).

- Cutflow v3 (`cutflow_zxtest/v3`, 7 samples): ZZ efficiency is dominated by ptll >= 200 (gen mumu 7.69% -> 0.26%);
  gen breakdown: mumu flavour 33.2%, two accepted leptons 9.0%, window 7.60%, ptll >= 200 0.258%. Jet-step loss in
  DY PTLL-200to400 (reco mumu, -39% after ptll): no jet >= 200 7%, then the ID step removes the leptons' own AK8 jet
  (410 of 415 lost jets overlap a selected muon; ZZ 17/17), dphi 15%. Gen-jet boson columns match a GenPart
  recomputation on ZZ/WZ (0 mismatches; radius 0.6 gives 17/39).
- JME docs (6 sites) mirrored to ~/nobackup/cms-wikis/jme-docs (SSO needs Kerberos + OTP; `sso_login.py`).
- JME review (`notes/zxtest_AN/jme_review.md`, from the local JME docs): compliant JEC V4/JER JRV2/PUPPI/MET-filter
  list; missing the mandatory Run 3 jet veto map (AK4-based event veto); CMSSW_15_0_22 `PFJetIDSelectionFunctor`
  RUN3 PUPPI TightLepVeto keeps NHF < 0.90 (unreachable else-if), 2 of ~69k |eta|<2.4 jets differ from `jetid.json.gz`;
  ECAL bad-crystal filter rerun for 2022 prompt era; payloads read from `latest/` (unpinned).
- JME follow-up implemented (user decisions): `jetVetoMap` flag (`JetVetoMapFlagProducer` on V4-corrected AK4 PUPPI;
  agrees with an FWLite recomputation on 3000 events, 69/1000 and 42/2000 vetoed); jet ID from `jetid.json.gz`
  (`JetId.h`, 0/395 mismatches; 6 mutations caught); `ecalBadCalib` rerun (crystal 838871812; probe with a present
  crystal flags exactly its 5 events); CAT paths pinned; eras `Run3, run3_nanoAOD_pre142X` from `inputs.eras`
  (needed for the calo geometry: no CASTOR) — NANO output identical with and without them. Soft-drop mass and MET
  flagged as future work.
