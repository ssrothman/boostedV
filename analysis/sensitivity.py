#!/usr/bin/env python3
"""Cut scans for the signal sensitivity of the jet E2C (SENSITIVITY_PLAN.md, Phase A).

  python3 sensitivity.py TABLES.coffea -o outdir [--obs e2cn1 e2cn2 both] [--lumi-pb 326030 --table-lumi-pb 326030]

TABLES.coffea: run.py output of configs/sensitivity.yaml with --lumi (the weights are expected yields). Both channels
are combined. For each signal definition (VV = WZ + ZZ; ZH = all ZH; everything else is background) and each cut,
relative to the baseline (Z pT > 200, jet pT > 200, |eta| < 2.0, medium muon ID), it writes to outdir/scan.md and
scan.json: efficiencies, the peak-window S/B, Z_tot and Z_shape (bvana/sensitivity.py; "mc": with the MC statistical
covariance added) and the DY shape distortion against the baseline, each jet-pT slice normalised on its own (chi2/ndf
at the luminosity, and the largest |ratio - 1| over bins with MC relative error < 5%). Thresholds of continuous variables are set at fixed baseline DY
efficiencies.
"""
import argparse
import json
import os

import numpy as np
from coffea.util import load

from bvana import sensitivity as sv

GROUPS = (('DY', ('DYto2L',)), ('ttbar', ('TTto',)), ('singleTop', ('TB', 'Tbar', 'TW')), ('WW', ('WW',)),
          ('WZ', ('WZ',)), ('ZZ', ('ZZ',)), ('ZH', ('ZH_', 'ggZH_', 'GluGluZH_')))
SIGNALS = {'VV': (('WZ', 'ZZ'), 91.1876), 'ZH': (('ZH',), 125.0)}
DY_EFFS = (0.5, 0.3, 0.1, 0.03)
TAGGER_EFFS = (0.1, 0.03, 0.01, 0.003, 0.001)
TEN_SLICES = np.array([200, 250, 300, 350, 400, 500, 600, 800, 1000, 1500, np.inf])
TAGGERS = {'VV': 'gpV', 'ZH': 'pnXbbVsQCD'}
MZ = 91.1876


def group(sample):
    for g, prefixes in GROUPS:
        if sample.startswith(prefixes):
            return g
    raise ValueError('no group for %s' % sample)


def loadTables(path):
    """Columns of both channels concatenated, plus 'group' and 'isMumu'."""
    out = load(path)
    parts = []
    for tname, regions in out['tables'].items():
        for rname, samples in regions.items():
            for sample, cols in samples.items():
                d = {k: v.value for k, v in cols.items()}
                n = len(d['weight'])
                d['group'] = np.full(n, group(sample))
                d['isMumu'] = np.full(n, tname == 'mumu')
                d.setdefault('allMediumId', np.ones(n))
                parts.append(d)
    del out
    keys = set.intersection(*(set(p) for p in parts))
    return {k: np.concatenate([p.pop(k) for p in parts]) for k in sorted(keys)}


def rapidity(pt, eta, m):
    pz, E = pt * np.sinh(eta), np.sqrt((pt * np.cosh(eta)) ** 2 + m ** 2)
    return 0.5 * np.log((E + pz) / (E - pz))


def derive(t, binCenters):
    e = t['e2cn1'][:, 1:-1]
    tot = e.sum(axis=1)
    with np.errstate(divide='ignore', invalid='ignore'):
        t['tau21'] = t['tau2'] / t['tau1']
        q = t['gpQCD']
        v = t['gpXqq'] + t['gpXcs'] + t['gpXbb'] + t['gpXcc']
        t['gpV'] = v / (v + q)
        t['gpHbb'] = t['gpXbb'] / (t['gpXbb'] + q)
        t['ptBalance'] = t['pt'] / t['zPt']
        t['fPeakZ'] = (e * sv.peakWindow(binCenters, t['pt'], MZ)).sum(axis=1) / tot
        t['fPeakH'] = (e * sv.peakWindow(binCenters, t['pt'], 125.0)).sum(axis=1) / tot
    t['absEta'] = np.abs(t['eta'])
    t['absZMassDev'] = np.abs(t['zMass'] - MZ)
    t['absYZ'] = np.abs(rapidity(t['zPt'], t['zEta'], t['zMass']))
    t['absDy'] = np.abs(rapidity(t['zPt'], t['zEta'], t['zMass']) - rapidity(t['pt'], t['eta'], t['mass']))
    t['absCosTheta'] = np.abs(sv.cosThetaHelicity(t['lmPt'], t['lmEta'], t['lmPhi'], t['zPt'], t['zEta'], t['zPhi'],
                                                  t['zMass']))


