# W neutrino reconstruction (leptonMET channels)

User decisions (2026-11-16): the neutrino reconstruction is a replaceable strategy; MET corrections are future work (the
MET stays `inputs.met`, i.e. `slimmedMETsPuppi`, and `genParticleLevel:mets` at gen); m_W is a configuration parameter
set to the world average; the same code runs at gen level; the way the neutrino was reconstructed is a property of the
reconstructed neutrino object.

## Recipe (default strategy `WMassConstraint`)
pT(nu) = MET pT; p_z(nu) from m(l nu) = m_W with massless l and nu. With mu = m_W^2/2 + pT_l pT_nu cos(dphi):
pT_l^2 p_z^2 - 2 mu p_z,l p_z + (E_l^2 pT_nu^2 - mu^2) = 0, discriminant/4 = E_l^2 (mu^2 - pT_l^2 pT_nu^2)
(negative exactly when mT(l, MET) > m_W; checked numerically on 200k toy events).
- two real roots: the one with smaller |p_z|, status 1;
- one root (discriminant exactly 0): it, status 2;
- complex: the real part mu p_z,l / pT_l^2, status 3 (m(l nu) != m_W then).

## Design (as implemented; the plugin factory of the first draft became separate EDProducers, user decision)
- `EventSelection/interface/Neutrino.h`, `src/Neutrino.cc`: framework-free `wMassNeutrino` and `NeutrinoResult`.
- `plugins/NeutrinoProducer.h`: `NeutrinoProducer<Strategy>` implements the module contract (inputs `leptons`, `met`;
  output `vector<LeafCandidate>`, `status()` = the strategy's code). Strategies are modules:
  `WMassNeutrinoProducer` (`wMass`) and `ZeroPzNeutrinoProducer` (p_z = 0, status 0).
- `LeptonNeutrinoBosonProducer`: boson = lepton + neutrino. `LeptonMETSelector` keeps only the flag and `leptons`.
- Python: `addChannel` adds `<ch>Neutrino` (module type from `channels.<ch>.neutrino.type`) and `<ch>Boson`;
  `bosonTag()` replaces `BOSON_INSTANCE`; table `<ch>Neutrino` with `status`.
- YAML: required `channels.<ch>.neutrino: {type, ...}` for leptonMET channels (default.yaml, schema).
- Docs: NANO.md (4.3), EventSelection/README.md, JOURNAL.md.

## Tests
- Unit (`test_selection.cc` style, no framework): both real roots reproduce m_W and the smaller |p_z| is returned;
  complex case gives the real part and status 3, with mT > m_W exactly when complex; discriminant 0 gives status 2;
  p_z,l = 0 and negative p_z,l; invariance under a common phi rotation. Mutations (take the larger |p_z|, wrong sign,
  drop the real-part branch) must each fail a test.
- Module (`test_modules.cc`): LeptonMETSelector with `neutrino` yields boson = lepton + neutrino, the status, the
  unchanged flag; an unknown `type` throws; a second, trivial test strategy is selected by name (the replaceability).
- Validation (not a unit test): reconstructed vs true neutrino p_z and m(l nu) at gen level and reco on `WZ_pythia8`
  events with W -> l nu; fractions of status 1/2/3.

## Open
- m_W value: world average (PDG), to be read from the PDG tables and cited in the config comment (not in the local wikis).
