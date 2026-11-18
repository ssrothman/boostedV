Abstract:
 - Need to update the git commit pointers

> **Claude:** Done. The abstract now gives EventSelection `ef02a1c`, JetSetup `6382203`, EECs `f9d33f2` and
> DataFormats `c2758a3` (the current submodule HEADs) and "boostedV `main` as of 18 November 2026", and no longer lists
> uncommitted changes. The review-2 code changes to EventSelection and JetSetup (vertex inequalities, extra-jet veto)
> are not committed yet, so those two hashes must be bumped when they are; I will do it in the same commit.

> **Human:**: Good.

Section 3:
 - The cross-sections should be formatted into a table(s), rather than in a paragraph of text

> **Claude:** Done: new Table "Cross sections" (`tab:xsec`) with every produced sample: signal and DY, the
> ttbar/WW/single-top backgrounds, the ZH samples, and the first production. Each row has the value and its
> source/order, and the branching fractions are in the caption. The paragraph now only states the normalisation formula,
> the caveats (generator-order diboson values; tau and low-mass gamma* included) and that `ZZto4Q`/`WZto4Q` are missing.

> **Human:**: Good.

 Section 4-6: the selections should be summarized in an easy-to-read table, referring to the text of sections 5-6 for detailed information

> **Claude:** Done: new Table "Summary of the ZX_test selection" (`tab:selsummary`) in Section 4. Columns: step, reco,
> gen and section; placeholders are marked with *. Rows: trigger, vertex, MET filters, jet veto map, lepton objects,
> dilepton pair, Z pT, extra-lepton veto, jets, overlap, back-to-back, extra-jet veto. It sits next to the
> selection-flag table.

> **Human:**: Good.

 Section 5.2:
 - The goodVertex, metFilters, and jet veto map are conceptually separate and should be separated here.

> **Claude:** Done: three subsections, "Primary vertex" (`sec:vertex`), "MET filters" (`sec:metfilters`, which also
> covers the ECAL bad-calibration rerun, since it is a MET filter) and "Jet veto map" (`sec:vetomap`). All references
> were updated.

> **Human:**: Good.

 - Can we modify the goodVertex requirement to be exactly identical to the production requirement (ie with the same strictness of inequalities)?

> **Claude:** Done. `VertexFlagProducer` now uses ndof > 4, |z| <= 24 cm and rho <= 2 cm, exactly the NanoAOD
> `goodPvCut` of CMSSW_15_0_22. For consistency I changed the two other users of the same config cuts the same way:
> the `PV_npvsGood` cut string and the vertex count of the MET XY correction.
> - New module test: z = 24 and rho = 2 pass; 24.01, 2.01, ndof = 4, a fake first vertex and no vertex fail. With `<`
>   restored, it fails.
> - The config test that checks the `npvsGood` string was updated.
> - All EventSelection module tests (72 assertions), JetSetup module tests and config tests (40) pass.

> **Human:**: Good.

 - No need to mention the Flag_goodVertices MET filter in the goodVertex description

> **Claude:** Removed.

> **Human:**: Good.

 - The list of metFilters should be formatted as an easy-to-read list or table

> **Claude:** Done: Table `tab:metfilters` lists the eight flags and the `ecalBadCalib` rerun, with their sources.

> **Human:**: Good.

 - We should make the 2D occupancy maps before/after the jet veto map

> **Claude:** Done: Figure `fig:vetomap` (new script `analysis/jetVetoMapOccupancy.py`). It covers the AK4 PUPPI jets
> (pT > 20 GeV, as stored) and the selected AK8 jets, with three panels each: before, after, and the fraction removed.
> - **Inputs:** three `PTLL`-200--400 DY files of `20261116_zxb2b`, copied locally with xrdcp, which took seconds.
> - **Event sample:** events passing a *gen* channel (85 409), because the reco selection already contains the veto.
>   5.45% of them fail the veto.
> - **Result:** all AK8 jets in the large vetoed region (eta ~1.5--2.0, phi ~1.8--2.7) are removed, plus a few small
>   spots; elsewhere about 5% are removed uniformly, through the event-level veto. In total 4.5% of the AK8 and 6.2% of
>   the AK4 jets are removed.
> - **Already visible before the veto:** the occupancy in that region is reduced.
>
> The effect on the observables is still open (issues list, TODO).

