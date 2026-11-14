"""Accessors for the EEC tables (conventions: simulation/NANO.md, "EEC per-jet and entries").

Per jet collection key C (e.g. Reco) and observable O (e.g. E2Cn1):
  events[C + O]             one row per jet of the jet table (E_jet, n, N, nEntries)
  events[C + O + 'Entries'] flat per event, iJet non-decreasing; unbinned columns: coordinates, weight, symfactor
"""
import awkward as ak


def entriesByJet(events, collection, observable, check=True):
    """Entries regrouped as [event][jet][entry], aligned with the jet table; check verifies them against iJet."""
    perJet = events[collection + observable]
    entries = events[collection + observable + 'Entries']
    nested = ak.unflatten(ak.unflatten(ak.flatten(entries), ak.flatten(perJet.nEntries)), ak.num(perJet))
    if check:
        if not ak.all(ak.num(entries) == ak.sum(perJet.nEntries, axis=1)):
            raise ValueError('%s%s: nEntries does not add up to the entries per event' % (collection, observable))
        jetIndex = ak.broadcast_arrays(ak.local_index(nested, axis=1), nested.iJet)[0]
        if not ak.all(ak.flatten(nested.iJet == jetIndex, axis=None)):
            raise ValueError('%s%sEntries: iJet does not match the per-jet nEntries' % (collection, observable))
    return nested


def tupleWeight(entries):
    """weight x symfactor: the full contribution of an unbinned entry (a multiset stands for all its orderings)."""
    return entries.weight * entries.symfactor


def renormalise(entries, perJet, newNorm):
    """Entry weights for another normalisation E' (newNorm per jet): w * (E_jet / E')^(n N)."""
    return entries.weight * (perJet.E_jet / newNorm) ** (perJet.n * perJet.N)


def toEntries(jetValues, nested):
    """Broadcast a per-jet [event][jet] quantity to [event][jet][entry]."""
    return ak.broadcast_arrays(jetValues, nested.weight)[0]
