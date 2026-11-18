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
- 2026-11-15 Second ZX_test production `20261115_zxb2b` submitted
- 2026-11-16 Corrupted `slimmedJetsAK8` pt (question for JME/PAT)
- 2026-11-17 Background production `20261117_zxb2bbkg` submitted (TTto2L2Nu, WWto2L2Nu, single top)
- 2026-11-17 Alternative jet axes, subjet JEC/JER soft-drop mass, charge/energy correlators
- 2026-11-18 Truth-rho details: generator sin²θ_W, selection bias, plain charge weight
- 2026-11-18 Truth axis: gamma/Z/W/H bosons, hard-process parton fallback
- 2026-11-18 AN review 2: vertex boundaries, 150 GeV gen jets, extra-jet veto, E1C frame scheme, veto-map occupancy
- 2026-11-18 Truth rho: realistic window, full tables, joint helicities, shape validation, singly-resonant Z->4f

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

## 2026-11-15 Second ZX_test production `20261115_zxb2b` submitted
- `production/samples_zxb2b.yaml`, ZX_test.yaml at boostedV 3d1c550 (EECs ef60354, EventSelection 75644f1, JetSetup
  9f87b81): jet veto map, ECAL crystal, JME jet ID, eras, jetProjective. 5 CRAB tasks, 374 jobs (ZZto2L2Q 149, WZto2L2Q
  47, DY PTLL-200to400 74, 400to600 50, 600 54). Dry run: all test jobs exit 0; the FJR "Process element not found"
  message also appeared in the 20261113_zxtest dry run.
- Before submitting: jetProjective phi = 0 toward the beam on the jet side checked with particles tilted toward the
  near/far beam (jetAxis, jetHelicity, jetProjective, 24 jets, both signs of pz); fixing s = +1 fails all 12 pz < 0 jets.

## 2026-11-16 `20261115_zxb2b` failed: jet ID on jets without PF specific
- Status: ZZ 149/149 failed, WZ 47/47, DY 200to400 72/74, 400to600 37/50, 600 26/53 (8001, plus one 8028 and one 60328).
- The 8001 messages shown by `crab status --verboseErrors` (ZZ, DY 200to400) are all `PATJetToEECJetProducer/'jetsRecoRaw'`:
  "This PAT jet was not made from a JPTJet nor from PFJet." MiniAOD `slimmedJetsAK8` has `dropSpecific = "pt < 170"` as well as
  `dropDaughters` (`applySubstructure_cff.py:210-211`), so the no-daughter jets smeared above 200 also lack the PF fractions that
  `JetId::bits` (new in 3d1c550) reads, before the no-daughters branch. Deterministic: resubmission will not help.
- Fix (user decisions): jets without PF specific get jetId bit 2 (4) only (`kNoPFSpecific`, `JetId.h`), so they fail
  idMask 1/3 and can be counted in the `jetId` column; they no longer block the back-to-back selection (the leading
  jet is then the next one passing the ID). Module test fails with the old `bits` (exception above), passes with the fix.

## 2026-11-16 Third ZX_test production `20261116_zxb2b` submitted
- Same manifest as `20261115_zxb2b` with the no-PF jet ID fix (JetSetup 66274b8, boostedV 441bae0): 5 CRAB tasks submitted;
  dry run: all 5 test jobs exit 0 (as before, not covering a no-PF jet). The failed `20261115_zxb2b` tasks are left as is.

## 2026-11-16 W neutrino reconstruction (leptonMET channels)
- Plan: `neutrinoReco_plan.md`. Neutrino reconstruction is its own module (`WMassNeutrinoProducer`, `ZeroPzNeutrinoProducer` =
  `NeutrinoProducer<Strategy>`; contract in `EventSelection/README.md`), the boson is `LeptonNeutrinoBosonProducer`
  (lepton + neutrino) at reco and gen. `LeptonMETSelector` no longer produces `boson`; `bosonTag()` (eventSelection_cff.py)
  gives the boson input for tables and back-to-back. New table `<ch>Neutrino` with `status`; `channels.<ch>.neutrino`
  required for leptonMET channels (default.yaml: `WMassNeutrinoProducer`, wMass 80.3692, PDG 2025 world average, user-given).
