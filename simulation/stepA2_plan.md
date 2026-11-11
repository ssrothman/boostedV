# Plan: Step A.2 — CMSSW integration & custom NanoAOD

## Context
A.1 delivered the framework-free EEC library (`simulation/EECs`, CMSSW package `SRothman/EECs`). A.2 adds the CMSSW glue so central MiniAOD (first target: Run3Summer22EE MiniAODv4 DY madgraphMLM, A.3) can be processed into a minimal custom NANO plus aggregated EEC histograms with covariance. All of A.2 is in scope (all 7 selections).

Decisions already taken with you: one git submodule per new package; reco + gen (no matching); jets from MiniAOD **and** fastjet reclustering; curated, extensible template instantiations; norm chosen at runtime (plugins always use `norm::External`); minimal custom NANO; selections as flag producers + thin filters; systematics = JES/JER, constituent drop, constituent scale, threshold variations; aggregator output via TFileService; E1C frame = runtime menu (lab, jet-rest helicity, CS-like); aggregation H = Σw·h, C = Σw²·h hᵀ plus Σw, Σw², N.

### Points still needing your OK (proposed defaults; everything is a python parameter)
1. **Curated instantiations**: pENC: weight {Energy, Pt} × angle {DeltaR, Angle3D} × output {Dense, SparseMerged, SparseUnmerged, Unbinned}, runtime N ∈ [2,6] (16 module types). E1C: weight {Energy, Pt} × same 4 outputs (8 types). Charge weights / Extras added later by one `DEFINE_FWK_MODULE` line each.
2. **JES/JER vary the jet 4-vector only** (selection and jetPt/jetE norms), not the constituents; constituent-level effects are the separate drop/scale variations.
3. **GitHub repos**: I create local repos `simulation/{EECDataFormats,JetSetup,EventSelection}`; you create the GitHub remotes (names your choice) and I then register them as submodules. CMSSW package names: `SRothman/DataFormats`, `SRothman/JetSetup`, `SRothman/EventSelection`.
4. **Event-selection defaults** (table in §5) — physics cuts for you to adjust.
5. Integrated workflow cfg lives in boostedV: `simulation/configs/eecNano_cfg.py`.

## 0. Setup
- Dev area `/uscms_data/d3/srothman/eecdev/CMSSW_15_0_22` (reads 130X MiniAODv4; has correctionlib 2.6.4, fastjet 3.4.1, catch2, `FWCore/TestProcessor`). Symlink each new repo into `src/SRothman/<Pkg>`; build from `$CMSSW_BASE/src` (memory: symlink trap, `-Werror=missing-braces`).
- Copy this plan to `simulation/stepA2_plan.md`; add `simulation/JOURNAL.md` (TOC, newest last) for A.2 findings.
- Dependency graph: `EECs` (lib) ← `DataFormats` ← {`EECs/plugins`, `JetSetup`}; `EventSelection` independent (JetSetup consumes its lepton/photon outputs for cleaning via `edm::View<reco::Candidate>`).

## 1. SRothman/DataFormats
- `EECParticle {px,py,pz,E; int8 charge; int32 pdgId; float puppiWeight; uint32 srcIdx}` (srcIdx = index in packedPFCandidates / packedGenParticles, kept for later matching).
- `EECJet {p4 (corrected) pt,eta,phi,m; rawPt; uint32 srcIdx; uint8 jetIdBits; vector<EECParticle> constituents}`; `EECJetCollection = std::vector<EECJet>`.
- EEC result dictionaries: `std::vector<eec::DenseResult|SparseResult|SparseUnmergedResult|UnbinnedResult<1..2>>` (index-aligned with the input `EECJetCollection`), `eec::JetMeta`, entry structs. Verify `std::size_t` / `std::array` members round-trip through ROOT I/O (test writes + reads a file).
- `classes.h`, `classes_def.xml`, BuildFile; catch2 test for helpers (e.g. `toPseudoJets(const EECJet&)` attaching `EECParticleInfo(charge,pdgId)`).

