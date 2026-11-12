#!/usr/bin/env python3
"""Merges one sample's job outputs (run inside cmsenv).

Usage: merge.py --tag T SAMPLE [SAMPLE ...] [--allow-missing] [--stage]
       merge.py --dir OUTDIR --out LOCALDIR [--data]          (any directory of job outputs)

Writes into <work>/<tag>/<sample>/merged/ (or --out):
  hists.root          hadd of every complete job's histogram file
  sample.json         jobs used and missing, NANO file list, Events written, and for MC the Runs-tree sums
                      genEventCount/genEventSumw/genEventSumw2 over the same jobs
  processedLumis.json (data) run -> lumi ranges from the NANO LuminosityBlocks trees
--stage copies merged/ to <outDir>/merged/ on EOS.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import outputs  # noqa: E402

WORK = os.path.join(HERE, 'work')
GEN_SUMS = ('genEventCount', 'genEventSumw', 'genEventSumw2')


def lumiRanges(pairs):
    """{run: [[first, last], ...]} from (run, lumi) pairs, in certification-JSON form."""
    out = {}
    for run, lumi in sorted(set(pairs)):
        r = out.setdefault(str(run), [])
        if r and r[-1][1] == lumi - 1:
            r[-1][1] = lumi
        else:
            r.append([lumi, lumi])
    return out


def nanoSummary(nanoFiles, isMC):
    import uproot
    summary = {'eventsWritten': 0}
    if isMC:
        summary.update({k: 0 for k in GEN_SUMS})
    lumis = []
    for f in nanoFiles:
        # CMSSW's uproot has no fsspec-xrootd, so remote files go through the XRootD bindings directly.
        kw = {'handler': uproot.source.xrootd.XRootDSource} if f.startswith('root://') else {}
        with uproot.open(f, **kw) as nano:
            summary['eventsWritten'] += nano['Events'].num_entries
            if isMC:
                runs = nano['Runs'].arrays(list(GEN_SUMS), library='np')
                for k in GEN_SUMS:
                    summary[k] += runs[k].sum().item()
            else:
                lb = nano['LuminosityBlocks'].arrays(['run', 'luminosityBlock'], library='np')
                lumis += zip(lb['run'].tolist(), lb['luminosityBlock'].tolist())
    return summary, (lumiRanges(lumis) if not isMC else None)


def merge(outDir, localOut, isMC, expected=None, allowMissing=False, meta=None):
    """Merges the complete jobs under outDir into localOut; returns the sample.json dict."""
    jobs, incomplete = outputs.pairJobs(outputs.listRoot(outDir))
    if not jobs:
        raise RuntimeError('no complete jobs under %s' % outDir)
    missing = sorted(set(expected) - set(jobs)) if expected is not None else incomplete
    unexpected = sorted(set(jobs) - set(expected)) if expected is not None else []
    if unexpected:
        raise RuntimeError('outputs of jobs that were not submitted: %s' % unexpected)
    if missing and not allowMissing:
        raise RuntimeError('%d jobs missing (%s); rerun after resubmission or pass --allow-missing'
                           % (len(missing), missing[:20]))
    os.makedirs(localOut, exist_ok=True)
    idx = sorted(jobs)
    hists = os.path.join(localOut, 'hists.root')
    subprocess.run(['hadd', '-f', hists] + [jobs[i]['hists'] for i in idx], check=True,
                   stdout=subprocess.DEVNULL)
    nano = [jobs[i]['nano'] for i in idx]
    summary, lumis = nanoSummary(nano, isMC)
    info = dict(meta or {}, isMC=isMC, jobs=idx, missing=missing, nanoFiles=nano, **summary)
    with open(os.path.join(localOut, 'sample.json'), 'w') as f:
        json.dump(info, f, indent=1)
    if lumis is not None:
        with open(os.path.join(localOut, 'processedLumis.json'), 'w') as f:
            json.dump(lumis, f)
    return info


def expectedOrFail(workDir):
    """The submitted job indices; without them a job that wrote nothing would go unnoticed."""
    expected = outputs.expectedJobs(workDir)
    if expected is None:
        raise RuntimeError('%s: no job list (CRAB: run status.py first)' % workDir)
    return expected


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('samples', nargs='*')
    ap.add_argument('--tag')
    ap.add_argument('--dir', help='merge an arbitrary output directory (with --out)')
    ap.add_argument('--out')
    ap.add_argument('--data', action='store_true', help='with --dir: the outputs are data')
    ap.add_argument('--allow-missing', action='store_true')
    ap.add_argument('--stage', action='store_true', help='copy merged/ next to the job outputs on EOS')
    args = ap.parse_args()
    if args.dir:
        if not args.out or args.samples or args.tag:
            ap.error('--dir needs --out and no samples or --tag')
        info = merge(args.dir, args.out, not args.data, allowMissing=True)
        print('%d jobs merged into %s' % (len(info['jobs']), args.out))
        return
    if not args.tag or not args.samples:
        ap.error('give --tag and samples')
    for name in args.samples:
        workDir = os.path.join(WORK, args.tag, name)
        sub = outputs.submission(workDir)
        outDir = sub['outDir']
        localOut = os.path.join(workDir, 'merged')
        info = merge(outDir, localOut, sub['isMC'], expectedOrFail(workDir), args.allow_missing,
                     meta={'sample': name, 'tag': args.tag, 'outDir': outDir})
        print('%s: %d jobs merged, %d missing -> %s' % (name, len(info['jobs']), len(info['missing']), localOut))
        if args.stage:
            for f in sorted(os.listdir(localOut)):
                subprocess.run(['xrdcp', '-f', os.path.join(localOut, f), '%s/merged/%s' % (outDir, f)], check=True)


if __name__ == '__main__':
    main()
