"""Per-jet correlator rows computed from stored constituents (table key `ceec`, E2C_NEXT_PLAN.md).

Spec {name: {source, N, n, bins, norm, select, eventTable, shape}}:
  source      jet: the jet's constituents (`<jet table>Constituents`; already PUPPI-weighted)
              event: the region channel's all-particle collection (`<eventTable><channel>Constituents`, or
              `<eventTable>Constituents` in productions without per-channel collections), the same row for every jet
              of the event unless select.dRJet is set
  N, n        tuple size (2-6) and energy-weight power; weights are pt
  bins        binning name (R_L for shape)
  norm        jetPt, zPt or sumPt (of the selected particles)
  shape       optional: xi or phi, the resolved E3C (N = 3) projected on (R_L, xi) or (R_L, phi), with
              binnings shapeBins (default xi: 5 bins in [0, 1], phi: 5 in [0, pi/2]); rows of R_L bins x (1 + shape
              bins), R_L fastest, without flow bins (unlike the 1D rows) except the first shape column, which holds
              the triples with R_S = 0 (eec::triangleShape puts them below every shape bin)
  select      particle filters, all optional:
              charged (true: charge != 0), ptMin, lostTracks (false: packed PF candidates only, `source == 0`),
              minFromPV, maxAbsDz, maxAbsDxy, minAbsDxy (charged particles only; neutral ones pass),
              minPuppi (puppiWeightRaw >= value), puppiWeighted (scale pt and E by puppiWeightRaw; event source),
              dRJet (particles within this Delta R of the kept jet), hemisphere (|dphi| to the boson > pi/2)
Jet-source particles get fromPV, dz, dxy, puppiWeightRaw from the event collection by srcIdx; a particle missing
there (|eta| > the collection's cut) fails every filter on those fields.
"""
import awkward as ak
import numpy as np

from . import eecext

SPEC_KEYS = {'source', 'N', 'n', 'bins', 'norm', 'select', 'eventTable', 'shape', 'shapeBins'}
SELECT_KEYS = {'charged', 'ptMin', 'lostTracks', 'minFromPV', 'maxAbsDz', 'maxAbsDxy', 'minAbsDxy', 'minPuppi',
               'puppiWeighted', 'dRJet', 'hemisphere'}
DETAILS = ('fromPV', 'dz', 'dxy', 'puppiWeightRaw')
SHAPE_EDGES = {'xi': np.linspace(0.0, 1.0, 6), 'phi': np.linspace(0.0, np.pi / 2, 6)}


class CeecError(ValueError):
    pass


def check(name, spec):
    if set(spec) - SPEC_KEYS or not {'source', 'N', 'n', 'bins', 'norm'} <= set(spec):
        raise CeecError('ceec %s: needs source, N, n, bins, norm (optional select, eventTable, shape, shapeBins)' % name)
    if spec['source'] not in ('jet', 'event'):
        raise CeecError('ceec %s: source must be jet or event' % name)
    if spec['source'] == 'event' and 'eventTable' not in spec:
        raise CeecError('ceec %s: event source needs eventTable' % name)
    if spec['norm'] not in ('jetPt', 'zPt', 'sumPt'):
        raise CeecError('ceec %s: norm must be jetPt, zPt or sumPt' % name)
    sel = spec.get('select') or {}
    if set(sel) - SELECT_KEYS:
        raise CeecError('ceec %s: unknown select keys %s' % (name, sorted(set(sel) - SELECT_KEYS)))
    if spec['source'] == 'jet' and set(sel) & {'puppiWeighted', 'dRJet', 'lostTracks'}:
        raise CeecError('ceec %s: puppiWeighted, dRJet and lostTracks are for the event source' % name)
    if 'shape' in spec and (spec['shape'] not in SHAPE_EDGES or spec['N'] != 3):
        raise CeecError('ceec %s: shape (xi or phi) needs N = 3' % name)


def _flatKeys(evIdx, src):
    return evIdx.astype(np.int64) * (1 << 32) + src.astype(np.int64)


def joinDetails(jetParts, evParts):
    """jetParts [event][jet][particle] with srcIdx, plus DETAILS from evParts [event][particle] (srcIdx, source) of
    the same event; NaN (fromPV -1) where there is no packed-PF match."""
    nJ = ak.num(jetParts, axis=1)
    perEvent = ak.flatten(jetParts.srcIdx, axis=2)                     # [event][particle]
    jEv = np.repeat(np.arange(len(perEvent)), ak.to_numpy(ak.num(perEvent)))
    jKey = _flatKeys(jEv, ak.to_numpy(ak.flatten(perEvent)))
    eSrc = ak.to_numpy(ak.flatten(evParts.srcIdx))
    eEv = np.repeat(np.arange(len(evParts)), ak.to_numpy(ak.num(evParts)))
    pf = ak.to_numpy(ak.flatten(evParts.source)) == 0
    eKey = _flatKeys(eEv[pf], eSrc[pf])
    order = np.argsort(eKey)
    eKey = eKey[order]
    pos = np.clip(np.searchsorted(eKey, jKey), 0, max(len(eKey) - 1, 0))
    found = (eKey[pos] == jKey) if len(eKey) else np.zeros(len(jKey), bool)
    out = jetParts
    counts = ak.flatten(ak.num(jetParts, axis=2))
    for f in DETAILS:
        v = ak.to_numpy(ak.flatten(evParts[f])).astype(np.float64)[pf][order]
        col = np.where(found, v[pos] if len(v) else np.nan, -1.0 if f == 'fromPV' else np.nan)
        out = ak.with_field(out, ak.unflatten(ak.unflatten(col, counts), nJ), f)
    return out