## 2. SRothman/JetSetup
a. **Translators → `EECJetCollection`** (shared base for constituent conversion):
   - `PATJetToEECJetProducer`: `edm::View<pat::Jet>` (default `slimmedJetsAK8`; AK4 `slimmedJetsPuppi` via cfg). Constituents from `daughterPtrVector()`; PUPPI weight from a ValueMap or packed `puppiWeight()` (mirrors `PhysicsTools/NanoAOD/plugins/JetPFConstituentVarProducer.cc`), applied by scaling the 4-vector (switchable). Jet ID bits via `PFJetIDSelectionFunctor` (RUN3PUPPI… versions exist in 15_0).
   - `GenJetToEECJetProducer`: `slimmedGenJetsAK8` → `packedGenParticles` constituents.
   - `ReclusterEECJetProducer`: any `edm::View<reco::Candidate>` (packedPFCandidates / packedGenParticles), fastjet algo + R from cfg, candidate preselection (e.g. drop neutrinos at gen, optional PUPPI weighting). No JEC/JER/ID for these jets (documented).
b. **Jet selection** `EECJetSelector`: pt, |η|, jet-ID bits, min constituents, ΔR-cleaning against any number of `View<reco::Candidate>` inputs (selected leptons/photons from §5).
c. **Constituent selection** `EECConstituentSelector`: pt min, |pdgId| allow/deny, charged-only, min PUPPI weight.
   **Variations** `EECJetVariationProducer` (`EECJetCollection → EECJetCollection`, one variation per instance):
   - `jes`: correctionlib `POG/JME/2022_Summer22EE/fatJet_jerc.json.gz` (path + key from cfg; key names verified with `correction summary`), shift up/down.
   - `jer`: hybrid smearing (SF + resolution from the same JSON; gen-jet match ΔR<R/2 & |Δpt|<3σ, else stochastic), nominal/up/down.
   - `constDrop`: drop constituents of a chosen category with probability p.
   - `constScale`: scale constituents of a category (charged had / neutral had / photon / e / μ) by 1+δ.
   - RNG deterministic per (run, lumi, event, jet index, module label) hash, so results are reproducible and thread-safe.
   - Threshold variations: python clones of selectors with changed cuts.
d. **Python**: `JetSetup/python/eecJets_cff.py` — `setupJets(process, level='reco'|'gen', mode='pat'|'recluster', …)`, `addJetVariations(process, base, variations)` producing label-suffixed chains; `EECJetTableProducer` (also here) writes jet kinematics + optional constituent table to NANO.

## 3. SRothman/EECs plugins (in `simulation/EECs/plugins`, `python/`; library stays framework-free)
a. **`PENCProducer<Weight, Angle, Output>`** / **`E1CProducer<Weight, Output>`** (`edm::stream::EDProducer`, one calculator per stream): input `EECJetCollection`; params N, n, `norm ∈ {sumE, sumPt, jetE, jetPt, unity}` (computed here, passed as externalNorm), binning PSet (`regular|log|variable` axes), E1C `frame ∈ {lab, jetHelicity, jetCS}` built per jet as `frame::BoostRotate`. Output `std::vector<Result>` aligned with jets; library exceptions are rethrown as `cms::Exception` rather than skipping the jet, so no data is dropped silently.
   - Framework-free helpers (frame construction, norm, binning-from-PSet-like struct) go in `SRothman/EECs/interface/cmssw/` or plugin-local headers with catch2 tests.
b. **`EECTableProducer<Result>`**: per-jet table `<name>` (E_jet, n, N, nEntries) + entries table `<name>Entries` (iJet, bin or coord0..D-1, weight, symfactor for unmerged; Dense writes all bins). Weight precision configurable (default full float). Binning edges written once per run as run-level FlatTables (supported by `NanoAODOutputModule`).
c. **`EECAggregator`** (`edm::one::EDAnalyzer`, TFileService), accepts any binned result: per event h_e = Σ_jets (sparse, touched-bin list); H += w·h_e, C += w²·h_e h_eᵀ; events with no jets still count in Σw, Σw², N. w from `GenEventInfoProduct` or 1 (cfg).
   - Core in library: `eec::CovarianceAccumulator` (header, framework-free): packed upper-triangle storage, sparse k² update per event; throws if totalBins exceeds a cfg limit. Benchmarked in `bench/`.
   - Output: TH1D values (flow-inclusive linear bins), TH2D covariance, per-axis edges + axis-type strings, TParameters Σw, Σw², N.

