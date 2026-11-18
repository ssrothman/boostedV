"""Jet-axis study for one-point polarimetry: per axis, the distance to the truth W/Z and the energy-weighted rest-frame
E1C moments of arXiv:2610.38688 Eq. D5, nominal and with the signal reweighted to pure longitudinal or transverse
bosons by the LHE quark decay angle (polar angle only, symmetrised in q <-> qbar).

Input: ZX_test NANOs with the axis columns, the E1CLab<axis> tables and LHEPart (signal, e.g. ZZto2L2Q).
    python3 axisStudy.py nano*.root --rho-json rho.json [--level Reco|Gen] [--pt-min 300] -o axes.md
Jets: matched to a truth boson (axisTruthStatus 0) in its mass window (truthRho.WINDOWS). Boost mass: the truth boson mass, so only the axis differs.
"""
import argparse
import json

import awkward as ak
import numpy as np
import uproot

import truthRho
from bvana import eec, frames, spin

AXES = ['jet', 'axisSoftDrop', 'axisSoftDropB1', 'axisSoftDropZ005', 'axisTrim', 'axisWtaCA', 'axisWtaKT', 'axisRecoil',
        'axisTruth']


def obsName(axis):
    return 'E1CLab' if axis == 'jet' else 'E1CLab' + axis[len('axis'):]


def load(files, level):
    J, out = level + 'Jet', []
    for f in files:
        t = uproot.open(f)['Events']
        names = [J + '_', 'n' + J, 'LHEPart_', 'genWeight'] + [level + obsName(a) for a in AXES]
        arr = t.arrays(filter_name=[n + '*' for n in names])
        z = lambda pre: ak.zip({k[len(pre):]: arr[k] for k in arr.fields if k.startswith(pre)})
        ev = {J: z(J + '_'), 'LHEPart': z('LHEPart_'), 'genWeight': arr['genWeight']}
        for a in AXES:
            o = level + obsName(a)
            ev[o], ev[o + 'Entries'] = z(o + '_'), z(o + 'Entries_')
        out.append(ak.zip(ev, depth_limit=1))
    return ak.concatenate(out)


def lheQuarkAngles(ev, jets):
    """cos(theta) of the LHE hadronic V's quark (pdgId > 0) in the V helicity frame, for the LHE V nearest each jet's
    truth axis (NaN if none within 0.4); and the pMinus of that quark."""
    P = ev.LHEPart
    pdg, st, mo = P.pdgId, P.status, P.firstMotherIdx
    safe = ak.where(mo >= 0, mo, 0)
    isQ = (st == 1) & (pdg > 0) & (pdg <= 6) & (mo >= 0) & (st[safe] == 2) & ((abs(pdg[safe]) == 23) | (abs(pdg[safe]) == 24))
    q = ak.local_index(pdg)[isQ]
    v = mo[q]
    jt, qq = ak.unzip(ak.cartesian([ak.zip({'eta': jets.axisTruthEta, 'phi': jets.axisTruthPhi}),
                                    ak.zip({'eta': P.eta[v], 'phi': P.phi[v], 'i': ak.local_index(q)})], nested=True))
    dR = np.sqrt((jt.eta - qq.eta) ** 2 + np.angle(np.exp(1j * (jt.phi - qq.phi))) ** 2)
    best = ak.argmin(dR, axis=-1, keepdims=True)
    qq = qq.i
    ok = ak.fill_none(ak.firsts(dR[best], axis=-1), 99) < 0.4
    qi = ak.fill_none(ak.firsts(qq[best], axis=-1), 0)
    vv, qq_ = v[qi], q[qi]
    flat = lambda x: ak.to_numpy(ak.flatten(x)).astype(float)
    th, _ = spin.helicityAngles((flat(P.pt[vv]), flat(P.eta[vv]), flat(P.phi[vv]), flat(P.mass[vv])),
                                (flat(P.pt[qq_]), flat(P.eta[qq_]), flat(P.phi[qq_]), 0 * flat(P.pt[qq_])))
    c = np.where(flat(ok) > 0, np.cos(th), np.nan)
    pm = np.array([(1 + spin.asymmetryParameter(p, b, 0.22263)) / 2 for p, b in zip(flat(pdg[qq_]), flat(abs(pdg[vv])))])
    return c, np.where(flat(ok) > 0, pm, np.nan), flat(abs(pdg[vv])), flat(P.pt[vv])


