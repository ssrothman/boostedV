# Plan: columnar analysis framework (`analysis/`)

## Contents
- [Goal](#goal)
- [Design](#design)
- [Example configuration](#example-configuration)
- [Files](#files)
- [Tests](#tests)
- [Decisions (user, 2026-11-13)](#decisions-user-2026-11-13)

## Goal
Kinematic and EEC plots from the boostedV NANO with selections, cuts and binnings declared in YAML, so a new
region, cut or binning needs no code. coffea (mambaforge `dev` env: coffea 2026.11, awkward 2.14, hist 2.12, mplhep).

## Design
1. **Objects** (`objects.py`): per region, the event view at one level (reco or gen) and channel:
   `boson`, `leptons`, `jets` (the channel's jet table, minus the jets vetoed for that channel), `met`, `event`
   (event-level columns), and lazily `eec[obs]`: the unbinned entries as [event][jet][entry], aligned with `jets`.
2. **Cuts** (`cuts.py`): strings evaluated on those objects with numpy/awkward in scope, e.g. `boson.pt > 200`.
   Three kinds by the array they return: event mask, jet mask (drops jets, with their EEC entries) and lepton mask
   (every selected lepton must pass). Each cut is a cutflow step with weighted and unweighted counts.
3. **Binnings** (`binning.py`): named axes, `regular: [n, lo, hi]`, `log: [n, lo, hi]`, `edges: [...]`, or
   `integer: [lo, hi]`; reused by name across histograms.
4. **Histograms** (`histograms.py`): each has a granularity, `event`, `jet` or `eec:<obs>`, and axes
   `{var: <expression>, bins: <binning>}`. Expressions of a coarser granularity broadcast (e.g. `jets.pt` on an EEC
   histogram). Weight: event weight × (EEC: `weight × symfactor`); `(E_jet/E')^(nN)` renormalisation optional.
   `hist.Hist` with Weight storage, one per (sample, region, histogram).
5. **Processor** (`processor.py`): generic, driven by the YAML; event weight = genWeight × xsec × lumi / genEventSumw
   when cross sections and `--lumi` are given (`samples.py`), else genWeight.
6. **Plotting** (`plotting.py`, `plot.py` CLI, mplhep CMS style):
   - 1D overlays and stacks of samples or regions, with ratio panel; normalisation to unit area, per bin width,
     or luminosity; log axes.
   - EEC plots: E2C vs ΔR (per log-bin width, optional R-weighting), slices in jet pt; E1C 2D (θ, φ) maps and their
     θ/φ projections.
   - Projections and slices of any multi-axis histogram by axis name, e.g. `--slice jetPt=300:500`.
7. **Run** (`run.py`): `--config analysis.yaml --tag <production tag> | --files ...`; futures executor locally,
   option for an LPC condor/dask executor later.

## Example configuration
```yaml
binning:
  zpt: {regular: [60, 0, 1200]}
  jetpt: {edges: [200, 300, 400, 600, 1000, 2000]}
  dR: {log: [50, 1.0e-3, 1.0]}
regions:
  ZmumuBoosted:
    level: reco
    channel: Zmumu
    cuts:
      - boson.pt > 200
      - leptons.tightId               # lepton mask: all selected leptons
      - jets.pt > 300                 # jet mask
      - abs(jets.eta) < 2.0
      - ak.num(jets) >= 1             # event mask
histograms:
  bosonPt: {granularity: event, axes: [{var: boson.pt, bins: zpt}]}
  jetMass: {granularity: jet, axes: [{var: jets.msoftdrop, bins: {regular: [40, 0, 200]}}]}
  E2C: {granularity: 'eec:E2Cn1', axes: [{var: eec.dR, bins: dR}, {var: jets.pt, bins: jetpt}]}
```

## Files
`objects.py`, `cuts.py`, `binning.py`, `histograms.py`, `processor.py` (replaces the example), `plotting.py`,
`plot.py`, `run.py`, `configs/zxtest.yaml`, `README.md`; kept: `schema.py`, `eec.py`, `samples.py`, `xsec.yaml`.

## Tests
- Cuts: event/jet/lepton masks on synthetic events; a jet cut removes the jet's EEC entries; cutflow counts.
- Histograms: fill totals vs an independent uproot computation on a real NANO (event, jet and EEC granularity).
- Binning: each spec type gives the expected edges.
- Plot smoke tests (files written, per-bin-width normalisation integrates back to the total).

## Decisions (user, 2026-11-13)
1. Cuts and variables: a restricted but flexible expression language, not free Python. Parsed with `ast` and
   evaluated from a whitelist: object fields (`jets.pt`, `event.PV.npvsGood`), numbers and booleans, arithmetic,
   comparisons (chains allowed: `200 < boson.pt < 400`), `and`/`or`/`not`, and the functions `abs`, `sqrt`, `log`,
   `log10`, `exp`, `num`, `sum`, `any`, `all`, `max`, `min`, `lead` (first object), `deltaR(a, b)`. Derived variables
   can be named in the YAML (`variables:`) and reused. Anything else is a configuration error.
2. Output: one `.coffea` per run; optional export to ROOT (uproot) or pickle.
3. Plot label: "CMS Simulation Work in progress".
