"""End-to-end checks of eecNano_cfg.py output (run with writeConstituents=1).
Usage: python3 checkEndToEnd.py nano.root hists.root
 (i)   E2C/E3C/E1C entries vs a brute-force numpy computation from the constituent table
 (ii)  sum rule: every jet's weights sum to 1 (Pt weights, sumPt norm, n = 1)
 (iii) aggregator H and C vs a recomputation from the NANO entries and Generator_weight (times ZmumuMuonSF_nominal
       at reco level, if stored), for Zmumu events at each selection level in the histogram file, skipping the jets
       with <jet table>_vetoZmumu (if stored)
"""
import sys
import numpy as np
import uproot

nano = uproot.open(sys.argv[1])
ev = nano['Events'].arrays(library='np')
hists = uproot.open(sys.argv[2])
ok = True


def report(name, cond, detail):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + name + ': ' + detail)


def binIndex(x, edges):
    """Flow-inclusive bin index (0 = underflow) with boost::histogram semantics (upper edge exclusive)."""
    return np.searchsorted(edges, x, side='right')


LOG = np.logspace(-3, 0, 51)
TH = np.linspace(0, np.pi, 21)
PH = np.linspace(-np.pi, np.pi, 21)


def constituents(jetTable, e, j):
    c = jetTable + 'Constituents_'
    sel = ev[c + 'iJet'][e] == j
    return tuple(ev[c + v][e][sel].astype(float) for v in ('pt', 'eta', 'phi', 'E'))


def penc(pt, eta, phi, N):
    w = pt / pt.sum()
    dphi = np.remainder(phi[:, None] - phi[None, :] + np.pi, 2 * np.pi) - np.pi
    D = np.hypot(eta[:, None] - eta[None, :], dphi)
    if N == 2:
        R, W = D, w[:, None] * w[None, :]
    else:
        R = np.maximum(np.maximum(D[:, :, None], D[:, None, :]), D[None, :, :])
        W = w[:, None, None] * w[None, :, None] * w[None, None, :]
    return np.bincount(binIndex(R.ravel(), LOG), weights=W.ravel(), minlength=52)


def e1c(pt, eta, phi, E, jpt, jeta, jphi, jm):
    w = pt / pt.sum()
    p = np.stack([pt * np.cos(phi), pt * np.sin(phi), pt * np.sinh(eta)], axis=1)
    J = np.array([jpt * np.cos(jphi), jpt * np.sin(jphi), jpt * np.sinh(jeta)])
    JE = np.sqrt(J @ J + jm * jm)
    b = J / JE
    g = JE / jm
    bp = p @ b
    # Lorentz boost into the jet rest frame (independent of the library's formula).
    pr = p + ((g - 1) * bp / (b @ b) - g * E)[:, None] * b[None, :]
    z = J / np.linalg.norm(J)
    x = np.array([0, 0, 1.0]) - z[2] * z
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    th = np.arctan2(np.hypot(pr @ x, pr @ y), pr @ z)
    ph = np.arctan2(pr @ y, pr @ x)
    lin = binIndex(th, TH) + 22 * binIndex(ph, PH)
    return np.bincount(lin, weights=w, minlength=22 * 22)


def stored(prefix, e, j, nb):
    sel = ev[prefix + 'Entries_iJet'][e] == j
    return np.bincount(ev[prefix + 'Entries_bin'][e][sel], weights=ev[prefix + 'Entries_weight'][e][sel], minlength=nb)


