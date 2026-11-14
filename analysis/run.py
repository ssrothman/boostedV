#!/usr/bin/env python3
"""Runs ZXProcessor over merged production samples or local files and saves the output (coffea.util.save).

  python3 run.py --tag 20261113_zxtest [--samples NAME ...] [--lumi PB] -o out.coffea [--workers 8]
  python3 run.py --files nano.root ... --name test -o out.coffea
--lumi (pb^-1) needs every sample's cross section in xsec.yaml; without it the MC weight is the bare genWeight.
"""
import argparse

from coffea import processor
from coffea.util import save

import samples
from processor import ZXProcessor
from schema import BoostedVSchema


def fileset(args):
    if args.files:
        return {args.name: {'files': {f: 'Events' for f in args.files}, 'metadata': {'sample': args.name}}}
    out = {}
    for name, s in samples.load(args.tag, args.samples).items():
        fs = s.fileset()
        if args.lumi is not None:
            fs['metadata']['lumiScale'] = s.lumiScale(args.lumi)
        out[name] = fs
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--tag')
    src.add_argument('--files', nargs='+')
    ap.add_argument('--samples', nargs='+')
    ap.add_argument('--name', default='local')
    ap.add_argument('--lumi', type=float)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--chunksize', type=int, default=200000)
    ap.add_argument('-o', '--output', required=True)
    args = ap.parse_args()
    run = processor.Runner(executor=processor.FuturesExecutor(workers=args.workers), schema=BoostedVSchema,
                           chunksize=args.chunksize)
    out = run(fileset(args), processor_instance=ZXProcessor(), treename='Events')
    save(out, args.output)
    for k, v in sorted(out['cutflow'].items()):
        print(k, v)


if __name__ == '__main__':
    main()
