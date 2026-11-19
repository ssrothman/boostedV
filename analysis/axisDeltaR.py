"""Distance between each stored jet axis and the truth object of the jet (the `axisTruth` column).

Input: ZX_test NANOs with the axis columns.
    python3 axisDeltaR.py nano*.root -o outdir [--truth vw|higgs|parton] [--levels Reco Gen] [--pt-edges 200 300 400 600 1e9]
--truth selects the jets and names the reference (TRUTH):
  vw      a boson (status 0) with mass in the W/Z windows (signal, e.g. ZZto2L2Q, WZto2L2Q); the default
  higgs   a boson (status 0) with mass 120-130 GeV (ZH with H -> bb, cc, gg; H -> WW gives the W, which fails the window)
  parton  a hard-process quark or gluon not from a boson (status 3): QCD jets, e.g. the recoil jet of Drell-Yan
Output: outdir/dR_<level>.pdf (normalised dR histograms per jet pT bin), outdir/dRmedian_<level>.pdf (median and
68%/90% quantiles vs jet pT), outdir/dR.md (summary table; event weights = genWeight).
"""
import argparse
import os

import awkward as ak
import matplotlib
import numpy as np
import uproot

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402

COLORS = dict(zip(['jet', 'axisSoftDrop', 'axisSoftDropB1', 'axisSoftDropZ005', 'axisTrim', 'axisWtaCA', 'axisWtaKT',
                   'axisRecoil'], ['#1f77b4', '#ff7f0e', '#d62728', '#8c564b', '#2ca02c', '#9467bd', '#e377c2', '#17becf']))
AXES = ['jet', 'axisSoftDrop', 'axisSoftDropB1', 'axisSoftDropZ005', 'axisTrim', 'axisWtaCA', 'axisWtaKT', 'axisRecoil']
QUANTILES = (0.5, 0.68, 0.9, 0.95)
FRACTIONS = (0.05, 0.1, 0.2)
# (status, mass window, label); vw: the union of the W (60-100) and Z (66-116) windows of truthRho.py
TRUTH = {'vw': (0, (60.0, 116.0), 'truth V'), 'higgs': (0, (120.0, 130.0), 'truth H'), 'parton': (3, None, 'truth parton')}


def wquantile(x, w, q):
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return np.interp(np.asarray(q) * c[-1], c, x[o])


def truthMask(jets, truth):
    status, window, _ = TRUTH[truth]
    m = jets.axisTruthStatus == status
    if window:
        m = m & (jets.axisTruthMass > window[0]) & (jets.axisTruthMass < window[1])
    return m


def load(files, level, truth):
    J = level + 'Jet'
    cols = ['pt', 'eta', 'phi', 'axisTruthEta', 'axisTruthPhi', 'axisTruthMass', 'axisTruthStatus']
    cols += [a + s for a in AXES if a != 'jet' for s in ('Eta', 'Phi', 'Status')]
    out = []
    for f in files:
        t = uproot.open(f)['Events']
        if t.num_entries == 0:   # a file without selected events has no branches
            continue
        arr = t.arrays([J + '_' + c for c in cols] + ['genWeight'])
        jets = ak.zip({c: arr[J + '_' + c] for c in cols})
        w = ak.broadcast_arrays(arr['genWeight'], jets.pt)[0]
        m = truthMask(jets, truth)
        out.append({c: ak.to_numpy(ak.flatten(jets[c][m])).astype(float) for c in cols}
                   | {'w': ak.to_numpy(ak.flatten(w[m])).astype(float)})
    return {k: np.concatenate([o[k] for o in out]) for k in out[0]}


