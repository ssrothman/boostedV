#!/usr/bin/env python3
"""Are the VV jets that are not the hadronic boson like the DY jets? (E2C_NEXT_QUESTIONS.md Q4, follow-up 2)

  python3 vvTruthSplit.py TABLES.coffea -o outdir

TABLES.coffea: run.py output of configs/sensitivity.yaml with the `truth` columns. Jets at the sensitivity baseline,
both channels, in the jet-pT slices of bvana/sensitivity.py. Groups: VV-boson (WZ + ZZ, truthStatus 0), VV-other (WZ +
ZZ, any other status), DY. Writes outdir/vvTruthSplit.md with
  - composition: truth status and parton type (gluon, light quark, b) of VV-other and DY;
  - shape compatibility: chi2/ndf between the unit-normalised VV-other (and VV-boson) and DY distributions of the E2C
    (n = 1), m_SD and the GloParT V score, per pT slice, with the MC-statistical covariance of both (compatChi2), and
    the same for two random halves of DY as the null reference, and for light-quark and gluon jets separately;
  - boson fraction of VV at the gpV working points and for the cuts of the scans;
  - Z_shape (with the MC term; e2cn1, 5 pT slices) with all VV as signal, with VV-other moved to the background, and
    with VV-other dropped.
"""
import argparse
import os

import numpy as np

import sensitivity
from bvana import sensitivity as sv

GPV_EDGES = np.linspace(0.0, 1.0, 21)


def histRows(x, edges):
    """One-hot rows of x in edges, values outside clipped into the end bins."""
    k = np.clip(np.searchsorted(edges, x, side='right') - 1, 0, len(edges) - 2)
    out = np.zeros((len(x), len(edges) - 1), dtype=np.float32)
    out[np.arange(len(x)), k] = 1.0
    return out


def normCov(H, Cmc):
    """Unit-normalised H and its covariance from the MC-statistical covariance Cmc of H."""
    n = H.sum()
    p = H / n
    J = (np.eye(len(p)) - np.outer(p, np.ones(len(p)))) / n
    return p, J @ Cmc @ J.T


def compatChi2(H1, C1, H2, C2):
    """(chi2, ndf) of the unit-normalised H1 against the unit-normalised H2, both with MC-statistical covariances, on the
    bins with variance in either."""
    p, Cp = normCov(H1, C1)
    q, Cq = normCov(H2, C2)
    keep = (np.diag(C1) > 0) | (np.diag(C2) > 0)
    d = p - q
    return float(d @ sv.pinv(Cp + Cq, keep) @ d), int(keep.sum()) - 1


def stats(V, w, pt, mask):
    return sv.Stats(V[mask], w[mask], pt[mask])


def blocks(st):
    k = len(st.H) // (len(sv.PT_SLICES) - 1)
    return [slice(i * k, (i + 1) * k) for i in range(len(sv.PT_SLICES) - 1)]


