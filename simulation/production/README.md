# Batch production

Runs `../configs/eecNano_cfg.py` over whole datasets on CRAB or LPC HTCondor, then merges the outputs per sample.

| File | Role |
|---|---|
| `samples.yaml` | manifest: one entry per sample (dataset or file list, MC/data, GlobalTag, analysis YAML, lumi mask, backend, splitting) |
| `samples.schema.yaml`, `manifest.py` | schema and loader; the loader also validates every referenced analysis YAML |
| `submit.py` | submits samples under a tag; records provenance |
| `crabBackend.py` | one CRAB task per sample |
| `condorBackend.py`, `job.sh` | DAS file list in chunks, CMSSW tarball on EOS, one condor job per chunk |
| `status.py` | progress; `--resubmit` resubmits failed jobs |
| `merge.py` | hadd of the histogram files, NANO bookkeeping (`sample.json`), processed lumis for data |
| `compareOutputs.py` | object-by-object comparison of two NANO or histogram files |
| `test_production.py`, `test_merge.py` | tests |

## Workflow
```
cd /uscms_data/d3/srothman/eecdev/CMSSW_15_0_22/src && cmsenv
source /cvmfs/cms.cern.ch/common/crab-setup.sh       # for CRAB samples
voms-proxy-init -voms cms -valid 192:00               # submit.py needs >= 24 h left
crab createmyproxy --days 30                          # CRAB only; asks for the grid pass phrase, so run it interactively
cd .../simulation/production
./submit.py samples.yaml --tag 20261112_dyMLM [--only NAME ...] [--dryrun]
./status.py --tag 20261112_dyMLM [--resubmit]
./merge.py --tag 20261112_dyMLM NAME ... [--stage] [--allow-missing]
```
- **Tag** is `YYYYMMDD_<desc>`. Outputs go to `<outputBase>/<tag>/<sample>/` on EOS (CRAB adds `<primary dataset>/<tag>/<timestamp>/0000/`), and local bookkeeping to `work/<tag>/` (git-ignored). A sample is submitted at most once per tag. A failed submission's directory is moved to `<sample>.failed<k>`.
- **Provenance** (`work/<tag>/provenance/`): the git hashes of boostedV and its submodules, the manifest, and each sample's analysis YAML. `submit.py` refuses a dirty tree unless `--allow-dirty`, in which case the diff is recorded.
- **Dry runs** go to `work/dryrun/<tag>/` and never block the real submission. condor: builds the tarball and the job list without uploading or submitting. CRAB: `crab submit --dryrun`.
- **Each job** writes `nano_<i>.root` and `hists_<i>.root`. A job counts as done only when both exist.
- **condor tarball**: `work/<tag>/cmssw.tgz` (copied to `<outputBase>/<tag>/`) is built at the first condor submission of a tag and reused, so rebuilt CMSSW libraries need a new tag. The cfg, analysis YAML and lumi mask are shipped per job and are always current.

## Manifest fields
- `input`: `{dataset: <DAS name>}` or `{fileList: <file of LFNs/URLs>}` (condor only).
- `globalTag`:
  - central MC: the GT in the dataset name (`submit.py` warns on a mismatch);
  - data: the GT of the MiniAOD processing, from `edmProvDump`. For `Muon/Run2022F-22Sep2023-v2` that is `130X_dataRun3_PromptAnalysis_v1`.
- `lumiMask`: certification JSON for data (required), `''` for MC. Pin a dated directory under `/cvmfs/cms-griddata.cern.ch/cat/metadata/DC/`, not `latest/`.
- `splitting`: `files` (both backends) or `events` (CRAB `EventAwareLumiBased`), with `unitsPerJob`.
- `maxJobs`: `-1` for everything, N for a test run of the first N jobs.

## Merging
`merge.py` uses exactly the complete jobs. It refuses if any expected job is missing (condor: `jobs.txt`; CRAB: the job list saved by the last `status.py`), unless `--allow-missing` is given.
- **`merged/hists.root`**: `hadd` of the histogram files.
  - Values and covariance (sums of w·h and w²·hhᵀ), `sumW`, `sumW2` and `nEvents` add.
  - The axis histograms and `axisTypes` are identical in every job and survive unchanged.
  - The test reproduces a single job to 1e-12.
- **`merged/sample.json`**: the jobs used and missing, the NANO files, the number of events written, and for MC the Runs-tree `genEventCount`/`genEventSumw`/`genEventSumw2` over the same jobs. Normalise with these sums, not with DAS event counts, so that missing jobs stay consistent.
- **`merged/processedLumis.json`** (data): the lumisections processed by the jobs used (from the NANO LuminosityBlocks trees), for brilcalc.
- `--stage` copies `merged/` next to the job outputs.

## Job sizing
Measured with `default.yaml`:
- **MC**: about 35 s per 1000 events locally on PTLL-400to600 (high-pT jets; inclusive events are cheaper). A Summer22EE DY MLM file holds about 20k events on average, but sizes vary (731 and 2279 seen), so 5 files make a job of about 1 h.
- **Data**: 9.4 ms per event on an LPC worker for Run2022F Muon, at about 67k events per file, so 8 files make a job of about 1.5 h.
- **Start-up**: about 2.5 min per job (GlobalTag from Frontier, tarball unpacking).
- **Output**: each job's histogram file is about 55–60 MB; the NANO depends on the selected events.

## Tests
```
python3 -m unittest -v test_production      # with crab-setup.sh sourced; seconds
python3 -m unittest -v test_merge           # about 5 min; set MERGE_TEST_DIR to cache the cmsRun outputs
```
`test_merge` splits `testdata/` files (DY PTLL-400to600 MC, and a 2000-event skim of 8 Run2022F lumis) into two jobs. It checks that the merge equals a single job over both halves (histograms, Runs sums, Events, processed lumis), and that merging only one half does not.
