# To do (next session)

Open questions for outside groups and decisions are in `OPEN_QUESTIONS.md`; this is our own work list.

- [ ] Validate the electron and photon setup against the EGM Run-3 recommendations (IDs, scale and smearing, SFs).
- [x] Validate the jet setup against the JME Run-3 recommendations (JEC/JER, jet ID, PUPPI, vetomaps): `notes/zxtest_AN/jme_review.md`; deviations there await decisions.
- [x] W tag: the neutrino reconstruction as a replaceable module (`WMassNeutrinoProducer`, `simulation/neutrinoReco_plan.md`); reco vs LHE p_z in `plots/neutrino_pz_WZtoLNu2Q_powheg.png` (smaller-|p_z| root closer to truth in 54-58% of the real-root events).
- [ ] W tag: alternative neutrino strategies to try (same module contract unless noted; compare with `EventSelection/test/validation/plotNeutrinoPz.py`):
  1. complex roots: rescale MET (or rotate it) to make the discriminant exactly zero, so m(l nu) = m_W holds, instead of the real part;
  2. root choice using the recoil: the W pT balance against the recoil jet or the Z, or m(W + jet) (adds a jet input to the contract);
  3. keep both roots (two neutrino candidates with weights or a flag; changes the output contract);
  4. likelihood / kinematic-fit root choice with the W pT spectrum and the decay-angle (polarisation) prior;
  5. a hybrid: real part for a small m_T excess, MET rescaling for a large one;
  6. a regression network for p_z from lepton, MET and jet kinematics (needs training samples and validation).
