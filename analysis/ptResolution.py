#!/usr/bin/env python3
"""How well the jet pT and the Z pT measure the true pT of the jet's truth particle (E2C_NEXT_PLAN.md, item 1).

  python3 ptResolution.py TABLES.coffea -o outdir

TABLES.coffea: run.py output of configs/sensitivity.yaml with the `truth` columns. Jets at the sensitivity baseline
(sensitivity.py), both channels. Truth: the hadronic boson (truthStatus 0) for VV (WZ + ZZ) and ZH, the recoiling
hard-process parton (truthStatus 3) for DY. Residual r = (pT_true - pT_reco) / pT_true for pT_reco = jet pT and Z pT,
in bins of pT_true. Writes outdir/resolution.md (weighted median, half-width of the central 68%, fraction with |r| > 0.3)
and one figure per sample group and pT_true bin.
"""
import argparse
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402
import numpy as np  # noqa: E402

import sensitivity  # noqa: E402
from bvana.plotting import label  # noqa: E402

GROUPS = (('VV', ('WZ', 'ZZ'), 0), ('ZH', ('ZH',), 0), ('DY', ('DY',), 3))
TRUTH_BINS = (0.0, 200.0, 300.0, 400.0, 600.0, np.inf)
R_EDGES = np.linspace(-1.0, 1.0, 101)


def quantiles(x, w, qs):
    """Weighted quantiles, each point at the middle of its weight in the cumulative sum (equal weights: the median of
    an odd sample is its middle value)."""
    o = np.argsort(x)
    c = np.cumsum(w[o]) - w[o] / 2
    return np.interp(np.asarray(qs) * w.sum(), c, x[o])


def summary(r, w):
    """(median, half-width of the central 68%, weighted fraction with |r| > 0.3)."""
    q16, q50, q84 = quantiles(r, w, (0.16, 0.5, 0.84))
    return q50, (q84 - q16) / 2, w[np.abs(r) > 0.3].sum() / w.sum()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tables')
    ap.add_argument('-o', '--outdir', required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    t = sensitivity.loadTables(a.tables)
    t['absEta'] = np.abs(t['eta'])
    base = (t['zPt'] > 200) & (t['pt'] > 200) & (t['absEta'] < 2.0) & (t['allMediumId'] > 0)
    lines = ['# Jet pT and Z pT vs the true pT', '', 'Tables %s; sensitivity baseline; r = (pT_true - pT_reco) / pT_true.'
             % a.tables, '', 'Matched fraction: weighted fraction of the baseline jets of the group with the given truth'
             ' status.', '',
             '| group | pT_true | matched fraction | jets | jet: median, 68% half-width, f(abs r > 0.3) | '
             'Z: median, 68% half-width, f(abs r > 0.3) |', '|---|---|---|---|---|---|']
    hep.style.use('CMS')
    for name, groups, status in GROUPS:
        g = base & np.isin(t['group'], groups)
        m = g & (t['truthStatus'] == status)
        frac = t['weight'][m].sum() / t['weight'][g].sum()
        for lo, hi in zip(TRUTH_BINS[:-1], TRUTH_BINS[1:]):
            b = m & (t['truthPt'] >= lo) & (t['truthPt'] < hi)
            if b.sum() < 10:
                continue
            w = t['weight'][b]
            cells, fig = [], plt.figure()
            ax = fig.gca()
            for reco, name_ in (('pt', 'jet $p_T$'), ('zPt', '$p_T^{\\ell\\ell}$')):
                r = (t['truthPt'][b] - t[reco][b]) / t['truthPt'][b]
                med, hw, tail = summary(r, w)
                cells.append('%.3f, %.3f, %.3f' % (med, hw, tail))
                h, _ = np.histogram(np.clip(r, R_EDGES[0], R_EDGES[-1] - 1e-9), R_EDGES, weights=w)
                hep.histplot(h / h.sum(), R_EDGES, ax=ax, label='%s (median %.3f, 68%% half-width %.3f)' % (name_, med, hw))
            ax.set_xlabel('$(p_T^{true} - p_T^{reco}) / p_T^{true}$')
            ax.set_ylabel('Fraction of jets')
            ax.legend(title='%s, $%g \\leq p_T^{true} < %g$ GeV' % (name, lo, hi), fontsize=14, title_fontsize=14)
            label(ax, fontsize=16)
            fig.savefig(os.path.join(a.outdir, 'resolution_%s_%g_%g.png' % (name, lo, hi)), bbox_inches='tight')
            plt.close(fig)
            lines.append('| %s | %g-%g | %.3f | %d | %s | %s |' % (name, lo, hi, frac, b.sum(), cells[0], cells[1]))
    with open(os.path.join(a.outdir, 'resolution.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
