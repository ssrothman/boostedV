#!/usr/bin/env python3
"""Where is the hadronic boson of VV events whose selected jet is not the boson? (E2C_NEXT_QUESTIONS.md Q4,
follow-up 1)

  python3 vvBosonLocation.py nano*.root -o out.md [--label WZ]

Input: NANO files of WZ/ZZ -> 2l2q (jet-free productions: Selection, <ch>Boson, <ch>Leptons, RecoJet with b2b<ch>,
AK4Jet, GenPart). Events: Selection_<ch> for Zmumu or Zee, with the sensitivity baseline on the selected jet and Z
(jet pT > 200, |eta| < 2.0, Z pT > 200, muons medium ID). Per event: the selected jet's truth status
(bvana/truth.py, dRMax 0.8) and the hadronic W/Z of GenPart (status 0 candidate; its two hardest quark daughters).
Writes, per jet truth status, genWeight-weighted fractions and quantiles of the boson pT, |eta|, Delta R to the jet,
|Delta phi| to the Z(ll), the q-qbar Delta R, and the fraction whose two quarks each have an AK4 jet within 0.4.
"""
import argparse

import awkward as ak
import numpy as np
import uproot
from coffea.nanoevents.methods import vector

from bvana import truth

ak.behavior.update(vector.behavior)
CHANNELS = ('Zmumu', 'Zee')
STATUS = {0: 'boson', 1: 'boson decay quark', 3: 'other hard parton', 2: 'none'}


def p4(arrs, prefix, extra=()):
    fields = {f: arrs[prefix + f] for f in ('pt', 'eta', 'phi', 'mass')}
    fields.update({f: arrs[prefix + f] for f in extra})
    return ak.zip(fields, with_name='PtEtaPhiMLorentzVector')


def hadronicBoson(gen):
    """Per event: the hardest hadronic W/Z (truth status 0) and its two hardest quark daughters (None if absent)."""
    c = truth.candidates(gen)
    a = abs(c.pdgId)
    isV = (c.truthStatus == truth.BOSON) & ((a == 23) | (a == 24))
    first = ak.argmax(ak.where(isV, c.pt, -1.0), axis=1, keepdims=True)
    hasV = ak.fill_none(ak.firsts(isV[first]), False)
    vIdx = ak.where(hasV, ak.fill_none(ak.firsts(first), -2), -2)    # -2 matches no mother index
    q = c[(c.genPartIdxMother == vIdx) & (a >= 1) & (a <= 6)]
    q = ak.pad_none(q[ak.argsort(q.pt, ascending=False)], 2)
    V = ak.mask(ak.firsts(c[first]), hasV)
    return V, q[:, 0], q[:, 1], hasV