def lrScore(t, base, sig, binCenters):
    """Per-jet mean of log(p_sig / p_DY) over its E2Cn1 entries, with the baseline mean shapes per pT slice."""
    e = t['e2cn1'][:, 1:-1].astype(np.float64)
    sl = np.searchsorted(sv.PT_SLICES, t['pt'], side='right') - 1
    score = np.full(len(e), np.nan)
    for i in range(len(sv.PT_SLICES) - 1):
        m = sl == i
        ps = t['weight'][base & m & sig] @ e[base & m & sig]
        pb = t['weight'][base & m & (t['group'] == 'DY')] @ e[base & m & (t['group'] == 'DY')]
        ok = (ps > 0) & (pb > 0)
        llr = np.zeros(e.shape[1])
        llr[ok] = np.log((ps[ok] / ps.sum()) / (pb[ok] / pb.sum()))
        tot = e[m].sum(axis=1)
        with np.errstate(divide='ignore', invalid='ignore'):
            score[m] = (e[m] @ llr) / tot
    return score


def vectors(t, obs, rebin=1, dRMin=0.0, centers=None):
    """Per-jet E2C rows without the flow bins; rebin merges groups of adjacent Delta R bins (the number of bins must
    divide by it), dRMin drops the bins whose centre is below it (before merging)."""
    def one(x):
        x = x[:, 1:-1]
        if dRMin > 0:
            x = x[:, centers >= dRMin]
            x = x[:, x.shape[1] % rebin:]   # incomplete group at the low end dropped
        if x.shape[1] % rebin:
            raise ValueError('rebin %d does not divide %d bins' % (rebin, x.shape[1]))
        return x.reshape(len(x), -1, rebin).sum(axis=2)
    if obs == 'both':
        return np.concatenate([one(t['e2cn1']), one(t['e2cn2'])], axis=1)
    return one(t[obs])


