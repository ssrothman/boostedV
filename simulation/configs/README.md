# Workflow configs

| File | Role |
|---|---|
| `default.yaml` | the analysis configuration: every physics setting and collection label |
| `analysis.schema.yaml` | JSON Schema (draft-07, in YAML) for the configuration: closed objects, all keys required |
| `analysisConfig.py` | `load(path)` validates against the schema plus cross-reference checks and returns a dict |
| `eecNano_cfg.py` | MiniAOD → minimal custom NANO + aggregated EEC histograms, built entirely from the YAML |
| `checkEndToEnd.py` | validation of the workflow output |
| `checkLevels.py` | validation of the reco-only / gen-only / OR selection modes |
| `test_analysisConfig.py` | loader and process-building tests |

```
cmsenv   # in /uscms_data/d3/srothman/eecdev/CMSSW_15_0_22/src
cmsRun eecNano_cfg.py config=default.yaml globalTag=<GT> inputFiles=file:in.root outputFile=nano.root histFile=hists.root \
       isMC=1 maxEvents=-1 [lumiMask=golden.json] [writeConstituents=1]
```
- Only the per-job settings are command-line arguments; everything else is in the YAML.
- `globalTag` is required (no default); no module reads conditions yet, and loading the GT adds about 1 min of Frontier start-up. `lumiMask` restricts the source to a certification JSON.
- Batch processing of whole datasets: `../production/README.md`.
- A relative `config` is looked up in the current directory, then next to `eecNano_cfg.py`. Batch jobs must ship the YAML, `analysisConfig.py` and `analysis.schema.yaml` with the cfg.
- VarParsing appends `_numEvent<N>` to `outputFile` when `maxEvents` is set.

## Configuration sections (`default.yaml`)
- **`inputs`:** MiniAOD labels, the gen-event-info label, and the HLT and MET-filter process names.
- **`selection`:**
  - `levels`: `[reco]`, `[gen]` or `[reco, gen]` (the OR). Events passing any channel at an enabled level are written, with all observables for both jet levels, and aggregated per channel and level. In MC both levels are always evaluated and their flags stored (`Selection_*`, `GenSelection_*`); data has only reco, and a gen-only configuration is an error there.
  - `reco`:
    - good-vertex cuts and MET filters;
    - muon momentum assignment (`muonCorrections.momentum`: pf | tuneP | hybrid by pT) and optional MUO POG medium- and high-pT momentum corrections (`muonCorrections.apply`, off by default);
    - MC muon efficiency scale factors per channel (`muonScaleFactors`), applied to that channel's reco-level aggregated histograms and stored as `<channel>MuonSF`;
    - optional lepton dressing (`dressing.mode: none | fsr | cone`, default `none`; with dressing, `dressedCut` selects on the dressed leptons);
    - objects (PAT string cuts) and channels with triggers.
    - See `EventSelection/README.md` for the open POG questions on the muon corrections.
  - `gen` (MC): Rivet particle-level settings, objects (cuts on dressed leptons or isolated photons), and channels without triggers. The default kinematic cuts mirror the reco ones.
  - A channel type is `dilepton`, `leptonMET` or `singleObject`; a new channel needs only a YAML entry.
- **`jets`:**
  - which channels' selected objects clean the jets (reco jets use the reco objects, gen jets the gen objects);
  - the jet collections: reco/gen, MiniAOD jets or reclustering, the translator, jet and constituent cuts, the table name, JME correctionlib keys (`jerc`), and variations (MC only).
  - A collection with `mcOnly: true` is skipped in data. The constituent-variation sizes are placeholders.
- **`observables`:** E2C/E3C (`penc`) and E1C (`e1c`) specs. They are computed for every jet collection and variation; tables are named `<Collection><Variation><observable>`.
- **`aggregation`:** channels, observables and the covariance memory guard. For each enabled level it writes `<channel>_<level>_eec<Collection><Variation><observable>` directories in `histFile`, filled from events passing that channel at that level, for every jet collection (e.g. reco observables in gen-selected events).
- **`output`:** whether to keep the HLT bits, and the MC event tables (genWeights, with Runs-tree sums over every processed event; Pileup; Generator).

`analysisConfig.load` reports every schema violation with its path. It also checks cross-references: channel object collections, cleaning and aggregation channels, binned aggregation observables, translator keys per jet type, JES/JER only on reco MiniAOD jets, and unique table names.

## Tests
- `python3 -m unittest -v test_analysisConfig` (inside cmsenv). It checks that:
  - malformed configurations are rejected;
  - for MC and data, no module of the SRothman packages relies on a `fillDescriptions` default, because every tracked parameter is set from the YAML;
  - YAML edits reach the right modules.
- `checkLevels.py reco.root gen.root or.root [miniaod.root]` (outputs of the three modes on the same input) checks:
  - every written event passes an enabled level, and the OR output is exactly the union of reco-only and gen-only;
  - every written event has EEC tables for all jets;
  - the gen dilepton masses are in the window;
  - gen Z→μμ is compared with an FWLite selection of bare prompt muons (approximate, since the gen selection uses dressed leptons).
- `checkEndToEnd.py nano.root hists.root` (run with `writeConstituents=1`; needs ≥ 20 jets per level, so use a high-pT sample) checks:
  - E2C/E3C/E1C against a numpy brute force;
  - the sum rule;
  - the Zmumu aggregator H, C and Σw at each level against a recomputation from NANO.
