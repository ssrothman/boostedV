# Open questions

Each item: the question, what the code does meanwhile, and where the details are. Remove an item once it is answered,
and record the answer in the relevant journal.

## Contents
- [Ask the MUO POG](#ask-the-muo-pog)
- [Ask JME](#ask-jme)
- [Analysis decisions (us)](#analysis-decisions-us)
- [Not yet verified](#not-yet-verified)
- [Literature survey](#literature-survey)

## Ask the MUO POG
Details: `simulation/EventSelection/README.md` § "Muon corrections: points to clarify with the MUO POG", `simulation/muonPOG_plan.md`.

1. **Muon smearing and its systematics, in every mode (medium, high, hybrid).** All are provisional:
   - Medium (MuonScaRe): the k in the resolution variation differs between the POG C++ (√(k_data² − k_mc²)) and Python (k_mc), by up to 0.6% in pT. Meanwhile `resolutionVariationK: cpp`.
   - Medium: in both POG references only the event number seeds the smearing, and all muons in an event share one random number. Meanwhile we follow the references. The `latest` MUO files also have a `RandomSmearing` correction (evtNr, lumiNr, phi), which we do not use.
   - High: the wiki's resolution systematic p → p(1 + N(0, 0.46·σ)). Meanwhile it is an extra smearing on top of the nominal one.
   - High: smearing seeded per (run, lumi, event, muon index), applied only for TuneP pT ≥ 200 GeV and |η| < 2.4.
2. **High-pT κ_b formula, sign, units and target sample.** Meanwhile κ_b is in c/TeV, and q/pT → q/pT + κ_b on MC (`kappaTarget: mc`).
3. **Medium scale above 200 GeV.** The POG C++ corrects it, while the Python and the stated validity do not. Meanwhile `highPtThreshold: 200`.
4. **PUPPI MET with TuneP muons (Wmunu).** The wiki asks for PF MET to be corrected by the TuneP − PF muon pT difference. Does this also apply to PUPPI MET, and how? Not implemented.
5. **Trigger SF with more than one muon.** The trigger SF uses only HLT-matched muons. What should be done when several muons match? Meanwhile only the highest-pT matched muon gets the trigger SF.
6. **Trigger fired but no selected muon matches an HLT object.** This happens when the trigger was fired by another object, e.g. a muon failing the Tight PF iso: 2 of about 730 single-tight-muon test events, both rejected by the Wmunu veto. What should the trigger SF be? Meanwhile a warning is emitted and the event gets no trigger SF (factor 1).
7. **Out of scope until asked:** the impact-parameter (dxy/dz) pileup-loss systematic for the Tight and HighPt IDs (the wiki leaves it to the analysis); the >500 GeV manual scale-shift sanity check; and the 2024/2025 high-pT κ_b tables, which are only in an SSO-protected PDF.

## Ask JME
1. **JRV2 JER SF uncertainty.** The stored `unc` matches JRV1's absolute shift (up − nom), but the reference code applies SF·(1 ± unc). Meanwhile we follow the reference. Details: `simulation/JME_JRV2_SFUncertainty.md` (to report).

## Analysis decisions (us)
1. **Default muon recipe.** `default.yaml` uses the medium recipe (`momentum: pf`, Tight ID, Tight PF iso, IsoMu24 SFs). Yet about half the muons in PTLL-400to600 have pT > 200 GeV, and the wiki recommends the high-pT recipe (or both) for such samples. A worked hybrid recipe exists: `simulation/EventSelection/test/validation/muonRecipes.py`.
2. **E1C of one-particle jets.** Jets are no longer removed near leptons, so the jet and EEC tables contain, for
   example, gen jets made of a single electron. Their E1C angles are undefined (the particle is at rest in the jet
   frame), and the stored bin is arbitrary. Should E1C need ≥ 2 constituents, or a stated convention? Channel X's
   histograms skip X's vetoed jets, but not other channels' (1 such gen jet in 1000 PTLL events).
3. **Constituent-variation sizes** (`JetSetup` `CONSTITUENT_VARIATIONS`) are invented placeholders: charged-hadron drop 2%; charged, neutral and photon scales ±1%, ±5% and ±2%.
4. **Coupling conventions.** Get a stated conversion between CMS g′_q, ATLAS axial-vector g_q and the flavour-universal g_q before quoting any comparison (`literature/checkin.md` §6.2).
5. **Literature ranges and the `plan.tex` step-4 edit.** Decide on the proposal in `literature/checkin.md` §4 and §6.6.

## Not yet verified
1. CRAB grid sites reading the `/cvmfs/cms-griddata.cern.ch` correction files (only LPC condor workers are checked).

## Literature survey
Full list: `literature/checkin.md` §6 and `literature/limits.md` §5.
1. Full texts are missing for ins335604, ins355978 and ins298412 (abstract and HEPData only). Can you provide the PDFs?
2. Text and HEPData disagree for 1606.00689, 1806.00843, 2607.20246, 2603.21965 and 2606.03222. These are flagged in the tables.
3. High-pT V+jets cross sections, needed for a Run-3 event-count scale, have not been extracted yet. The proposal is to do this at the start of step 2.