def select(p, sel, jets=None, boson=None):
    """Mask of the particles p ([event][jet][particle]) passing sel; jets [event][jet] and boson [event] broadcast."""
    keep = ak.ones_like(p.pt, dtype=bool)
    charged = p.charge != 0
    if sel.get('charged'):
        keep = keep & charged
    if 'ptMin' in sel:
        keep = keep & (p.pt > sel['ptMin'])
    if sel.get('lostTracks') is False:
        keep = keep & (p.source == 0)
    if 'minFromPV' in sel:
        keep = keep & (~charged | (p.fromPV >= sel['minFromPV']))
    if 'maxAbsDz' in sel:
        keep = keep & (~charged | (abs(p.dz) < sel['maxAbsDz']))
    if 'maxAbsDxy' in sel:
        keep = keep & (~charged | (abs(p.dxy) < sel['maxAbsDxy']))
    if 'minAbsDxy' in sel:
        keep = keep & (~charged | (abs(p.dxy) > sel['minAbsDxy']))
    if 'minPuppi' in sel:
        keep = keep & (p.puppiWeightRaw >= sel['minPuppi'])
    if sel.get('puppiWeighted'):
        keep = keep & (p.puppiWeightRaw > 0)
    if 'dRJet' in sel:
        deta = p.eta - jets.eta
        dphi = (p.phi - jets.phi + np.pi) % (2 * np.pi) - np.pi
        keep = keep & (deta ** 2 + dphi ** 2 < sel['dRJet'] ** 2)
    if sel.get('hemisphere'):
        keep = keep & (abs((p.phi - boson.phi + np.pi) % (2 * np.pi) - np.pi) > np.pi / 2)
    return ak.fill_none(keep, False)


def eventCollection(events, table, channel):
    for name in (table + channel + 'Constituents', table + 'Constituents'):
        if name in events.fields:
            return events[name]
    raise CeecError('no %s(%s)Constituents in the events' % (table, channel))


def particlesPerJet(view, spec):
    """[event][kept jet][particle] after the spec's selection (pt and E PUPPI-scaled if requested)."""
    ns = view.namespace()
    jets, sel = ns['jets'], spec.get('select') or {}
    boson = ns.get('boson')
    if spec['source'] == 'jet':
        c = view.events[view.region.jetTable + 'Constituents']
        nAll = ak.num(view.events[view.region.jetTable])
        byJet = ak.unflatten(eecext.byJet(c, nAll), ak.to_numpy(nAll))[view.jetIdx]
        if set(sel) & {'minFromPV', 'maxAbsDz', 'maxAbsDxy', 'minAbsDxy', 'minPuppi'}:
            evp = eventCollection(view.events, spec.get('eventTable', 'RecoEvtAllJet'), view.region.channel)
            byJet = joinDetails(byJet, evp)
        p = byJet[select(byJet, sel, jets, boson)]
    else:
        evp = eventCollection(view.events, spec['eventTable'], view.region.channel)
        perJet = evp[:, None][ak.zeros_like(jets.pt, dtype=np.int64)]       # the event's particles for each jet
        p = perJet[select(perJet, sel, jets, boson)]
        if sel.get('puppiWeighted'):
            p = ak.with_field(p, p.pt * p.puppiWeightRaw, 'pt')
            p = ak.with_field(p, p.E * p.puppiWeightRaw, 'E')
    return p


def rows(view, spec, edges, shapeEdges=None):
    """(kept jets, columns) float32 correlator rows of the spec."""
    p = particlesPerJet(view, spec)
    ns = view.namespace()
    flat = ak.flatten(p, axis=1)                                              # [jet][particle]
    if spec['norm'] == 'jetPt':
        norm = ak.to_numpy(ak.flatten(ns['jets'].pt)).astype(np.float64)
    elif spec['norm'] == 'zPt':
        norm = ak.to_numpy(ak.flatten(ak.broadcast_arrays(ns['boson'].pt, ns['jets'].pt)[0])).astype(np.float64)
    else:
        norm = ak.to_numpy(ak.sum(flat.pt, axis=1)).astype(np.float64)
    norm = np.where(norm > 0, norm, 1.0)                                      # empty lists give zero rows anyway
    return correlatorRows(ak.zip({k: flat[k] for k in ('pt', 'eta', 'phi', 'E')}), norm, spec, edges, shapeEdges)


def correlatorRows(cols, norm, spec, edges, shapeEdges=None):
    """rows() from the selected particles cols [jet][particle] (pt, eta, phi, E) and the per-jet norm."""
    if 'shape' not in spec:
        return eecext.projectedENC(cols, norm, spec['N'], spec['n'], edges).astype(np.float32)
    se = SHAPE_EDGES[spec['shape']] if shapeEdges is None else shapeEdges
    xi, phi = (se, np.array([0.0, 1.0])) if spec['shape'] == 'xi' else (np.array([0.0, 1.0]), se)
    full = eecext.resolvedE3C(cols, norm, spec['n'], edges, xi, phi)          # (jets, RL, xi, phi), flow bins
    proj = (full.sum(axis=3) if spec['shape'] == 'xi' else full.sum(axis=2))[:, 1:-1, :-1]   # shape underflow: R_S = 0
    return proj.transpose(0, 2, 1).reshape(len(proj), -1).astype(np.float32)   # R_L fastest