def singleMigration(d, w, tol=1e-6):
    """True if d is zero, or +x and -x in two bins adjacent along theta or phi with x one particle weight."""
    k = np.nonzero(np.abs(d) > tol)[0]
    if len(k) == 0:
        return True
    if len(k) != 2 or abs(d[k[0]] + d[k[1]]) > tol or np.min(np.abs(w - abs(d[k[0]]))) > tol:
        return False
    (t0, p0), (t1, p1) = [(b % 22, b // 22) for b in k]
    return abs(t0 - t1) + abs(p0 - p1) == 1


MAXM = 250  # E3C brute force needs M^3 doubles
for level in ('Reco', 'Gen'):
    jt = level + 'Jet'
    obs = [level + 'E2C', level + 'E3C', level + 'E1C']
    worst = {k: 0 for k in obs}
    sums = {k: [] for k in obs}
    nj = skipped = 0
    unexplained = {k: 0 for k in obs}
    single = 0
    for e in range(len(ev[jt + '_pt'])):
        for j in range(len(ev[jt + '_pt'][e])):
            pt, eta, phi, E = constituents(jt, e, j)
            if len(pt) > MAXM:
                skipped += 1
                continue
            nj += 1
            ref = [penc(pt, eta, phi, 2), penc(pt, eta, phi, 3),
                   # float64 jet kinematics: in float32 the rest frame of a light, boosted jet is badly conditioned.
                   e1c(pt, eta, phi, E, *(float(ev[jt + v][e][j]) for v in ('_pt', '_eta', '_phi', '_mass')))]
            single += len(pt) < 2
            for k, r in zip(obs, ref):
                s = stored(k, e, j, len(r))
                d = s - r
                if k.endswith('E1C') and not singleMigration(d, pt / pt.sum()):
                    unexplained[k] += 1
                worst[k] = max(worst[k], np.abs(d).sum())
                sums[k].append(s.sum())
    report('%s jets have >= 2 constituents' % level, single == 0, '%d with fewer' % single)
    for k in obs:
        if k.endswith('E1C'):
            # Float-stored inputs may move one particle into an adjacent bin; anything else is a failure.
            report('%s vs brute force' % k, nj >= 20 and unexplained[k] == 0,
                   'jets %d, not explained by a single-particle edge migration %d, max sum|diff| %.2e'
                   % (nj, unexplained[k], worst[k]))
        else:
            # Float-stored inputs can move a tuple across a bin edge; allow 1e-3 of the total weight.
            report('%s vs brute force' % k, nj >= 20 and worst[k] < 1e-3,
                   'jets %d (skipped %d with > %d constituents), max sum|diff| %.2e' % (nj, skipped, MAXM, worst[k]))
        report('%s sum rule' % k, np.allclose(sums[k], 1.0, atol=1e-5), 'min %.6f max %.6f' % (min(sums[k]), max(sums[k])))

# (iii) aggregator recomputation for Zmumu, per selection level present in the histogram file
for level, flag in (('reco', 'Selection_Zmumu'), ('gen', 'GenSelection_Zmumu')):
    if 'Zmumu_%s_eecRecoE2C' % level not in [k.split(';')[0] for k in hists.keys(recursive=False)]:
        continue
    for obs, nb in (('RecoE2C', 52), ('RecoE3C', 52), ('RecoE1C', 484), ('GenE2C', 52)):
        H = np.zeros(nb)
        C = np.zeros((nb, nb))
        sw = 0.0
        veto = ('RecoJet' if obs.startswith('Reco') else 'GenJet') + '_vetoZmumu'
        nVetoed = 0
        for e in np.nonzero(ev[flag])[0]:
            keep = np.ones(len(ev[obs + 'Entries_bin'][e]), bool)
            if veto in ev:
                keep = ~ev[veto][e][ev[obs + 'Entries_iJet'][e]]
                nVetoed += int(ev[veto][e].sum())
            h = np.bincount(ev[obs + 'Entries_bin'][e][keep], weights=ev[obs + 'Entries_weight'][e][keep], minlength=nb)
            w = float(ev['Generator_weight'][e])
            if level == 'reco' and 'ZmumuMuonSF_nominal' in ev:
                w *= float(ev['ZmumuMuonSF_nominal'][e])
            H += w * h
            C += w * w * np.outer(h, h)
            sw += w
        d = hists['Zmumu_%s_eec%s' % (level, obs)]
        hv = d['values'].values(flow=False)
        hc = d['covariance'].values(flow=False)
        scale = max(np.abs(H).max(), 1e-30)
        tag = 'Zmumu[%s] %s aggregator' % (level, obs)
        report(tag + ' H', np.allclose(hv, H, rtol=1e-4, atol=1e-6 * scale), 'max|diff| %.2e (max H %.2e)' % (np.abs(hv - H).max(), scale))
        report(tag + ' C', np.allclose(hc, C, rtol=1e-4, atol=1e-6 * max(np.abs(C).max(), 1e-30)), 'max|diff| %.2e' % np.abs(hc - C).max())
        report(tag + ' sumW', np.isclose(d['sumW'].member('fVal'), sw, rtol=1e-4),
               'aggregator %.6g vs nano %.6g; Zmumu-vetoed jets skipped %d' % (d['sumW'].member('fVal'), sw, nVetoed))
sys.exit(0 if ok else 1)
