# NANO additions plan (items 1, 3, 5, 6, 7, 8, 9)

Status: proposal, 2026-11-12. Decisions marked **Q** are asked of the user; the answers will be recorded here.

## Principles
- Everything is driven by the analysis YAML (new keys in `analysis.schema.yaml`, defaults in `default.yaml`, no hidden
  defaults), MC-only pieces are skipped in data, and every new table is documented in `NANO.md`.
- Prefer the standard CMSSW NanoAOD producers and their column names where they exist, so the branches mean what NanoAOD
  users expect.
- Column lists that are physics choices (taggers, IDs) are YAML lists of `{name, expr, type}` with PAT string expressions,
  so they can be changed without code.

## Items
1. **Jet tagging columns (AK8).** A new `EECJetExtensionTableProducer` (JetSetup) reads the selected `EECJetCollection`
   and the source `pat::Jet` view, uses each jet's `srcIdx`, evaluates the YAML expressions on that `pat::Jet` and adds
   the columns to the jet table as a NanoAOD extension table. Collection key `jets.collections.<C>.table.extraVariables`
   (pat mode only). **Q1** which columns; **Q8** on variation tables too or not.
3. **Gen particles.** The standard NanoAOD `finalGenParticles` pruning plus `genParticleTable` (`GenPart`: pt, eta, phi,
   mass, pdgId, status, statusFlags, genPartIdxMother). Switch `output.genParticles`. **Q2** pruning.
5. **Lepton and photon details.** Per channel, extension columns on `<ch>Leptons` / `<ch>Objects`: each selected object
   is matched (ΔR < 0.01, same charge) to the pat object it came from, and the YAML expressions for its source type
   (muons, electrons, photons) are evaluated on it. Also an `undressedPt`, and a `triggerMatched` flag against the
   channel's trigger paths (last filter, ΔR < 0.1, as for the muon SFs). Gen objects get none. **Q6**.
6. **Pileup, PV, gen vertex.**
   - The `Pileup` table is already there.
   - `PV`: standard `vertexTable` columns (npvs, npvsGood, x, y, z, chi2, ndof, score).
   - `Rho`: the `fixedGridRho*` values.
   - `GenVtx`: x, y, z, t0, from `genParticles:xyz0`/`t0`, MC only.
   - Optional in-job pileup weights from the LUM correctionlib file (`puWeights.json.gz`, nominal/up/down). **Q4**.
7. **MET.** Standard-format tables for PUPPI MET (pt, phi, sumEt, significance, and the JES/JER/unclustered-energy
   shifted pt and phi), raw PUPPI MET and PF MET. **Q3** naming relative to our existing `MET`.
8. **Jet correction details.** On the pat-mode jet tables:
   - `area`;
   - the MiniAOD JEC-corrected pt (so the JEC factor is `jecPt/rawPt`);
   - the JER smearing factor actually applied. This needs a `jerFactor` field in `srothman::EECJet` (DataFormats
     change, set by `EECJetVariationProducer`).
   **Q7**.
9. **AK4 jets.** `slimmedJetsPuppi` selected by a YAML cut, with a `SimplePATJetFlatTableProducer` (`AK4Jet`): kinematics,
   area, raw pt, jetId, hadron/parton flavour (MC), and b/c-tagging scores. **Q5** cut, taggers, JEC.

## Validation (per item)
- Config tests: schema, cross-checks, the modules and their parameters, no hidden defaults; mutations of the wiring.
- cmsRun on the PTLL MC and data test files, with independent checks: the extension columns equal FWLite reads of the
  source pat objects; GenPart against prunedGenParticles; the PV/rho/GenVtx/MET values against FWLite; the AK4 table
  against FWLite with the same cut; the pileup weights against correctionlib in Python.
- Unit tests for the new C++ producers (TestProcessor), with mutations.
- `checkEndToEnd` still 36/36, and data runs. `NANO.md`, the journal and the READMEs are updated.

## Decisions (user, 2026-11-12)
- Q1 AK8 columns: the NanoAODv12 FatJet set (msoftdrop, tau1-4, n2b1, n3b1, ParticleNet-with-mass {W,Z,T,H4q,Hbb,Hcc}vsQCD,
  ParticleNet-from-MiniAOD class probabilities + massCorr, hadron/partonFlavour, nB/nCHadrons), as a YAML list.
- Q2 GenPart: standard NanoAOD `finalGenParticles` pruning.
- Q3 MET: rename ours to `SelectionMET` / `GenSelectionMET`; `MET` = PF MET as in standard NanoAOD, plus `PuppiMET`
  (with shifts, sumEt, significance) and `RawPuppiMET`.
- Q4 Pileup weights in-job from the LUM correctionlib file (nominal/up/down); not applied to the aggregated histograms.
- Q5 AK4 jets: DeepJet, ParticleNet and RobustParT scores; **re-apply the latest JME JECs in-job** (correctionlib, MC and
  data with the run-dependent data keys) and add the JES total up/down.
- Q6 Lepton/photon columns: the ID/iso/IP/SC set.
- Q7 Add `jerFactor` to `srothman::EECJet`; columns area, jecPt, jerFactor.
- Q8 Tagging and correction columns on the nominal jet tables only (variation tables match via srcIdx).

## Status (2026-11-13): implemented
All items (1, 3, 5, 6, 7, 8, 9) are in; table reference in `NANO.md`, results in `JOURNAL.md`. Not covered on real
events: photon detail columns (no GammaJets events in the local DY file) and gen-level W leptons.
