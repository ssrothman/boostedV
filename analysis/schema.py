"""coffea NanoEvents schema for the boostedV NANO (eecNano_cfg.py; table names: simulation/NANO.md).

Collections are recognised by name, since table names come from the analysis YAML:
  *Jet                      four-vectors (pt, eta, phi, mass; no charge)
  *Leptons, *Boson          candidates (pt, eta, phi, mass, charge)
  *JetConstituents          candidates from (pt, eta, phi, E)
EEC per-jet tables (<C><obs>) and entries (<C><obs>Entries) stay plain records; see eec.py.
Only the standard-NanoAOD cross references whose index branch exists are kept, so absent collections give no warnings.
"""
from coffea.nanoevents import NanoAODSchema

MIXIN_SUFFIXES = (('JetConstituents', 'PtEtaPhiECandidate'), ('Jet', 'PtEtaPhiMLorentzVector'),
                  ('Leptons', 'PtEtaPhiMCandidate'), ('Boson', 'PtEtaPhiMCandidate'))


class BoostedVSchema(NanoAODSchema):
    def __init__(self, base_form, version='latest'):
        branches = set(base_form['fields'])
        names = {b[1:] for b in branches if b.startswith('n')} & {b.split('_')[0] for b in branches}
        self.mixins = dict(NanoAODSchema.mixins)
        for name in names:
            for suffix, mixin in MIXIN_SUFFIXES:
                if name.endswith(suffix) and name not in NanoAODSchema.mixins:
                    self.mixins[name] = mixin
                    break
        self.all_cross_references = {k: v for k, v in NanoAODSchema.all_cross_references.items() if k in branches}
        super().__init__(base_form, version)
