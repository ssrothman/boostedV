"""Projected N-point correlators computed offline from stored constituents, with the EEC library of the production
(simulation/EECs, Python module built by build_eecs_py.sh into bvana/_ext).

projectedENC(constituents, norms, N, n, edges, weight='Pt', angle='DeltaR') -> numpy (jets, len(edges) + 1)
  constituents: awkward [jet][particle] with pt, eta, phi, E (e.g. a NANO <table>Constituents grouped by iJet);
  norms: the per-jet normalisation (e.g. the summed constituent pt, the jet pt or the boson pt).
Row j: underflow, the len(edges) - 1 bins, overflow; self tuples (angle 0) are in the underflow when edges[0] > 0.
"""
import awkward as ak
import numpy as np

from ._ext import eecs_py


def projectedENC(constituents, norms, N, n, edges, weight='Pt', angle='DeltaR'):
    c = constituents
    pt, eta, phi, E = (ak.to_numpy(ak.flatten(c[f], axis=None)).astype(np.float64) for f in ('pt', 'eta', 'phi', 'E'))
    offsets = np.concatenate([[0], np.cumsum(ak.to_numpy(ak.num(c, axis=1)))]).astype(np.int64)
    return eecs_py.projected_enc(pt * np.cos(phi), pt * np.sin(phi), pt * np.sinh(eta), E, offsets,
                                 np.asarray(norms, dtype=np.float64), int(N), float(n),
                                 np.asarray(edges, dtype=np.float64), weight, angle)


def byJet(constituents, nJets):
    """[event][constituent] table with iJet (rows grouped by jet, as EECJetTableProducer writes them) -> [jet][constituent]
    over the jets of all events in order; nJets: jets per event."""
    nJets = ak.to_numpy(nJets).astype(np.int64)
    start = np.concatenate([[0], np.cumsum(nJets)[:-1]])
    g = ak.to_numpy(ak.flatten(constituents.iJet + start)).astype(np.int64)
    if np.any(np.diff(g) < 0):
        raise ValueError('constituents are not grouped by jet')
    return ak.unflatten(ak.flatten(constituents), np.bincount(g, minlength=int(nJets.sum())))
