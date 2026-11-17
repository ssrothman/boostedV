#!/usr/bin/env python3
"""Runs the configured analysis over merged production samples or local NANO files.

  python3 run.py configs/zxtest.yaml --tag 20261113_zxtest [--samples NAME ...] [--lumi PB] -o out.coffea
  python3 run.py configs/zxtest.yaml --files [NAME=]nano.root ... [--name local] -o out.coffea
  python3 run.py configs/zxtest.yaml --fileset fileset.json -o out.coffea       (coffea fileset, metadata included)
  [--workers N] [--chunksize N] [--export out.root | out.pkl]
  --backend condor [--files-per-job 20] [--cpus 1] [--memory MB] [--condor-name NAME] [--dryrun]: submit LPC condor
  jobs instead of running locally; then `condor.py status|resubmit|collect work/NAME` (collect writes -o).
--lumi (pb^-1) needs every sample's cross section in xsec.yaml; without it the MC weight is genWeight alone.
"""
import argparse
import json
import pickle

from coffea import processor
from coffea.util import save

from bvana import config, samples
from bvana.processor import Processor
from bvana.schema import BoostedVSchema


def fileset(args):
    if args.fileset:
        with open(args.fileset) as f:
            return json.load(f)
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
    src.add_argument('--fileset')
    ap.add_argument('--samples', nargs='+')
    ap.add_argument('--name', default='local')
    ap.add_argument('--lumi', type=float)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--chunksize', type=int, default=20000, help='events per chunk; peak memory grows with it')
    ap.add_argument('-o', '--output', required=True)
    ap.add_argument('--export')
    ap.add_argument('--backend', default='local', choices=['local', 'condor'])
    ap.add_argument('--files-per-job', type=int, default=20)
    ap.add_argument('--cpus', type=int, default=1, help='condor: request_cpus, also the workers per job')
    ap.add_argument('--memory', type=int, default=2500, help='condor: request_memory in MB')
    ap.add_argument('--condor-name', help='condor: work/<name> (default: the output file name)')
    ap.add_argument('--dryrun', action='store_true', help='condor: prepare the jobs, submit nothing')
    args = ap.parse_args()
    cfg = config.load(args.config)
    if args.backend == 'condor':
        if args.export:
            raise SystemExit('--export is not available with --backend condor')
        import condor
        condor.submit(fileset(args), args)
        return
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
