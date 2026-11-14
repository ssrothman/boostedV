"""Checks the Unbinned EEC tables of eecNano_cfg.py output against a numpy recomputation from the constituent tables
(run with writeConstituents=1). Supports pENC with N = 2 and E1C (frames lab, jetAxis, jetHelicity, jetCS), with
weight Pt and norm jetPt or sumPt.
Usage: python3 checkUnbinned.py nano.root analysis.yaml [--mutate]
  --mutate perturbs the recomputation (n + 0.1, E1C x axis flipped); every comparison must then FAIL.
Checks per jet collection and observable: E_jet; nEntries and iJet order; every entry (coordinates, weight, symfactor)
as a sorted multiset; constituents charged if chargedOnly.
"""
import sys

import numpy as np
import uproot
import yaml

MUTATE = '--mutate' in sys.argv
nano = uproot.open(sys.argv[1])['Events'].arrays(library='np')
cfg = yaml.safe_load(open(sys.argv[2]))
ok = True


def report(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + name + (': ' + detail if detail else ''))


def p4(pt, eta, phi, E):
    return np.stack([pt * np.cos(phi), pt * np.sin(phi), pt * np.sinh(eta), E], axis=-1)


def boostToRest(p, rest):
    """Particles p (k, 4) into the rest frame of the four-vector rest (4,)."""
    b = rest[:3] / rest[3]
    b2 = b @ b
    g = 1.0 / np.sqrt(1.0 - b2)
    bp = p[:, :3] @ b
    v = p[:, :3] + ((g - 1.0) * bp / b2 - g * p[:, 3])[:, None] * b
    return v


def angles(v, z, x):
    z = z / np.linalg.norm(z)
    x = x - (x @ z) * z
    x = x / np.linalg.norm(x)
    y = np.cross(z, x)
    vx, vy, vz = v @ x, v @ y, v @ z
    return np.arctan2(np.hypot(vx, vy), vz), np.arctan2(vy, vx)


def e1cCoords(frame, cons, jet):
    sgnX = -1.0 if MUTATE else 1.0
    beam = np.array([0.0, 0.0, 1.0])
    jdir = jet[:3]
    if frame == 'lab':
        return angles(cons[:, :3], beam, np.array([sgnX, 0.0, 0.0]))
    if frame == 'jetAxis':
        return angles(cons[:, :3], jdir, sgnX * beam)
    v = boostToRest(cons, jet)
    if frame == 'jetHelicity':
        return angles(v, jdir, sgnX * beam)
    if frame == 'jetCS':
        s = -1.0 if jet[2] < 0 else 1.0
        a = boostToRest(np.array([[0, 0, s, 1.0]]), jet)[0]
        b = boostToRest(np.array([[0, 0, -s, 1.0]]), jet)[0]
        a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
        return angles(v, a - b, sgnX * -(a + b))
    raise ValueError(frame)


def dphi(a, b):
    return (a - b + np.pi) % (2 * np.pi) - np.pi


def expected(spec, cons, jet, Ejet):
    pt = cons[:, 4]
    n = spec['n'] + (0.1 if MUTATE else 0.0)
    w1 = (pt / Ejet) ** n
    if spec['kind'] == 'e1c':
        th, ph = e1cCoords(spec['frame'], cons[:, :4], jet)
        return np.stack([th, ph], 1), w1, np.ones(len(pt))
    i, j = np.triu_indices(len(pt))
    eta, phi = cons[:, 5], cons[:, 6]
    dR = np.hypot(eta[i] - eta[j], dphi(phi[i], phi[j]))
    return dR[:, None], w1[i] * w1[j], np.where(i == j, 1.0, 2.0)


def sortRows(c, w, s):
    order = np.lexsort(tuple(np.round(c[:, k], 6) for k in reversed(range(c.shape[1]))) + (np.round(w, 9),))
    return c[order], w[order], s[order]