def deltaR(d, axis):
    eta, phi = (d['eta'], d['phi']) if axis == 'jet' else (d[axis + 'Eta'], d[axis + 'Phi'])
    return np.hypot(eta - d['axisTruthEta'], np.angle(np.exp(1j * (phi - d['axisTruthPhi']))))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('-o', '--outdir', required=True)
    ap.add_argument('--levels', nargs='+', default=['Reco', 'Gen'])
    ap.add_argument('--truth', choices=sorted(TRUTH), default='vw')
    ap.add_argument('--pt-edges', type=float, nargs='+', default=[200, 300, 400, 600, 1e9])
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    hep.style.use('CMS')
    edges = a.pt_edges
    bins = np.logspace(-3, 0, 31)   # first bin: underflow, last: overflow
    label = TRUTH[a.truth][2]
    lines = ['# Distance between jet axes and the %s (--truth %s; weights genWeight)' % (label, a.truth), '',
             'Quantiles q50/q68/q90/q95 of dR(axis, truth); f<x: weighted fraction with dR < x. Status: soft-drop '
             '1 = groomed to one particle, 2 = no subjet (jet axis); recoil 2 = no back-to-back boson.', '']
    for level in a.levels:
        d = load(a.files, level, a.truth)
        lines += ['## %s jets (%d)' % (level, len(d['w'])), '',
                  '| axis | jet pT | N | mean | q50 | q68 | q90 | q95 | ' + ' | '.join('f<%.2f' % x for x in FRACTIONS)
                  + ' | status 1 | status 2 |', '|' + '---|' * (6 + len(QUANTILES) + len(FRACTIONS))]
        nb = len(edges) - 1
        fig, axs = plt.subplots(2, (nb + 1) // 2, figsize=(9 * ((nb + 1) // 2), 16), squeeze=False)
        med = {ax: [] for ax in AXES}
        for k in range(nb):
            sel = (d['pt'] >= edges[k]) & (d['pt'] < edges[k + 1])
            pane = axs.flat[k]
            for ax in AXES:
                dr, w = deltaR(d, ax)[sel], d['w'][sel]
                if len(dr) == 0:
                    med[ax].append([np.nan] * 3)
                    continue
                q = wquantile(dr, w, QUANTILES)
                med[ax].append([q[0], wquantile(dr, w, 0.16), q[2]])
                st = d[ax + 'Status'][sel] if ax != 'jet' else np.zeros_like(dr)
                lines.append('| %s | %.0f-%s | %d | %.4f | %s | %s | %.3f | %.3f |' % (
                    ax, edges[k], '%.0f' % edges[k + 1] if edges[k + 1] < 1e8 else 'inf', len(dr),
                    np.sum(w * dr) / np.sum(w), ' | '.join('%.4f' % x for x in q),
                    ' | '.join('%.3f' % (np.sum(w * (dr < x)) / np.sum(w)) for x in FRACTIONS),
                    np.sum(w * (st == 1)) / np.sum(w), np.sum(w * (st == 2)) / np.sum(w)))
                h, _ = np.histogram(np.clip(dr, bins[0] * 1.0001, bins[-1] * 0.9999), bins=bins, weights=w)
                hep.histplot(h / np.sum(w), bins, label=ax, ax=pane, color=COLORS[ax],
                             ls='--' if ax in ('axisWtaKT', 'axisSoftDropZ005') else '-')
            pane.set_xlabel(r'$\Delta R$(axis, %s) (first/last bin: under/overflow)' % label)
            pane.set_ylabel('Fraction of jets')
            pane.set_xscale('log')
            pane.set_title('%s jets, $p_T$ %.0f-%s GeV' % (level, edges[k], '%.0f' % edges[k + 1] if edges[k + 1] < 1e8 else 'inf'),
                           fontsize=18)
            pane.legend(fontsize=14)
        for pane in list(axs.flat)[nb:]:
            pane.axis('off')
        fig.savefig(os.path.join(a.outdir, 'dR_%s.pdf' % level), bbox_inches='tight')
        plt.close(fig)
        fig, pane = plt.subplots(figsize=(11, 8))
        centres = [(edges[k] + min(edges[k + 1], 2 * edges[k])) / 2 for k in range(nb)]
        for i, ax in enumerate(AXES):
            m = np.array(med[ax])
            x = np.array(centres) * (1 + 0.02 * (i - len(AXES) / 2))
            pane.errorbar(x, m[:, 0], yerr=[m[:, 0] - m[:, 1], m[:, 2] - m[:, 0]], fmt='o', label=ax, capsize=3,
                          color=COLORS[ax])
        pane.set_xlabel('Jet $p_T$ (GeV; last bin: centre at 1.5 x lower edge)')
        pane.set_ylabel(r'$\Delta R$(axis, %s): median, 16%%-90%%' % label)
        pane.set_yscale('log')
        pane.set_title('%s jets' % level, fontsize=18)
        pane.legend(fontsize=13, ncol=2)
        fig.savefig(os.path.join(a.outdir, 'dRmedian_%s.pdf' % level), bbox_inches='tight')
        plt.close(fig)
        lines.append('')
    open(os.path.join(a.outdir, 'dR.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
