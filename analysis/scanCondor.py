#!/usr/bin/env python3
"""sensitivity.py scans on LPC HTCondor: each scan of a scan file is split into one job per (tagger pair or signal,
observable), run in the cvmfs coffea container on tables read from EOS, then collected into <outBase>/<scan>/ as if
run locally (scan.md, scan.json, run.log).

  python3 scanCondor.py submit SCANS.yaml -n NAME [--memory 12000] [--dryrun]
  python3 scanCondor.py status work/NAME
  python3 scanCondor.py resubmit work/NAME [--memory MB]
  python3 scanCondor.py collect work/NAME [--allow-missing]

SCANS.yaml: {outBase: dir, tables: {key: xrootd URL}, scans: {name: {tables: key, args: [sensitivity.py options],
split: {taggers: [...] | signals: [...], obs: [...]}}}}. A job runs args + --taggers T (or --signals S) + --obs O.
"""
import argparse
import json
import os
import subprocess
import sys
import tarfile

import yaml

ANALYSIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ANALYSIS)
from condor import IMAGE, WORK, codeState, load, logStatus, proxyPath, removeFromQueue  # noqa: E402
from condor import condorCommand, parseSubmit  # noqa: E402


def jobsOf(spec):
    """[(scan, sensitivity.py argv without the tables and -o)] in the order a local run writes its sections."""
    out = []
    for name, s in spec['scans'].items():
        split = s['split']
        (key, values), = [(k, split[k]) for k in ('taggers', 'signals') if k in split]
        for v in values:
            for o in split['obs']:
                out.append({'scan': name, 'tables': spec['tables'][s['tables']],
                            'args': list(map(str, s['args'])) + ['--' + key, v, '--obs', o]})
    return out


def jdl(workDir, proxy, memory):
    d = workDir
    return '\n'.join([
        'universe = vanilla',
        'executable = %s/inputs/scan_job.sh' % d,
        'arguments = $(idx)',
        '+ApptainerImage = "%s"' % IMAGE,
        'transfer_input_files = %s/inputs/analysis.tgz, %s/inputs/job_$(idx).json' % (d, d),
        'should_transfer_files = YES',
        'when_to_transfer_output = ON_EXIT',
        'transfer_output_files = out_$(idx).tgz',
        'transfer_output_remaps = "out_$(idx).tgz = %s/parts/out_$(idx).tgz"' % d,
        'x509userproxy = %s' % proxy,
        'request_cpus = 1',
        'request_memory = %d' % memory,
        'output = %s/logs/job_$(idx)_$(Cluster).out' % d,
        'error = %s/logs/job_$(idx)_$(Cluster).err' % d,
        'log = %s/logs/condor.log' % d,
        'queue idx from %s/inputs/queue.txt' % d,
        ''])


JOB_SH = """#!/bin/bash
# Condor job of scanCondor.py, run in the coffea container. Arg: job index.
set -e
echo "job $1 on $(hostname) at $(date)"
tar -xzf analysis.tgz
python3 scanCondor.py job job_$1.json out_$1.tgz
echo "done at $(date)"
"""


def runJob(jobFile, outTgz):
    """Inside the job: fetch the tables, run sensitivity.py, pack its outdir and log."""
    with open(jobFile) as f:
        job = json.load(f)
    subprocess.run(['xrdcp', '-s', job['tables'], 'tables.coffea'], check=True)
    with open('scan.log', 'w') as log:
        rc = subprocess.run([sys.executable, 'sensitivity.py', 'tables.coffea', '-o', 'out'] + job['args'],
                            stdout=log, stderr=subprocess.STDOUT).returncode
    if rc:
        sys.stdout.write(open('scan.log').read()[-5000:])
        raise SystemExit('sensitivity.py exit %d' % rc)
    with tarfile.open(outTgz, 'w:gz') as tar:
        tar.add('out/scan.md', arcname='scan.md')
        tar.add('out/scan.json', arcname='scan.json')
        tar.add('scan.log', arcname='run.log')
    os.remove('tables.coffea')


def queue(workDir, state, jobs, dryrun):
    with open(os.path.join(workDir, 'inputs', 'queue.txt'), 'w') as f:
        f.write(''.join('%d\n' % j for j in jobs))
    with open(os.path.join(workDir, 'submit.jdl'), 'w') as f:
        f.write(jdl(workDir, state['proxy'], state['memory']))
    if not dryrun:
        c = parseSubmit(condorCommand('condor_submit', os.path.join(workDir, 'submit.jdl')))
        c['jobs'], c['memory'] = list(jobs), state['memory']
        state['clusters'].append(c)
    with open(os.path.join(workDir, 'state.json'), 'w') as f:
        json.dump(state, f, indent=1)