def wquantiles(x, w, qs):
    o = np.argsort(x)
    cw = np.cumsum(w[o]) - 0.5 * w[o]
    return np.interp(np.asarray(qs) * w.sum(), cw, x[o])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--label', default='VV')
    a = ap.parse_args()
    rows = {k: [] for k in ('status', 'w', 'vPt', 'vAbsEta', 'dRjV', 'dPhiZV', 'dRqq', 'ak4Both', 'hasV', 'jetPt',
                            'zPt', 'vqqInJet')}
    branches = None
    for path in a.files:
        t = uproot.open(path)['Events']
        if branches is None:
            keys = set(t.keys())
            branches = [k for k in keys if k.startswith(('Selection_', 'GenPart_', 'AK4Jet_pt', 'AK4Jet_eta', 'AK4Jet_phi',
                                                         'AK4Jet_mass', 'RecoJet_pt', 'RecoJet_eta', 'RecoJet_phi',
                                                         'RecoJet_mass', 'RecoJet_b2b'))
                        or any(k.startswith(ch + p) for ch in CHANNELS for p in ('Boson_', 'Leptons_mediumId'))]
            branches += ['genWeight', 'nGenPart']
        e = t.arrays(branches)
        gen = ak.zip({f: e['GenPart_' + f] for f in ('pt', 'eta', 'phi', 'mass', 'pdgId', 'status', 'statusFlags',
                                                     'genPartIdxMother')}, with_name='PtEtaPhiMLorentzVector')
        jetsAll = p4(e, 'RecoJet_', ['b2b' + ch for ch in CHANNELS])
        ak4 = p4(e, 'AK4Jet_')
        V, q1, q2, hasV = hadronicBoson(gen)
        for ch in CHANNELS:
            sel = e['Selection_' + ch]
            jet = ak.firsts(jetsAll[jetsAll['b2b' + ch]])
            cands = p4(e, ch + 'Boson_')
            Z = ak.firsts(cands[ak.argmax(cands.pt, axis=1, keepdims=True)])   # the selection's candidate
            medium = ak.all(e[ch + 'Leptons_mediumId'], axis=1) if ch + 'Leptons_mediumId' in e.fields else True   # as the tables
            ok = sel & ~ak.is_none(jet) & ~ak.is_none(Z)
            ok = ak.fill_none(ok & (jet.pt > 200) & (abs(jet.eta) < 2.0) & (Z.pt > 200) & medium, False)
            ok = ak.to_numpy(ok)
            if not ok.any():
                continue
            jet_, Z_, V_, q1_, q2_, hasV_ = jet[ok], Z[ok], V[ok], q1[ok], q2[ok], ak.to_numpy(hasV[ok])
            st = truth.truthColumns(ak.singletons(jet_), gen[ok], 0.8)['truthStatus']
            rows['status'].append(ak.to_numpy(ak.firsts(st)))
            rows['w'].append(np.sign(ak.to_numpy(e['genWeight'][ok])))
            rows['hasV'].append(hasV_)
            nan = lambda x: ak.to_numpy(ak.fill_none(x, np.nan)).astype(np.float64)
            rows['vPt'].append(nan(V_.pt))
            rows['vAbsEta'].append(nan(abs(V_.eta)))
            rows['dRjV'].append(nan(jet_.delta_r(V_)))
            rows['dPhiZV'].append(nan(abs(Z_.delta_phi(V_))))
            rows['dRqq'].append(nan(q1_.delta_r(q2_)))
            rows['jetPt'].append(ak.to_numpy(jet_.pt).astype(np.float64))
            rows['zPt'].append(ak.to_numpy(Z_.pt).astype(np.float64))
            rows['vqqInJet'].append(ak.to_numpy(ak.fill_none((jet_.delta_r(q1_) < 0.8) & (jet_.delta_r(q2_) < 0.8),
                                                             False)))
            ak4ok = ak4[ok]
            m1 = ak.fill_none(ak.any(ak4ok.delta_r(q1_) < 0.4, axis=1), False)
            m2 = ak.fill_none(ak.any(ak4ok.delta_r(q2_) < 0.4, axis=1), False)
            rows['ak4Both'].append(ak.to_numpy(m1 & m2))
    r = {k: np.concatenate(v) for k, v in rows.items()}
    lines = ['# Hadronic boson location, %s (%d files)' % (a.label, len(a.files)), '',
             'Selected events at the sensitivity baseline (both channels); weights sign(genWeight). Quantiles 16/50/84%.',
             'AK4 match: both decay quarks have an AK4 jet within 0.4 (the AK4 collection may include the selected AK8',
             'jet\'s area). qq in jet: both quarks within 0.8 of the selected jet.', '',
             '| jet truth | weight share | has hadronic V | V pT [GeV] | V abs eta | dR(jet, V) | abs dphi(Z, V) | '
             'dR(q, q) | f(V pT > 200, abs eta < 2.4, dR(qq) < 0.8) | f(qq in jet) | f(AK4 match) | jet pT / Z pT median |',
             '|---|---|---|---|---|---|---|---|---|---|---|---|']
    W = r['w'].sum()
    for s, name in STATUS.items():
        m = r['status'] == s
        if not m.any():
            continue
        w = r['w'][m]
        mv = m & r['hasV']
        cells = ['%.3f' % (w.sum() / W), '%.3f' % (r['w'][mv].sum() / w.sum())]
        for k in ('vPt', 'vAbsEta', 'dRjV', 'dPhiZV', 'dRqq'):
            g = mv & np.isfinite(r[k])
            cells.append(' / '.join('%.2f' % x for x in wquantiles(r[k][g], r['w'][g], (0.16, 0.5, 0.84)))
                         if g.sum() > 5 else '-')
        ak8able = mv & (r['vPt'] > 200) & (r['vAbsEta'] < 2.4) & (r['dRqq'] < 0.8)
        cells.append('%.3f' % (r['w'][ak8able].sum() / w.sum()))
        cells.append('%.3f' % (r['w'][m & r['vqqInJet']].sum() / w.sum()))
        cells.append('%.3f' % (r['w'][mv & r['ak4Both']].sum() / w.sum()))
        cells.append('%.2f' % wquantiles(r['jetPt'][m] / r['zPt'][m], w, (0.5,))[0])
        lines.append('| %s (%d) | %s |' % (name, m.sum(), ' | '.join(cells)))
    lines.append('')
    with open(a.out, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
