# Workflow configs

`eecNano_cfg.py`: MiniAOD → minimal custom NANO plus aggregated EEC histograms with covariance.

```
cmsenv   # in /uscms_data/d3/srothman/eecdev/CMSSW_15_0_22/src
cmsRun eecNano_cfg.py inputFiles=file:in.root outputFile=nano.root histFile=hists.root isMC=1 maxEvents=-1 \
       [writeConstituents=1] [aggregateChannels=Zmumu,Zee]
```
VarParsing appends `_numEvent<N>` to `outputFile` when `maxEvents` is set.

- **Selections** (`SRothman/EventSelection`): every channel as a flag in `Selection_*`, and selected bosons/objects. Only events passing at least one channel are written.
- **Jets** (`SRothman/JetSetup`):
  - Reco: AK8 PUPPI from `slimmedJetsAK8` (translator ptMin 180, above the MiniAOD 170 GeV daughter cut), with JER nominal in MC and cuts pt > 200, |η| < 2.4, tight ID, cleaned against the selected leptons/photons.
  - MC variations: JES and JER up/down, plus the placeholder constituent variations `CONSTITUENT_VARIATIONS` from `eecJets_cff.py` (sizes invented).
- **Selection overrides:** the `addAllChannels(...)` call takes `objectCuts`, `metFilters`, `triggers` and `channelCuts`.
  - Gen: `slimmedGenJetsAK8` with the same kinematic cuts.
- **EECs** (`SRothman/EECs`), per jet collection: E2C and E3C (Pt weights, ΔR, sumPt norm, 50 log bins over 1e-3–1) and E1C in the jet helicity frame (20 × 20 bins). All are stored as `SparseMerged` NANO tables (`<Level><Var>E{1,2,3}C[Entries]`), with bin edges in the Runs tree.
- **Aggregation**: for each channel in `aggregateChannels`, `<ch>_eec<Level><Var>E<N>C` directories in `histFile`, filled from events passing that channel.
- **Event info (MC)**: `genWeightsTable` (scheduled, so the Runs-tree sums include every processed event), `Pileup`, `Generator`. HLT bits are also written.

`checkEndToEnd.py nano.root hists.root` (needs `writeConstituents=1`) checks:
- E2C/E3C/E1C against a numpy brute force;
- the sum rule;
- the Zmumu aggregator H, C and Σw against a recomputation from the NANO entries.

It needs ≥ 20 jets per level, so use a high-pT sample.
