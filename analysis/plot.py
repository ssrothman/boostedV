#!/usr/bin/env python3
"""Plots histograms from a run.py output.

Overlay samples (default) or regions, or the bins of one axis (--split), after slicing and projecting:
  python3 plot.py out.coffea --hist bosonPt --region ZmumuReco --logy -o zpt.pdf
  python3 plot.py out.coffea --hist E2Cn1 --region ZmumuReco --samples DY --split jetpt --project dR \\
                  --norm area --width log --logx -o e2c.pdf
  python3 plot.py out.coffea --hist E1CHelicity --region ZmumuReco --samples TT -o e1c.pdf      (2D map)
  python3 plot.py out.coffea --hist jetPt --regions ZmumuReco ZeeReco --samples TT --ratio ZmumuReco -o r.pdf
--slice AXIS=LO:HI (bin edges) sums over a range; --project keeps the listed axes. A result with two axes is drawn
as a map (one figure per sample).
"""
import argparse
import os

import numpy as np
from coffea.util import load

from bvana import plotting


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input')
    ap.add_argument('--hist', required=True)
    reg = ap.add_mutually_exclusive_group(required=True)
    reg.add_argument('--region')
    reg.add_argument('--regions', nargs='+', help='overlay these regions (one sample)')
    ap.add_argument('--samples', nargs='+')
    ap.add_argument('--slice', action='append', default=[], metavar='AXIS=LO:HI')
    ap.add_argument('--project', nargs='+')
    ap.add_argument('--split', metavar='AXIS', help='overlay each bin of AXIS (one sample, one region)')
    ap.add_argument('--norm', default='none', choices=['none', 'area'])
    ap.add_argument('--width', default='none', choices=['none', 'linear', 'log'])
    ap.add_argument('--stack', action='store_true')
    ap.add_argument('--ratio', metavar='LEGEND', help='ratio panel with this curve as denominator')
    ap.add_argument('--ratio-sum', metavar='PREFIX',
                    help='ratio panel of the sum of all samples to the sum of those starting with PREFIX')
    ap.add_argument('--group', action='append', default=[], metavar='NAME=PREFIX[,PREFIX]',
                    help='sum the samples starting with any PREFIX into one curve NAME (empty PREFIX: all)')
    ap.add_argument('--ylim-rel', type=float, nargs=2, metavar=('LO', 'HI'),
                    help='main-panel y range as multiples of the largest bin of the (stacked) total')
    ap.add_argument('--logx', action='store_true')
    ap.add_argument('--logy', action='store_true')
    ap.add_argument('--logz', action='store_true')
    ap.add_argument('--lumi', type=float, help='luminosity label in fb^-1')
    ap.add_argument('-o', '--output', required=True)
    a = ap.parse_args()
    out = load(a.input)
    if a.hist not in out['hists']:
        raise SystemExit('no histogram %s; have %s' % (a.hist, sorted(out['hists'])))
    byRegion = out['hists'][a.hist]
    slices = [plotting.parseSlice(s) for s in a.slice]
    curves = {}
    if a.regions:
        if not a.samples or len(a.samples) != 1:
            raise SystemExit('--regions needs exactly one --samples')
        for r in a.regions:
            curves[r] = byRegion[r][a.samples[0]]
    else:
        samples = a.samples or sorted(byRegion[a.region])
        curves = {s: byRegion[a.region][s] for s in samples}
    curves = {k: plotting.reduce(h, slices) for k, h in curves.items()}
    curves = plotting.group(curves, a.group)
    if a.split:
        if len(curves) != 1:
            raise SystemExit('--split needs one sample and one region')
        (key, h), = curves.items()
        edges = h.axes[a.split].edges
        curves = {}
        for lo, hi in zip(edges[:-1], edges[1:]):
            curves['%s [%g, %g)' % (a.split, lo, hi)] = plotting.reduce(h, [(a.split, lo, hi)])
    if a.project:
        curves = {k: h.project(*a.project) for k, h in curves.items()}
    ndim = {len(h.axes) for h in curves.values()}
    if ndim == {1}:
        fig = plotting.plot1d(curves, norm=a.norm, width=a.width, stack=a.stack, ratio=a.ratio, logx=a.logx,
                              logy=a.logy, lumi=a.lumi, ylimRel=a.ylim_rel,
                              ratioSum=(a.ratio_sum, [k for k in curves if k.startswith(a.ratio_sum)]) if a.ratio_sum else None)
        fig.savefig(a.output, bbox_inches='tight')
        print('wrote', a.output)
    elif ndim == {2}:
        base, ext = os.path.splitext(a.output)
        for k, h in curves.items():
            fig = plotting.plot2d(h, norm=a.norm, logz=a.logz, lumi=a.lumi)
            path = a.output if len(curves) == 1 else '%s_%s%s' % (base, k.replace(' ', '_'), ext)
            fig.savefig(path, bbox_inches='tight')
            print('wrote', path)
    else:
        raise SystemExit('after slicing/projection the histograms have %s axes; use --project' % sorted(ndim))


if __name__ == '__main__':
    np.seterr(divide='ignore', invalid='ignore')
    main()
