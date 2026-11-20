#!/usr/bin/env python3
"""Jet-free E2C at reco vs gen level (E2C_NEXT_PLAN.md item 4: the pileup and detector effect on the event E2C).

  python3 jetfreeGenReco.py RECO.coffea GEN.coffea -o outdir

RECO.coffea, GEN.coffea: run.py outputs of configs/jetfree_evt.yaml and configs/jetfree_gen.yaml. Jets at the
baseline of their level (jet pT > 200, |eta| < 2.0, Z pT > 200; reco also medium muon ID), both channels, in Z-pT
slices (bvana/sensitivity.py PT_SLICES). Per reco/gen pair (PAIRS): the DY shape difference (chi2/ndf of the
unit-normalised shapes with the MC statistics of both, as if independent, and the largest |reco/gen - 1| over bins
with MC relative error < 5% in both), and the stat-only Z_shape with the MC term of VV (boson jets) and ZH against all other jets at each level.
"""
import argparse
import os

import numpy as np

import sensitivity
import vvTruthSplit
from bvana import sensitivity as sv

PAIRS = (('c_evtPV', 'c_genCh'), ('c_evtPVHemi', 'c_genChHemi'), ('c_evtPuppi', 'c_genAll'),
         ('c_evtPuppiHemi', 'c_genAllHemi'))
SIGNALS = {'VV': ('WZ', 'ZZ'), 'ZH': ('ZH',)}


def level(path, reco):
    t = sensitivity.loadTables(path)
    base = (t['zPt'] > 200) & (t['pt'] > 200) & (np.abs(t['eta']) < 2.0)
    if reco:
        base &= t['allMediumId'] > 0
    return t, base


def zShape(t, base, col, names):
    V = sensitivity.vectors(t, col)
    w = t['weight']
    isS = np.isin(t['group'], names)
    sig = sv.Stats(V[base & isS], w[base & isS], t['zPt'][base & isS])
    bkg = sv.Stats(V[base & ~isS], w[base & ~isS], t['zPt'][base & ~isS])
    return sv.significance(sig.H, bkg.H, bkg.C + bkg.Cmc + sig.Cmc, support=np.diag(bkg.C) > 0)[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('reco')
    ap.add_argument('gen')
    ap.add_argument('-o', '--outdir', required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    (tr, br), (tg, bg) = level(a.reco, True), level(a.gen, False)
    lines = ['# Jet-free E2C, reco vs gen', '', 'Reco %s, gen %s; Z-pT slices [GeV].' % (a.reco, a.gen), '',
             '| reco | gen | Z pT slice | DY chi2/ndf | DY max abs(reco/gen - 1) |', '|---|---|---|---|---|']
    names = ['%g-%g' % (lo, hi) for lo, hi in zip(sv.PT_SLICES[:-1], sv.PT_SLICES[1:])]
    zrows = []
    for rc, gc in PAIRS:
        S = {}
        for key, t, b, c in (('reco', tr, br, rc), ('gen', tg, bg, gc)):
            m = b & (t['group'] == 'DY')
            S[key] = sv.Stats(sensitivity.vectors(t, c)[m], t['weight'][m], t['zPt'][m])
        k = len(S['reco'].H) // (len(sv.PT_SLICES) - 1)
        for i in range(len(sv.PT_SLICES) - 1):
            b = slice(i * k, (i + 1) * k)
            hr, hg = S['reco'].H[b], S['gen'].H[b]
            if hr.sum() <= 0 or hg.sum() <= 0:
                continue
            c, n = vvTruthSplit.compatChi2(hr, S['reco'].Cmc[b, b], hg, S['gen'].Cmc[b, b])
            with np.errstate(divide='ignore', invalid='ignore'):
                ok = (np.sqrt(np.diag(S['reco'].Cmc[b, b])) / hr < 0.05) & (np.sqrt(np.diag(S['gen'].Cmc[b, b])) / hg < 0.05)
                dev = np.abs((hr / hr.sum()) / (hg / hg.sum()) - 1)
            lines.append('| %s | %s | %s | %.1f / %d = %.2f | %s |' % (rc, gc, names[i], c, n, c / max(n, 1),
                                                                       '%.3f' % dev[ok].max() if ok.any() else '-'))
        zrows.append('| %s | %s | %s |' % (rc, gc, ' | '.join(
            '%.2f / %.2f' % (zShape(tr, br, rc, s), zShape(tg, bg, gc, s)) for s in SIGNALS.values())))
    lines += ['', '## Z_shape with the MC term, 5 Z-pT slices, reco / gen', '', '| reco | gen | VV | ZH |',
              '|---|---|---|---|'] + zrows
    with open(os.path.join(a.outdir, 'genReco.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