- MET corrections stay future work: MET = `inputs.met` (`slimmedMETsPuppi`) / `genParticleLevel:mets`.
- Tests: `wMassNeutrino` unit tests (4 mutations each fail a test: larger |p_z|, complex -> 0, wrong cos sign, repeated-root
  status), module tests of the three producers, `test_analysisConfig.py` 38 passed.
- Validation vs the LHE neutrino (`EventSelection/test/validation/plotNeutrinoPz.py`, plot `plots/neutrino_pz_WZtoLNu2Q_powheg.png`;
  WZtoLNu2Q_powheg, first 8000 events of one file, default.yaml W channels; LHEPart is empty for the pythia-only WZ_pythia8).
  Reco (709 events): status 1 n=290, median(reco-true p_z) -3.6 GeV, 68% of |reco-true| < 101 GeV, smaller-|p_z| root closer
  to the truth in 57.9%; status 3 n=419, median 5.3, 68% < 81.5 GeV. Gen (699): status 1 n=445, 53.9% closer root; status 3 n=254.

## 2026-11-16 MET corrections (PUPPI MET, Summer22EE)
- Plan and sources: `metCorrections_plan.md`. User decisions: JER propagation yes; XY yes (switch); muon propagation yes (switch);
  JEC/JER variation propagation and electron/photon propagation deferred (TODO.md).
- Modules (JetSetup): `PATMETType1Producer` (raw MET - sum (p_T full - p_T L1) over AK4 PUPPI jets, muon-subtracted;
  `jetsetup::type1Shift` in `METTools.h`), `PATMETXYCorrectionProducer` (`met_xy_corrections`), `PATMETMuonShiftProducer`;
  `METUtil.h::withMETP4` keeps the Raw and Type1 levels (pat::MET stores them as packed shifts from the default p4: setP4 alone
  moves them; packing error ~1e-4 relative). Wiring `_metCorrections` (eventSelection_cff.py): `metType1Jets`, `metType1JetsJer`,
  `metType1`, `metXY`, per suffix `correctedMET`; `metLabel(..., process)` picks the last one; YAML `selection.reco.metCorrections`
  (default.yaml: apply, no muon propagation because default muonCorrections are off; ZX_test.yaml: apply false, so the running
  production configuration is unchanged).
- Tests: `type1Shift` unit tests; module tests of the three producers; 7 mutations each fail a test (cut on L1 pt, sign, muon
  shift sign, isPFMuon, data as MC, no JER, no EM cut); `test_analysisConfig.py` 39 passed (wiring, switches, loader checks).
- Validation (`test/validation/validateMET_cfg.py`, `checkMET.py`, 2000 DY MC and 2000 Run2022F events): the module equals an
  independent FWLite + correctionlib recomputation of the V4 Type-1 and XY MET to 1e-5 GeV (MC and data);
  MC closure: Type-1 from the stored production factors vs `slimmedMETsPuppi` 8e-3 GeV in 2000/2000 events (the first version
  used `pat::Jet::jecFactor(level)` as a raw-to-level factor and failed by 30 GeV: it is the factor from the level to Uncorrected);
  data closure: 5/2000 events differed by 1-20 GeV. Cause (4 events): muon-dominated jets whose standalone-only PF muon has unset packed flags (`pat::PackedCandidate::isStandAloneMuon` false) while `slimmedMuons` says isStandAloneMuon: production subtracts the muon, the jet falls below 15 GeV after JEC and drops out. Kept jets all had tracker-type muons. Fix: also subtract daughters that are the source candidate of a `slimmedMuons` muon with isGlobalMuon or isStandAloneMuon; data closure 1999/2000, MC 2000/2000. Subtracting every |pdgId| 13, PUPPI-weighting the muon or a full-jet pT > 15 cut are worse. Rest: one event whose production p4 and Type1 level disagree by 11.8 GeV (TODO.md). The Production code (runMETCorrectionsAndUncertainties.py, PATJetCleanerForType1MET, PATPackedCandidateProducer) was read in CMSSW_15_0_22; MiniAOD jets carry no muonSubtrRawPt (NanoAOD adds it with the same packed flags). `pat::MET` also stores a NoShift offset that `withMETP4` zeroes. V4 vs production Type-1 (MC): median 0.013 GeV, 99% 4 GeV,
  max 4.9; XY shift median 0.44 GeV, max 1.0 (MC); JER propagation (MC): median 3.8 GeV, 99% 37 GeV.