> **Human:**: Good.

Section 5-7:
 - The properties that are stored for each type of object should be summarized in tables in each of the appropriate subsections. In general lists should not appear as long blocks of paragraph text.

> **Claude:** Done:
> - **Leptons and Z candidate:** the lepton table now covers the Z candidate and all selected leptons at both levels,
>   plus the reco muon and electron extras.
> - **MET:** new table `tab:metcols`.
> - **Jets:** new table `tab:jetcols`, replacing the long "Stored jet properties" paragraph. It covers kinematics, ID,
>   corrections, substructure, taggers, PF content, flavour, gen boson, axes and flags, with a both/reco/gen marker.
> - **Axes:** see Section 7.2 below.
>
> Paragraph lists converted to itemize or enumerate:
> - the MET correction steps;
> - the gen object definitions;
> - the jet-veto-map jet requirements;
> - the back-to-back criteria;
> - the analysis histogram list.

> **Human:**: Good.

Section 7.2
 - The soft drop corrections and soft drop mass should be documented in their own subsection, not as part of the jet axis definitions (which is conceptually unrelated)

> **Claude:** Done: new subsection "Soft-drop subjets and the corrected soft-drop mass" (`sec:softdrop`), containing the
> corrections, the mass and the validation. "Alternative jet axes" (`sec:axes`) now only refers to it.

> **Human:**: Good.

 - Please provide a table of all of the axis definitions

> **Claude:** Done: Table `tab:axes` gives each axis's definition and its status codes, so it replaces the earlier
> status-only table. The appendix keeps the full definitions.

> **Human:**: Good.

Section 7.3:
 - It seems like the pT > 180 GeV requirement is completely redudant with the pT > 200 GeV requirement

> **Claude:** Agreed: the gen-jet pT is not changed by the charged-constituent selection, so the 180 GeV pre-threshold
> was redundant. There is now a single gen threshold (translator and jet cuts both 150 GeV, see below). The reco side
> has the same structure: the translator at 200 GeV and the jet selection at 200 GeV are on the same pT. I left that as
> is because the translator cut is what drops jets before the constituents are copied (cost), but the AN states the
> threshold once in the jet-selection step.

> **Human:**: Good.

 - If we can, we should keep genjets a bit softer than the reco jet threshold so that we can control/study migrations

> **Claude:** Done, at 150 GeV (your choice; a placeholder) in `ZX_test.yaml`.
> - **Gen selection:** the gen back-to-back jet may now be 150--200 GeV, so the gen channels accept more events. A gen
>   region that should match the reco fiducial threshold must cut `jets.pt > 200` offline; the AN says so in Sections
>   7.3 and 12.
> - **Analysis binnings:** `jetpt` and `jetptSlices` now start at 150 GeV in all three analysis configs, so gen jets of
>   150--200 GeV are not lost to underflow.
> - **Reco:** unchanged.

> **Human:**: One modification: we should keep the 200 GeV gen-level cut at analysis leevl. I only meant we should keep softer gen jets at gen level (for migration studies)

> **Claude:** Done. The NANO keeps gen jets from 150 GeV, and the analysis gen regions restore 200 GeV. `ZmumuGen` and
> `ZeeGen` in `zxtest.yaml` and `zxtest_e2c_scaled.yaml` now have the cuts `jets.pt >= 200` (jet level) and
> `num(jets) >= 1` (event level, so that an event whose only gen jet is 150--200 GeV leaves the region). The jet-pT
> binnings are back to starting at 200 GeV. The AN regions table and Sections 7.3 and 12 say so. Tested on 1000 local DY
> events (the regions fill).

Section 7.5:
 - There are two channels, not five, right?

> **Claude:** Right: two channels (`Zmumu`, `Zee`). The text said "all four channels", meaning two channels times two
> levels, which was confusing. It now says "both channels, at both levels".

> **Human:**: Good.

 - We should add an optional "extra jet veto"

