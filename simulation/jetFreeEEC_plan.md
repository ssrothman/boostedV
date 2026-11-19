# Jet-free EEC collections (plan, 2026-11-19; reviewed)

Context: `analysis/SENSITIVITY_PLAN.md` Phase B2. Reference definition: arXiv:2608.14793 Eq. (6) (all final-state
particles but the boson's decay products, |η| < 2.4, weights ∏ p_T,i / p_T,V^N, R_ij in (η, φ), all tuples).
User decisions: write the code now; try all particle sets (charged PV-associated, all PUPPI-weighted, each also
restricted to the recoil hemisphere).

## Contents
- [Design](#design)
- [Collections](#collections)
- [Tests and validation](#tests-and-validation)
- [Analysis side](#analysis-side)
- [Open questions](#open-questions)

## Design
A jet-free observable is one pseudo-jet per event whose constituents are the selected particles, so the existing
chain (constituent selector, EEC observables, tables) is reused unchanged.
1. `EventEECJetProducer` (JetSetup/plugins): candidates (`packedPFCandidates` or `packedGenParticles`) → an
   `EECJetCollection` with 0 or 1 jet (p4 = vector sum, srcIdx 0, constituents with PUPPI weights applied if asked).
   Parameters: `absEtaMax`; `minFromPV` (reco; `PackedCandidate::fromPV()` ≥ value, charged only; 1 = PVLoose, the
   JME/CHS definition, PackedCandidate.h:716); `applyPuppiWeights`; `dropAbsPdgIds` (gen: neutrinos);
   exclusion: the selected leptons of every channel at that level (`excludeObjects`: VInputTag; a candidate is removed
   if within `excludeDR` and of the same charge); `hemisphere: none | recoil` with `recoilFlags`/`recoilObjects` in
   order, as `EECJetAxisProducer`'s recoil axis (keep particles with |Δφ(particle, boson)| > π/2); no jet if no
   channel passes (hemisphere mode) or fewer than 2 particles.
   The selection logic goes in a pure function in `JetSetup/src` (unit-testable without the framework).
2. `setupJets`: new `mode: event` (no JEC/JER/axes/variations/back-to-back; cleaning flags off). Charged-only and pT
   thresholds use the existing `constituentCuts`.
3. Observables: new optional key `collections: [names]` on an observable (schema + `eecNano_cfg.py` loop), so the event
   collections get only an unbinned E2C n = 1 (user: unbinned, binning settled in bvana) and no E3C. n = 2 needs no
   table: with the same norm its pair weight is the square of the n = 1 weight. Size per event is measured first
   (O(10^4) pairs charged, up to O(10^5) PUPPI-all).
4. Normalisation: `norm: jetPt` (vector-sum pT of the pseudo-jet) in the job; renormalised offline to the boson pT
   (stored `E_jet`; `bvana` `renormalise: boson.pt`), the paper's p_T,V.

## Collections
| name | level | particles |
|---|---|---|
| `EvtCh` | reco | charged, fromPV ≥ 1, \|η\| < 2.4, minus the selected leptons |
| `EvtPuppi` | reco | all, PUPPI-weighted, \|η\| < 2.4, minus the selected leptons |
| `EvtChHemi`, `EvtPuppiHemi` | reco | the same, recoil hemisphere only |
| `GenEvtCh`, `GenEvtAll`, + `Hemi` | gen | stable visible charged / all, \|η\| < 2.4, minus the selected gen leptons |

## Tests and validation
- Unit tests (pure function): η cut, fromPV cut on charged only, lepton removal (same charge within ΔR; an
  opposite-charge or distant particle kept), hemisphere boundary, no jet below two particles or without a passing
  channel; each checked by mutation.
- On the dev MiniAOD (`~/nobackup/boostedV/testdata/`, 1000 PTLL-400to600 events): the selected leptons are absent from
  the pseudo-jet (closest constituent ΔR); multiplicity per variant; the E2C n = 1 sum rule (Σ weights with the
  self-pairs = (Σ p_T / p_T,jet)² for norm jetPt); CPU per event and NANO size per variant.
- Reduced test production (DY 400-600 and 600, WZ, ZZ, ZH bb): prepared, not submitted, until you approve.

## Analysis side
`bvana` tables of the event collections (`jetTables: {reco: RecoEvtCh}` etc.; `eec.bin` with an integer binning gives
the per-event row), then the same significance and distortion metrics as for the AK8 E2C on the same events.

## Decisions (2026-11-19)
1. Lepton removal by ΔR + charge (`excludeDR` 0.005). Dressing is off in `ZX_test.yaml` (`mode: none`), so no photon
   removal now.
2. One test production: the jet-free collections plus `writeConstituents=1` and an E3C for the AK8 jets.
3. Jet-free E2C unbinned; binning studied in bvana.

## Revision after the dev-MiniAOD test (2026-11-19)
Findings on 100 DY PTLL-400to600 events (48 written; `analysis/SENSITIVITY_JOURNAL.md`):
- ΔR + charge removal missed one selected electron: its PF candidate (ΔR 5e-5, same pT) has the opposite charge.
- Gen: FSR photons up to 53% of the lepton pT within the dressing cone.
- fromPV ≥ 1 keeps 293 charged/event (519 GeV) vs gen 105 (409 GeV); ≥ 2: 90 (378 GeV), as PUPPI-charged 91 (395).
- Unbinned pair tables: ~935 kB per written event (RecoEvtCh 322, GenEvtAll 218 kB); constituents ~20 kB.
User decisions:
1. Remove exactly the selected leptons and, at gen, exactly the photons used in their dressing (no cones):
   `DileptonSelector` adds `leptonPtrs` (std::vector<edm::Ptr<reco::Candidate>>, the two selected leptons);
   reco: the leptons' `sourceCandidatePtr`s into the candidate collection; gen: the dressed lepton's daughters
   (`genParticleLevel:consts` copies, which keep the packedGenParticles four-momenta through MergedGenParticles and
   HepMC) matched to packedGenParticles by pdgId and four-momentum. Event collections then need every
   `jets/cleaning` channel to be a dilepton channel.
2. fromPV ≥ 2 (PVTight). Cut studies on dz, dxy, PUPPI weight and inverted dxy (displaced tracks) offline: a loose
   `RecoEvtAll` collection (no PV cut, no PUPPI weighting, constituents only) with per-constituent fromPV,
   pvAssociationQuality, dz, dxy, dzError, dxyError and the raw PUPPI weight (new constituent extension table).
3. Unbinned EvtE2Cn1 only for RecoEvtCh, RecoEvtPuppi, GenEvtCh, GenEvtAll; no Hemi collections (the hemisphere is a
   subset computable offline from the constituents and the boson φ); constituents written; AK8 E3Cn1 kept.
