# Muon POG Run-3 compliance plan

Source: MUO POG wiki (`muo-wiki`, downloaded 2026-11-12): `docs/guidelines/recommendations.md`, `docs/guidelines/corrections.md`, `docs/code/ptcorr/index.md`.

## Contents
- [Decisions taken](#decisions-taken)
- [Gap analysis](#gap-analysis)
- [Status](#status-2026-11-12-implemented)
- [Out of scope](#out-of-scope)
- [Tests](#tests)

## Decisions taken
- Recipe configurable: `momentum` pf (medium), tuneP (high), hybrid (per muon: PF pT ≥ 200 → high).
- Efficiency SFs computed in-job, stored in NanoAOD (`<ch>MuonSF`), nominal applied to the reco-level aggregated histograms; variations in NanoAOD only.
- Momentum corrections stay `apply: false` in `default.yaml`; default SFs = medium recipe (Tight ID, Tight PF iso, IsoMu24) for Zmumu and Wmunu.
- High-pT κ_b and smearing: 2022 preEE/postEE, 2023 preBPix/postBPix only.
- κ_b: q/pT → q/pT + κ_b [c/TeV] on MC (`kappaTarget: mc`, default) or − κ_b on data (`kappaTarget: data`). **To confirm with the MUO POG.**

## Gap analysis
Measured on the 1000-event PTLL-400to600 Summer22EE file: 347/697 muons (Tight or HighPt ID, pT > 15) have pT > 200 GeV; the leading muon is above 200 GeV in 263/275 events with two muons.

| Item | Now | Wiki (Run 3) |
|---|---|---|
| ID/iso | Tight + PFIsoTight | medium: OK. high: HighPt/TrkHighPt ID + TkIso, TuneP pT |
| Trigger | IsoMu24 | high: Mu50 \|\| HighPtTkMu100 \|\| CascadeMu100 |
| ID/iso/trigger SFs | none | `muon_Z.json.gz`, `muon_HighPt.json.gz` |
| Global-muon reco SF (high pT, binned in p) | none | `muon_HighPt.json.gz` |
| Medium scale+smearing | done (26–200 GeV) | apply for percent-level analyses |
| High scale (GE κb) | none | apply as correction (Run 3) |
| High smearing + 10% syst | none | per-era formula |
| Tracking SF, prefiring, medium reco SF | none | not needed in Run 3 |

## Status (2026-11-12): implemented
See `EventSelection/README.md` (modules, options, validation) and `JOURNAL.md` (results).
Choices made without an explicit decision (object if wrong):
- **Ask the POG:** the smearing and its systematics in every mode (medium, high, hybrid), including:
  - High-pT resolution systematic = an extra smearing (f = 0.46) on top of the nominal one.
  - High-pT smearing seeded per (run, lumi, event, muon index); κ_b and smearing only for TuneP pT ≥ 200 and |η| < 2.4.
- Regime is decided on the PF pT; SFs use the matched corrected muon's pT/η (undressed).
- Trigger SF: only the triggering muon (HLT-matched; **ask the POG**: provisionally the highest-pT matched muon, and no trigger SF with a warning if a path fired but nothing matches). Variations: SF ± stat or syst separately; the files' `systup` is nominal + syst only.
- **Ask the POG:** PUPPI MET in Wmunu is not corrected for TuneP − PF (the wiki asks for PF MET with TuneP muons).

## Out of scope
- Impact-parameter cut (dxy/dz) PU-loss systematic for Tight/HighPt ID: the analysis has to estimate it itself.
- The >500 GeV manual scale-shift sanity check from the wiki.
- 2024/2025 high-pT κb tables.

## Tests
- Unit tests: κb lookup at bin edges; TuneP p4; smearing width matching σ·factor (seeded, statistical tolerance); trigger-SF combination by hand for 1 and 2 muons; SF variations differing from nominal; the aggregator weight being applied.
- Mutation checks: κb sign flipped, η/φ bins swapped, p vs pT input to the reco SF, stat/syst mixed up.
- Real data and MC: run on `testdata` and compare SF weights with an independent correctionlib Python evaluation.