class Evaluator:
    def __init__(self, t, base, obs, binCenters, lumiScale, rebin=1, slices=sv.PT_SLICES, dRMin=0.0):
        self.t, self.obs, self.binCenters, self.slices = t, obs, binCenters, slices
        self.w = t['weight'] * lumiScale
        self.V = vectors(t, obs, rebin, dRMin, binCenters)
        self.groups = [g for g, _ in GROUPS]
        self.baseStats = self.stats(base)
        self.baseYield = {g: self.w[base & (t['group'] == g)].sum() for g in self.groups}

    def stats(self, mask):
        out = {}
        for g in self.groups:
            m = mask & (self.t['group'] == g)
            out[g] = sv.Stats(self.V[m], self.w[m], self.t['pt'][m], self.slices)
        return out

    def evaluate(self, mask, signal):
        names, mass = SIGNALS[signal]
        st = self.stats(mask)
        sig = sum((st[g] for g in names[1:]), st[names[0]])
        bkgNames = [g for g in self.groups if g not in names]
        bkg = sum((st[g] for g in bkgNames[1:]), st[bkgNames[0]])
        ztot, zshape = sv.significance(sig.H, bkg.H, bkg.C)
        ztotMC, zshapeMC = sv.significance(sig.H, bkg.H, bkg.C + bkg.Cmc + sig.Cmc)
        t, w = self.t, self.w
        win = (t['e2cn1'][:, 1:-1] * sv.peakWindow(self.binCenters, t['pt'], mass)).sum(axis=1)
        isSig = np.isin(t['group'], names)
        sPeak, bPeak = (w * win)[mask & isSig].sum(), (w * win)[mask & ~isSig].sum()
        y = {g: w[mask & (t['group'] == g)].sum() for g in self.groups}
        eff = lambda gs: sum(y[g] for g in gs) / sum(self.baseYield[g] for g in gs)
        dy, dyBase = st['DY'], self.baseStats['DY']
        nS = len(self.slices) - 1
        chi2, ndf = sv.slicedShapeChi2(dy.H, dy.C, dyBase.H, nS)
        # normalised within each pT slice, as the chi2
        norm = lambda h: h / np.repeat(np.maximum(h.reshape(nS, -1).sum(axis=1), 1e-300), len(h) // nS)
        p, q = norm(dy.H), norm(dyBase.H)
        with np.errstate(divide='ignore', invalid='ignore'):
            relErr = np.sqrt(np.diag(dy.Cmc)) / dy.H
            ok = (dy.H > 0) & (q > 0) & (relErr < 0.05)
        maxDev = float(np.max(np.abs(p[ok] / q[ok] - 1))) if ok.any() else float('nan')
        return {'effSig': eff(names), 'effDY': eff(['DY']), 'effBkg': eff(bkgNames), 'S': sum(y[g] for g in names),
                'B': sum(y[g] for g in bkgNames), 'SBpeak': sPeak / bPeak, 'Ztot': ztot, 'Zshape': zshape,
                'ZtotMC': ztotMC, 'ZshapeMC': zshapeMC, 'chi2ndfDY': chi2 / ndf if ndf > 0 else float('nan'),
                'maxDevDY': maxDev}


def thresholds(x, base, isDY, w, above, effs=DY_EFFS):
    """Cut values that keep the fractions effs of the baseline DY yield, for x > c (above) or x < c."""
    m = base & isDY & np.isfinite(x)
    xs, ws = x[m], w[m]
    order = np.argsort(xs)
    cum = np.cumsum(ws[order]) / ws.sum()
    out = []
    for e in effs:
        k = np.searchsorted(cum, 1 - e if above else e)
        out.append(float(xs[order][min(k, len(xs) - 1)]))
    return out


def scans(t, base, w, signal):
    """[(label, mask)] relative to the baseline."""
    isDY = t['group'] == 'DY'
    out = [('baseline', base)]
    fixed = [('zPt > %g' % c, t['zPt'] > c) for c in (250, 300, 400, 500)]
    fixed += [('pt > %g' % c, t['pt'] > c) for c in (250, 300, 400)]
    fixed += [('|eta| < %g' % c, t['absEta'] < c) for c in (1.5, 1.0)]
    fixed += [('%g < pt/zPt < %g' % (a, b), (t['ptBalance'] > a) & (t['ptBalance'] < b))
              for a, b in ((0.7, 1.4), (0.8, 1.25), (0.9, 1.1))]
    fixed += [('|mll - mZ| < %g' % c, t['absZMassDev'] < c) for c in (20, 10, 5)]
    fixed += [('MET < %g' % c, t['metPt'] < c) for c in (100, 60, 40)]
    fixed += [('AK4 max b tag < %g' % c, t['ak4MaxBtag'] < c) for c in (0.8, 0.4, 0.1)]
    fixed += [('n AK4 <= %d' % c, t['ak4N'] <= c) for c in (2, 1, 0)]
    fixed += [('|y_Z| < %g' % c, t['absYZ'] < c) for c in (1.5, 1.0)]
    fixed += [('|y_Z - y_j| < %g' % c, t['absDy'] < c) for c in (1.5, 1.0)]
    fixed += [('|cos theta*| < %g' % c, t['absCosTheta'] < c) for c in (0.9, 0.7, 0.5)]
    fixed += [('|cos theta*| > %g' % c, t['absCosTheta'] > c) for c in (0.3, 0.5)]
    mWin = (65, 105) if signal == 'VV' else (100, 150)
    fixed += [('%g < msd < %g (mass cut, reference)' % mWin, (t['msd'] > mWin[0]) & (t['msd'] < mWin[1]))]
    out += [(label, base & m) for label, m in fixed]
    cont = [('gpV', True), ('gpHbb', True), ('pnXqqVsQCD', True), ('pnXbbVsQCD', True), ('gpWithMassZvsQCD', True),
            ('n2b1', False), ('tau21', False), ('chMultiplicity', False), ('fPeakZ' if signal == 'VV' else 'fPeakH', True),
            ('lr' + signal, True)]
    for var, above in cont:
        for e, c in zip(DY_EFFS, thresholds(t[var], base, isDY, w, above)):
            out.append(('%s %s %.4g (DY eff %g)' % (var, '>' if above else '<', c, e),
                        base & ((t[var] > c) if above else (t[var] < c))))
    return out


def slicedThresholdMask(x, pt, base, isDY, w, eff, slices):
    """x > c_k for jets in jet-pT slice k, with c_k keeping the fraction eff of the baseline DY yield of that slice (a
    flat DY efficiency in jet pT)."""
    sl = np.searchsorted(slices, pt, side='right') - 1
    keep = np.zeros(len(x), dtype=bool)
    for k in range(len(slices) - 1):
        m = sl == k
        if np.any(base & isDY & m):
            keep |= m & (x > thresholds(np.where(m, x, np.nan), base, isDY, w, True, effs=(eff,))[0])
    return keep


def taggerScans(t, base, w, signal):
    """[(label, mask)]: the signal's tagger at fixed baseline DY efficiencies, one global threshold or one per jet-pT
    slice (TEN_SLICES)."""
    var, isDY = TAGGERS[signal], t['group'] == 'DY'
    out = [('baseline', base)]
    for e, c in zip(TAGGER_EFFS, thresholds(t[var], base, isDY, w, True, effs=TAGGER_EFFS)):
        out.append(('%s > %.4g (DY eff %g)' % (var, c, e), base & (t[var] > c)))
    for e in TAGGER_EFFS:
        out.append(('%s, per-pT-slice threshold (DY eff %g in each slice)' % (var, e),
                    base & slicedThresholdMask(t[var], t['pt'], base, isDY, w, e, TEN_SLICES)))
    return out


def fmt(r):
    return ('%.3g | %.3g | %.3g | %.4f | %.1f | %.1f | %.1f | %.1f | %.2g | %.3f'
            % (r['effSig'], r['effDY'], r['effBkg'], r['SBpeak'], r['Ztot'], r['Zshape'], r['ZtotMC'], r['ZshapeMC'],
               r['chi2ndfDY'], r['maxDevDY']))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tables')
    ap.add_argument('-o', '--outdir', required=True)
    ap.add_argument('--obs', nargs='+', default=['e2cn1'], choices=['e2cn1', 'e2cn2', 'both'])
    ap.add_argument('--signals', nargs='+', default=list(SIGNALS), choices=list(SIGNALS))
    ap.add_argument('--lumi-pb', type=float, default=326030.0, help='target luminosity')
    ap.add_argument('--table-lumi-pb', type=float, default=326030.0, help='--lumi given to run.py')
    ap.add_argument('--scan', default='full', choices=['full', 'tagger'],
                    help='full: all cuts and binnings; tagger: the signal tagger (taggerScans) with 5 and 10 pT slices')
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    edges = np.geomspace(1e-3, 1.6, 41)   # configs/sensitivity.yaml dRTable
    centers = np.sqrt(edges[:-1] * edges[1:])
    t = loadTables(a.tables)
    if t['e2cn1'].shape[1] != len(edges) + 1:
        raise SystemExit('E2C rows do not match the dRTable binning')
    derive(t, centers)
    base = (t['zPt'] > 200) & (t['pt'] > 200) & (t['absEta'] < 2.0) & (t['allMediumId'] > 0)
    for s, (names, _) in SIGNALS.items():
        t['lr' + s] = lrScore(t, base, np.isin(t['group'], names), centers)
    results = {}
    lines = ['# Sensitivity scans', '', 'Luminosity %.0f pb^-1; tables %s.' % (a.lumi_pb, a.tables), '',
             'Columns: eff sig | eff DY | eff bkg | S/B peak window | Z_tot | Z_shape | Z_tot, Z_shape (+MC stat cov.) | '
             'DY chi2/ndf vs baseline | DY max |ratio - 1|', '']
    if a.scan == 'tagger':
        for signal in a.signals:
            cuts = taggerScans(t, base, t['weight'], signal)
            for obs in a.obs:
                for nS, slices in ((5, sv.PT_SLICES), (10, TEN_SLICES)):
                    ev = Evaluator(t, base, obs, centers, a.lumi_pb / a.table_lumi_pb, slices=slices)
                    lines += ['## Tagger, %s, %s, %d pT slices' % (signal, obs, nS), '',
                              '| cut | eff sig | eff DY | eff bkg | S/B peak | Z_tot | Z_shape | Z_tot MC | Z_shape MC | DY chi2/ndf | DY max dev |',
                              '|---|---|---|---|---|---|---|---|---|---|---|']
                    for label, mask in cuts:
                        r = ev.evaluate(mask, signal)
                        results.setdefault(signal, {}).setdefault('%s/%d' % (obs, nS), {})[label] = r
                        lines.append('| %s | %s |' % (label, fmt(r)))
                        print(signal, obs, nS, label, fmt(r), flush=True)
                    lines.append('')
        with open(os.path.join(a.outdir, 'scan.md'), 'w') as f:
            f.write('\n'.join(lines) + '\n')
        with open(os.path.join(a.outdir, 'scan.json'), 'w') as f:
            json.dump(results, f, indent=1)
        return
    for signal in a.signals:
        cuts = scans(t, base, t['weight'], signal)
        for obs in a.obs:
            ev = Evaluator(t, base, obs, centers, a.lumi_pb / a.table_lumi_pb)
            lines += ['## %s, %s' % (signal, obs), '',
                      '| cut | eff sig | eff DY | eff bkg | S/B peak | Z_tot | Z_shape | Z_tot MC | Z_shape MC | DY chi2/ndf | DY max dev |',
                      '|---|---|---|---|---|---|---|---|---|---|---|']
            for label, mask in cuts:
                r = ev.evaluate(mask, signal)
                results.setdefault(signal, {}).setdefault(obs, {})[label] = r
                lines.append('| %s | %s |' % (label, fmt(r)))
                print(signal, obs, label, fmt(r), flush=True)
            lines.append('')
    # E2C binning at the baseline: Delta R bin merging, jet-pT slicing, low-Delta R cut
    binnings = [('40 dR bins, 5 pT slices', {}), ('20 dR bins', {'rebin': 2}), ('10 dR bins', {'rebin': 4}),
                ('5 dR bins', {'rebin': 8}), ('1 pT slice', {'slices': np.array([200.0, np.inf])}),
                ('10 pT slices', {'slices': np.array([200, 250, 300, 350, 400, 500, 600, 800, 1000, 1500, np.inf])}),
                ('dR > 0.01', {'dRMin': 0.01}), ('dR > 0.1', {'dRMin': 0.1})]
    for signal in a.signals:
        for obs in a.obs:
            lines += ['## Binning, %s, %s (baseline cuts)' % (signal, obs), '',
                      '| binning | eff sig | eff DY | eff bkg | S/B peak | Z_tot | Z_shape | Z_tot MC | Z_shape MC | DY chi2/ndf | DY max dev |',
                      '|---|---|---|---|---|---|---|---|---|---|---|']
            for label, kw in binnings:
                r = Evaluator(t, base, obs, centers, a.lumi_pb / a.table_lumi_pb, **kw).evaluate(base, signal)
                results.setdefault('binning', {}).setdefault(signal, {}).setdefault(obs, {})[label] = r
                lines.append('| %s | %s |' % (label, fmt(r)))
                print('binning', signal, obs, label, fmt(r), flush=True)
            lines.append('')
    with open(os.path.join(a.outdir, 'scan.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(a.outdir, 'scan.json'), 'w') as f:
        json.dump(results, f, indent=1)


if __name__ == '__main__':
    main()
