# The eecNano NANO format

What `configs/eecNano_cfg.py` writes to `outputFile`, and how the analysis YAML and the cmsRun arguments decide it.
The table set is **not fixed**: most table names and many columns come from the configuration. `default.yaml` is used
below only as a worked example.

## Contents
- [1. Overview](#1-overview)
- [2. What the configuration controls](#2-what-the-configuration-controls)
- [3. Conventions](#3-conventions)
- [4. Table reference](#4-table-reference)
  - [4.1 Event identity](#41-event-identity)
  - [4.2 Selection flags](#42-selection-flags)
  - [4.3 Channel candidates, leptons and MET](#43-channel-candidates-leptons-and-met)
  - [4.4 Muon scale factors](#44-muon-scale-factors)
  - [4.5 Jets and constituents](#45-jets-and-constituents)
  - [4.6 EEC observables](#46-eec-observables)
  - [4.7 MC event tables](#47-mc-event-tables)
  - [4.8 LHE tables](#48-lhe-tables)
  - [4.9 HLT bits](#49-hlt-bits)
  - [4.10 MET](#410-met)
  - [4.11 Vertices, rho, gen vertex, pileup weights](#411-vertices-rho-gen-vertex-pileup-weights)
  - [4.12 Gen particles](#412-gen-particles)
  - [4.13 AK4 jets](#413-ak4-jets)
- [5. Worked example: default.yaml](#5-worked-example-defaultyaml)
- [6. Pitfalls](#6-pitfalls)

## 1. Overview
- A standard `NanoAODOutputModule` file with the trees `Events`, `Runs`, `LuminosityBlocks`, `MetaData` and `ParameterSets`.
- **Which events are written.** An event is written if it passes at least one channel at at least one level listed in
  `selection.levels` (`reco`, `gen`, or both; in data only `reco` exists). Every written event carries every table,
  whichever level or channel selected it.
- **What is kept.** Every `nanoaod::FlatTable` from a module whose label ends in `Table`, the mergeable counter tables
  (Runs-tree sums of weights), the NANO metadata and, optionally, the HLT `TriggerResults` (§4.9).
- **Not in the NANO.** The aggregated EEC histograms with covariance go to the separate `histFile` (TFileService). They
  are controlled by `aggregation` and are not described here (see `EECs/docs/guide.md` §11).

## 2. What the configuration controls
Each row is one family of tables. "Name" says where the table name comes from. Data jobs (`isMC=0`) never write the
MC-only families.

| Family | Tree | Exists if | Name | Contents controlled by |
|---|---|---|---|---|
| Event identity | Events | always | `run`, `luminosityBlock`, `event`, ... | — |
| Selection flags | Events | always | `Selection` (reco), `GenSelection` (gen, MC only) | channel names: `selection.<level>.channels` keys; one set of flags per channel |
| Channel candidates | Events | one per channel | `<ch>Boson` (dilepton, leptonMET) or `<ch>Objects` (singleObject); `Gen` prefix at gen | the channel's `type`, `objects`, cuts; at reco also `muonCorrections` and `dressing` |
| Selected leptons | Events | one per dilepton or leptonMET channel | `<ch>Leptons`, `Gen<ch>Leptons` | as above |
| Lepton/photon details | Events | one per reco channel (extends `<ch>Leptons` or `<ch>Objects`) | same table | `selection.reco.objectTables.{muons,electrons,photons}` (by the channel's object `source`); `triggerMatched` from the channel's `triggers` |
| Selection MET | Events | the level has at least one leptonMET channel | `SelectionMET` (reco), `GenSelectionMET` (gen) | reco: `inputs.met`; gen: the particle level (`selection.gen.particleLevel`) |
| MET | Events | one pair per entry of `output.metTables`; `GenMET` in MC | `<name>`, `Raw<name>` (keys of `output.metTables`) | the pat::MET label of each entry |
| Vertices | Events | `output.vertexTables` | `PV`, `OtherPV`, `SV`; MC: `GenVtx` | `inputs.vertices`, `secondaryVertices`, `pfCandidates`, `genVertex`; `npvsGood` uses `selection.reco.vertex` |
| Rho | Events | `output.rhoTable` not empty | `Rho` | the listed `fixedGridRho*` |
| Pileup weights | Events | MC, `output.pileupWeights.file` set (needs `mcEventTables`) | extends `Pileup` | `output.pileupWeights.{file,key}`, `inputs.pileupInfo` |
| Gen particles | Events | MC and `output.genParticles` | `GenPart` | `inputs.prunedGenParticles`; standard NanoAOD pruning |
| AK4 jets | Events | `output.ak4Jets.enabled` | `output.ak4Jets.name` | `output.ak4Jets`: `src`, `cut`, `jec` keys (MC or data), `jetId`, `variables` |
| Muon SFs | Events | MC, one per key of `selection.reco.muonScaleFactors` | `<ch>MuonSF` | the channel's term list: column names come from the term `name`s |
| Jets | Events | one per jet collection and variation | `<table.name><variation>` | `jets.collections.<C>`: `src`, `mode`, cuts, `cleaningDR`, `table.precision`; `jets.cleaning.channels`; `variations` (MC only); `mcOnly` collections are skipped in data |
| Jet veto flags | Events | every jet table, if `jets.cleaning.channels` is not empty | extends the jet table: `veto<ch>` | `jets.cleaning.channels`, the collection's `cleaningDR`; the channel's selected objects at the jet's level |
| Jet extension columns | Events | nominal table of a reco `pat` collection with `table.extraVariables` or `retag` | same table | `table.extraVariables` (PAT expressions on the MiniAOD jet; `mcOnly` ones skipped in data); `retag.variables` (on the re-tagged copy; taggers `retag.taggers`) |
| Jet constituents | Events | cmsRun `writeConstituents=1` | `<jet table>Constituents` | `constituentCuts`, `translator` |
| EEC per-jet and entries | Events | one per jet collection × variation × observable | `<C><variation><obs>`, `<C><variation><obs>Entries` | `observables.<obs>`: `kind`, `N`, `n`, `weight`, `angle`/`frame`, `norm`, `output`, `axes`, `table` |
| EEC axes | Runs | binned `output` (not `Unbinned`) | `<C><variation><obs>Axis<k>`, `...AxisType` | `observables.<obs>.axes` |
| MC event tables | Events, Runs | MC and `output.mcEventTables` | `genWeight`, `Generator`, `Pileup`, `LHEWeight`, `LHEScaleWeight`, `LHEPdfWeight`, `LHEReweightingWeight`, `PSWeight`; Runs: `genEventCount`, `genEventSumw`, `genEventSumw2`, `LHEScaleSumw`, `LHEPdfSumw`, `PSSumw` | CMSSW defaults of `genWeightsTable`, `puTable`, `genTable` |
| LHE tables | Events | MC and `output.lheTables` | `LHE`, `LHEPart` | `inputs.lheInfo` (the first label present is used) |
| HLT bits | Events | `output.keepHLTBits` | one bool per path | the input file's HLT menu (`inputs.hltProcess`) |

Here `<ch>` is a channel name, `<C>` a key of `jets.collections` (for example `Reco`), `<variation>` a key of that
collection's `variations` (empty for the nominal), `<obs>` a key of `observables`, and `table.name` that collection's
`table.name` (for example `RecoJet`). The jet tables are named from `table.name` and the EEC tables from the collection
key. In `default.yaml` they happen to differ: `RecoJet` / `RecoE2C`.

cmsRun arguments that change the content (rather than the configuration): `isMC`, `writeConstituents`, `lumiMask`
(which lumisections are read) and `maxEvents`.

## 3. Conventions
- Standard NanoAOD flat tables. A collection `X` has a counter `nX` and columns `X_<col>`, all jagged per event.
  A singleton table (`SelectionMET`, `MET`, `PuppiMET`, `PV`, `Rho`, `GenVtx`, `<ch>MuonSF`, `LHE`, `Generator`, `Pileup`) has
  one value per event and no counter.
- Extension tables add columns to an existing table with the same name and rows (the jet, lepton and pileup-weight
  columns below); in the file they are ordinary branches of that table.
- Units: GeV for momenta, masses and MET; radians for angles.
- Float precision: `-1` means full float. Otherwise the value is the number of mantissa bits kept. Our tables use full
  float except where a configuration key says otherwise: `jets.collections.<C>.table.precision` (jets and
  constituents), `observables.<obs>.table.weightPrecision` / `coordPrecision` (EEC). The LHE momenta use 14 bits and the
  LHE weights CMSSW's default of 14.
- Indices: `iJet` in `...Entries` and `...Constituents` is the row of the jet in the jet or EEC per-jet table of the
  same event. `srcIdx` indexes the source collection in the MiniAOD (or the reclustering input).

## 4. Table reference

### 4.1 Event identity
`run`, `luminosityBlock`, `event`, `bunchCrossing`, `orbitNumber` (written by the output module). Use
(`run`, `luminosityBlock`, `event`) to match events between files.

### 4.2 Selection flags
Table `Selection` (reco) and, in MC, `GenSelection` (gen). All columns are bool.

| Column | Level | Meaning |
|---|---|---|
| `goodVertex` | reco | `selection.reco.vertex` cuts on the first primary vertex: not fake, ndof > `ndofMin`, \|z\| ≤ `absZMax`, ρ ≤ `rhoMax` (NanoAOD `goodPvCut`) |
| `metFilters` | reco | AND of the `selection.reco.metFilters` paths (`inputs.metFilterProcess`) |
| `ecalBadCalib` | reco | only if `selection.reco.ecalBadCalib.crystals` is non-empty: `EcalBadCalibFilter` rerun on those crystals (JME, 2022-23 prompt-reco ECAL crystal) |
| `jetVetoMap` | reco | JME Run 3 jet veto map (`selection.reco.jetVetoMap`): no JEC-corrected AK4 jet with pt > `ptMin`, TightLeptonVeto ID and chEmEF + neEmEF < `emFractionMax` in a vetoed (η, φ) bin |
| `<ch>Trigger` | reco | OR of the channel's `triggers` (globs, `inputs.hltProcess`) |
| `<ch>Sel` | both | the channel's object selection alone (§4.3) |
| `<ch>B2B` | both | only for channels with `backToBack.enabled`: `<ch>Sel` AND a back-to-back jet at the same level |
| `<ch>` | both | the full channel selection. Reco: `<ch>Trigger` AND `goodVertex` AND `metFilters` [AND `ecalBadCalib`] AND `jetVetoMap` AND `<ch>Sel` [AND `<ch>B2B`]. Gen: `<ch>Sel` [AND `<ch>B2B`] |

In MC both levels are always evaluated and stored, whatever `selection.levels` says. `selection.levels` only decides
which events are written (§1).

### 4.3 Channel candidates, leptons and MET
The columns are those of the selector outputs: the reco objects after `muonCorrections` (muons) and `dressing`; the gen
objects from the Rivet particle level (dressed leptons, prompt photons). They are filled whenever `<ch>Sel` passes, and
are empty otherwise.

| Table | Rows | Columns |
|---|---|---|
| `<ch>Boson` (dilepton) | 1: the sum of the two selected leptons | `pt`, `eta`, `phi`, `mass`, `charge` (sum) |
| `<ch>Boson` (leptonMET) | 1: the selected lepton + the reconstructed neutrino | `pt`, `eta`, `phi`, `mass`, `charge` (the lepton's) |
| `<ch>Neutrino` (leptonMET) | 1: the reconstructed neutrino (massless, pT = MET) | `pt`, `eta`, `phi`, `mass`, `status` (strategy code) |
| `<ch>Objects` (singleObject) | the selected objects (for example photons) | `pt`, `eta`, `phi`, `mass`, `charge` |
| `<ch>Leptons` (dilepton, leptonMET) | 2 (leading first) or 1 | `pt`, `eta`, `phi`, `mass`, `charge`, `pdgId` |
| `SelectionMET`, `GenSelectionMET` | singleton | `pt`, `phi` of the MET the leptonMET selectors use |

The channel types, with the YAML keys of each:
- `dilepton` (`objects`, `vetoes`, `leadPtMin`, `subleadPtMin`, `massMin`, `massMax`, `oppositeCharge`, `targetMass`,
  `pairPtMin`): the pair passing the cuts with mass closest to `targetMass`; the channel fails if that pair's pt is
  below `pairPtMin` (a lower-pt pair is not replaced by another), or if any candidate of the `vetoes` collections lies
  farther than ΔR = 0.01 from both selected leptons (the pair itself, also present in a same-flavour veto collection,
  is not vetoed). `ZX_test.yaml` uses 200 GeV at reco and gen, and vetoes `vetoMuons`/`vetoElectrons` (loose ID and
  isolation, pt > 10) at reco and their gen equivalents. With reco dressing, each collection is dressed on its own, so a
  selected lepton and its copy in a veto collection can differ (as for `leptonMET`); both configurations dress nothing.
- `leptonMET` (`objects`, `vetoes`, `ptMin`, `metMin`, `mtMin`, `neutrino`): exactly one `objects` lepton above `ptMin`, no
  other object in `vetoes`, MET > `metMin`, m_T > `mtMin`. `neutrino: {type, ...}` names the neutrino reconstruction
  module (`WMassNeutrinoProducer`: `wMass`; `ZeroPzNeutrinoProducer`: none); it does not affect the selection.
  `WMassNeutrinoProducer`: p_T = MET, p_z from m(ℓν) = `wMass`; `status` 1 two real roots (smaller |p_z|), 2 one root,
  3 complex roots (real part; m_T > `wMass`). `ZeroPzNeutrinoProducer`: p_z = 0, `status` 0. The MET is `inputs.met`
  (`slimmedMETsPuppi`) without further corrections.
- `singleObject` (`objects`, `vetoes`, `nMin`, `nMax`): between `nMin` and `nMax` objects, no vetoed object.

The `<ch>Boson` mass of a leptonMET channel is the invariant mass of lepton + reconstructed neutrino, not m_T.

**Back-to-back jet** (every channel, key `backToBack: {enabled, dPhiMin, asymmetryMax, extraJetAlphaMax}`; enabled in
`ZX_test.yaml` with 2.8, 0.3 and −1, disabled in `default.yaml`). For an enabled channel, the highest-pt jet of the level's collection that
passes `jetCuts` and is not `veto<ch>` must have Δφ > `dPhiMin` to the channel's highest-pt `<ch>Boson`/`<ch>Objects`
candidate and |pt_jet − pt_V| / (pt_jet + pt_V) < `asymmetryMax`; a failing leading jet is not replaced by the next one.
With `extraJetAlphaMax` ≥ 0 (extra-jet veto), no jet of `selection.<level>.extraJets` may have pt ≥
`extraJetAlphaMax` · pt_V (0: any such jet vetoes); negative disables it. Those jets are AK4: at reco `src`
(`slimmedJetsPuppi`) with the re-applied JEC, the nominal JER in MC and the `idMask` jet ID; at gen `src`
(`slimmedGenJets`). At both levels: pt > `ptMin`, |η| < `absEtaMax`, and jets within `dRJet` of the back-to-back jet or
`dRLepton` of the channel's selected objects are ignored.
- `<ch>B2B` records the requirement (with `<ch>Sel`), and `<ch>` includes it, so the event filter and the aggregated
  histograms count the channel only with such a jet.
- The jet table and its EECs hold only the jets selected by some enabled channel (normally one); `b2b<ch>` marks the
  channel(s) that selected each jet. The jet is chosen whenever `<ch>Sel` passes, also if the trigger fails.
- Validation rejects it for `leptonMET` channels (W selection to be refined), `singleObject` channels with `nMin` 0,
  channels missing from `jets.cleaning.channels`, more than one jet collection at the level, and jet variations
  (per-variation selection deferred: `backToBack_plan.md`).

**Lepton and photon details (reco).** Each row of `<ch>Leptons` / `<ch>Objects` is matched to the nearest same-charge
PAT object (ΔR < 0.1; `correctedMuons` for muons when it exists, otherwise the MiniAOD collection), and these columns are
added:
- `undressedPt`: the matched object's pt (for muons after the momentum assignment and corrections, before dressing).
- `triggerMatched`: within ΔR < 0.1 of an HLT object from the last filter of a fired path among the channel's `triggers`.
- The `selection.reco.objectTables` columns for the object type. `default.yaml`:
  - muons: `dxy`, `dz`, `highPtRegime` (−1 without a momentum assignment), `tunePPt` (uncorrected), `pfRelIso04`,
    `tkRelIso`, and the bools `looseId`, `mediumId`, `tightId`, `highPtId`, `trkHighPtId`;
  - electrons: `dxy`, `dz`, `scEta`, `cutBased` (0–4: fail, veto, loose, medium, tight; RunIIIWinter22 V1), `pfRelIso03`, `r9`;
  - photons: `scEta`, `cutBased` (0–3; RunIIIWinter22 122X V1), `pixelSeed`, `electronVeto`, `pfRelIso03`, `r9`,
    `sieie`, `hoe`.

### 4.4 Muon scale factors
Singleton `<ch>MuonSF` for each channel listed in `selection.reco.muonScaleFactors` (MC only).

| Column | Meaning |
|---|---|
| `nominal` | event weight: product of the per-muon SFs; trigger SF of the triggering muon only |
| `<term>_statUp`, `_statDown`, `_systUp`, `_systDown` | the event weight with that term's SFs shifted by ± their stat or syst uncertainty |

- `<term>` are the `name`s of the channel's terms (`id`, `iso`, `trig` in `default.yaml`), so the columns change with the
  term list.
- Every column is 1 in events failing `<ch>` (the full reco selection).
- The rules (regimes, HLT matching, out-of-range handling) are in `EventSelection/README.md`; some are provisional
  (`OPEN_QUESTIONS.md`).
- The reco-level aggregated histograms already include `nominal`. NANO users have to multiply it in themselves.

### 4.5 Jets and constituents
One jet table per collection and per variation: `<table.name>` for the nominal, `<table.name><variation>` otherwise.
The rows are the selected jets (after `jetCuts` and constituent selection), in the order of the source collection.
Jets near leptons or photons are **not removed**. Every jet table (nominal and variations) carries one bool column
`veto<ch>` per channel in `jets.cleaning.channels`: true if the jet is within the collection's `cleaningDR` of a selected
object of channel `<ch>` (reco jets: reco objects; gen jets: gen objects). The EEC tables keep the same rows, so the
flags apply to them through `iJet`. The aggregated histograms of channel `<ch>` skip the jets with `veto<ch>`, and only
those; other channels' vetoes are not applied.

| Column | Type | Meaning |
|---|---|---|
| `pt`, `mass` | float | after the corrections (JER smearing in MC, applied before every jet cut, including `translator.ptMin`) and the variation |
| `eta`, `phi` | float | |
| `rawPt` | float | uncorrected pt |
| `jetId` | uint8 | bit 0 Tight, bit 1 TightLeptonVeto of the JME correctionlib jet ID (`translator.jetId`; 0 for gen and reclustered jets); bit 2 (4): MiniAOD dropped the jet's PF specific (`slimmedJetsAK8`, pt < 170), bits 0 and 1 are then clear |
| `nConstituents` | uint32 | constituents after `constituentCuts` |
| `srcIdx` | uint32 | index in the source collection |

**Extension columns (nominal table only).** For a reco `pat` collection, `table.extraVariables` adds columns evaluated
on the jet `src[srcIdx]` after the `jec` step, plus the built-in `jerFactor` (the JER smearing factor applied, 1 in data). The
variation tables have no extension columns: match them to the nominal through `srcIdx`. `default.yaml` (`RecoJet`):
- corrections: `jecPt` (pt with the re-applied `jec` correction, before JER; `pt = jecPt × jerFactor`), `jecFactor`, `area`, `rawFactor`;
- substructure: `msoftdrop`, `tau1`–`tau4`, `n2b1`, `n3b1`, `subJetIdx1`, `subJetIdx2` (MiniAOD soft-drop subjets, not stored);
- ParticleNet with mass: `particleNetWithMass_{QCD,TvsQCD,WvsQCD,ZvsQCD,H4qvsQCD,HbbvsQCD,HccvsQCD}`;
- ParticleNet from MiniAOD: `particleNet_{QCD,QCD2HF,QCD1HF,QCD0HF,massCorr}`, `particleNet_{Xbb,Xcc,Xqq,Xgg,Xtt,Xtm,Xte}VsQCD`;
- energy fractions and multiplicities: `chHEF`, `neHEF`, `chEmEF`, `neEmEF`, `muEF`, `chMultiplicity`, `neMultiplicity`;
- MC only: `hadronFlavour`, `partonFlavour`, `nBHadrons`, `nCHadrons`.

The names follow the NanoAODv12 `FatJet` table where it has them.

**Gen `pat` collections (nominal table, e.g. `GenJet`).** Built-in extension columns:
- `partonFlavour`, `hadronFlavour`, `nBHadrons`, `nCHadrons`: ghost clustering (`HadronAndPartonSelector`,
  `JetFlavourClustering` with the collection's R), as for NanoAOD `GenJetAK8`;
- `bosonPdgId`, `bosonPt`, `bosonDR`: the closest last-copy W/Z/H with a quark or gluon daughter in `prunedGenParticles`
  within ΔR < R of the jet axis (`bosonPdgId` 0, the others -1 if none);
- `nBosonDaughters`: that boson's quark and gluon daughters within ΔR < R of the jet axis.

**Re-tagged columns (GloParT).** Taggers that the MiniAOD does not store are run in the job when the collection has a
`retag` block (`taggers: [GlobalParT]` in `default.yaml`).
- **How:** the standard NanoAOD recipe, `updateJetCollection` with the GlobalTag JECs of `retag.jecPayload`. The
  re-tagged copy of `src` only provides the `retag.variables` columns, read at the same index (a jet that differs in
  η/φ is an error).
- **Unchanged:** the EEC jets, the selection and every other column use the `jec` re-corrected jets, not the tagger's JECs.
- **`default.yaml` columns:** the 23 NanoAOD `globalParT3_*` columns (GlobalParticleTransformer AK8, model V03):
  - the class scores `Xbb`, `Xcc`, `Xcs`, `Xqq`, `Xtauhtau{e,m,h}`, `XWW4q`, `XWW3q`, `XWWqq{e,m}v`, `TopbWqq`, `TopbWq`,
    `TopbW{e,m,tauh}v`, `QCD`;
  - `WvsQCD` = (Xqq + Xcs)/(Xqq + Xcs + QCD);
  - the mass regressions `massCorrX2p`, `massCorrGeneric` (multiply by mass × (1 − rawFactor));
  - `withMass{Top,W,Z}vsQCD`.
- **Class scores do not sum to 1** per jet (0.0–1.5 on the test file). NanoAOD's own `globalParT3_*` values are
  identical per jet, so this comes from how CMSSW stores the model outputs, not from this job. Build discriminants as
  sig/(sig + bkg), as the NanoAOD docs say.

**Alternative jet axes (nominal table only; `jets.collections.<C>.axes`).** `EECJetAxisProducer` computes each axis
from all (PUPPI-weighted) constituents before `constituentCuts`. Columns per axis `<name>`: `<name>Pt`, `<name>Eta`,
`<name>Phi`, `<name>Mass` (float) and `<name>Status` (uint8). Status 2 always means unavailable, with the axis equal to
the jet four-momentum.
- `softDrop` (β, z_cut, R0; C/A declustering as MiniAOD `SoftDropPuppi`): the sum of the subjets. Status 1: the groomed
  jet is one particle (axis = that subjet).
  - `corrected: true`: each subjet gets the `subjetJec` (AK4 PUPPI), then in MC the AK4 hybrid JER (`subjetJer`)
    against the MiniAOD gen soft-drop subjets. `<name>Mass` is then the JME-prescription soft-drop mass.
  - With the production parameters and the MiniAOD subjet JEC factors, this reproduces `groomedMass('SoftDropPuppi')`.
    Clustering is identical where the constituents agree; 0.6% of jets differ by MiniAOD packing
    (`JetSetup/test/validation/checkSoftDrop.py`).
- `trimming` (kt subjets of R_sub with pt fraction > f_cut, as `ak8PFJets*Trimmed`): sum of the kept subjets,
  uncorrected.
- `wta`: winner-take-all axis (C/A or kt, `WTA_pt_scheme`). Its mass is that of the winning particle.
- `recoil`: η of the jet, φ of the first passing back-to-back channel's boson + π. Status 2 without one.
- `truth` (MC, `prunedGenParticles`, ΔR < R): the four-momentum of the nearest hadronic boson (status 0): γ, Z, W or H,
  the last copy in the pruned record, with a quark or gluon daughter (photons only from the hard process; H→WW/ZZ gives
  the W/Z). Without one, the nearest outgoing hard-process quark or gluon (Pythia status 23, before FSR): status 1 if
  it is from a boson decay (resolved decay), 3 otherwise. Status 2: no match. A parton axis has the record mass (0 for
  gluons and MadGraph light quarks; 0.33/0.5/4.8 GeV for u,d/s/b in the Powheg samples), so rest-frame boosts about it
  need a fixed mass hypothesis; `addRestFrame` rejects only masses below 2 m_π.

- Variations exist in MC only. JES and JER variations change only the jet four-momentum (on the pat::Jet, before the
  translator); constituent variations
  (`constScale`, `constDrop`) change the constituents and so the EECs. See `JetSetup/README.md`.
- With `writeConstituents=1`, every jet table also gets `<jet table>Constituents`: `iJet`, `pt`, `eta`, `phi`, `E`,
  `charge`, `pdgId`, `puppiWeight` (already applied to the momentum), `srcIdx`.

**Jet-free collections (`mode: event`).** One collection `<C><ch>` (table `<table name><ch>`, e.g.
`RecoEvtAllJetZmumu`) per `jets.cleaning` channel `<ch>` (all must be dilepton channels), so that each removes only
its own channel's leptons. It holds one pseudo-jet in the events where that channel's dilepton selection passes, else
none (0 also when fewer than `minConstituents` particles pass), made of the event's candidates (`src`: packed PF or
packed gen particles) with |η| < `absEtaMax`, charged candidates with `fromPV() >= minFromPV` (if ≥ 0), optionally
only the recoil hemisphere (|Δφ| > π/2 to the channel's boson), PUPPI-weighted if `applyPuppiWeights`, without the
channel's two selected leptons: at reco their PF candidates and, for electrons, the
candidate matching their CTF track (`sourceCandidatePtr`s; a
selected electron usually has one, its PF electron, but can have several, including photons and charged hadrons), at gen the
dressed lepton's bare lepton and the photons used in its dressing (except photons whose pt packs to 0 in MiniAOD,
whose packed copies are never kept). Then the usual `constituentCuts` (e.g.
`chargedOnly`). The p4 is the vector sum of the (weighted) particles before `constituentCuts`; `rawPt` = `pt`; no ID,
axes, variations, cleaning or back-to-back columns. Observables are restricted to collections with their
`collections:` key. Translator `extraSrcs` (reco, e.g. `[lostTracks]`) adds more packed candidates after `src`;
constituent `srcIdx` then indexes the concatenation. `simulation/configs/ZX_jetfree.yaml` (from
`make_jetfree_config.py`) defines `RecoEvtAll` (packed PF candidates and lostTracks, no PV cut or PUPPI weighting) and
`GenEvtAll`, constituents only. Production `20261119_jetfree` predates the per-channel split: its single collections
`RecoEvtAllJet`, `GenEvtAllJet` remove the selected leptons of every passing channel (both channels pass in 6 of
132822 DY 600+ reco events, 0 at gen). With translator `constituentDetails` (reco), `<table>Constituents` also has `source`
(0: `src`, then `extraSrcs`), `fromPV`, `pvAssociationQuality` (uint8), `dz`, `dxy` (cm; NaN for neutrals), `dzError`,
`dxyError` (NaN without track details), `puppiWeightRaw`, `puppiWeightNoLep`.

### 4.6 EEC observables
For each jet collection `<C>`, variation `<v>` and observable `<obs>` (name `<C><v><obs>`):

**Per-jet table `<C><v><obs>`** (one row per jet, in the same order as the jet table):

| Column | Type | Meaning |
|---|---|---|
| `E_jet` | double | the normalisation used (`norm`: `sumE`, `sumPt`, `jetE`, `jetPt`, `unity`) |
| `n` | float | the energy-weight power |
| `N` | uint8 | particles per tuple (1 for E1C) |
| `nEntries` | uint32 | rows of this jet in `<C><v><obs>Entries` |

**Entries table `<C><v><obs>Entries`.** Its columns depend on `output`:

| `output` | Columns | One row per |
|---|---|---|
| `Dense` | `iJet`, `bin`, `weight` | every bin of the binning, flow bins included |
| `SparseMerged` | `iJet`, `bin`, `weight` | non-empty bin (weights summed, symmetry factors included) |
| `SparseUnmerged` | `iJet`, `bin`, `weight`, `symfactor` | tuple (multiset); `weight` excludes the symmetry factor |
| `Unbinned` | `iJet`, `<coordNames...>`, `weight`, `symfactor` | tuple, with its coordinates instead of a bin |

- `weight` is the product of (E_p / E_jet)ⁿ over the tuple, with E_p from `weight` (`Energy` or `Pt`).
- `bin` is the flow-inclusive linear index over all axes: 0 is underflow, axis 0 varies fastest.
- `kind: resolvedE3C` (N = 3; modules `RE3CProducer_<Weight>_<Angle>_<Output>`): three axes (R_L, ξ, φ), R_L the
  largest pairwise angle and ξ = R_S/R_M, φ = arcsin √(1 − (R_L − R_M)²/R_S²) the triangle shape of arXiv:2201.07800
  Eq. (3); a tuple with R_S = 0 (a repeated particle, or coincident ones) has ξ = φ = −1, i.e. the ξ and φ underflow
  bins. Summed over ξ and φ it is the pENC with N = 3. Default unbinned coordinate names `RL`, `xi`, `phi`. No production config enables it yet (2026-11-19).
- Axis 0 is θ_max (pENC) or the first frame coordinate (E1C). For E1C the coordinates are (θ, φ) in `frame`
  (`lab`, `jetAxis`, `jetHelicity`, `jetCS`, `jetProjective`; see `EECs/interface/Config.h`). The jet frames take the
  beam on the jet side (sign of the jet pz) as reference; `jetProjective` has θ = ΔR to the jet axis and φ the
  direction in the (η, φ) plane, 0 toward that beam.
- E1C with `axis: <axis name>` (frame `jetAxis` only): θ, φ about that axis instead of the jet; the normalisation
  still uses the jet. Nominal jets only (no table for variations).
- Charge weight (`Charge`; pENC with `DeltaR` only): the constituent charge, not scaled by the PUPPI weight.
- To use another normalisation E′, multiply the weights by (E_jet / E′)^(n·N).
- Definitions and conventions: `EECs/docs/guide.md`.

**Run tables** (binned outputs only), in the `Runs` tree:
- `<C><v><obs>Axis<k>`, column `edge`: the bin edges of axis k, without the flow bins.
- `<C><v><obs>AxisType`, column `type`: 0 regular, 1 log, 2 variable.

### 4.7 MC event tables
With `output.mcEventTables` (MC), the standard CMSSW modules `genWeightsTable`, `puTable` and `genTable`, with their
CMSSW defaults:
- **Events:**
  - `genWeight`;
  - `Generator_*`: `weight`, `id1`, `id2`, `x1`, `x2`, `xpdf1`, `xpdf2`, `scalePDF`, `binvar`;
  - `Pileup_*`: `nPU`, `nTrueInt`, `sumEOOT`, `sumLOOT`, `pudensity`, `gpudensity`, `pthatmax`;
  - `LHEWeight_originalXWGTUP`;
  - `LHEScaleWeight`, `LHEPdfWeight`, `PSWeight` and `LHEReweightingWeight`, all as ratios to the nominal. The branch
    titles give the index meaning (for example the μ_R/μ_F order of `LHEScaleWeight`).
- **Runs:** `genEventCount`, `genEventSumw`, `genEventSumw2`, `LHEScaleSumw`, `LHEPdfSumw`, `PSSumw`.
  - These sum over **every processed event**, not just the written ones, so they are the right normalisation.
    `genWeightsTable` runs on its own path for this reason.

### 4.8 LHE tables
With `output.lheTables` (MC), CMSSW's `LHETablesProducer` with the standard NanoAOD settings (14-bit momenta, particles
stored):
- **`LHE`** (singleton): `HT`, `HTIncoming`, `Vpt`, `AlphaS`, `Njets`, `Nb`, `Nc`, `Nuds`, `Nglu`, `NpLO`, `NpNLO`.
- **`LHEPart`:** `pt`, `eta`, `phi`, `mass`, `incomingpz` (incoming partons, which have pt = 0), `pdgId`, `status`
  (−1 incoming, 1 outgoing), `spin`, `firstMotherIdx`, `lastMotherIdx`.
- A sample without an `LHEEventProduct` gets empty tables.

### 4.9 HLT bits
With `output.keepHLTBits`, the `NanoAODOutputModule` writes one bool per path of the input's `inputs.hltProcess`
menu, with the `_v<N>` suffix removed.
- It keeps only paths whose names start with `HLT`, `Flag` or `L1`, or contain `Scouting`. This is why
  `Dataset_ScoutingPF*`, `DST_*Scouting*` and `MC_*Scouting*` appear but other `Dataset_*`, `DST_*` and `MC_*` paths do not.
- The branch set depends on the menu of the input sample. The channel triggers the analysis uses are in `Selection_<ch>Trigger`.

### 4.10 MET
- `SelectionMET` / `GenSelectionMET` (§4.3): the MET the W selections use. At reco it is `inputs.met`, or, with
  `selection.reco.metCorrections.apply`, the corrected MET below.
- **MET corrections** (`selection.reco.metCorrections`, reco only, in this order; JME `cms-jme-jmar` MET corrections):
  1. `metType1`: Type-1 PUPPI MET recomputed as raw MET - sum over the AK4 PUPPI jets (`type1.jets`) of (p_T full -
     p_T L1) along the muon-subtracted jet direction (the muon daughters removed from the raw jet: packed flags
     isGlobalMuon or isStandAloneMuon, or the source candidate of a `inputs.muons` muon with either flag; the packed
     flags alone miss standalone-only PF muons that production subtracts), for jets with
     corrected p_T > `ptMin` (15 GeV), |eta| < `absEtaMax` (5.2) and chEmEF + neEmEF < `emFractionMax` (0.9). The JEC
     is the V4 payload (`mcKey`/`dataKey`, L1 from `l1McKey`/`l1DataKey`) evaluated on the muon-subtracted raw jet; in MC
     with `type1.jer.enabled` the nominal JER factor of each jet (`PATJetJERCProducer`, AK4 PUPPI JRV2) multiplies the
     full p_T. MiniAOD jets below its own threshold are not available; jets without PF specific are not cut on the EM fraction.
  2. `metXY` (`xy.enabled`): JME XY shift (`met_xy_corrections`, `metType`, `epoch`, `variation`, data or MC, number of
     good vertices of `selection.reco.vertex`).
  3. `correctedMET` (`muons.propagate`, needs `muonCorrections` to change the muons): MET + sum over the PF muons of
     (p_T of `inputs.muons` - p_T of `correctedMuons`), as the MUO POG recommends for TuneP muons.
  Not propagated: the jet and MET variations (JES, JER, unclustered), electrons and photons. The pat::MET products keep
  their Raw and Type1 levels; the JES/JER/unclustered shifts stored in them (and so the `PuppiMET` table's variations)
  are the MiniAOD ones. The module and validation details are in `JetSetup/README.md`.
- One table per entry of `output.metTables` (`name: pat::MET label`), with the standard NanoAOD `PuppiMET` columns: `pt`,
  `phi`, `sumEt`, `significance`, `covXX`, `covXY`, `covYY`, `sumPtUnclustered`, `pt`/`phi` `UnclusteredUp`/`Down`, plus
  `ptJESUp`/`Down`, `phiJESUp`/`Down`, `ptJERUp`/`Down`, `phiJERUp`/`Down`.
  - The shifts are the ones stored in MiniAOD, made with the MiniAOD-era JECs, not the in-job V4 JECs.
- `Raw<name>`: `pt`, `phi`, `sumEt` without the type-1 corrections.
- MC: `GenMET` (`pt`, `phi`) from the first `metTables` entry's `genMET()`.
- `default.yaml`: `MET` = `slimmedMETs` (type-1 PF MET, the NanoAOD v12 name) and `PuppiMET` = `slimmedMETsPuppi`,
  with `RawMET` and `RawPuppiMET`.

### 4.11 Vertices, rho, gen vertex, pileup weights
- `PV` (singleton, standard `vertexTable`): `npvs`, `npvsGood`, `x`, `y`, `z`, `chi2`, `ndof`, `score`, `sumpt2`,
  `sumpx`, `sumpy`. `npvsGood` uses the `selection.reco.vertex` cuts, so it counts vertices the way
  `Selection_goodVertex` judges the first one. `OtherPV`: `z`, `score` of the other vertices.
- `SV`: the standard secondary-vertex table (from `inputs.secondaryVertices`).
- `Rho`: the `output.rhoTable` values, for example `fixedGridRhoFastjetAll` (the JEC rho).
- MC: `GenVtx` (singleton): `x`, `y`, `z`, `t0` of the generated primary vertex.
- MC: the `Pileup` table gains `weight`, `weightUp`, `weightDown`: the LUM correctionlib weights at the in-time
  `nTrueInt`. They are not applied to the aggregated histograms.

### 4.12 Gen particles
MC and `output.genParticles`: `GenPart`, the standard NanoAOD table, with the standard pruning (`finalGenParticles`):
hard process, W/Z/H, leptons, neutrinos, heavy-flavour hadrons, prompt photons, top quarks, high-pt partons before
hadronisation.
- Columns: `pt`, `eta`, `phi`, `mass`, `pdgId`, `status`, `statusFlags` (bitwise, see the branch title), `genPartIdxMother`.
- Precision: 8 bits for the momenta, as in standard NanoAOD.
- Not written: the standard `iso` column, which needs a module not run here.

### 4.13 AK4 jets
`output.ak4Jets` (enabled in `default.yaml`, table `AK4Jet`): the `src` jets (`slimmedJetsPuppi`) with the JECs
**re-applied in the job**.
- **Correction:** p4 = raw p4 × C, where C is the correctionlib compound correction (`jec.mcKey` in MC, `jec.dataKey` in
  data; V4 L1L2L3Res AK4 PUPPI) at the raw pt and η, the jet area and `rho`. The jets are then cut with `cut` (on the
  corrected jets) and sorted by corrected pt.
- **Built-in columns:** `pt`, `eta`, `phi`, `mass` (corrected), `rawPt`, `jecFactor` (C), `jetId` (bit 0 Tight, bit 1
  TightLeptonVeto, JME correctionlib `jetId`), `srcIdx` (index in `src`), and with `jec.uncKey` `jesUncTotal` (the relative Total JES
  uncertainty at the corrected pt; shift with pt × (1 ± jesUncTotal)).
- **Not applied:** JER smearing.
- **`variables` in `default.yaml`:**
  - `area`;
  - DeepJet: `btagDeepFlavB`, `CvL`, `CvB`, `QG`;
  - ParticleNet: `btagPNetB`, `CvL`, `CvB`, `QvG`, `TauVJet`;
  - RobustParT: `btagRobustParTAK4B`, `CvL`, `CvB`, `QG`;
  - energy fractions and `nConstituents`;
  - MC only: `hadronFlavour`, `partonFlavour`.
- The AK4 jets are not cleaned against leptons, and they are not used by the selection or the EECs.

## 5. Worked example: default.yaml
Measured on 300 events of `DYto2L-4Jets_MLL-50_PTLL-400to600` (Summer22EE MC, 222 written) and on Run2022F Muon data.

- **Channels:**
  - reco and gen: `Zmumu`, `Zee` (dilepton), `Wmunu`, `Wenu` (leptonMET), `Hadronic`, `GammaJets` (singleObject).
  - So: 6 candidate tables per level, 4 `Leptons` tables per level, `SelectionMET` and `GenSelectionMET`.
  - Reco lepton/photon detail columns: muons 11 + 2 built-in, electrons 6 + 2, photons 8 + 2.
  - `Selection` has 20 columns, `GenSelection` 12.
- **Muon SFs:** `ZmumuMuonSF` and `WmunuMuonSF`, with 13 columns each (`nominal` + {id, iso, trig} × 4).
- **Jets:**
  - `Reco` (AK8 PUPPI, `slimmedJetsAK8`) with 11 MC variations (JES ±, JER ±, TrkDrop, Charged/Neutral/Photon scale ±):
    the tables `RecoJet` and `RecoJet<variation>`.
  - `RecoJet` has 42 extension columns in MC (38 in data), 23 GloParT columns and `jerFactor`.
  - `Gen` (MC only): `GenJet`.
- **EECs:** `E2C`, `E3C`, `E1C`, all `SparseMerged`, for every collection and variation. That is 39 per-jet + 39
  Entries tables in MC (12 Reco chains × 3 + Gen × 3) and 3 + 3 in data, plus their axis tables in `Runs`.
- **Event tables:** `MET`, `RawMET`, `PuppiMET`, `RawPuppiMET`, `PV`, `OtherPV`, `SV`, `Rho` (6 values), `AK4Jet`; in MC
  also `GenMET`, `GenVtx`, `GenPart`, `Pileup` with weights, the MC event tables and the LHE tables. About 620 HLT bits.
- **Data:** the same minus everything marked MC: no `Gen*`, no jet variations, no muon SFs, no LHE, no generator or
  pileup tables, no Runs-tree sums, and no flavour columns. The AK4 jets use the data JEC key.

## 6. Pitfalls
- `<ch>Sel` does not include the trigger. To select events, use `Selection_<ch>` (reco) or `GenSelection_<ch>` (gen).
- A written event may have been selected by a different channel or level. Always cut on the flag of the channel you analyse.
- The candidate and lepton tables of a reco channel are filled even if its trigger failed (they follow `<ch>Sel`).
- MC normalisation: use `Runs` `genEventSumw` (all processed events), not a sum over the written events.
- The muon SF and the pileup weights are not applied to anything in the NANO. Multiply `<ch>MuonSF_nominal` and
  `Pileup_weight` into the MC weights yourself; the aggregated histograms include the muon SF but not the pileup weight.
- `MET` is the PF MET, as in standard NanoAOD; the MET the W selections use is `SelectionMET` (PUPPI in `default.yaml`).
- Jets overlapping leptons or photons are in the jet and EEC tables. To reproduce what the aggregated histograms of
  channel X use, drop the jets with `veto<X>`.
- Every jet has at least two constituents after `constituentCuts` (`jetCuts.minConstituents >= 2`, enforced by the
  config check): a one-particle jet has no E1C frame.
- The AK8 `RecoJet` pt has the JEC of the collection's `jec` block (re-applied from raw; V4 in `default.yaml`) and,
  in MC, the JER smearing; `jecPt` has no JER. The AK4 `AK4Jet` pt has the re-applied V4 JEC and no JER.
- Table and column names follow the configuration. Code reading these files should take the names from the YAML used
  (kept in the job provenance) rather than hard-coding the `default.yaml` names.