def partonType(pdg):
    a = np.abs(pdg)
    return np.where(a == 21, 'g', np.where(a == 5, 'b', np.where((a >= 1) & (a <= 4), 'q', 'other')))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tables')
    ap.add_argument('-o', '--outdir', required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    edges = np.geomspace(1e-3, 1.6, 41)
    centers = np.sqrt(edges[:-1] * edges[1:])
    t = sensitivity.loadTables(a.tables)
    sensitivity.derive(t, centers)
    base = (t['zPt'] > 200) & (t['pt'] > 200) & (t['absEta'] < 2.0) & (t['allMediumId'] > 0)
    w = t['weight']
    isVV = np.isin(t['group'], ('WZ', 'ZZ'))
    boson = isVV & (t['truthStatus'] == 0)
    other = isVV & (t['truthStatus'] != 0)
    isDY = t['group'] == 'DY'
    half = np.random.default_rng(11).random(len(w)) < 0.5
    sl = np.searchsorted(sv.PT_SLICES, t['pt'], side='right') - 1
    sliceNames = ['%g-%g' % (lo, hi) for lo, hi in zip(sv.PT_SLICES[:-1], sv.PT_SLICES[1:])]
    lines = ['# VV jets that are not the boson vs DY jets', '', 'Tables %s; sensitivity baseline; weighted.' % a.tables, '']

    lines += ['## Composition', '', '| group | pT slice | weight share of group | status 0 / 1 / 3 / 2 | status 1, 3: g / q / b |',
              '|---|---|---|---|---|']
    ptype = partonType(np.nan_to_num(t['truthPdgId']).astype(np.int64))
    for name, g in (('VV', base & isVV), ('VV-other', base & other), ('DY', base & isDY)):
        for i, sn in [(None, 'all')] + list(enumerate(sliceNames)):
            m = g if i is None else g & (sl == i)
            W = w[m].sum()
            if W <= 0:
                continue
            st = ' / '.join('%.2f' % (w[m & (t['truthStatus'] == s)].sum() / W) for s in (0, 1, 3, 2))
            parton = m & np.isin(t['truthStatus'], (1, 3))
            Wp = w[parton].sum()
            pt_ = ' / '.join('%.2f' % (w[parton & (ptype == c)].sum() / Wp) for c in ('g', 'q', 'b')) if Wp > 0 else '-'
            lines.append('| %s | %s | %.3f | %s | %s |' % (name, sn, W / w[g].sum(), st, pt_))
    lines.append('')

    lines += ['## Shape compatibility with DY (chi2/ndf, MC statistics of both)', '',
              'DY A vs B: two random halves of DY (null reference). Per jet-pT slice [GeV].', '',
              'q, g: only the jets matched to a light quark (d-c) or a gluon, in both groups.',
              'n_eff: (sum w)^2 / sum w^2 of the VV-other jets.', '',
              '| observable | pT slice | VV-other vs DY | VV-boson vs DY | DY A vs B | VV-other vs DY, q | VV-other vs DY, g | '
              'VV-other / DY jets (unweighted), VV-other n_eff |',
              '|---|---|---|---|---|---|---|---|']
    light, glu = np.isin(ptype, ('q',)), ptype == 'g'
    obsRows = {'E2C n=1': sensitivity.vectors(t, 'e2cn1'), 'm_SD': sensitivity.msdRows(t['msd']),
               'gpV': histRows(np.nan_to_num(t['gpV']), GPV_EDGES)}
    for oname, V in obsRows.items():
        S = {k: stats(V, w, t['pt'], base & m) for k, m in
             (('other', other), ('boson', boson), ('dy', isDY), ('dyA', isDY & half), ('dyB', isDY & ~half),
              ('otherQ', other & light), ('dyQ', isDY & light), ('otherG', other & glu), ('dyG', isDY & glu))}
        for i, b in enumerate(blocks(S['dy'])):
            cells = []
            for x, y in (('other', 'dy'), ('boson', 'dy'), ('dyA', 'dyB'), ('otherQ', 'dyQ'), ('otherG', 'dyG')):
                if S[x].H[b].sum() > 0 and S[y].H[b].sum() > 0:
                    c, n = compatChi2(S[x].H[b], S[x].Cmc[b, b], S[y].H[b], S[y].Cmc[b, b])
                    cells.append('%.1f / %d = %.2f' % (c, n, c / n) if n > 0 else '-')
                else:
                    cells.append('-')
            mo = base & other & (sl == i)
            nj = '%d / %d, %.0f' % (mo.sum(), (base & isDY & (sl == i)).sum(), w[mo].sum() ** 2 / (w[mo] ** 2).sum())
            lines.append('| %s | %s | %s | %s |' % (oname, sliceNames[i], ' | '.join(cells), nj))
    lines.append('')

    lines += ['## Boson fraction of VV at the gpV working points', '', '| cut | VV weight | boson fraction |',
              '|---|---|---|']
    cuts = sensitivity.taggerScans(t, base, w, 'gpV')
    for label, m in cuts:
        W = w[m & isVV].sum()
        lines.append('| %s | %.1f | %.3f |' % (label, W, w[m & boson].sum() / W))
    lines.append('')

    lines += ['## Boson fraction of VV and DY efficiency for the cuts of the scans (sensitivity.scans)', '',
              '| cut | DY eff | VV eff | VV boson fraction |', '|---|---|---|---|']
    t['lrVV'] = sensitivity.lrScore(t, base, isVV, centers)
    W0, D0 = w[base & isVV].sum(), w[base & isDY].sum()
    for label, m in sensitivity.scans(t, base, w, 'VV'):
        W = w[m & isVV].sum()
        lines.append('| %s | %.3f | %.3f | %.3f |' % (label, w[m & isDY].sum() / D0, W / W0, w[m & boson].sum() / W))
    lines.append('')

    lines += ['## Z_shape (with MC term), e2cn1, 5 jet-pT slices', '',
              'all: every VV jet is signal; other-as-bkg: VV-other in the background; other-dropped: VV-other removed.',
              'Half-sample Z (no MC term) A, B in brackets.', '',
              '| cut | all | other-as-bkg | other-dropped |', '|---|---|---|---|']
    groups0 = sensitivity.GROUPS
    variants = {}
    for vname in ('all', 'other-as-bkg', 'other-dropped'):
        tv = dict(t)
        if vname != 'all':
            tv['group'] = np.where(other, 'VVother' if vname == 'other-as-bkg' else 'dropped', t['group'])
        # Evaluator takes its groups from sensitivity.GROUPS; 'dropped' is in none, so it is ignored.
        sensitivity.GROUPS = groups0 + ((('VVother', ()),) if vname == 'other-as-bkg' else ())
        try:
            variants[vname] = sensitivity.Evaluator(tv, base, 'e2cn1', centers, 1.0)
        finally:
            sensitivity.GROUPS = groups0
    for label, m in cuts:
        cells = []
        for vname, ev in variants.items():
            r = ev.evaluate(m, 'VV')
            za, zb = ev.halfSampleZ(m, 'VV')
            cells.append('%.2f (%.2f, %.2f)' % (r['ZshapeMC'], za, zb))
        lines.append('| %s | %s |' % (label, ' | '.join(cells)))
    lines.append('')
    with open(os.path.join(a.outdir, 'vvTruthSplit.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