- End to end (`eecNano_cfg.py` on 2000 DY events, muon corrections on and propagated): exit 0; on the 53 W-selected events
  `SelectionMET` vs `PuppiMET` median |dpt| 1.9 GeV.
- Muon subtraction vs central NanoAOD (`JetSetup/test/validation/checkMuonSubtraction.py`; Run2022F test file vs the central
  `/Muon/Run2022F-22Sep2023-v2/NANOAOD` file with the same 3 lumis, copied to `~/nobackup/boostedV/testdata/central_nano/`):
  8062 of 8062 `slimmedJetsPuppi` jets (2000 events) match a Nano jet (`Jet` or `CorrT1METJet`, dR < 0.01); with the packed-flags rule
  our muon-subtracted raw pt gives Nano's `muonSubtrFactor` for all of them (max |d| 7.8e-3 = Nano's 6-bit storage, 2108 jets
  with a pdgId 13 daughter). The `+muons` rule of `PATMETType1Producer` differs from Nano on exactly 4 jets (the standalone-only
  muon jets, factor 0.82, 0.89, 1.0, 0.82 vs Nano 0); production's MET dropped those, so central Nano's `muonSubtrFactor`
  has the same blind spot and a Nano-based Type-1 recomputation would not close on them. Not done: the MC file.

## 2026-11-16 Corrupted `slimmedJetsAK8` pt (question for JME/PAT)
- The two ZX_test jets with MiniAOD pt 88/165 GeV are ~340 GeV jets (gen jet, subjets, AK4 jet agree): the stored p4 is scaled by 0.27/0.51, not by any JEC (V4 L2L3 >= 1.06). None in 1.5M AK8 jets elsewhere. Daughters were dropped because of the corrupted pt. Written up in `pog_question_ak8_corrupt_pt.md`.

## 2026-11-17 Background production `20261117_zxb2bbkg` submitted (TTto2L2Nu, WW, single top)
- Manifest `production/samples_zxb2b_bkg.yaml` (boostedV 85ca453 at submission; ZX_test.yaml unchanged from 20261116_zxb2b): 15 CRAB tasks,
  839 jobs, ~300k events/job, base datasets only (no `_ext1`). Samples: TTto2L2Nu_powheg (rerun with the pT > 200 and back-to-back
  selections), WWto2L2Nu_powheg, t-channel 4FS powheg-madspin (top/antitop x LNu/2Q), tW powheg (TWminus/TbarWplus x 2L2Nu/LNu2Q/4Q),
  s-channel (TBbartoLplusNuBbar, TbarBtoLminusNuB amcatnlo, TBbarto2Q powheg).
- Dry run: all 15 test jobs exit 0, no exceptions; CRAB's runtime estimates (400-1700 min) come from an 11-event test and are not meaningful.
- Gap (accepted by the user): the hadronic antitop s-channel sample does not exist in Summer22EE (`TBbarto2Q-s-channel` is top only: 3000/3000
  events have a top, none an antitop; checked on the first MiniAOD file). It would be 4.534 x 0.6741 = 3.06 pb. To be neglected if the
  selection acceptance of fully hadronic modes is negligible (to be checked on the new samples).
