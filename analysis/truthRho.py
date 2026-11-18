"""Truth spin-density matrix of LHE vector bosons (bvana/spin.py), per boson, decay mode and V pT bin.

Input: NANO files with LHEPart (e.g. simulation/configs/lheNano_cfg.py, every event, no selection).
    python3 truthRho.py lhe1.root [lhe2.root ...] -o rho.json [--absy-max 0.5] [--pt-edges 0 100 125 ...]
Fermion = the decay product with pdgId > 0. Mass windows: Z 66-116 GeV, W 60-100 GeV (arXiv:2610.38688 Sec. IV.2).
--both-in-window: in ZZ -> 2l2q the leptonic and hadronic Z agree only when both bosons are on shell (2026-11-17).
"""
import argparse
import json

import awkward as ak
import numpy as np
import uproot

from bvana import spin

PT_EDGES = [0, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 600, 800, 1e9]
WINDOWS = {23: (66.0, 116.0), 24: (60.0, 100.0)}


def decays(P):
    """Flat numpy arrays, one entry per LHE V -> f fbar (exactly two status-1 daughters, one with pdgId > 0): boson
    |pdgId|, hadronic flag, V and fermion kinematics, event weight."""
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
            'fphi': flat(P.LHEPart_phi[fi]), 'fpdg': flat(pdg[fi]).astype(int),
            'w': flat(ak.broadcast_arrays(w, fi)[0]),
            'allVInWindow': flat(ak.broadcast_arrays(allVInWindow(P), fi)[0]).astype(bool)}


def allVInWindow(P):
    """Per event: every LHE W/Z (status 2) lies in its mass window."""
    st, pdg, m = P.LHEPart_status, abs(P.LHEPart_pdgId), P.LHEPart_mass
    isV = (st == 2) & ((pdg == 23) | (pdg == 24))
    inWin = ((pdg == 23) & (m > WINDOWS[23][0]) & (m < WINDOWS[23][1])) | ((pdg == 24) & (m > WINDOWS[24][0]) & (m < WINDOWS[24][1]))
    return ak.all(inWin | ~isV, axis=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('-o', '--output', required=True)
    ap.add_argument('--absy-max', type=float, default=None, help='|y_V| cut (paper: 0.5); default none')
    ap.add_argument('--pt-edges', type=float, nargs='+', default=PT_EDGES)
    ap.add_argument('--sin2', type=float, default=0.22263,
                    help='generator sin^2 theta_W for the Z couplings; default: Powheg ZZ/WZ, 1 - mW^2/mZ^2 with '
                         'mW = 80.399, mZ = 91.1876 (smcouplings.f). MadGraph DY (sm-ckm_no_b_mass): 0.23154')
    ap.add_argument('--both-in-window', action='store_true',
                    help='require every LHE W/Z of the event in its window (diboson lep/had consistency: otherwise the '
                         'partner populations differ)')
    a = ap.parse_args()
    parts = []
    for f in a.files:
        t = uproot.open(f)['Events']
        parts.append(decays(t.arrays(filter_name=['LHEPart_*', 'genWeight', 'Generator_weight'])))
    D = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    lo = np.where(D['bos'] == 23, WINDOWS[23][0], WINDOWS[24][0])
    hi = np.where(D['bos'] == 23, WINDOWS[23][1], WINDOWS[24][1])
    ok = (D['Vm'] > lo) & (D['Vm'] < hi)
    pz, E = D['Vpt'] * np.sinh(D['Veta']), np.sqrt((D['Vpt'] * np.cosh(D['Veta'])) ** 2 + D['Vm'] ** 2)
    y = 0.5 * np.log((E + pz) / (E - pz))
    if a.both_in_window:
        ok &= D['allVInWindow']
    if a.absy_max is not None:
        ok &= np.abs(y) < a.absy_max
    th, ph = spin.helicityAngles((D['Vpt'], D['Veta'], D['Vphi'], D['Vm']),
                                 (D['fpt'], D['feta'], D['fphi'], np.zeros_like(D['fpt'])))
    pMinus = np.array([(1 + spin.asymmetryParameter(p, b, a.sin2)) / 2 for p, b in zip(D['fpdg'], D['bos'])])
    out = []
    edges = a.pt_edges
    for bos in (23, 24):
        for had in (False, True):
            for k in range(len(edges) - 1):
                s = ok & (D['bos'] == bos) & (D['had'] == had) & (D['Vpt'] >= edges[k]) & (D['Vpt'] < edges[k + 1])
                if s.sum() < 50:
                    continue
                r, cov = spin.extract(th[s], ph[s], pMinus[s], D['w'][s])
                out.append({'boson': int(bos), 'mode': 'had' if had else 'lep', 'ptLo': edges[k], 'ptHi': edges[k + 1],
                            'n': int(s.sum()), 'params': dict(zip(spin.PARAMS, r.tolist())),
                            'errors': dict(zip(spin.PARAMS, np.sqrt(np.diag(cov)).tolist())), 'cov': cov.tolist()})
                e = np.sqrt(np.diag(cov))
                print('%s %s pT %5.0f-%-6.0f n %7d  rho00 %.4f +- %.4f  rho++-rho-- %+.4f +- %.4f  Re rho+- %+.4f +- %.4f'
                      % ('Z' if bos == 23 else 'W', out[-1]['mode'], edges[k], min(edges[k + 1], 9999), s.sum(),
                         r[1], e[1], r[0] - r[2], np.sqrt(cov[0, 0] + cov[2, 2] - 2 * cov[0, 2]), r[5], e[5]))
    json.dump({'files': a.files, 'absyMax': a.absy_max, 'sin2': a.sin2, 'bothInWindow': a.both_in_window, 'convention': spin.__doc__, 'bins': out}, open(a.output, 'w'),
              indent=1)


if __name__ == '__main__':
    main()