> **Claude:** Done, as you specified. Key `backToBack.extraJetAlphaMax`, mandatory in the schema. The event fails if
> another selected jet that does not overlap the leptons has pT >= alpha * pT(Z); alpha < 0 disables the cut, and
> alpha = 0 is the strictest form (no other such jet). It is set to -1 (disabled) in all channels of `ZX_test.yaml`
> and `default.yaml`.
> - **Jets considered:** the AK8 jets of the same level that pass the jet selection, as agreed. With the gen threshold
>   at 150 GeV, the gen veto sees jets down to 150 GeV and the reco veto down to 200 GeV. So with alpha*pT(Z) below
>   200 GeV the two levels differ, and alpha*pT(Z) >= 200 GeV is needed for reco/gen consistency. Tell me if you would
>   rather veto on softer jets (that would need the pre-selection jets).
> - **Tests:**
>   - unit: threshold inclusive, vetoed jets ignored, alpha = 0, disabled;
>   - module: alpha = -1 and 0, which also checks that the parameter reaches the cut;
>   - config: wiring, and rejection when the key is missing.
> - **Mutations:** removing the veto, ignoring alpha = 0, an exclusive threshold, and counting lepton-overlapping jets
>   each fail at least one test.
> - **Documentation:** AN (new back-to-back section, summary table, order table, issues) and NANO.md.

> **Human:**: Good. Although it is a problem that we only see jets above threshold for this veto. Lets change to consider AK4 Puppi jets (which are kept to lower pT), and apply the veto w.r.t. this collection, with only the "basic selections" plus the requirement that they not overlap the AK8 jet under consideration nor the leptons. 

> **Claude:** Done, with the cuts you chose in the dialog. The veto now runs on a dedicated AK4 collection per level,
> configured in the new mandatory block `selection.<level>.extraJets`; the AK8-based version is removed.
> - **Reco:** `slimmedJetsPuppi` with the V4 JEC re-applied (as for the jet veto map), in MC the nominal AK4 hybrid JER
>   (JRV2, matched to `slimmedGenJets`, with the same seeds as the MET Type-1 JER, so a jet gets the same smearing in
>   both), and the TightLeptonVeto ID.
> - **Gen:** `slimmedGenJets`, no ID.
> - **Both levels:** pT > 20 GeV, |eta| < 2.4. Ignored: jets within dR < 1.2 of the back-to-back AK8 jet and within
>   dR < 0.4 of a selected lepton. Veto if pT >= alpha * pT(Z). alpha < 0 disables it (ZX_test: -1); alpha = 0 vetoes on
>   any such jet.
> - **One implementation detail:** the PAT string parser has no bitwise `&`, so the ID mask is applied as the list of
>   `jetId` values containing it (e.g. 2, 3, 6, 7 for TightLeptonVeto).
>
> Tests:
> - **Unit:** the alpha threshold (inclusive), pT > 20 (exclusive), eta, the jet and lepton overlaps, alpha = 0 and
>   disabled.
> - **Module:** the overlaps, the threshold, and a configuration error if the input is missing.
> - **Config:** wiring at both levels, the JEC -> JER -> ID chain, no JER in data, and the missing `extraJets` block
>   rejected at either level.
> - **Mutations:** seven (alpha exclusive, no jet overlap, no lepton overlap, inclusive pT cut, no eta cut, veto off in
>   the module, dRJet not wired), each caught.
> - **End to end:** 300 DY events with alpha = 0.3. The dilepton flags are unchanged, the selected events are a subset
>   of the nominal ones, and the veto removes 5/67 (2/56) reco and 4/69 (5/62) gen Zmumu (Zee) events.
>
> The AN (back-to-back section, summary table, order section and table) and NANO.md are updated.

 - We don't need to mention the logically impossible path with the non-PF jets here

> **Claude:** Removed, both from the back-to-back section and from step J10 of the order section. The code path itself
> is still there (it is harmless); the jets-section text that explains why such jets fail the ID is kept.

> **Human:**: Good.

 - The back-to-back requirement is conceptually part of the event selection, not part of the jet reconstruction. I think it needs to not be a subsection of the jets section

> **Claude:** Done: it is now its own section, "Event selection: back-to-back jet" (Section 8, label `sec:b2b`), right
> after the jets section (it needs the jet definitions). The overview and summary table point to it.

> **Human:**: Good.

 - The pT asymmetry bullet is confusingly worded. Please fix

> **Claude:** Reworded: "the transverse momenta of the leading jet and of the Z candidate must be balanced: their
> asymmetry A = |pTj - pTll|/(pTj + pTll) must be below 0.3, i.e. 0.54 < pTj/pTll < 1.86."

