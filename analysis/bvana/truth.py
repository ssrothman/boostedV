"""Truth match of jets to the NANO GenPart record, with the rules of the production truth axis
(JetSetup `TruthAxis.h`, NANO.md `axisTruth`): the nearest hadronic gamma/Z/W/H within dRMax, else the nearest outgoing
hard-process parton. Status: 0 boson, 1 quark from a boson decay, 3 other hard-process parton, 2 none."""
import awkward as ak
import numpy as np

IS_HARD_PROCESS, FROM_HARD_PROCESS = 7, 8          # GenPart statusFlags bits
NONE, BOSON, DECAY_QUARK, PARTON = 2, 0, 1, 3
COLUMNS = ('truthPt', 'truthEta', 'truthPhi', 'truthMass', 'truthPdgId', 'truthStatus')


def candidates(gen):
    """GenPart fields plus `truthStatus` per particle ([event][particle]); NONE for non-candidates."""
    counts = ak.to_numpy(ak.num(gen.pdgId))
    start = np.cumsum(counts) - counts
    pdg = ak.to_numpy(ak.flatten(gen.pdgId)).astype(np.int64)
    status = ak.to_numpy(ak.flatten(gen.status))
    flags = ak.to_numpy(ak.flatten(gen.statusFlags)).astype(np.int64)
    mother = ak.to_numpy(ak.flatten(gen.genPartIdxMother)).astype(np.int64)
    n = len(pdg)
    hasMother = mother >= 0
    gm = np.where(hasMother, mother + np.repeat(start, counts), 0)
    a = np.abs(pdg)
    qg = ((a >= 1) & (a <= 6)) | (a == 21)
    sameAsMother = hasMother & (pdg == pdg[gm])
    hasSameDaughter = np.bincount(gm[sameAsMother], minlength=n) > 0
    hasQGDaughter = np.bincount(gm[hasMother & qg], minlength=n) > 0
    isBoson = (a >= 22) & (a <= 25)
    hadronic = isBoson & ~((a == 22) & ((flags >> FROM_HARD_PROCESS) & 1 == 0)) & ~hasSameDaughter & hasQGDaughter
    motherBoson = hasMother & (np.abs(pdg[gm]) >= 22) & (np.abs(pdg[gm]) <= 25)
    parton = (((flags >> IS_HARD_PROCESS) & 1) == 1) & (status != 21) & (((a >= 1) & (a <= 5)) | (a == 21))
    st = np.full(n, NONE, dtype=np.int64)
    st[parton] = np.where(motherBoson[parton], DECAY_QUARK, PARTON)
    st[hadronic] = BOSON
    return ak.with_field(gen, ak.unflatten(st, counts), 'truthStatus')


def truthColumns(jets, gen, dRMax):
    """{truthPt, truthEta, truthPhi, truthMass, truthPdgId, truthStatus} per jet ([event][jet]); NaN and status 2
    without a match."""
    c = candidates(gen)
    pairs = ak.cartesian([jets, c], axis=1, nested=True)      # [event][jet][particle]
    p = pairs['1']
    dR = pairs['0'].delta_r(p)
    fields = {'truthPt': 'pt', 'truthEta': 'eta', 'truthPhi': 'phi', 'truthMass': 'mass', 'truthPdgId': 'pdgId',
              'truthStatus': 'truthStatus'}
    out = {k: ak.full_like(jets.pt, np.nan, dtype=np.float64) for k in fields}
    found = ak.zeros_like(jets.pt, dtype=bool)
    # Bosons take precedence over partons at any distance.
    for want in (lambda s: s == BOSON, lambda s: (s == DECAY_QUARK) | (s == PARTON)):
        d = ak.where(want(p.truthStatus) & (dR < dRMax), dR, np.inf)
        best = ak.argmin(d, axis=2, keepdims=True)
        take = ~found & ak.fill_none(ak.firsts(d[best], axis=2) < np.inf, False)
        for k, f in fields.items():
            v = ak.values_astype(ak.fill_none(ak.firsts(p[f][best], axis=2), np.nan), np.float64)
            out[k] = ak.where(take, v, out[k])
        found = found | take
    out['truthStatus'] = ak.values_astype(ak.where(found, out['truthStatus'], NONE), np.int64)
    return out
