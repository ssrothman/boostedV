# Workflow configs

| File | Role |
|---|---|
| `default.yaml` | the analysis configuration: every physics setting and collection label |
| `analysis.schema.yaml` | JSON Schema (draft-07, in YAML) for the configuration: closed objects, all keys required |
| `analysisConfig.py` | `load(path)` validates against the schema plus cross-reference checks and returns a dict |
| `eecNano_cfg.py` | MiniAOD → minimal custom NANO + aggregated EEC histograms, built entirely from the YAML |
| `checkEndToEnd.py` | validation of the workflow output |
| `test_analysisConfig.py` | loader and process-building tests |

```
cmsenv   # in /uscms_data/d3/srothman/eecdev/CMSSW_15_0_22/src
cmsRun eecNano_cfg.py config=default.yaml inputFiles=file:in.root outputFile=nano.root histFile=hists.root \
       isMC=1 maxEvents=-1 [writeConstituents=1]
```
- Only the per-job settings are command-line arguments; everything else is in the YAML.
- A relative `config` is looked up in the current directory, then next to `eecNano_cfg.py`. Batch jobs must ship the YAML, `analysisConfig.py` and `analysis.schema.yaml` with the cfg.
- VarParsing appends `_numEvent<N>` to `outputFile` when `maxEvents` is set.

## Configuration sections (`default.yaml`)
- **`inputs`:** MiniAOD labels, the gen-event-info label, and the HLT and MET-filter process names.
- **`selection`:** good-vertex cuts, MET filters, object definitions (PAT string cuts), and channels. A channel type is `dilepton`, `leptonMET` or `singleObject`; a new channel needs only a YAML entry.
- **`jets`:**
  - which channels' selected objects clean the jets;
  - the jet collections: reco/gen, MiniAOD jets or reclustering, the translator, jet and constituent cuts, the table name, JME correctionlib keys (`jerc`), and variations (MC only).
  - A collection with `mcOnly: true` is skipped in data. The constituent-variation sizes are placeholders.
- **`observables`:** E2C/E3C (`penc`) and E1C (`e1c`) specs. They are computed for every jet collection and variation; tables are named `<Collection><Variation><observable>`.
- **`aggregation`:** channels, observables and the covariance memory guard. It writes `<channel>_eec<Collection><Variation><observable>` directories in `histFile`.
- **`output`:** whether to keep the HLT bits, and the MC event tables (genWeights, with Runs-tree sums over every processed event; Pileup; Generator).

`analysisConfig.load` reports every schema violation with its path. It also checks cross-references: channel object collections, cleaning and aggregation channels, binned aggregation observables, translator keys per jet type, JES/JER only on reco MiniAOD jets, and unique table names.

## Tests
- `python3 -m unittest -v test_analysisConfig` (inside cmsenv). It checks that:
  - malformed configurations are rejected;
  - for MC and data, no module of the SRothman packages relies on a `fillDescriptions` default, because every tracked parameter is set from the YAML;
  - YAML edits reach the right modules.
- `checkEndToEnd.py nano.root hists.root` (run with `writeConstituents=1`; needs ≥ 20 jets per level, so use a high-pT sample) checks:
  - E2C/E3C/E1C against a numpy brute force;
  - the sum rule;
  - the Zmumu aggregator H, C and Σw against a recomputation from NANO.
