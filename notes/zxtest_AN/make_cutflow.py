"""Cutflow of the ZX_test selection from NANO files produced with ZX_loose.yaml (ZX_test.yaml with pairPtMin 0 and
backToBack disabled), which writes every event passing a channel at either level, with all jets passing jetCuts.

Usage: python3 make_cutflow.py OUT.tex NAME=nano.root [NAME=nano.root ...]
Steps per (level, channel), cumulative, as unweighted counts and genWeight-weighted fractions of the processed events
(Runs-tree genEventCount / genEventSumw). The pT, Delta phi and asymmetry cuts are those of ZX_test.yaml.
"""
import math
import sys

import awkward as ak
import numpy as np
import uproot

PT_MIN, DPHI_MIN, ASYM_MAX = 150.0, 2.8, 0.3
LEVELS = {'reco': ('', 'RecoJet'), 'gen': ('Gen', 'GenJet')}
CHANNELS = ('Zmumu', 'Zee')
STEPS = {'reco': ['channel flag', r'$\pt^{\ell\ell} > 150\GeV$', r'$\geq 1$ jet', r'$\Delta\phi > 2.8$',
                  r'asymmetry $< 0.3$'],
         'gen': ['channel flag', r'$\pt^{\ell\ell} > 150\GeV$', r'$\geq 1$ jet', r'$\Delta\phi > 2.8$',
                 r'asymmetry $< 0.3$']}


def steps(ev, level, ch):
    """Boolean arrays, cumulative, one per step."""
    P, J = LEVELS[level]
    flag = np.asarray(ev[P + 'Selection_' + ch], dtype=bool)
    bpt = ak.fill_none(ak.firsts(ev[P + ch + 'Boson_pt']), -1.0)
    bphi = ak.fill_none(ak.firsts(ev[P + ch + 'Boson_phi']), 0.0)
    pt = ev[J + '_pt'][~ev[J + '_veto' + ch]]
    phi = ev[J + '_phi'][~ev[J + '_veto' + ch]]
    lead = ak.argmax(pt, axis=1, keepdims=True)
    lpt = ak.fill_none(ak.firsts(pt[lead]), -1.0)
    lphi = ak.fill_none(ak.firsts(phi[lead]), 0.0)
    dphi = np.abs(np.remainder(np.asarray(lphi - bphi) + math.pi, 2 * math.pi) - math.pi)
    asym = np.abs(np.asarray(lpt - bpt)) / np.maximum(np.asarray(lpt + bpt), 1e-9)
    s1 = flag
    s2 = s1 & (np.asarray(bpt) > PT_MIN)
    s3 = s2 & (np.asarray(lpt) > 0)
    s4 = s3 & (dphi > DPHI_MIN)
    s5 = s4 & (asym < ASYM_MAX)
    return [s1, s2, s3, s4, s5]


def main():
    out, pairs = sys.argv[1], [a.split('=', 1) for a in sys.argv[2:]]
    rows = {}  # (level, ch) -> {sample: [(n, frac_w), ...]}
    totals = {}
    for name, path in pairs:
        f = uproot.open(path)
        runs = f['Runs'].arrays(['genEventCount', 'genEventSumw'], library='np')
        nProc, wProc = runs['genEventCount'].sum(), runs['genEventSumw'].sum()
        ev = f['Events'].arrays(library='ak')
        w = np.asarray(ev['genWeight'])
        anyPass = np.zeros(len(w), dtype=bool)
        for level in LEVELS:
            for ch in CHANNELS:
                ss = steps(ev, level, ch)
                anyPass |= ss[-1]
                rows.setdefault((level, ch), {})[name] = [(int(s.sum()), float(w[s].sum() / wProc)) for s in ss]
        totals[name] = (int(nProc), int(len(w)), int(anyPass.sum()), float(w[anyPass].sum() / wProc))
        print(name, totals[name])
    names = [n for n, _ in pairs]
    lines = [r'\begin{tabular}{ll' + 'r' * len(names) + '}', r'\toprule',
             'Level, channel & Step & ' + ' & '.join(r'\texttt{%s}' % n.replace('_', r'\_') for n in names) + r' \\',
             r'\midrule',
             r'\multicolumn{2}{l}{Processed events} & ' + ' & '.join('%d' % totals[n][0] for n in names) + r' \\',
             r'\midrule']
    for (level, ch), byName in rows.items():
        for k, step in enumerate(STEPS[level]):
            head = '%s %s' % (level, ch) if k == 0 else ''
            cells = []
            for n in names:
                cnt, frac = byName[n][k]
                cells.append('%d (%s)' % (cnt, fmt(frac)))
            lines.append('%s & %s & %s \\\\' % (head, step, ' & '.join(cells)))
        lines.append(r'\midrule')
    lines.append(r'\multicolumn{2}{l}{Written (any level, channel)} & ' +
                 ' & '.join('%d (%s)' % (totals[n][2], fmt(totals[n][3])) for n in names) + r' \\')
    lines += [r'\bottomrule', r'\end{tabular}']
    with open(out, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', out)


def fmt(x):
    """Weighted fraction in percent, three significant digits."""
    return ('%.3g' % (100 * x)) + r'\%'


if __name__ == '__main__':
    main()
