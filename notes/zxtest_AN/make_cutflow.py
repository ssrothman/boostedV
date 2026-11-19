"""Cutflow of the ZX_test selection from NANO files produced with ZX_cutflow.yaml (written by make_cutflow_config.py:
ZX_test.yaml with pairPtMin 0, backToBack disabled and jetCuts relaxed except minConstituents >= 2), which writes every
event passing a dilepton selection (including the extra-lepton veto) at either level, with all jets above the
translator threshold (reco 200 GeV after JEC and JER, gen 150 GeV). The extra-jet veto is disabled in ZX_test and not
modelled.

Usage: python3 make_cutflow.py OUT.tex [--final ROWS.json] NAME=nano.root [NAME=nano.root ...]
--final: final_rows.py output keyed by the same NAMEs; adds the reco <c> efficiencies of a full production, labelled as
upper bounds (valid only if that production's reco selection contains the current one).
Steps per (level, channel), cumulative, as unweighted counts and genWeight-weighted fractions of the processed events
(Runs-tree genEventCount / genEventSumw). The jet steps require at least one jet passing all jet requirements so far;
the back-to-back steps use the leading such jet. Cut values are those of ZX_test.yaml. Events failing the channel at
both levels are not written, so the first reco steps are fractions of the written events' flags.
"""
import json
import math
import sys

import awkward as ak
import numpy as np
import uproot

PT_MIN, JET_ETA, JET_ID, DPHI_MIN, ASYM_MAX = 200.0, 2.4, 3, 2.8, 0.3
JET_PT = {'reco': 200.0, 'gen': 150.0}
LEVELS = {'reco': ('', 'RecoJet'), 'gen': ('Gen', 'GenJet')}
CHANNELS = ('Zmumu', 'Zee')
CLEANING = ('goodVertex', 'metFilters', 'ecalBadCalib', 'jetVetoMap')
STEPS = {'reco': [r'dilepton and lepton veto (no $\ptll$ cut)', r'+ trigger', r'+ event cleaning',
                  r'$\ptll \geq 200\GeV$', r'jet $\pt \geq 200\GeV$', r'jet $|\eta| \leq 2.4$',
                  r'jet ID tight + lepton veto', r'jet not overlapping a lepton', r'$\Delta\phi > 2.8$',
                  r'asymmetry $< 0.3$'],
         'gen': [r'dilepton and lepton veto (no $\ptll$ cut)', r'$\ptll \geq 200\GeV$', r'jet $\pt \geq 150\GeV$',
                 r'jet $|\eta| \leq 2.4$', r'jet not overlapping a lepton', r'$\Delta\phi > 2.8$',
                 r'asymmetry $< 0.3$']}


def steps(ev, level, ch):
    """Boolean arrays, cumulative, one per step of STEPS[level]."""
    P, J = LEVELS[level]
    flags = P + 'Selection_'
    out = [np.asarray(ev[flags + ch + 'Sel'], dtype=bool)]
    if level == 'reco':
        out.append(out[-1] & np.asarray(ev[flags + ch + 'Trigger'], dtype=bool))
        clean = out[-1].copy()
        for c in CLEANING:  # absent in NANO produced before the ECAL and jet veto map flags
            if flags + c in ev.fields:
                clean &= np.asarray(ev[flags + c], dtype=bool)
        out.append(clean)
    bpt = ak.fill_none(ak.firsts(ev[P + ch + 'Boson_pt']), -1.0)
    bphi = ak.fill_none(ak.firsts(ev[P + ch + 'Boson_phi']), 0.0)
    out.append(out[-1] & (np.asarray(bpt) >= PT_MIN))
    fields = ['pt', 'eta', 'phi', 'veto' + ch] + (['jetId'] if level == 'reco' else [])
    jets = ak.zip({k: ev[J + '_' + k] for k in fields})
    cuts = [jets.pt >= JET_PT[level], abs(jets.eta) <= JET_ETA]
    if level == 'reco':
        cuts.append((jets.jetId & JET_ID) == JET_ID)
    cuts.append(~jets['veto' + ch])
    keep = cuts[0]
    for c in cuts:
        keep = keep & c
        out.append(out[-1] & np.asarray(ak.any(keep, axis=1)))
    pt, phi = jets.pt[keep], jets.phi[keep]
    lead = ak.argmax(pt, axis=1, keepdims=True)
    lpt = ak.fill_none(ak.firsts(pt[lead]), -1.0)
    lphi = ak.fill_none(ak.firsts(phi[lead]), 0.0)
    dphi = np.abs(np.remainder(np.asarray(lphi - bphi) + math.pi, 2 * math.pi) - math.pi)
    asym = np.abs(np.asarray(lpt - bpt)) / np.maximum(np.asarray(lpt + bpt), 1e-9)
    out.append(out[-1] & (dphi > DPHI_MIN))
    out.append(out[-1] & (asym < ASYM_MAX))
    assert len(out) == len(STEPS[level])
    return out


def main():
    args = sys.argv[1:]
    final = None
    if '--final' in args:
        i = args.index('--final')
        final = json.load(open(args[i + 1]))
        del args[i:i + 2]
    out, pairs = args[0], [a.split('=', 1) for a in args[1:]]
    rows = {}  # (level, ch) -> {sample: [(n, frac_w), ...]}
    totals = {}
    for name, path in pairs:
        f = uproot.open(path)
        runs = f['Runs'].arrays(['genEventCount', 'genEventSumw'], library='np')
        nProc, wProc = runs['genEventCount'].sum(), runs['genEventSumw'].sum()
        ev = f['Events'].arrays(filter_name=['*Selection_*', '*Boson_pt', '*Boson_phi', 'RecoJet_*', 'GenJet_*',
                                             'genWeight'], library='ak')
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
            cells = ['%d (%s)' % (byName[n][k][0], fmt(byName[n][k][1])) for n in names]
            lines.append('%s & %s & %s \\\\' % (head, step, ' & '.join(cells)))
        lines.append(r'\midrule')
    lines.append(r'\multicolumn{2}{l}{Written (any level, channel)} & ' +
                 ' & '.join('%d (%s)' % (totals[n][2], fmt(totals[n][3])) for n in names) + r' \\')
    if final:
        lines.append(r'\midrule')
        for k, ch in enumerate(CHANNELS):
            head = ('full production', '(upper bound)')[k]
            cells = ['%d (%s)' % (final[n]['pass']['Selection_' + ch]['n'], fmt(final[n]['pass']['Selection_' + ch]['frac']))
                     if n in final else '--' for n in names]
            lines.append('%s & reco %s, full selection & %s \\\\' % (head, ch, ' & '.join(cells)))
        lines.append(r'\multicolumn{2}{l}{full production: processed events} & ' +
                     ' & '.join('%d' % final[n]['genEventCount'] if n in final else '--' for n in names) + r' \\')
    lines += [r'\bottomrule', r'\end{tabular}']
    with open(out, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', out)


def fmt(x):
    """Weighted fraction in percent, three significant digits."""
    return ('%.3g' % (100 * x)) + r'\%'


if __name__ == '__main__':
    main()
