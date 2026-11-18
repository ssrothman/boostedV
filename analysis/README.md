# Columnar analysis of the boostedV NANO (`bvana`)

coffea-based kinematic and EEC histograms with regions, cuts and binnings declared in YAML. Design and decisions:
`PLAN.md`. NANO contents: `../simulation/NANO.md`.

## Environment
```
source /uscms/home/srothman/nobackup/mambaforge/bin/activate dev     # coffea 2026.11, awkward 2.14, hist, mplhep
cd analysis
```

## Run and plot
```
python3 run.py configs/zxtest.yaml --tag 20261113_zxtest [--samples NAME ...] [--lumi PB] -o out.coffea [--export out.root]
python3 run.py configs/zxtest.yaml --files DY=nano_dy.root TT=nano_tt.root -o out.coffea
python3 plot.py out.coffea --hist bosonPt --region ZmumuReco --norm area --logy -o zpt.pdf
python3 plot.py out.coffea --hist E2Cn1 --region ZmumuReco --samples DY --split jetpt --project dR \
                --norm area --width log --logx -o e2c.pdf
python3 plot.py out.coffea --hist E1CHelicity --region ZmumuReco --samples TT -o e1c.pdf
```
- `--tag` reads the merged samples (`simulation/production/merge.py` → `merged/sample.json`). `--lumi` normalises MC to
  xsec × lumi / genEventSumw and needs every cross section in `xsec.yaml`; none is filled yet.
- `run.py` output: `hists[hist][region][sample]` (`hist.Hist`), `cutflow[region][sample][cut]` (`n`, `sumw`, `jets`),
  `sumw[sample]`.
- `plot.py`: overlay samples (default), regions (`--regions`), or the bins of an axis (`--split`); `--slice AXIS=LO:HI`
  (bin edges), `--project`, `--norm area`, `--width linear|log`, `--stack`, `--ratio LEGEND`, `--ratio-sum PREFIX` (pad: (D + X)/D per other sample and for their sum, D = samples starting with PREFIX), `--group NAME=PREFIX` (sum samples into one curve; empty PREFIX = all), log axes. Two remaining
  axes give a map. Label: "CMS Simulation Work in progress".

## LPC HTCondor (`condor.py`, design: `CONDOR_PLAN.md`)
```
python3 run.py CONFIG --tag TAG --lumi PB -o out.coffea --backend condor [--files-per-job 20] [--cpus 1] [--memory 2500] [--condor-name NAME] [--dryrun]
python3 condor.py status work/NAME          # complete / running / idle / failed / unsubmitted per job
python3 condor.py resubmit work/NAME        # failed or unsubmitted jobs
python3 condor.py collect work/NAME [--allow-missing]   # accumulates the parts into the -o path
```
Jobs run in the cvmfs coffea container on a snapshot of `bvana/`, `run.py` and the config taken at submission, and need
a grid proxy. `--backend local` (default) runs on this machine. `work/` is git-ignored.

## Configuration (`configs/zxtest.yaml`)
- `variables`: named expressions, e.g. `tau21: jets.tau2 / jets.tau1`.
- `binning`: `{regular: [n, lo, hi]}`, `{log: [n, lo, hi]}`, `{edges: [...]}`, `{integer: [lo, hi]}`, optional `label`.
- `regions`: `level` (reco | gen), `channel`, `cuts` (in order; each is a cutflow step), optional `weights`
  (event-level factors).
- `histograms`: `granularity` (event | jet | lepton | `eec:<observable>`), `axes` (`var`, `bins`, optional `name`),
  optional `cuts` (e.g. `eec.dR > 0`), `weight`, `renormalise` (EEC: weights × (E_jet/E′)^(nN)), `regions`.

**Expressions** are a restricted Python subset (`bvana/expr.py`): the objects `boson`, `leptons`, `jets`, `met`,
`event`, `eec` and their fields; numbers and booleans; `+ - * / ** %`; comparisons, chained or not; `and`, `or`, `not`;
`abs sqrt log log10 exp cos sin`; the reductions `num sum any all max min lead`; `deltaR(a, b)`.
Each expression has a level, which decides what a cut does:

| Level | Examples | As a region cut |
|---|---|---|
| event | `boson.pt > 200`, `num(jets) >= 1`, `met.pt < 50` | drops events |
| jet | `jets.pt > 300`, `deltaR(jets, boson) > 2` | drops jets, with their EEC entries |
| lepton | `leptons.mediumId` | drops events in which any selected lepton fails |
| eec | `eec.dR > 0` | histogram cuts only |

- A region requires its channel flag `<channel>`, which includes the back-to-back requirement `<channel>B2B` when the
  production enabled it. Its jets are those with `b2b<channel>` if the jet table has that column (a back-to-back NANO
  keeps only the selected jets), and otherwise the jets not vetoed for its channel (`veto<channel>`).
- A missing value, such as `max()` over no jets, fails a cut and goes to the overflow bin of an axis.
- EEC entries are filled with event weight × `weight` × `symfactor`.
- Columns present only at reco level (`msoftdrop`, taggers) need `regions:` limited to reco regions.- `restFrame: {axis: jet | <axis name>, mass: axis | <GeV>}` (EEC histograms of an E1C with weight Pt, n = 1, frame
  `jetAxis` about that axis, e.g. `E1CLabSoftDrop` with `axisSoftDrop`). Adds `eec.thetaRest`, `eec.phiRest`,
  `eec.cosThetaRest` and `eec.ERest` (rest-frame energy / M). `mass: axis` uses the axis' own mass; a number is the
  boson-mass hypothesis. Every particle is given m_π±. For rest-frame energy weights use
  `weight: eec.ERest / eec.weight`. See `bvana/frames.py`; the closure against the C++ `E1CHelicity` is in
  `tests/test_frames.py`.

## Truth spin-density matrix (`truthRho.py`)
```
cmsRun ../simulation/configs/lheNano_cfg.py inputFiles=file:in.root outputFile=lhe.root   # LHE tables, every event
python3 truthRho.py lhe*.root -o rho.json [--absy-max 0.5] [--pt-edges ...]
```
ρ of each LHE W/Z (helicity frame, fermion = the decay product with pdgId > 0) per boson, decay mode (lep/had) and V pT
bin, by spherical-harmonic moments (`bvana/spin.py`). Mass windows: Z 66–116 GeV, W 60–100 GeV.

## Jet-axis study (`axisStudy.py`, `axisDeltaR.py`)
```
python3 axisStudy.py nano*.root --rho-json rho.json [--level Reco|Gen] -o axes.md   # rest-frame E1C moments per axis
python3 axisDeltaR.py nano*.root -o outdir                                            # dR(axis, truth V) plots and table
```
Signal NANOs with the axis columns and `E1CLab<axis>` tables. Jets matched to a truth W/Z inside its mass window
(low-mass gamma* would dominate the rest-frame weights). `axisStudy.py` also needs LHEPart and the unselected truth rho
of `truthRho.py` (hadronic bins of the same bosons) for the L/T reweighting; it prints paired differences of the
sensitivity between axes. Documented in the ZX_test AN, Appendix B.

## Tests
```
python3 -m unittest discover -s tests            # ANALYSIS_TEST_NANO=<ZX_test NANO> adds the real-file comparison
```