def moments(thetaRest, phiRest):
    c, s = np.cos(thetaRest), np.sin(thetaRest)
    return {'P2': (3 * c * c - 1) / 2, 's2cos2phi': s * s * np.cos(2 * phiRest), 'sin2cosphi': 2 * s * c * np.cos(phiRest),
            'cos': c}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--level', default='Reco')
    ap.add_argument('--pt-min', type=float, default=0.0)
    ap.add_argument('-o', '--output', required=True)
    ap.add_argument('--rho-json', required=True, help='truthRho.py output for the same sample (unselected LHE)')
    a = ap.parse_args()
    ev = load(a.files, a.level)
    J = a.level + 'Jet'
    keep = (ev[J].axisTruthStatus == 0) & (ev[J].pt > a.pt_min)
    jets = ev[J][keep]
    cq, pm, bos, vpt = lheQuarkAngles(ev, jets)
    good = ~np.isnan(cq)
    wEv = ak.to_numpy(ak.flatten(ak.broadcast_arrays(ev.genWeight, jets.pt)[0])).astype(float)
    # Reweighting to pure L or T: f_L,T(c) / f_true(c), with rho00 of the unselected truth (truthRho.py) in the LHE V's
    # pT bin; the jet acceptance multiplies both and cancels. f is the polar distribution of a massless fermion pair.
    truth = [b for b in json.load(open(a.rho_json))['bins'] if b['mode'] == 'had']
    rho00 = np.full(len(cq), np.nan)
    for b in truth:
        sel = (bos == b['boson']) & (vpt >= b['ptLo']) & (vpt < b['ptHi'])
        rho00[sel] = b['params']['rho_00']
    good &= ~np.isnan(rho00)
    # Same boson definition as the truth rho (truthRho.WINDOWS): low-mass gamma* -> qq (Powheg mllmin 4 GeV) would be
    # boosted with gamma ~ 100 and dominate the rest-frame energy weights.
    mTruth = ak.to_numpy(ak.flatten(jets.axisTruthMass)).astype(float)
    lo = np.where(bos == 24, truthRho.WINDOWS[24][0], truthRho.WINDOWS[23][0])
    hi = np.where(bos == 24, truthRho.WINDOWS[24][1], truthRho.WINDOWS[23][1])
    good &= (mTruth > lo) & (mTruth < hi)
    c0, r0 = np.nan_to_num(cq), np.nan_to_num(rho00)
    f = (1 - r0) * 3 / 8 * (1 + c0 * c0) + r0 * 3 / 4 * (1 - c0 * c0)
    wL = np.where(good, 3 / 4 * (1 - c0 ** 2) / f, 0.0)
    wT = np.where(good, 3 / 8 * (1 + c0 ** 2) / f, 0.0)
    nJets = int(good.sum())
    lines = ['# Axis study (%s jets, pT > %.0f GeV, truth-matched with LHE match: %d jets; truth rho00 from %s)'
             % (a.level, a.pt_min, nJets, a.rho_json), '',
             '| axis | median dR(truth) | 90% dR | <P2> nom | <P2> L | <P2> T | <P2> T - L | <s2 cos2phi> nom | <sin2 cosphi> nom | <cos> nom |',
             '|---|---|---|---|---|---|---|---|---|---|']
    M = jets.axisTruthMass
    sensBy = {}
    for ax in AXES:
        o = a.level + obsName(ax)
        nested = eec.entriesByJet(ev, a.level, obsName(ax), check=True)[keep]
        perJet = ev[o][keep]
        rf = frames.addRestFrame(nested, perJet, jets, ax, M)
        eta, phi = (jets.eta, jets.phi) if ax == 'jet' else (jets[ax + 'Eta'], jets[ax + 'Phi'])
        dR = np.hypot(ak.to_numpy(ak.flatten(eta - jets.axisTruthEta)),
                      np.angle(np.exp(1j * ak.to_numpy(ak.flatten(phi - jets.axisTruthPhi)))))
        e = rf.ERest
        flatE = lambda x: ak.to_numpy(ak.flatten(x, axis=None)).astype(float)
        jetW = lambda w: flatE(ak.broadcast_arrays(ak.unflatten(w, ak.num(jets.pt)), e)[0])
        f_, ee = moments(flatE(rf.thetaRest), flatE(rf.phiRest)), flatE(e)
        # Per-jet sums N_j = sum e f, D_j = sum e; ratio-of-sums R = sum w N / sum w D with delta-method errors (jets
        # independent; entries of one jet are correlated, which the per-jet sums keep).
        counts = ak.to_numpy(ak.flatten(ak.num(e, axis=2)))
        jetOf = np.repeat(np.arange(len(counts)), counts)
        Dj = np.bincount(jetOf, weights=ee, minlength=len(counts))
        Nj = {k: np.bincount(jetOf, weights=ee * v, minlength=len(counts)) for k, v in f_.items()}
        res, infl = {}, {}
        for name, w in (('nom', wEv * good), ('L', wEv * wL), ('T', wEv * wT)):
            sD = np.sum(w * Dj)
            res[name] = {k: np.sum(w * N) / sD for k, N in Nj.items()}
            infl[name] = {k: w * (N - res[name][k] * Dj) / sD for k, N in Nj.items()}
        err = lambda x: np.sqrt(np.sum(x ** 2))
        sens = res['T']['P2'] - res['L']['P2']
        lines.append('| %s | %.4f | %.4f | %.4f ± %.4f | %.4f | %.4f | %.4f ± %.4f | %.4f | %.4f | %.4f |' % (
            ax, np.median(dR[good]), np.quantile(dR[good], 0.9), res['nom']['P2'], err(infl['nom']['P2']),
            res['L']['P2'], res['T']['P2'], sens, err(infl['T']['P2'] - infl['L']['P2']),
            res['nom']['s2cos2phi'], res['nom']['sin2cosphi'], res['nom']['cos']))
        sensBy[ax] = (sens, infl['T']['P2'] - infl['L']['P2'])
    # Same jets for every axis, so the per-jet influences give the error of a difference including the correlation.
    lines += ['', '| axis | (T - L) - (T - L)[jet] | (T - L) - (T - L)[axisTruth] |', '|---|---|---|']
    for ax, (s, i) in sensBy.items():
        lines.append('| %s | %s |' % (ax, ' | '.join('%+.4f ± %.4f' % (s - sensBy[r][0], err(i - sensBy[r][1]))
                                                      for r in ('jet', 'axisTruth'))))
    open(a.output, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
