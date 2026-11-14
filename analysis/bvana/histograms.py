"""Binnings and histogram definitions.

Binning spec (named under `binning:` or inline): {regular: [n, lo, hi]}, {log: [n, lo, hi]} (log-spaced edges),
{edges: [e0, e1, ...]} or {integer: [lo, hi]}; optional `label`.
Histogram spec: granularity event | jet | lepton | eec:<observable>; axes [{var: <expr>, bins: <name or spec>,
name: <axis name>}]; optional cuts (at the histogram's granularity or coarser, e.g. `eec.dR > 0`), `weight`
(an extra factor, any compatible level) and, for EEC histograms, `renormalise: <jet-level expr>` (weights times
(E_jet/E')^(nN)). Fill weight: event weight, times weight x symfactor for EEC entries.
"""
import re

import awkward as ak
import hist
import numpy as np

from .expr import DEPTH, Expr, asBool, combine
from . import eec as eecTools

GRANULARITY_LEVEL = {'event': 'event', 'jet': 'jet', 'lepton': 'lepton'}


class HistError(ValueError):
    pass


def makeAxis(spec, name, label):
    if set(spec) - {'regular', 'log', 'edges', 'integer', 'label'}:
        raise HistError('axis %s: unknown binning keys %s' % (name, sorted(set(spec) - {'regular', 'log', 'edges', 'integer', 'label'})))
    label = spec.get('label', label)
    kinds = [k for k in ('regular', 'log', 'edges', 'integer') if k in spec]
    if len(kinds) != 1:
        raise HistError('axis %s: give exactly one of regular, log, edges, integer' % name)
    k, v = kinds[0], spec[kinds[0]]
    if k == 'regular':
        return hist.axis.Regular(int(v[0]), float(v[1]), float(v[2]), name=name, label=label)
    if k == 'log':
        if not (v[1] > 0 and v[2] > v[1]):
            raise HistError('axis %s: log binning needs 0 < lo < hi' % name)
        return hist.axis.Variable(np.geomspace(float(v[1]), float(v[2]), int(v[0]) + 1), name=name, label=label)
    if k == 'edges':
        e = np.asarray(v, dtype=float)
        if len(e) < 2 or np.any(np.diff(e) <= 0):
            raise HistError('axis %s: edges must increase' % name)
        return hist.axis.Variable(e, name=name, label=label)
    return hist.axis.Integer(int(v[0]), int(v[1]), name=name, label=label)


def axisName(var):
    return re.sub(r'\W+', '_', var).strip('_')


class HistDef:
    def __init__(self, name, spec, binnings, variables):
        self.name = name
        unknown = set(spec) - {'granularity', 'axes', 'cuts', 'weight', 'renormalise', 'regions'}
        if unknown:
            raise HistError('histogram %s: unknown keys %s' % (name, sorted(unknown)))
        g = spec.get('granularity', 'event')
        self.observable = g.split(':', 1)[1] if g.startswith('eec:') else None
        self.level = 'eec' if self.observable else GRANULARITY_LEVEL.get(g)
        if self.level is None:
            raise HistError('histogram %s: granularity must be event, jet, lepton or eec:<observable>' % name)
        self.axes, self.vars = [], []
        for a in spec['axes']:
            e = Expr(a['var'], variables)
            self._compatible(e, 'axis')
            b = a['bins']
            if isinstance(b, str):
                if b not in binnings:
                    raise HistError('histogram %s: unknown binning %r' % (name, b))
                b = binnings[b]
            self.axes.append(makeAxis(b, a.get('name', axisName(a['var'])), a['var']))
            self.vars.append(e)
        if len({ax.name for ax in self.axes}) != len(self.axes):
            raise HistError('histogram %s: duplicate axis names' % name)
        self.cuts = [Expr(c, variables) for c in spec.get('cuts', [])]
        for c in self.cuts:
            self._compatible(c, 'cut')
        self.weight = Expr(spec['weight'], variables) if 'weight' in spec else None
        if self.weight is not None:
            self._compatible(self.weight, 'weight')
        self.renorm = Expr(spec['renormalise'], variables) if 'renormalise' in spec else None
        if self.renorm is not None and (self.level != 'eec' or self.renorm.level != 'jet'):
            raise HistError('histogram %s: renormalise needs an eec histogram and a jet-level expression' % name)

    def _compatible(self, e, what):
        if combine(e.level, self.level, e.text) != self.level:
            raise HistError('histogram %s: %s %r is %s-level, finer than the histogram (%s)'
                            % (self.name, what, e.text, e.level, self.level))

    def empty(self):
        return hist.Hist(*self.axes, storage='weight')

    def fill(self, view):
        ns = view.namespace(self.observable)
        if self.level == 'event':
            template = view.weight
        elif self.level == 'jet':
            template = ns['jets'].pt
        elif self.level == 'lepton':
            template = ns['leptons'].pt
        else:
            template = ns['eec'].weight
        w = ak.broadcast_arrays(view.weight, template)[0]
        if self.level == 'eec':
            entries, perJet = view.entries(self.observable)
            ew = eecTools.tupleWeight(entries)
            if self.renorm is not None:
                newNorm = self.renorm(ns)
                ew = ew * ak.broadcast_arrays((perJet.E_jet / newNorm) ** (perJet.n * perJet.N), ew)[0]
            w = w * ew
        if self.weight is not None:
            w = w * ak.broadcast_arrays(self.weight(ns), template)[0]
        keep = ak.ones_like(template, dtype=bool)
        for c in self.cuts:
            keep = keep & ak.broadcast_arrays(asBool(c(ns)), template)[0]
        def flat(x):
            # Missing values (e.g. max() over no jets) become NaN, which hist puts in the overflow bin.
            x = ak.broadcast_arrays(x, template)[0][keep]
            x = ak.flatten(x, axis=None) if DEPTH[self.level] > 0 else x
            return ak.to_numpy(ak.fill_none(x, np.nan))
        values = [flat(v(ns)) for v in self.vars]
        for k, ax in enumerate(self.axes):
            if isinstance(ax, hist.axis.Integer):
                values[k] = np.where(np.isnan(values[k]), ax.edges[-1], values[k]).astype(np.int64)
        h = self.empty()
        h.fill(*values, weight=flat(w))
        return h
