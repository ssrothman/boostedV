# MET corrections (PUPPI MET, Run 3 Summer22EE)

Why: the leptonMET channels and the neutrino reconstruction use `slimmedMETsPuppi` as it is (`inputs.met`; gen: `genParticleLevel:mets`).
Sources: JME `cms-jme-jmar` MET corrections page and `cms-jme-jerc` Type-1 page and worked example (`Type1MET.pdf`), both in
`~/nobackup/cms-wikis/jme-docs`; MUO wiki `guidelines/{recommendations,corrections}.md`; `notes/zxtest_AN/jme_review.md` item 7.

## What JME and MUO say
- Run 3: use Type-1 corrected PUPPI MET (mandatory). Type-1 in MiniAOD carries the production AK4 JEC, not V4: recompute it from the same
  corrected AK4 jets; propagate only AK4 jets, never AK8.
- Type-1 (worked example): raw MET - sum over AK4 jets with corrected pT > 15 GeV, |eta| < 5.2, EM fraction (chEmEF + neEmEF) < 0.9 of
  (p_T^full - p_T^L1) along the muon-subtracted jet direction; MiniAOD jets below the Nano 15 GeV cut (`CorrT1METJet` in Nano) must be included.
- JER smearing is mandatory for simulated jets; propagating it to MET is optional (use the nominal smearing of each Type-1 jet).
- XY shift: optional, file `met_xyCorrections_2022_2022EE.json.gz` (inputs `pt_phi`, `met_type`, `epoch`, `dtmc`, `variation`, `met_pt`,
  `met_phi`, `npvGood`); must match the MET definition; validate both pT and phi.
- Recoil calibration: optional and analysis specific; JME: do not add JER smearing on top of it unless it was derived with it.
- Variations: JEC propagation mandatory (same nuisance as the jets); JER, lepton/photon and unclustered-energy variations optional.
- MUO: TuneP is not PF-based; "use PF MET but correcting the pT of the muon (PF) with the one given by TuneP".

## Pipeline (implemented 2026-11-16 as three producers; see NANO.md 4.10 and JOURNAL.md; decisions: JER yes, XY yes and muons yes, each with a switch; variations and electron/photon deferred)
1. Raw PUPPI MET from `slimmedMETsPuppi` (`pat::MET::uncorP4`).
2. AK4 PUPPI jets `slimmedJetsPuppi`: V4 JEC (and JER in MC) from the existing `PATJetJECProducer` / `PATJetJERCProducer`, muon-subtracted raw
   p_T/direction from CMSSW's `PATJetCleanerForType1MET` (the module Nano uses), L1 = the level-1 factor of the V4 chain (to check: trivial for PUPPI).
3. Type-1 sum with the cuts above.
4. Optionally the XY shift.
5. Muon momentum: for each selected muon, MET += p_PF - p_assigned (assigned = TuneP or MuonScaRe / kappa_b corrected; our `muonCorrections`).
6. Output: a MET collection with the same interface as `slimmedMETsPuppi`, selected by `inputs.met`; the `SelectionMET`/`MET` tables follow.
Gen level needs nothing (particle-level MET).

## Validation
- Unit test of the Type-1 sum against a hand computation; check that with the production JEC it reproduces `slimmedMETsPuppi`'s own Type-1
  MET (closure test, MiniAOD `corP4(Type1)`), then switch to V4.
- Z -> mumu recoil (u_parallel, u_perp, MET phi) data vs MC before and after, as JME asks for XY.

## Not in scope
Recoil calibration, DeepMET, MET significance, unclustered-energy and object variations (until the systematics), electron/photon propagation
(no EGM scale/smearing is applied in-job yet).