for cname, coll in cfg['jets']['collections'].items():
    jt = coll['table']['name']
    ctab = jt + 'Constituents_'
    if ctab + 'pt' not in nano:
        report('%s constituents stored' % cname, False, 'run with writeConstituents=1')
        continue
    if coll['constituentCuts']['chargedOnly']:
        nNeutral = sum(int((c == 0).sum()) for c in nano[ctab + 'charge'])
        report('%s constituents are charged' % cname, nNeutral == 0, '%d neutral' % nNeutral)
    for oname, spec in cfg['observables'].items():
        if spec['output'] != 'Unbinned':
            continue
        tab, ent = cname + oname, cname + oname + 'Entries'
        names = spec['table']['coordNames']
        nJets = nEnt = 0
        bad = {'E_jet': 0, 'nEntries': 0, 'order': 0, 'count': 0, 'coords': 0, 'weight': 0, 'symfactor': 0}
        maxdev = {'coords': 0.0, 'weight': 0.0}
        for e in range(len(nano['n' + jt])):
            jpt, jeta, jphi, jm = (nano[jt + '_' + v][e].astype(float) for v in ('pt', 'eta', 'phi', 'mass'))
            Ejet = nano[tab + '_E_jet'][e]
            iJet = nano[ent + '_iJet'][e]
            if len(Ejet) != len(jpt):
                bad['E_jet'] += 1
                continue
            bad['order'] += int(np.any(np.diff(iJet) < 0))
            cJet = nano[ctab + 'iJet'][e]
            cons = np.stack([nano[ctab + v][e].astype(float) for v in ('pt', 'eta', 'phi', 'E')], 1)
            cons = np.column_stack([p4(cons[:, 0], cons[:, 1], cons[:, 2], cons[:, 3]), cons[:, 0], cons[:, 1], cons[:, 2]])
            for k in range(len(jpt)):
                nJets += 1
                ck = cons[cJet == k]
                ref = jpt[k] if spec['norm'] == 'jetPt' else ck[:, 4].sum()
                bad['E_jet'] += int(abs(Ejet[k] / ref - 1) > 1e-6)
                sel = iJet == k
                nEnt += int(sel.sum())
                bad['nEntries'] += int(nano[tab + '_nEntries'][e][k] != sel.sum())
                jet = p4(np.array([jpt[k]]), np.array([jeta[k]]), np.array([jphi[k]]),
                         np.array([np.sqrt((jpt[k] * np.cosh(jeta[k])) ** 2 + jm[k] ** 2)]))[0]
                c, w, s = expected(spec, ck, jet, Ejet[k])
                gc = np.stack([nano[ent + '_' + v][e][sel].astype(float) for v in names], 1)
                gw = nano[ent + '_weight'][e][sel].astype(float)
                gs = nano[ent + '_symfactor'][e][sel].astype(float)
                if len(gw) != len(w):
                    bad['count'] += 1
                    continue
                c, w, s = sortRows(c, w, s)
                gc, gw, gs = sortRows(gc, gw, gs)
                dc = np.abs(dphi(gc, c)) if c.size else np.zeros(1)
                dw = np.abs(gw / w - 1) if w.size else np.zeros(1)
                maxdev['coords'] = max(maxdev['coords'], dc.max(initial=0))
                maxdev['weight'] = max(maxdev['weight'], dw.max(initial=0))
                bad['coords'] += int(dc.max(initial=0) > 1e-4)
                bad['weight'] += int(dw.max(initial=0) > 1e-5)
                bad['symfactor'] += int(np.any(gs != s))
        detail = '%d jets, %d entries; bad %s; max |dcoord| %.1e, max |dw/w| %.1e' % (
            nJets, nEnt, {k: v for k, v in bad.items() if v}, maxdev['coords'], maxdev['weight'])
        report('%s %s' % (tab, '(mutated)' if MUTATE else ''), nJets > 0 and nEnt > 0 and not any(bad.values()), detail)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