def submit(args):
    with open(args.scans) as f:
        spec = yaml.safe_load(f)
    workDir = os.path.join(WORK, args.name)
    if os.path.exists(workDir):
        raise SystemExit('%s exists; pick another -n' % workDir)
    for sub in ('inputs', 'parts', 'logs'):
        os.makedirs(os.path.join(workDir, sub))
    jobs = jobsOf(spec)
    for k, j in enumerate(jobs):
        with open(os.path.join(workDir, 'inputs', 'job_%d.json' % k), 'w') as f:
            json.dump(j, f)
    skip = lambda info: None if '__pycache__' in info.name or '/_ext' in info.name else info
    with tarfile.open(os.path.join(workDir, 'inputs', 'analysis.tgz'), 'w:gz') as tar:
        for p in ('bvana', 'sensitivity.py', 'scanCondor.py', 'condor.py'):
            tar.add(os.path.join(ANALYSIS, p), arcname=p, filter=skip)
        tar.add(os.path.join(os.path.dirname(ANALYSIS), 'simulation', 'production', 'condorBackend.py'),
                arcname='condorBackend.py')
    sh = os.path.join(workDir, 'inputs', 'scan_job.sh')
    with open(sh, 'w') as f:
        f.write(JOB_SH)
    os.chmod(sh, 0o755)
    state = {'scans': os.path.abspath(args.scans), 'outBase': os.path.abspath(os.path.join(os.path.dirname(args.scans),
             spec['outBase'])), 'order': list(spec['scans']), 'nJobs': len(jobs), 'memory': args.memory,
             'proxy': proxyPath(), 'image': IMAGE, 'code': codeState(), 'clusters': []}
    queue(workDir, state, range(len(jobs)), args.dryrun)
    print('%s: %d jobs %s' % (workDir, len(jobs), '(dry run)' if args.dryrun else 'submitted'))


def status(workDir):
    state = load(workDir)
    log = logStatus(workDir, state)
    out = {}
    for j in range(state['nJobs']):
        if os.path.exists(os.path.join(workDir, 'parts', 'out_%d.tgz' % j)):
            out[j] = 'complete'
        else:
            out[j] = {'done': 'failed', None: 'unsubmitted'}.get(log.get(j), log.get(j))
    return out


def merge(a, b, where=''):
    """Recursive union of two result dicts; a key present in both must hold dicts."""
    for k, v in b.items():
        if k in a:
            if not (isinstance(a[k], dict) and isinstance(v, dict)):
                raise ValueError('result %s/%s produced by two jobs' % (where, k))
            merge(a[k], v, where + '/' + k)
        else:
            a[k] = v
    return a


def splitMarkdown(text):
    """(header lines, [section texts]) of a scan.md; sections start at '## '."""
    head, secs = [], []
    for line in text.split('\n'):
        if line.startswith('## '):
            secs.append([line])
        elif secs:
            secs[-1].append(line)
        else:
            head.append(line)
    return head, ['\n'.join(s).rstrip('\n') for s in secs]


def collectScan(parts):
    """(scan.md, scan.json dict, run.log) of one scan from its jobs' (md, json, log) in job order. Full scans write the
    binning sections after all cut sections, as a local run does."""
    head, secs, res, logs = None, [], {}, []
    for md, js, log in parts:
        h, s = splitMarkdown(md)
        head = head if head is not None else h
        secs += s
        merge(res, js)
        logs.append(log)
    secs.sort(key=lambda s: s.startswith('## Binning'))   # stable
    return '\n'.join(head).rstrip('\n') + '\n\n' + '\n\n'.join(secs) + '\n', res, ''.join(logs)


def collect(workDir, allowMissing):
    state = load(workDir)
    st = status(workDir)
    missing = [j for j, s in st.items() if s != 'complete']
    if missing and not allowMissing:
        raise SystemExit('jobs not complete: %s' % ' '.join(map(str, missing)))
    byScan = {}
    for j in range(state['nJobs']):
        if j in missing:
            continue
        with open(os.path.join(workDir, 'inputs', 'job_%d.json' % j)) as f:
            scan = json.load(f)['scan']
        with tarfile.open(os.path.join(workDir, 'parts', 'out_%d.tgz' % j)) as tar:
            md, js, log = (tar.extractfile(n).read().decode() for n in ('scan.md', 'scan.json', 'run.log'))
        byScan.setdefault(scan, []).append((md, json.loads(js), log))
    for scan in state['order']:
        if scan not in byScan:
            continue
        md, res, log = collectScan(byScan[scan])
        out = os.path.join(state['outBase'], scan)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, 'scan.md'), 'w') as f:
            f.write(md)
        with open(os.path.join(out, 'scan.json'), 'w') as f:
            json.dump(res, f, indent=1)
        with open(os.path.join(out, 'run.log'), 'w') as f:
            f.write(log)
        print('wrote %s from %d jobs' % (out, len(byScan[scan])))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('submit')
    s.add_argument('scans')
    s.add_argument('-n', '--name', required=True)
    s.add_argument('--memory', type=int, default=12000)
    s.add_argument('--dryrun', action='store_true')
    for c in ('status', 'resubmit', 'collect'):
        p = sub.add_parser(c)
        p.add_argument('workdir')
        if c == 'resubmit':
            p.add_argument('--memory', type=int)
        if c == 'collect':
            p.add_argument('--allow-missing', action='store_true')
    j = sub.add_parser('job')
    j.add_argument('jobfile')
    j.add_argument('out')
    a = ap.parse_args()
    if a.cmd == 'submit':
        submit(a)
    elif a.cmd == 'job':
        runJob(a.jobfile, a.out)
    elif a.cmd == 'status':
        st = status(a.workdir)
        counts = {}
        for v in st.values():
            counts[v] = counts.get(v, 0) + 1
        print(', '.join('%s %d' % kv for kv in sorted(counts.items())))
        bad = sorted(j for j, v in st.items() if v == 'failed')
        if bad:
            print('failed jobs:', ' '.join(map(str, bad)))
    elif a.cmd == 'resubmit':
        state = load(a.workdir)
        jobs = sorted(j for j, v in status(a.workdir).items() if v in ('failed', 'unsubmitted'))
        if a.memory:
            state['memory'] = a.memory
        removeFromQueue(state, jobs)
        if jobs:
            queue(a.workdir, state, jobs, False)
        print('resubmitted %d jobs' % len(jobs))
    else:
        collect(a.workdir, a.allow_missing)


if __name__ == '__main__':
    main()