- Cross sections (`analysis/xsec.yaml`): GEN wiki 13.6 TeV top-group inclusive NNLO values (t-channel 145.0/87.2, tW 87.9 for top+antitop,
  s-channel 7.244/4.534 pb) x W BRs (lep 3 x 0.1086 = 0.3258, had 0.6741). Unverified assumptions: t/s-channel LNu/2Q refers to the top
  decay (W BR alone); tW LNu2Q covers either W leptonic (factor 2); L includes tau.
- ZZto4Q_powheg and WZto4Q_powheg cross sections are still null (not in this manifest).

## 2026-11-17 Alternative jet axes, subjet JEC/JER soft-drop mass, charge/energy correlators
Plan and decisions: `axesPolarimetry_plan.md`; questions: `axesPolarimetry_questions.md`.
- Soft drop recomputed in `EECJetAxisProducer` (`JetSetup/src/Axes.cc`). Against MiniAOD `SoftDropPuppi` (1000 DY
  PTLL-400to600 events):
  - Where the constituent sets agree (2071/2083 jets), the subjets equal the sum of MiniAOD's own packed daughters to
    7e-16, so the clustering is identical.
  - 12 jets differ in subjet membership. All 12 change under packing-size input perturbations (vs 3.1% of the agreeing
    jets): attributed to MiniAOD packing.
  - The soft-drop mass with MiniAOD's subjet JEC factors agrees within 1.7%.
  - V4 AK4 subjet JEC: msd ratio to MiniAOD, median 1.0001. Subjet AK4 JER: pt rms shift 1.7%.
- Axes: SD (production, β=1, z_cut=0.05), trimming, WTA (C/A, kt), recoil, truth. Lab E1C per axis
  (`E1CLab<axis>`). A truth axis falling back to the jet reproduces `E1CLab` exactly.
- Charge (Charge/ChargePt/ChargeEnergy) and energy correlators: sum rules hold to float precision on 300 DY events.
  They are held back in `configs/polarimetryObservables.yaml`.
- 16.8% of charged constituents in DY reco jets have 0 < PUPPI weight < 1.
- Truth ρ from LHE (`analysis/truthRho.py`; unselected LHE NANOs from `configs/lheNano_cfg.py`; 23 ZZto2L2Q, 8 WZto2L2Q
  and 6 DY PTLL-400to600 files):
  - ZZ, leptonic vs hadronic Z: they agree only with both Z on shell (`--both-in-window`). Otherwise, at pT < 50, ρ00
    differs by up to 16σ from the different partner populations.
  - With both on shell and sin²θ_W = 0.2229, all 9 elements agree (pT < 100: χ² 6.3/8).
  - With sin²θ_W = 0.2315, the parity-odd entries disagree (χ² 40/8). The Powheg header says "using mW, mZ. gmu scheme",
    i.e. on-shell sin²θ_W.
  - DY Z+jets, pT 400–500: ρ00 = 0.040 ± 0.007 and 0.044 ± 0.009. That fits between the paper's ρ00/(1−ρ00) ≈ 14%
    (γ ≈ 1.7) and 2–3% (γ ≈ 7) (Fig. 4, figure only; LO MLM vs NNLO, no |y| cut).
- Axis study (`analysis/axisStudy.py`, 16 ZZ + 8 WZ signal files, 2127 reco / 2263 gen truth-matched jets): ρ00
  sensitivity ⟨P₂⟩_T − ⟨P₂⟩_L, paired against the truth axis (0.13 ± 0.01).
  - Jet, soft drop and trimming: consistent with truth (|Δ| ≤ 0.016 ± 0.011–0.017).
  - WTA: −0.070 ± 0.009. Recoil: −0.09 ± 0.02.

## 2026-11-18 Truth-rho details: generator sin²θ_W, selection bias, plain charge weight
Replies in `axesPolarimetry_questions.md`; study files in `~/nobackup/boostedV/axisStudy_20261118` (the scratchpad
with the 2026-11-17 NANOs was wiped, so the inputs were regenerated there).
- Charge weights: only plain `Charge` (E1C and E2C, `DeltaR`). E2CCharge on 395 DY reco jets: Σ w·sym = (ΣQ)²
  exactly, and Σ w·sym·ΔR = Σ_{i≠j} Q_iQ_j ΔR_ij to 1e-5.
