#!/usr/bin/env python3
"""Runs the configured analysis over merged production samples or local NANO files.

  python3 run.py configs/zxtest.yaml --tag 20261113_zxtest [--samples NAME ...] [--lumi PB] -o out.coffea
  python3 run.py configs/zxtest.yaml --files [NAME=]nano.root ... [--name local] -o out.coffea
  [--workers N] [--chunksize N] [--export out.root | out.pkl]
--lumi (pb^-1) needs every sample's cross section in xsec.yaml; without it the MC weight is genWeight alone.
"""
import argparse
import pickle

from coffea import processor
from coffea.util import save

from bvana import config, samples
from bvana.processor import Processor
from bvana.schema import BoostedVSchema


def fileset(args):
    if args.files:
        out = {}
        for item in args.files:
            name, path = item.split('=', 1) if '=' in item else (args.name, item)
            out.setdefault(name, {'files': {}, 'metadata': {'sample': name}})['files'][path] = 'Events'
        return out
    out = {}
    for name, s in samples.load(args.tag, args.samples).items():
        fs = s.fileset()
        if args.lumi is not None:
            fs['metadata']['lumiScale'] = s.lumiScale(args.lumi)
        out[name] = fs
    return out


def export(out, path):
    flat = {'%s/%s/%s' % (s, r, h): x for h, d in out['hists'].items() for r, dd in d.items() for s, x in dd.items()}
    if path.endswith('.pkl'):
        with open(path, 'wb') as f:
            pickle.dump(out, f)
    elif path.endswith('.root'):
        import uproot
        with uproot.recreate(path) as f:
            for k, x in flat.items():
                f[k] = x
    else:
        raise SystemExit('--export: .root or .pkl')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('config')
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--tag')
    src.add_argument('--files', nargs='+')
    ap.add_argument('--samples', nargs='+')
    ap.add_argument('--name', default='local')
    ap.add_argument('--lumi', type=float)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--chunksize', type=int, default=200000)
    ap.add_argument('-o', '--output', required=True)
    ap.add_argument('--export')
    args = ap.parse_args()
    cfg = config.load(args.config)
    run = processor.Runner(executor=processor.FuturesExecutor(workers=args.workers), schema=BoostedVSchema,
                           chunksize=args.chunksize)
    out = run(fileset(args), processor_instance=Processor(cfg), treename='Events')
    out['config'] = args.config
    save(out, args.output)
    if args.export:
        export(out, args.export)
    for r, d in out['cutflow'].items():
        for s, flow in d.items():
            print('%s %s: ' % (r, s) + ', '.join('%s %d' % (c, v['n']) for c, v in flow.items()))


if __name__ == '__main__':
    main()
