"""Per-jet tables: one row per kept jet of a region, for offline scans (e.g. sensitivity.py).

Spec (configuration key `tables:`, {name: spec}):
  regions   region names (default: all)
  columns   {name: expression}, event or jet level; event-level values are repeated on each jet of the event
  eec       {name: {observable, var (eec- or jet-level expression), bins (binning name or spec), cuts: [...]}}: the
            jet's EEC histogram as one row of length nbins + 2 (underflow, bins, overflow), each entry weighted by
            weight x symfactor; the event weight is not applied
  ak4       optional {ptMin, absEtaMax, dRJet, dRLepton}: AK4 jets (event table AK4Jet) with pt > ptMin and
            |eta| < absEtaMax, farther than dRJet from the row's jet and dRLepton from every selected lepton; adds
            ak4N, ak4HT and ak4MaxBtag (max btagRobustParTAK4B, -1 without any)
Every table also has the column `weight` (the event weight of the region). Missing values become NaN.
Output: {column: numpy array}; EEC rows are float32 arrays of shape (jets, nbins + 2), other columns float64.
"""
import awkward as ak
import numpy as np

from . import eec as eecTools
from .expr import Expr, asBool, combine
from .histograms import makeAxis

AK4_KEYS = {'ptMin', 'absEtaMax', 'dRJet', 'dRLepton'}


class TableError(ValueError):
    pass


class TableDef:
    def __init__(self, name, spec, binnings, variables):
        self.name = name
        unknown = set(spec) - {'regions', 'columns', 'eec', 'ak4'}
        if unknown:
            raise TableError('table %s: unknown keys %s' % (name, sorted(unknown)))
        self.columns = {}
        for c, text in (spec.get('columns') or {}).items():
            e = Expr(text, variables)
            if combine(e.level, 'jet', text) != 'jet':
                raise TableError('table %s: column %s (%r) is %s-level, not event or jet' % (name, c, text, e.level))
            self.columns[c] = e
        self.eec = {}
        for c, e in (spec.get('eec') or {}).items():
            if set(e) - {'observable', 'var', 'bins', 'cuts'} or not {'observable', 'var', 'bins'} <= set(e):
                raise TableError('table %s: eec %s needs observable, var, bins (and optional cuts)' % (name, c))
            b = e['bins']
            if isinstance(b, str):
                if b not in binnings:
                    raise TableError('table %s: unknown binning %r' % (name, b))
                b = binnings[b]
            var, cuts = Expr(e['var'], variables), [Expr(x, variables) for x in e.get('cuts', [])]
            for x in [var] + cuts:
                if combine(x.level, 'eec', x.text) != 'eec':
                    raise TableError('table %s: eec %s: %r is %s-level' % (name, c, x.text, x.level))
            self.eec[c] = (e['observable'], var, cuts, makeAxis(b, c, e['var']).edges)
        self.ak4 = spec.get('ak4')
        if self.ak4 is not None and set(self.ak4) != AK4_KEYS:
            raise TableError('table %s: ak4 needs exactly %s' % (name, sorted(AK4_KEYS)))
        if {'weight'} & (set(self.columns) | set(self.eec)) or set(self.columns) & set(self.eec):
            raise TableError('table %s: duplicate or reserved (weight) column names' % name)

    def fill(self, view):
        ns = view.namespace()
        jetPt = ns['jets'].pt

        def perJet(x):
            return ak.to_numpy(ak.fill_none(ak.flatten(ak.broadcast_arrays(x, jetPt)[0], axis=1), np.nan)).astype(np.float64)
        out = {'weight': perJet(view.weight)}
        for c, e in self.columns.items():
            out[c] = perJet(e(ns))
        for c, (obs, var, cuts, edges) in self.eec.items():
            out[c] = jetHistograms(view, obs, var, cuts, edges)
        if self.ak4 is not None:
            out.update({k: perJet(v) for k, v in ak4Columns(view.events.AK4Jet, ns['jets'], ns.get('leptons'),
                                                            **self.ak4).items()})
        return out


def jetHistograms(view, observable, var, cuts, edges):
    """(jets, nbins + 2) histogram of each kept jet's EEC entries in var, weighted by weight x symfactor."""
    ns = view.namespace(observable)
    entries = view.entries(observable)[0]
    template = entries.weight
    keep = ak.ones_like(template, dtype=bool)
    for c in cuts:
        keep = keep & ak.broadcast_arrays(asBool(c(ns)), template)[0]
    x = ak.broadcast_arrays(var(ns), template)[0][keep]
    w = eecTools.tupleWeight(entries)[keep]
    perJetCount = ak.flatten(ak.num(x, axis=2))
    nJets = len(perJetCount)
    jetOfEntry = np.repeat(np.arange(nJets), ak.to_numpy(perJetCount))
    xs = ak.to_numpy(ak.flatten(x, axis=None)).astype(np.float64)
    ws = ak.to_numpy(ak.flatten(w, axis=None)).astype(np.float64)
    nb = len(edges) + 1          # underflow, len(edges) - 1 bins, overflow
    # NaN (missing) goes to the overflow, as hist does.
    b = np.where(np.isnan(xs), nb - 1, np.searchsorted(edges, xs, side='right'))
    out = np.bincount(jetOfEntry * nb + b, weights=ws, minlength=nJets * nb)
    return out.reshape(nJets, nb).astype(np.float32)


def ak4Columns(ak4, jets, leptons, ptMin, absEtaMax, dRJet, dRLepton):
    """ak4N, ak4HT, ak4MaxBtag per kept AK8 jet ([event][jet])."""
    ak4 = ak4[(ak4.pt > ptMin) & (abs(ak4.eta) < absEtaMax)]
    if leptons is not None:
        pairs = ak.cartesian([ak4, leptons], axis=1, nested=True)
        ak4 = ak4[ak.all(pairs['0'].delta_r(pairs['1']) > dRLepton, axis=2)]
    pairs = ak.cartesian([jets, ak4], axis=1, nested=True)      # [event][jet][ak4]
    a = pairs['1'][pairs['0'].delta_r(pairs['1']) > dRJet]
    return {'ak4N': ak.num(a, axis=2), 'ak4HT': ak.sum(a.pt, axis=2),
            'ak4MaxBtag': ak.fill_none(ak.max(a.btagRobustParTAK4B, axis=2), -1.0)}