- Charged-constituent PUPPI weights (1000 DY events): 16.5% are fractional, with median 0.996; 2.5% have w < 0.9.
- Generator sin²θ_W:
  - Powheg ZZ/WZ `smcouplings.f`: mW 80.399, mZ 91.1876, so 0.22263 (the truthRho default).
  - MadGraph DY header: MW 79.907, so 0.23154.
  - ZZ lep vs had (both on shell, 24 files) at 0.22263: χ²/8 = 16.8 (pT < 100), 6.0, 7.4. At 0.23154: 71.5.
- Hadronic Z at V pT > 200: 93.5% in 66–116 GeV, 77% with both Z on shell. ρ00 does not depend on the window
  definition above 100 GeV.
- Selection bias, hadronic Z (149 production NANOs, channel + matched jet, vs unselected LHE): Δρ00 = −0.145 ± 0.019
  at V pT 200–300 and about −0.07 at 300–600. The acceptance rises by about 15% toward |cos θ*| = 1.
- The `dilepton` type has no lepton veto. Zmumu and Zee overlap: 0 of 429 DY events.
- Source of the bias: `<ch>` includes the back-to-back jet (pT > 200). At V pT 200–300, uncontained symmetric decays
  (ΔR(q,q̄) ≈ 2m/(pT sinθ*) > 0.8) fail it, while asymmetric single-quark jets pass. LHE emulation: ρ00 0.098 →
  −0.25; restored with R = 1.2 merging; the balance and Δφ cuts don't matter; no bias at 300+.
- A two-prong requirement sculpts much more: both quarks in the jet, or m_SD 70–110, give ρ00 ≈ 0.5–1.2 vs truth ≈ 0.1.
  z_cut = 0.1 removes |cos θ*| > 0.8.
- γ*/Z interference (ZZ LHE, leptonic vs hadronic ρ++ − ρ−− in m_ℓℓ bins): the effective A_ℓ ratio runs from −3.0
  (66–81) to +3.9 (101–116), and is 0.00 ± 0.04 for pure γ* (4–40). Window-averaged: 0.95 ± 0.07.
- Correction to the axis study above: it lacked the truth-boson mass window. Low-mass γ* → qq̄ (4–6 GeV) boosted with
  γ ≈ 100 dominated the weights. With the window (23 new signal files, 1728 reco jets), relative to the truth axis
  (0.149 ± 0.007): WTA −0.060 ± 0.005, recoil −0.053 ± 0.007, jet +0.008 ± 0.005, soft drop and trimming +0.020 ±
  0.005 (+0.013 ± 0.001 over the jet axis).
- Extra-lepton veto in the dilepton channels (both flavours, pair excluded by ΔR < 0.01), ZX_test and default.yaml.
  1000 DY events: reco Zmumu 192 → 187, Zee 176 → 174; no overlap.
- ZX_test AN updated (selections, MET, axes, soft-drop mass, observables, samples, cross sections) with Appendix A
  (truth ρ) and Appendix B (axis study, ΔR plots). Build: latexmk in notes/zxtest_AN.

## 2026-11-18 Truth axis: gamma/Z/W/H bosons, hard-process parton fallback
- Rules in `JetSetup/interface/TruthAxis.h`. Status 0 = boson: γ/Z/W/H, last copy in prunedGenParticles, q/g daughter;
  γ only `fromHardProcess`. Otherwise the nearest outgoing hard-process q/g (Pythia status 23, before FSR): status 1
  if its mother is a boson, 3 otherwise. 2 = none.