- [x] MET corrections: Type-1 with V4 JEC, JER propagation, XY shift and muon propagation, each with a configuration switch (`simulation/metCorrections_plan.md`); to enable in a production, set `selection.reco.metCorrections.apply` (and `muons.propagate` with `muonCorrections`).
- [ ] MET: one data event (Run2022F, run 360459 lumi 4 event 6476300) does not close (5.9 GeV): its production `slimmedMETsPuppi` is itself inconsistent, the default p4 differs from its own Type1 level by 11.8 GeV and our stored-JEC Type-1 lies halfway between them. Closure is otherwise exact (MC 2000/2000, data 1999/2000, within 0.05 GeV). Ask JME/MET only if it recurs in a larger sample (check 20k data events).
- [ ] MET: propagate the JEC and JER variations (and the optional unclustered-energy variation) to the MET together with the jet systematics (JME: JEC mandatory for variations); the `PuppiMET` table variations are still the MiniAOD ones (deferred, 2026-11-16).
- [ ] MET: propagate electron and photon corrections once the EGM scale and smearing are applied in-job (deferred, 2026-11-16).
- [ ] MET: validate Z -> mumu recoil (u_parallel, u_perp, MET phi) data vs MC before and after the corrections (JME XY validation).
- [ ] MET: after the neutrino strategies, re-run `plotNeutrinoPz.py` with the corrected MET (the plot of 2026-11-16 used the uncorrected MiniAOD MET).
- [ ] W tag: the W boson (definition and its NANO output).
- [ ] Loose-selection pair bias (`simulation/configs/ZX_test.yaml`): only the dilepton pair closest to the Z mass among the loose (ID-less) objects is stored, so tighter IDs/isolation applied offline do not reproduce a tight selection exactly. Study the size of the effect, probably by storing the selected pair for each of several IDs/selections.
- [ ] Validate and document carefully the NANO contents and format. The documentation is in `simulation/NANO.md`; still to do: a systematic validation of every table.
- [ ] AK8 jets with an anomalous MiniAOD JEC (`20261113_zxtest`, TTto2L2Nu jobs 17, 112 and 223): `slimmedJetsAK8` jets with MiniAOD pt 88.3 / 165.1 but raw pt 326.8 in both events (run 1, lumi 87440, event 61994860; lumi 48407, event 34320277), so V4 JEC gives ~348 GeV (348.45 in all three failures, the third at lumi 112543, event 79792614), while MiniAOD dropped their daughters (pt < 170) and `PATJetToEECJetProducer` throws. Find out why the raw pt is identical (MiniAOD artifact?) and decide how to treat such jets. The failed jobs are left out of the merge for now (user decision, 2026-11-13). Investigated 2026-11-16: the MiniAOD corrected p4 is corrupted (not JEC-explainable), ~1e-6 of AK8 jets, handled by the no-PF ID bit; ask JME/PAT, note in `simulation/pog_question_ak8_corrupt_pt.md`.
- [ ] Refine the W selection (leptonMET channels: neutrino p_z, W candidate definition). Back-to-back jet selection is rejected for leptonMET channels until then (`simulation/backToBack_plan.md`).
- [ ] Back-to-back selection per jet variation (JES/JER/constituent/cuts): deferred; the first implementation uses nominal jets only and rejects `backToBack.enabled` with variations. What is needed: `simulation/backToBack_plan.md`, "Deferred" section.
- [ ] Electron no-isolation MVA IDs: Run-3 MiniAOD `slimmedElectrons` noIso MVA decisions include isolation in the barrel (EGM POG docs, Run3_EleMvaID); our `mvaNoIsoWP80/90` columns inherit the bug. Apply the POG fix (EgammaPostRecoTools on MiniAOD) or drop the columns.
- [ ] Electron energy scale (data) and smearing (MC): recommended by the EGM POG for Run 3 (Run3/SaS), not applied in-job.
- [ ] Study the impact of each muon momentum correction (assignment, MuonScaRe, kappa_b, smearing) and of their systematic variations on the selection and the correlators (review 1, 2026-11-15).
- [ ] Study the impact of reco-level lepton dressing (`dressing.mode`) and its systematics (review 1; deferred).
- [x] E1C with other jet-axis definitions (e.g. winner-take-all) (review 1): implemented and studied (AN Appendix B, 2026-11-18); the axis choice is open.
- [x] Compare our AK8 jet ID (`PFJetIDSelectionFunctor`) with the JME correctionlib jet ID (`JME/.../jetid.json.gz`, `AK8PUPPI_Tight`/`_TightLeptonVeto`) on MiniAOD jets.
- [x] Soft-drop mass per JME: re-apply AK4 JEC and JER to both soft-drop subjets and recompute (`RecoJet_axisSoftDropMass`, nominal; `simulation/NANO.md` 4.5).
- [ ] Soft-drop mass systematics: subjet JES/JER variations, JMS ±1 %, JMR ±2 % (`notes/zxtest_AN/jme_review.md` item 6).
- [ ] MET per JME: recompute Type-1 PUPPI MET with the V4 AK4 JEC (and optionally JER and XY) before any MET use (`jme_review.md` item 7).
- [ ] Before jet systematics: switch JES from `Total` to the `Regrouped_*` sources (`jme_review.md` item 5).
- [ ] Jet veto map: document its effect on the observables (JME requirement); the (eta, phi) occupancy is done (`analysis/jetVetoMapOccupancy.py`, AN Fig. "vetomap", 2026-11-18).
- [x] Regenerate the AN cutflow with the current configuration (veto map, extra-lepton veto, 150 GeV gen jets) and all produced processes (signal, DY, ttbar, WW, single top, ZH) (review 2): production `20261118_cutflow`, AN Tables "cutflow" to "cutflowZH", 2026-11-18.
- [x] Cutflow efficiencies of ttbar, WW and single top from full productions: reco final rows from 20261116_zxb2b, 20261117_zxb2bbkg and 20261117_zh, as upper bounds (2026-11-18).
- [ ] Exact final cutflow rows (reco and gen) from `samples_zxall.yaml` once produced.
- [ ] Submit `samples_zxall.yaml` (all 30 samples, current code) and `samples_lhe.yaml` (unselected LHE NANO, ZZ/WZ and DY 200-400/400-600/600); prepared, not submitted (2026-11-18).
- [ ] High-statistics AN Appendix A: `truthRho.py`/`truthStudy.py` hold every decay in memory; accumulate the sums per file.
- [ ] High-statistics AN Appendix B: `axisStudy.py` concatenates the per-entry E1C tables; reduce each file to per-jet sums. Then QCD (DY, `axisDeltaR.py --truth parton`) and Higgs (ZH, `--truth higgs`) versions of the dR figure.
- [ ] Analysis configs: switch from the MiniAOD `msoftdrop` to `axisSoftDropMass` once a production contains it.
- [ ] Report the `PFJetIDSelectionFunctor` TIGHTLEPVETO NHF bug (CMSSW_15_0_22) to JME / CMSSW.
