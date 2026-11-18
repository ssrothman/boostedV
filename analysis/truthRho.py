"""Truth spin-density matrix of LHE vector bosons (bvana/spin.py), per boson, decay mode and V pT bin.

Input: NANO files with LHEPart (e.g. simulation/configs/lheNano_cfg.py, every event, no selection).
    python3 truthRho.py lhe1.root [lhe2.root ...] -o rho.json [--window leptonic] [--absy-max 0.5] [--pt-edges ...]
Fermion = the decay product with pdgId > 0. --window:
  self      the boson itself in its window (Z 66-116, W 60-100 GeV; arXiv:2610.38688 Sec. IV.2)
  both      every W/Z of the event in that window (the leptonic and hadronic Z of ZZ -> 2l2q agree only then)
  leptonic  every leptonically decaying boson of the event in the selection's dilepton window (ZX_test: 61.1876-121.1876),
            nothing on the hadronic one: the truth of the measurement
  none
--joint: diagonal of the joint density matrix of events with one leptonic and one hadronic boson, in bins of the
hadronic boson pT (same --window).
"""
import argparse
import json

import awkward as ak
import numpy as np
import uproot

from bvana import spin

PT_EDGES = [0, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 600, 800, 1e9]
WINDOWS = {23: (66.0, 116.0), 24: (60.0, 100.0)}
LEPTONIC_WINDOWS = {23: (61.1876, 121.1876), 24: (60.0, 100.0)}


def decays(P):
    """Flat numpy arrays, one entry per LHE V -> f fbar (exactly two status-1 daughters, one with pdgId > 0): boson
    |pdgId|, hadronic flag, V and fermion kinematics, event weight, event index."""
    pdg, st, mo = P.LHEPart_pdgId, P.LHEPart_status, P.LHEPart_firstMotherIdx
    safe = ak.where(mo >= 0, mo, 0)
    parentIsV = (mo >= 0) & (st[safe] == 2) & ((abs(pdg[safe]) == 23) | (abs(pdg[safe]) == 24))
    f = (st == 1) & (pdg > 0) & parentIsV
    a, b = ak.unzip(ak.cartesian([mo[f], mo], nested=True))
    _, final = ak.unzip(ak.cartesian([mo[f], st == 1], nested=True))
    nDau = ak.sum((a == b) & final, axis=-1)
    fi = ak.local_index(pdg)[f][nDau == 2]
    v = mo[fi]
    w = P['genWeight'] if 'genWeight' in P.fields else P['Generator_weight']
    flat = lambda x: ak.to_numpy(ak.flatten(x)).astype(float)
    return {'bos': flat(abs(pdg[v])), 'had': flat(abs(pdg[fi]) <= 6).astype(bool),
            'Vpt': flat(P.LHEPart_pt[v]), 'Veta': flat(P.LHEPart_eta[v]), 'Vphi': flat(P.LHEPart_phi[v]),
            'Vm': flat(P.LHEPart_mass[v]), 'fpt': flat(P.LHEPart_pt[fi]), 'feta': flat(P.LHEPart_eta[fi]),
            'fphi': flat(P.LHEPart_phi[fi]), 'fm': np.maximum(flat(P.LHEPart_mass[fi]), 0), 'fpdg': flat(pdg[fi]).astype(int),
            'w': flat(ak.broadcast_arrays(w, fi)[0]),
            'evt': flat(ak.broadcast_arrays(np.arange(len(P)), fi)[0]).astype(np.int64)}


def inWindow(bos, m, windows):
    lo = np.where(bos == 23, windows[23][0], windows[24][0])
    hi = np.where(bos == 23, windows[23][1], windows[24][1])
    return (m > lo) & (m < hi)


def allInEvent(evt, flag):
    """Per decay: flag holds for every decay of its event (evt sorted)."""
    bad = np.zeros(evt.max() + 1 if len(evt) else 0, bool)
    bad[evt[~flag]] = True
    return ~bad[evt]


def load(files, sin2):
    """Decays of all files with helicity angles, analysing power and per-decay window flags."""
    parts, offset = [], 0
    for f in files:
        t = uproot.open(f)['Events']
        p = decays(t.arrays(filter_name=['LHEPart_*', 'genWeight', 'Generator_weight']))
        p['evt'] += offset
        offset += t.num_entries
        parts.append(p)
    D = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    # The LHE fermion mass, not zero: a massless boost distorts the angles of light quarks from bosons of a few GeV.
    D['theta'], D['phi'] = spin.helicityAngles((D['Vpt'], D['Veta'], D['Vphi'], D['Vm']),
                                               (D['fpt'], D['feta'], D['fphi'], D['fm']))
    D['aF'] = np.array([spin.asymmetryParameter(p, b, sin2) for p, b in zip(D['fpdg'], D['bos'])])
    pz, E = D['Vpt'] * np.sinh(D['Veta']), np.sqrt((D['Vpt'] * np.cosh(D['Veta'])) ** 2 + D['Vm'] ** 2)
    D['y'] = 0.5 * np.log((E + pz) / (E - pz))
    D['inWin'] = inWindow(D['bos'], D['Vm'], WINDOWS)
    D['allInWin'] = allInEvent(D['evt'], D['inWin'])
    D['lepInWin'] = allInEvent(D['evt'], D['had'] | inWindow(D['bos'], D['Vm'], LEPTONIC_WINDOWS))
    return D