## 4. Minimal custom NANO
`NanoAODOutputModule` keeping: our EEC/jet/selection tables, `genWeightsTable` (genWeight + Runs genEventSumw), pileup table (`NPUTablesProducer`), HLT bits (`TriggerResults`), selected-object tables via `SimpleCandidateFlatTableProducer`.

## 5. SRothman/EventSelection
Object selection reuses existing `PATMuonSelector` / `PATElectronSelector` / `PATPhotonSelector` (string cuts) and `CandViewShallowCloneCombiner`; our producers do event-level logic and write `bool` flags + selected objects (`std::vector<reco::LeafCandidate>` boson candidate). Generic `EventFlagFilter` (AND/OR of flags) provides filter mode. Python `eventSelection_cff.py` with per-channel helpers and threshold-variation clones.

| Selection | Proposed default |
|---|---|
| a. Trigger | OR of `HLT_*` path patterns (version wildcard) + MET filter flags from PAT `TriggerResults`; ≥1 good PV |
| b. Z→μμ | `HLT_IsoMu24`; 2 OS muons, tight ID + PFIsoTight, pT>26/15, \|η\|<2.4; 71<m<111, pair closest to m_Z |
| c. Z→ee | `HLT_Ele32_WPTight_Gsf`; 2 OS electrons, cut-based tight (RunIIIWinter22 V1, name verified in file), pT>35/15, \|η\|<2.5 excl. 1.4442–1.566; same mass window |
| d. W→μν | `HLT_IsoMu24`; exactly 1 tight iso μ pT>30, veto extra loose leptons; PUPPI MET>40, m_T>50 |
| e. W→eν | `HLT_Ele32_WPTight_Gsf`; exactly 1 tight e pT>35; same vetos/MET/m_T |
| f. Hadronic | `HLT_AK8PFJet500` OR `HLT_PFHT1050`; veto loose leptons and tight photons |
| g. γ+jets | `HLT_Photon200`; 1 tight photon pT>220, \|η\|<1.4442; lepton veto |

## 6. Implementation order (each step: code → tests → review → run → commit in its repo, conventional commits + `Assisted-by: ClaudeCode:claude-opus-5-5`)
1. Scaffolding + DataFormats (+ ROOT I/O round-trip test).
2. `CovarianceAccumulator` in library + tests + bench.
3. EECs plugins (producers, tables, aggregator).
4. JetSetup (translators, selectors, variations, tables, cff).
5. EventSelection.
6. `simulation/configs/eecNano_cfg.py` + end-to-end run; README per package, guide/stepA.md updates, journal.

## Verification
- **Unit (catch2, `scram b runtests`)**: framework-free helpers (frames: known boosts/axes; norms; JER smearing formula; variation RNG reproducibility; selection logic on hand-built candidates). `CovarianceAccumulator` vs brute-force dense outer product on random sparse histograms; non-vacuity shown by mutation (e.g. drop off-diagonal doubling / w instead of w²) making tests fail.
- **Module tests** with `edm::test::TestProcessor`: hand-built `EECJetCollection` in → EEC results equal direct library calls; table contents; aggregator H/C on 2–3 synthetic events vs hand computation.
- **End-to-end**: cmsRun on ~500 events of the DY MLM Run3Summer22EE MiniAODv4 file (needs your `voms-proxy-init` and a DAS file pick). Python (uproot/numpy, `-I`) cross-checks: (i) recompute pENC/E1C from the NANO constituent table by brute force and compare to stored entries; (ii) recompute H and C from NANO entries + genWeight and compare to aggregator ROOT output; (iii) sum rule Σ=1 for n=1, norm=sumE; (iv) flag rates sanity (Z→μμ peak at m_Z).
- Existing EECs tests (`ctest`, `scram b runtests`) still pass.