> **Human:**: Good. Remove the i.e. part

> **Claude:** Removed.

Section 8:
 - We need to unify the strategies across the different E1C frames and axis approaches.

> **Claude:** Done, as decided: laboratory-frame tables plus offline boosts, with Collins--Soper as the one rest frame
> also computed in C++.
> - **Production:** `E1CHelicity` is removed from `ZX_test.yaml`. ZX_test now writes `E1CLab` (about the jet),
>   `E1CLab<Axis>` (about each axis), `E1CProjective` and `E1CCS`. The C++ `jetHelicity` frame stays in the library as
>   the closure reference.
> - **Analysis:** the `E1CHelicity` histograms in `zxtest.yaml` and `zxtest_boosted.yaml` are now filled from `E1CLab`
>   with `restFrame: {axis: jet, mass: axis}`. A test run on 1000 local DY events fills them, with the same total
>   weight as `E1CCS`, as expected. This also works on the existing productions.
> - **AN:** Section 9 now opens with the strategy and a frame table (`tab:e1cframes`: frame, reference axis, where it
>   is computed). The frame definitions are written for a generic reference axis.
>
> Open question: the Collins--Soper frame is only available about the jet. If you also want it about the other axes,
> it would have to be added offline; tell me if so.

> **Human:**: Good. We can keep CS only w.r.t. the jet axis

> **Claude:** OK, no change.

 Section 11:
 - We need to update the cutflow, and include the other physics processes of interest.

> **Claude:** Not done yet, because it needs long cmsRun jobs. The cutflow uses a loose-configuration cmsRun on one
> input file per sample, then `make_cutflow.py`. The current configuration adds the jet veto map, the extra-lepton
> veto and the 150 GeV gen jets.
>
> Plan, about 25 samples:
> - signal and DY (5);
> - ttbar and WW;
> - the 13 single-top samples;
> - the 10 ZH samples;
> - optionally the inclusive DY/ZZ/WZ of the first production.
>
> Each job takes roughly 5--30 minutes locally, or the whole set can run as one condor submission. Shall I go ahead,
> and locally or on condor?
>
> Until then, the cutflow text and the issues list say that the table is out of date and what the regenerated version
> will contain (also added to TODO.md).

> **Human:**: I agree. Run it on condor

> **Claude:** Submitted.
> - **Production:** tag `20261118_cutflow`, manifest `simulation/production/samples_cutflow.yaml`. One input file (the
>   first DAS file) for each of the 30 produced samples: signal, DY, the ttbar/WW/single-top backgrounds and the ZH
>   samples.
> - **Loose configuration:** `ZX_cutflow.yaml`. It is now generated reproducibly from `ZX_test.yaml` by
>   `make_cutflow_config.py`; the earlier `ZX_loose2.yaml` was never committed.
> - **`make_cutflow.py`:** updated. The gen jet step is now at 150 GeV, and the first step includes the extra-lepton
>   veto.
>
> **Claude:** Done.
> - **Outputs:** all 30 jobs succeeded and were merged. The code that ran is byte-identical to the committed HEAD
>   (libraries and Python in the job tarball compared).
> - **Tables:** Section 11 now has five tables:
>   - signal, DY, ttbar and WW;
>   - t- and s-channel single top;
>   - tW;
>   - qq→ZH;
>   - gg→ZH.
> - **Text:** rewritten with the new numbers:
>   - a new event-cleaning paragraph: the jet veto map removes 3--9% of the events after the trigger, in line with the
>     5.45% of the veto-map section;
>   - the jet steps;
>   - the written fractions for all processes;
>   - the diboson acceptance, with `gen_breakdown.py` rerun on the same file.
> - **Closure re-checked with the current configuration** (1000 DY events): `make_cutflow.py` reproduces the full
>   `<c>` flags exactly in all four level-channel pairs. Mutations of the asymmetry and Δφ cuts are caught. Removing
>   the jet ID changes nothing here, because jets failing it overlap a lepton.
> - **Caveats:**
>   - One file per sample leaves ttbar, WW and single top with at most a few tens of events after the ptll cut. This is
>     now the issues-list item.
>   - The ZZ gen ptll ≥ 200 fraction moved from 0.26% to 0.19%, about 2σ between two files. This is stated in the
>     text.

 Section 12:
 - Make sure everything here is up to date with the latest setup.