- MiniAOD (`axisStudy_20261118/truthMatch/checkTruthRules.py`): 3000 ZZ, 3000 WZ and 3000 DY events give the same bosons
  as the old rule; no photon has q/g daughters. Boosted ggH→bb: one H (status 62) per event.
  Outgoing hard partons are status 23, with mother = boson (status 62) for decay quarks.
- NANO, same events as before (`compareNano.py`): status-0 jets and their axes are identical. ZZ: 15 of the 16
  previously unmatched reco jets get status 3. DY PTLL 400-600: all 388 reco jets get status 3.
- Parton masses in the record: 0 for gluons and MadGraph light quarks; Powheg u/d 0.33, s 0.5, b 4.8 GeV.
  `addRestFrame` raises only below 2 m_π, so parton axes must be boosted with a fixed mass.

## 2026-11-18 AN review 2: vertex boundaries, 150 GeV gen jets, extra-jet veto, E1C frame scheme, veto-map occupancy
- **goodVertex:** `|z| <= 24`, `rho <= 2`, exactly the NanoAOD `goodPvCut`. The same applies to `npvsGood` and the MET XY
  vertex count. A boundary module test fails with `<`.
- **Gen AK8 jets:** one threshold of 150 GeV (translator and jet cuts; placeholder), for migrations. The analysis
  jet-pT binnings now start at 150.
- **Extra-jet veto:** `backToBack.extraJetAlphaMax` is mandatory. The event fails if another selected, non-overlapping
  jet has pt >= alpha * pt_V; negative disables it, 0 is the strictest. It is -1 everywhere. Four mutations are each
  caught.
- **E1C frames:** ZX_test writes only lab tables (jet and per axis), projective and CS. Helicity is computed offline
  (`restFrame: {axis: jet, mass: axis}`); `E1CHelicity` was dropped.
- **Veto-map occupancy** (`analysis/jetVetoMapOccupancy.py`, three DY 200-400 files copied with xrdcp; never the EOS FUSE
  mount): events passing a gen channel, 85 409; 5.45% fail the veto. AK8 jets: 4.5% removed; AK4 jets: 6.2%. The
  region eta 1.5-2.0, phi 1.8-2.7 is fully removed.
- **Cutflow regeneration with all processes:** pending the user's go-ahead (long cmsRun jobs).

## 2026-11-18 Truth rho: realistic window, full tables, joint helicities, shape validation, singly-resonant Z->4f
Reply to the Appendix A comments of `notes/zxtest_AN/human-review-2.md`; study `axisStudy_20261118/truthStudy.py`
(outputs in `truthStudy/`, LaTeX rows from `truthStudyTables.py`).
- `truthRho.py --window self|both|leptonic|none` (replaces `--both-in-window`); `leptonic` = leptonic boson in the
  selection's 61.19-121.19 window, nothing on the hadronic one (the truth of the measurement). `--joint`: diagonal of
  the joint helicity density from per-decay projector functions (`spin.helicityWeights`, `spin.jointDiagonal`).
- Frame bug: the fermion was boosted as massless. Powheg quarks have 0.33-4.8 GeV, so hadronic bosons below ~10 GeV
  got wrong angles (l=3,4 chi2 237/16 -> 13/16 with the LHE mass). Bosons in the window: rho00 changes <= 0.004.
- Shape test (`spin.higherMoments`, l=3,4 moments vanish for spin 1; 2D histogram vs `spin.binnedPrediction`): all bins
  pass except the ZZ leptonic Z at pT < 50, caused by singly-resonant Z->4f (m4f within 5 GeV of mZ; 21.5% of that bin;
  the ll pair is not from one propagator). 0.35% of leptonic Z above 200 GeV, absent in WZ.
- PDG 2025 (Table 10.2): on-shell 0.22342(9), MSbar 0.23122(6), effective 0.23154(6). The old 0.2229 row was an
  on-shell guess with mW = 80.385. Lep/had chi2 at pT < 100: Powheg 15.7/8, PDG on-shell 17.5, MSbar 66.7.
- Hadronic Z in window given the leptonic Z in the selection window: 0.94 above 200 GeV.