def selection(D, window, absyMax=None):
    ok = {'self': D['inWin'], 'both': D['allInWin'], 'leptonic': D['lepInWin'],
          'none': np.ones_like(D['inWin'])}[window].copy()
    if absyMax is not None:
        ok &= np.abs(D['y']) < absyMax
    return ok


def joint(D, ok, edges):
    """Joint helicity diagonal, (l_had, l_lep) in (+1, 0, -1) order, per hadronic-V pT bin, for events with exactly one
    leptonic and one hadronic boson, both passing ok."""
    evts, counts = np.unique(D['evt'][ok], return_counts=True)
    two = np.isin(D['evt'], evts[counts == 2]) & ok
    had, lep = np.flatnonzero(two & D['had']), np.flatnonzero(two & ~D['had'])
    pair = np.intersect1d(D['evt'][had], D['evt'][lep])
    had, lep = had[np.isin(D['evt'][had], pair)], lep[np.isin(D['evt'][lep], pair)]   # evt sorted: aligned
    fh, fl = spin.helicityWeights(D['theta'][had], D['aF'][had]), spin.helicityWeights(D['theta'][lep], D['aF'][lep])
    out = []
    for bos in (23, 24):
        for k in range(len(edges) - 1):
            s = (D['bos'][had] == bos) & (D['Vpt'][had] >= edges[k]) & (D['Vpt'][had] < edges[k + 1])
            if s.sum() < 50:
                continue
            P, cov = spin.jointDiagonal(fh[:, s], fl[:, s], D['w'][had][s])
            out.append({'hadBoson': int(bos), 'lepBoson': [int(b) for b in np.unique(D['bos'][lep][s])],
                        'ptLo': edges[k], 'ptHi': edges[k + 1], 'n': int(s.sum()), 'P': P.tolist(),
                        'errors': np.sqrt(np.diag(cov)).reshape(3, 3).tolist(), 'cov': cov.tolist()})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('-o', '--output', required=True)
    ap.add_argument('--absy-max', type=float, default=None, help='|y_V| cut (paper: 0.5); default none')
    ap.add_argument('--pt-edges', type=float, nargs='+', default=PT_EDGES)
    ap.add_argument('--sin2', type=float, default=0.22263,
                    help='generator sin^2 theta_W for the Z couplings; default: Powheg ZZ/WZ, 1 - mW^2/mZ^2 with '
                         'mW = 80.399, mZ = 91.1876 (smcouplings.f). MadGraph DY (sm-ckm_no_b_mass): 0.23154')
    ap.add_argument('--window', choices=['self', 'both', 'leptonic', 'none'], default='self')
    ap.add_argument('--joint', action='store_true', help='also the joint helicity diagonal (see above)')
    a = ap.parse_args()
    D = load(a.files, a.sin2)
    ok = selection(D, a.window, a.absy_max)
    pMinus = (1 + D['aF']) / 2
    out = []
    edges = a.pt_edges
    for bos in (23, 24):
        for had in (False, True):
            for k in range(len(edges) - 1):
                s = ok & (D['bos'] == bos) & (D['had'] == had) & (D['Vpt'] >= edges[k]) & (D['Vpt'] < edges[k + 1])
                if s.sum() < 50:
                    continue
                r, cov = spin.extract(D['theta'][s], D['phi'][s], pMinus[s], D['w'][s])
                out.append({'boson': int(bos), 'mode': 'had' if had else 'lep', 'ptLo': edges[k], 'ptHi': edges[k + 1],
                            'n': int(s.sum()), 'params': dict(zip(spin.PARAMS, r.tolist())),
                            'errors': dict(zip(spin.PARAMS, np.sqrt(np.diag(cov)).tolist())), 'cov': cov.tolist()})
                e = np.sqrt(np.diag(cov))
                print('%s %s pT %5.0f-%-6.0f n %7d  rho00 %.4f +- %.4f  rho++-rho-- %+.4f +- %.4f  Re rho+- %+.4f +- %.4f'
                      % ('Z' if bos == 23 else 'W', out[-1]['mode'], edges[k], min(edges[k + 1], 9999), s.sum(),
                         r[1], e[1], r[0] - r[2], np.sqrt(cov[0, 0] + cov[2, 2] - 2 * cov[0, 2]), r[5], e[5]))
    res = {'files': a.files, 'absyMax': a.absy_max, 'sin2': a.sin2, 'window': a.window, 'convention': spin.__doc__,
           'bins': out}
    if a.joint:
        res['joint'] = joint(D, ok, edges)
    json.dump(res, open(a.output, 'w'), indent=1)


if __name__ == '__main__':
    main()