> **Claude:** Updated:
> - **Gen jets:** at least 150 GeV, and how to get the reco-like gen region.
> - **E1C histograms:** the helicity frame comes offline from `E1CLab`; Collins--Soper from `E1CCS`.
> - **Binning:** jet-pT edges now start at 150 GeV.
> - **Histogram list:** now itemized.
> - **Soft-drop mass:** the analysis still uses the MiniAOD `msoftdrop`, because the existing productions do not
>   contain `axisSoftDropMass`. The switch is a TODO for the first production with the new code.
>
> I checked the regions table against the three configs: it matches.

> **Human:**: Good.

 Section 14:
 - Make sure everything here is up-to-date with respect to the to do list, and the list of open questions

> **Claude:** Done. Compared with `TODO.md` and `OPEN_QUESTIONS.md`.
>
> Updated items:
> - **Cutflow:** now also covers the gen threshold and the list of processes.
> - **Productions:** what they predate.
> - **Soft-drop:** why the analysis still uses `msoftdrop`.
> - **Placeholders:** now include the extra-jet veto, the 150 GeV gen threshold and the constituent-variation sizes.
> - **POG cross-checks** became "Questions for the POGs":
>   - JetMET: the JRV2 SF-uncertainty convention, the JSON payloads versus the global tag, and the
>     `PFJetIDSelectionFunctor` bug report;
>   - EGamma: gen electrons in the ECAL gap;
>   - the MET-filter list is marked as checked.
>
> New items:
> - jet veto map effect on the observables;
> - the loose-selection pair choice;
> - NANO validation;
> - MET validation, including the one non-closing data event.
>
> Left out on purpose:
> - the W-tag and leptonMET items of TODO.md and the MUO questions on trigger SFs (not used by ZX_test);
> - the literature and coupling-convention items (not about this note).
>
> TODO.md was updated in turn: the axis study ticked, and new entries for the cutflow and the `axisSoftDropMass` switch.

> **Human:**: Good.

---

Other changes made while doing the above (for your review):
- **Unit macros:** a `\GeV`/`\TeV` followed by a word swallowed the space ("GeVthe"), in about 12 places, some of them
  older. Fixed with `\GeV{}`.
- **AN build:** 47 pages; the only overfull boxes left are three under 2 pt.
- **Not committed yet:** the code changes. They are in EventSelection and JetSetup, the configs and schema, the
  analysis configs, `jetVetoMapOccupancy.py`, NANO.md, TODO.md and the AN.
- **Study data:** the three copied DY NANOs (1 GB) are in `axisStudy_20261118/vetomap/nano/` (untracked); delete them
  when no longer needed.

> **Human:**: Good.





NEW COMMENTS ON APPENDIX A:

 - Please add a column to the analyzing power table with the neutrino analyzing power (for completeness)

> **Claude:** Done: $A_\nu = 1$ for every $\sin^2\theta_W$ ($Q = 0$, so $g_V = g_A$).

 - Please add some plots of the actual theta, phi distributions, and some basic validation that the distributions really do have the predicted shapes (does the analytic form with the extracted rho matrix describe the simulated data?)

