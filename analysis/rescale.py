#!/usr/bin/env python3
"""Applies xsec * lumi / genEventSumw to an unnormalised run.py output (as run.py --lumi would), without rerunning.

  python3 rescale.py out.coffea --tag 20261116_zxb2b --lumi 1 -o out_xsec.coffea
Histograms have Weight storage, so values scale by s and variances by s^2; cutflow sumw and sumw scale by s.
"""
import argparse

from coffea.util import load, save

from bvana import samples


def rescale(out, scales):
    for byRegion in out['hists'].values():
        for bySample in byRegion.values():
            for name, h in bySample.items():
                v = h.view(flow=True)
                v['value'] *= scales[name]
                v['variance'] *= scales[name] ** 2
    for bySample in out['cutflow'].values():
        for name, flow in bySample.items():
            for c in flow.values():
                c['sumw'] *= scales[name]
    for name in out['sumw']:
        out['sumw'][name] *= scales[name]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input')
    ap.add_argument('--tag', required=True)
    ap.add_argument('--lumi', type=float, required=True, help='pb^-1')
    ap.add_argument('-o', '--output', required=True)
    a = ap.parse_args()
    out = load(a.input)
    scales = {n: s.lumiScale(a.lumi) for n, s in samples.load(a.tag, list(out['sumw'])).items()}
    save(rescale(out, scales), a.output)


if __name__ == '__main__':
    main()
