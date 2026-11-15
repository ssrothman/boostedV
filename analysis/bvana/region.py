"""A region: one channel at one level (reco or gen) of the boostedV NANO, narrowed by a list of cuts.

Objects seen by expressions (table names: simulation/NANO.md):
  boson    the channel's candidate (<p><ch>Boson, first row)      event level
  leptons  the channel's selected leptons (<p><ch>Leptons)         lepton level
  jets     the level's jets of ch: those with b2b<ch> if the NANO   jet level
           has back-to-back columns, else those without veto<ch>
  met      PuppiMET (reco) or GenMET (gen)                         event level
  event    the whole event record (event.PV.npvsGood, ...)         event level
  eec      entries of one EEC observable, [event][jet][entry]      eec level (histograms only)
A cut's level decides what it removes: event cuts drop events, jet cuts drop jets (and their EEC entries), lepton
cuts drop events in which any selected lepton fails.
Events must pass <flags>_<ch> and, when the NANO has it, <flags>_B2B<ch> (the back-to-back requirement, cutflow step
'backToBack'); such a NANO holds only back-to-back jets, so another channel's or level's event has none for ch.
"""
import awkward as ak

from . import eec as eecTools
from .expr import Expr, asBool

LEVELS = {'reco': dict(flags='Selection', prefix='', collection='Reco', met='PuppiMET'),
          'gen': dict(flags='GenSelection', prefix='Gen', collection='Gen', met='GenMET')}


class RegionError(ValueError):
    pass


class Region:
    def __init__(self, name, spec, variables, jetTables):
        self.name = name
        unknown = set(spec) - {'level', 'channel', 'cuts', 'weights'}
        if unknown:
            raise RegionError('region %s: unknown keys %s' % (name, sorted(unknown)))
        self.level = spec['level']
        if self.level not in LEVELS:
            raise RegionError('region %s: level must be reco or gen' % name)
        self.channel = spec['channel']
        self.jetTable = jetTables[self.level]
        self.cuts = [Expr(c, variables) for c in spec.get('cuts', [])]
        for c in self.cuts:
            if c.level == 'eec':
                raise RegionError('region %s: cut %r is per EEC entry; use the histogram cuts' % (name, c.text))
        self.weights = [Expr(w, variables) for w in spec.get('weights', [])]
        for w in self.weights:
            if w.level != 'event':
                raise RegionError('region %s: weight %r is not event-level' % (name, w.text))

    def select(self, events, eventWeight):
        """Applies the cuts; returns (View, cutflow {cut: {'n', 'sumw', 'jets'}}: 'channel', then 'backToBack' if
        the NANO has it, then the cuts)."""
        L = LEVELS[self.level]
        flags = events[L['flags']]
        sel = asBool(flags[self.channel])
        view = View(self, events[sel], eventWeight[sel])
        for w in self.weights:
            view.weight = view.weight * w(view.namespace())
        flow = {'channel': view.count()}
        if 'B2B' + self.channel in flags.fields:
            view = view.keepEvents(asBool(view.events[L['flags']]['B2B' + self.channel]))
            flow['backToBack'] = view.count()
        for c in self.cuts:
            m = asBool(c(view.namespace()))
            if c.level == 'event':
                view = view.keepEvents(m)
            elif c.level == 'lepton':
                view = view.keepEvents(ak.all(m, axis=1))
            else:
                view = view.keepJets(m)
            flow[c.text] = view.count()
        return view, flow


class View:
    """Events of a region and the indices of their kept jets in the full jet table."""

    def __init__(self, region, events, weight, jetIdx=None):
        self.region, self.events, self.weight = region, events, weight
        self._L = LEVELS[region.level]
        if jetIdx is None:
            jets = events[region.jetTable]
            idx = ak.local_index(jets.pt)
            b2bName, vetoName = 'b2b' + region.channel, 'veto' + region.channel
            if b2bName in jets.fields:
                jetIdx = idx[jets[b2bName]]
            else:
                jetIdx = idx[~jets[vetoName]] if vetoName in jets.fields else idx
        self.jetIdx = jetIdx
        self._eec = {}

    def keepEvents(self, mask):
        return View(self.region, self.events[mask], self.weight[mask], self.jetIdx[mask])

    def keepJets(self, mask):
        """mask is aligned with the currently kept jets."""
        # awkward accepts a shorter jagged mask silently, so alignment is checked explicitly.
        if not ak.all(ak.num(mask) == ak.num(self.jetIdx)):
            raise ValueError('jet mask not aligned with the kept jets')
        return View(self.region, self.events, self.weight, self.jetIdx[mask])

    def count(self):
        return {'n': int(len(self.weight)), 'sumw': float(ak.sum(self.weight)), 'jets': int(ak.sum(ak.num(self.jetIdx)))}

    def entries(self, observable):
        """([event][jet][entry] entries, [event][jet] per-jet table) of an EEC observable for the kept jets."""
        if observable not in self._eec:
            nested = eecTools.entriesByJet(self.events, self._L['collection'], observable)
            perJet = self.events[self._L['collection'] + observable]
            self._eec[observable] = (nested[self.jetIdx], perJet[self.jetIdx])
        return self._eec[observable]

    def namespace(self, observable=None):
        ev, ch, p = self.events, self.region.channel, self._L['prefix']
        ns = {'event': ev, 'jets': ev[self.region.jetTable][self.jetIdx], 'met': ev[self._L['met']]}
        if p + ch + 'Boson' in ev.fields:
            ns['boson'] = ak.firsts(ev[p + ch + 'Boson'])
        if p + ch + 'Leptons' in ev.fields:
            ns['leptons'] = ev[p + ch + 'Leptons']
        if observable is not None:
            ns['eec'] = self.entries(observable)[0]
        return ns