> **Claude:** Done: new Section A.7, Figure `truthAngles.pdf`.
> - **Plots:** cos θ and φ for the hadronic and leptonic boson of ZZ and WZ, at 0–50 and 200–300 GeV, with W(θ, φ)
>   evaluated with the ρ extracted from the same events.
> - **What the test can show:** the estimator reproduces the l ≤ 2 moments by construction, so the real test is that
>   nothing else is present. Two statistics per bin, both with unit tests (they pass on samples drawn from W; the
>   l = 3, 4 test catches a |cos θ| < 0.8 cut and the histogram test a wrong A_f):
>   - the χ² of the 10×8 (cos θ, φ) histogram (71 dof);
>   - the χ² of the 16 l = 3, 4 harmonic moments against zero.
> - **Result:** 31 of 32 bins are compatible with a spin-1 decay. Four have p < 0.05 in the l = 3, 4 test (1.5
>   expected). Three of those have at most 400 events, where the moment means are not yet Gaussian.
>
> The test found two things:
> 1. **A frame bug, now fixed.** The fermion was boosted as massless. Powheg quarks carry 0.33–4.8 GeV, so hadronic
>    "Z" bosons of a few GeV got wrong angles: χ² 237/16 below 5 GeV, 13/16 with the LHE mass. `truthRho.py` now uses
>    the LHE mass. For bosons in the window, ρ00 moves by at most 0.004 above 100 GeV. The selection-bias study (A.9)
>    and the reweighting (A.10) still use massless fermions; the AN says so.
> 2. **Singly-resonant Z → 4f in ZZto2L2Q.** These are events whose four-fermion mass is within 5 GeV of m_Z, with one
>    pair radiated off the other fermion line. The pair labelled as the radiating "Z" then does not come from a
>    single propagator. They are 21.5% of the leptonic Z at pT < 50 GeV:
>    - without them, χ² is 19.1/16;
>    - they alone give 73.6/16;
>    - the radiated qq̄ pair of the same events, which is a genuine γ*/Z decay, gives 17.3/16.
>
>    Above 200 GeV they are 0.35% of the leptonic Z and none of the hadronic Z; WZ has none. They don't matter at our
>    pT. Should the truth definition exclude them explicitly (e.g. |m4f − m_Z| > 5 GeV)? I haven't done that.

 - In the table of spin analyzing powers, where does 0.2229 come from? The PDG (2026) value is 0.23122(6) (I think? In principle I guess it's dependent on your renormalization scheme and potentially runs with the scale.....)

> **Claude:** 0.2229 was my early guess at the Powheg value: on-shell $1 - m_W^2/m_Z^2$ with $m_W = 80.385$. It was
> superseded by the actual Powheg value (0.22263, from `smcouplings.f`) but stayed in the table. I've replaced it.
>
> The table now has the PDG values from the 2025 update of the electroweak review, Table 10.2 (checked in the PDF):
> - on-shell $s_W^2$ = 0.22342(9);
> - $\overline{\rm MS}$ $\hat s_Z^2$ = 0.23122(6): yours;
> - effective $\bar s_\ell^2$ = 0.23154(6), which happens to equal the MadGraph DY value.
>
> As you say, they differ by scheme ($\overline{\rm MS}$ runs; it is quoted at $m_Z$). At tree level they coincide, so a
> LO generator is free to pick one. What matters for the extraction is the generator's own value.
>
> The lep/had χ² table now uses these rows, recomputed with the frame fix. At pT < 100 GeV:
>
> | $\sin^2\theta_W$ | χ² (8 dof) |
> |---|---|
> | Powheg 0.22263 | 15.7 |
> | PDG on-shell | 17.5 (indistinguishable from Powheg) |
> | $\overline{\rm MS}$ | 66.7 |
> | effective | 70.1 |
>
> The PDG reference is added to `references.bib`.

 - In A.5, what is meant by ``The measured boson''? Both bosons are measured right?

> **Claude:** Yes, that was unclear. It meant the boson whose ρ is being extracted: the leptonic Z for the leptonic ρ and
> the hadronic Z for the hadronic ρ. Requiring only that boson in its window (`--window self`) makes the two
> extractions use different events with different partner populations. I've rewritten the paragraph that way. The
> numbers are refreshed with the fix: 0.272 ± 0.003 versus 0.203 ± 0.002 at pT < 50 GeV.

 - In A.6, what we are interested in is surely the fraction of hadronic Z in window given the leptonic one in window? (Inverted from the third column) of the first table?

> **Claude:** Agreed; that column was the wrong conditional. The table now has, in bins of the hadronic Z pT, the
> fractions with:
> - the hadronic Z in its window;
> - the leptonic Z in the selection's 61.19–121.19 GeV window;
> - **the hadronic Z in its window given the leptonic Z in the selection window**: 0.74 for all pT, 0.94 above
>   200 GeV, 0.91 above 400 GeV;
> - both in window.

 - Similar comment for the second table

> **Claude:** Done. The ρ00 table has a new column, "leptonic in window (truth)". Above 100 GeV all four definitions
> agree within statistics. Below 100 GeV the truth definition gives 0.321 ± 0.002, against 0.217 for the hadronic Z
> alone in its window.

 - You say the realistic selection (leptonic decay in window, no cut on the hadronic decay) is not implemented? Please implement that and then rederive these results.

> **Claude:** Implemented. `truthRho.py --window self|both|leptonic|none` replaces `--both-in-window`:
> - `leptonic` requires every leptonically decaying boson of the event in the selection's window, with nothing on the
>   hadronic one;
> - `self` stays the default, so `axisStudy.py` is unchanged;
> - `self` and `both` reproduce the earlier JSON outputs exactly (before the mass fix);
> - new unit tests cover the per-event window flag and the pairing, and both checks catch a mutation.
>
> All A.6 results are rederived with it: the fractions, the ρ00 comparison, and the truth tables (next items).

 - Please add a table all of the spin density matrix parameters as a function of the boson pT (as in A.5 or A.6 but for all the parameters) for the hadronic partner in both ZZ and WZ, without cuts on the hadronic boson mass (i.e., mimicking a measurement).

> **Claude:** Done: Table 16, all nine parameters, 8 pT bins from 0 to above 600 GeV, for the hadronic Z (ZZ) and the
> hadronic W (WZ). The leptonic Z is in the selection's window and there is no cut on the hadronic mass. It replaces
> the old two-column table. Above 200 GeV, 0.55% of the hadronic Z have m < 20 GeV (a γ* radiated off the lepton line).

 - Please add a similar table for all of the spin density matrix parameters as a function of the boson pT for the leptonic partner, requiring the mass to be in the window.

> **Claude:** Done: Table 17, for the leptonic Z of ZZ and of WZ in the selection's window, binned in its own pT, with
> no requirement on the hadronic partner. Its parity-odd entries rely on A_ℓ ≈ 0.22, so their errors are three to
> four times those of the quarks. They also carry the window-averaged γ*/Z interference (about 5%, A.8). The AN says both.

 - For the same selection please also supply a table of the joint probability that the two bosons are in the helicity states (++, +0, +-, 0+, 00, 0-, -+, -0, --) (ie the diagonal of the joint spin density).

> **Claude:** Done: Table 18, for ZZ (hadronic Z, leptonic Z) and WZ (hadronic W, leptonic Z), binned in the hadronic
> boson pT. If you meant the leptonic pT, it's a one-line change.
>
> **Method:** per decay, $f_0 = (1 - 10P_2)/3$ and $f_\pm = (1 - f_0)/2 \mp \cos\theta/A_f$. These satisfy
> $\langle f_\lambda\rangle = \rho_{\lambda\lambda}$ for any ρ, i.e. they are the helicity projectors. So the event
> mean of $f_{\lambda_h} f_{\lambda_\ell}$ is $P(\lambda_h, \lambda_\ell)$, including the spin correlations, with
> each decay's own A_f.
>
> **Checks:**
> - **Unit test:** an entangled two-boson state, sampled from the full joint decay distribution, is recovered (all
>   pulls < 4.5). It differs from the product of the marginals by more than 10σ. Both catch mutations.
> - **On data:** the probabilities sum to 1, and the sum over λ_ℓ gives the ρ00 of Table 16 to 1e-9.
>
> **Result:** at 200–300 GeV in ZZ, (+,−) and (−,+) dominate: 0.28 ± 0.04 and 0.29 ± 0.04, with (0,0) at
> −0.05 ± 0.03. The leptonic ± split has large errors because A_ℓ is small. The estimator is not constrained to be
> positive.

 - In section A.7, what is Q_f? The electric charge?

> **Claude:** Yes, the electric charge in units of e. It's now defined where the couplings are introduced (A.4), and
> A.8 uses it as $Q_f$.
 

 - (Follow-up) Please also add a table of the spin analyzing power for the W

> **Claude:** Done, in A.4 after the Z table. The W couples only to left-handed fermions, so $A_f = 1$ for every
> decay: $W^+ \to \ell^+\nu$ (fermion ν), $W^- \to \ell^-\bar\nu$ (fermion ℓ⁻), $W^+ \to u_i \bar d_j$ (fermion $u_i$)
> and $W^- \to d_j \bar u_i$ (fermion $d_j$). This holds independently of $\sin^2\theta_W$ and of the CKM elements,
> up to $\mathcal{O}(m_f^2/m_W^2)$. "Fermion" is the product with pdgId > 0, which is left-handed for both charges;
> choosing the antifermion would give −1 (the exchange symmetry of A.2). `spin.asymmetryParameter` returns 1 for every
> W decay at both $\sin^2\theta_W$ values.
