# Plan: human review 1 of the ZX_test AN

Source: `human-review-1.md`. Items are grouped by the kind of work. Each item gives the review point (§), what was found, and the action.

## Contents
- [A. Code changes](#a-code-changes)
- [B. Investigations](#b-investigations)
- [C. Questions for POGs (to OPEN_QUESTIONS.md)](#c-questions-for-pogs-to-open_questionsmd)
- [D. Deferred studies (to TODO.md)](#d-deferred-studies-to-todomd)
- [E. Note-only edits](#e-note-only-edits)
- [Order of work](#order-of-work)
- [Status](#status)

## A. Code changes

A1. **Flag naming (Table 3, §12).**
- `<c>Sel` is the dilepton selection, and `<c>B2B` the back-to-back requirement.
- `<c>` = `<c>Sel` AND `<c>B2B` (if enabled) AND, at reco, `<c>Trigger` AND `goodVertex` AND `metFilters`.
- The `B2B<c>` columns go away. The per-jet column `b2b<c>` is renamed `<c>B2B` for consistency (to confirm).
- Plumbing:
  - `eecNano_cfg.py`: the FlagCombiner now takes the B2B flag, and `anyChannel` takes `<c>`.
  - `eecJets_cff.backToBackFlag`.
  - bvana `region.py`: cutflow steps become `channel` (= `<c>`), with the B2B step folded in. The old-NANO fallback is kept.
  - Tests and `NANO.md` updated.

A2. **TIGHTLEPVETO jet ID (§7).**
- The jet selection requires bit 1 instead of bit 0.
- This is a config change in `ZX_test.yaml` jetCuts, plus a check of how the ID bit is selected.

A3. **JER before selections (§9 J3).**
- Today the translator drops jets with JEC pT < 180 *before* the JER smearing.
- Constraint: MiniAOD stores AK8 daughters only for jets with MiniAOD pT > 170, so a jet with no constituents cannot enter the correlators.
- Proposed: smear the `pat::Jet` (after JEC, before translation), then apply the 180 cut to the smeared pT. Decision needed (Q1).

A4. **E1C frames (§8).**
- In `jetAxis` and `jetHelicity`, x̂ is turned toward the beam closest to the jet: sign(jet p_z), +z if p_z = 0, as in `jetCS`. Checked: `EECs/src/Config.cc:102-113`. CS already does this.
- New frame `jetProjective`: θ = ΔR(particle, jet axis), and φ = the angle of (Δη, Δφ) in the η–φ plane, with φ = 0 pointing toward the closer beam. The handedness convention needs a decision (Q3).

A5. **GenJet flavour and boson association (§7).**
- `slimmedGenJetsAK8` carries no flavour. Add the hadron and parton flavour as in central NanoAOD `GenJetAK8`, by `JetFlavourClustering` on `slimmedGenJetsAK8` (to be checked in PhysicsTools/NanoAOD).
- Boson association, proposed:
  - for each gen jet, the index and PDG ID of the closest last-copy, hadronically decaying W/Z/H in `prunedGenParticles` with ΔR(jet, boson) < 0.8;
  - also the number of its quark daughters within ΔR < 0.8.
- To confirm (plan review).

A6. **bvana boosted region (Table 8).** Drop ΔR(jet, Z) > 2.0, and set jet pT > 200 to match ptll > 200 (analysis config).

A7. **Cross sections (`analysis/xsec.yaml`).**
- WITHDRAWN 2026-11-15: the values below are 13 TeV cross sections (user); none is used. Kept only as a record.
- Fill from the user-given totals times PDG 2024 branching ratios:
  - DY MLL-50: 6077.22 pb (FEWZ 3.1, NNLO QCD + NLO EW);
  - ZZ: 16.523 pb;
  - WZ: 47.13 pb;
  - TTto2L2Nu: 88.51 (Q4);
  - WW: 118.7 pb, which has no sample yet and is recorded for later.
- ZZto2L2Q = 2 · σ_ZZ · B(Z→ℓℓ) · B(Z→qq). WZto2L2Q = σ_WZ · B(Z→ℓℓ) · B(W→qq'). Both depend on whether ℓ includes τ (B4).
- The PTLL-binned DY needs per-bin cross sections, which were not given (Q4).

## B. Investigations

B1. **goodVertex (§5.2).**
- Central NanoAOD (`PhysicsTools/NanoAOD/python/vertices_cff.py:12`, CMSSW_15_0_22) uses `!isFake && ndof > 4 && abs(z) <= 24 && position.Rho <= 2` and counts every good vertex (`PV_npvsGood`).
- Ours requires the *first* vertex with `ndof > 4, |z| < 24, rho < 2`. The difference is only `<` vs `<=`, which is measure zero.
- Also check against `Flag_goodVertices` (already in the MET-filter AND).
- Action: state this in the note. Optionally switch to `<=` to match exactly.

B2. **MET filters (§5.2).** The JME wiki is not in `~/nobackup/cms-wikis` (only the EGM and MUO wikis are). This needs the user, or SSO access. A `cookies.txt` exists there, but I will not use it unless the user asks.

B3. **JEC levels and a central producer (§7).**
- List the levels: the compound L1L2L3Res = L1FastJet, L2Relative, L3Absolute, L2L3Residual (MC: residual = 1). Check this in the correctionlib json.
- Check whether the GT `130X_mcRun3_2022_realistic_postEE_v6` carries Summer22EE V4 AK8PFPuppi. If it does, `updateJetCollection` (central, `JetCorrFactorsProducer`) could replace `PATJetJECProducer`. Compare the two on the 802-jet validation sample.

B4. **ZZto2L2Q channel-flag efficiency (Table 7).**
- Measure a gen-level breakdown on one MiniAOD file per sample: Z→ee/μμ/ττ fractions, lepton acceptance, pT thresholds, mass window, and the trigger at reco.
- Use FWLite on `prunedGenParticles`, with a new script `notes/zxtest_AN/gen_breakdown.py`. This also answers the τ question for the cross sections.

B5. **≥1 jet efficiency (Table 7).** Rerun the loose cutflow with jetCuts relaxed (pT ≥ 180, no |η|, ID or constituent cut). Then break the loss down into: jet pT < 200, |η| > 2.4, ID, the lepton veto, and no jet at all. Expected main cause, unverified: with ptll ≈ 150–250 the recoil is shared among several jets, so the leading AK8 jet is often below 200.

B6. **Back-to-back in other analyses (§7).** A short survey of CMS/ATLAS Z+jet balance analyses (JEC Z+jet balance, V+jet substructure): Δφ cut, asymmetry or α cut, second-jet veto, and whether softer jets are allowed as a fallback. Cite only papers actually read.

## C. Questions for POGs (to OPEN_QUESTIONS.md)
- **MUO:**
  - Should the regime threshold use the PF or the TuneP pT? The wiki does not say: `guidelines/corrections.md:331-336` speaks of "pT > 200 GeV" only.
  - Should the TuneP direction be used? `tunePMuonBestTrack()` gives η and φ, and the MUO NanoAOD extension stores `tuneP_eta/phi` (`code/nano/index.md:176`). The wiki only says to take the *pT* from TuneP (`guidelines/recommendations.md:182-190, 234`).
  - Plus the existing MUO list.
- **EGM:** should gen electrons in the barrel–endcap gap be dropped?
- **JME:**
  - the MET-filter list (B2);
  - the AK8 JEC levels and central producer (B3);
  - the TIGHTLEPVETO recommendation for AK8 PUPPI.

## D. Deferred studies (to TODO.md)
- Impact of each muon correction and its systematics.
- EGM electron scale and smearing (already in TODO).
- Impact of reco lepton dressing and its systematics.
- Alternative jet-axis definitions for the E1C (e.g. WTA).

## E. Note-only edits
- Explain the CS frame more clearly (§8).
- Add the goodVertex comparison (B1) and the JEC levels (B3).
- Add the ZZ and ≥1-jet explanations with numbers (B4, B5).
- Add the cross sections (A7).
- Update the flags table (A1), the TIGHTLEPVETO ID (A2), the order J3–J7 (A3), the frames (A4), Table 8 (A6) and the issues list (C, D).

## Decisions (2026-11-15)
- Q1: smear the pat::Jet (JEC -> JER -> 180 cut on the smeared pT -> translate).
- Q2: pairPtMin 200 in ZX_test.yaml (production), matching jet pT >= 200; boosted region ptll > 200, jet > 200, no dR cut.
- Q3: projective phi = atan2(-s dphi, s deta), s = sign(eta_jet) (equals jetAxis phi at small dR).
- Q4: (withdrawn: 13 TeV values) all cross sections null until 13.6 TeV values are collected.

## Order of work
1. A1, A2, A6 and A7, together with their tests.
2. A3, after Q1.
3. A4, after Q3.
4. A5.
5. B1, B3, B4 and B5, with B6 alongside.
6. Note revision, then rebuild.
7. Commit after each group.

## Status
- Done: A1 (flags), A2 (idMask 3), A3 (JER on pat::Jet; validated against `SmearedPATJetProducer`), A4 (beam on the
  jet side; `jetProjective`), A5 (gen-jet flavour and boson association), A6, A7 (the given cross sections were 13 TeV values,
  withdrawn by the user; all null), B1, B3 (JEC levels; GT payloads), B4 (`gen_breakdown.py`), B5 (cutflow v3 with jet-step breakdown), B6
  (CMS JES and SMP-20-010 selections), C (OPEN_QUESTIONS.md), D (TODO.md), E (note).
- Added on the way (user decisions 2026-11-15): translator threshold 200; jets without MiniAOD daughters kept without
  constituents with a warning, blocking the back-to-back selection when they would lead.
- Open: B2 (MET filters; JME docs now mirrored in ~/nobackup/cms-wikis/jme-docs).

