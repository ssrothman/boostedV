#!/usr/bin/env python3
"""LPC HTCondor backend for run.py: one job per K files of a sample, run in the cvmfs coffea container, then a local
collect step that accumulates the per-job outputs.

  python3 run.py CONFIG --tag TAG [--lumi PB] -o out.coffea --backend condor [--files-per-job 20] [--cpus 1]
  python3 condor.py status  work/<name>
  python3 condor.py resubmit work/<name>          jobs that ended without an output
  python3 condor.py collect work/<name> [--allow-missing]      writes the -o path given at submission
Work directory work/<name>/: inputs/ (code snapshot, per-job filesets), parts/, logs/, state.json.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tarfile

ANALYSIS = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ANALYSIS, 'work')
IMAGE = '/cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-almalinux9:2026.11.0-py3.13'
sys.path.insert(0, os.path.join(os.path.dirname(ANALYSIS), 'simulation', 'production'))
from condorBackend import condorCommand, parseSubmit  # noqa: E402


def split(fileset, filesPerJob):
    """[(sample, {sample: entry with K of its files})] in file order; a job never mixes samples."""
    jobs = []
    for name, entry in fileset.items():
        files = list(entry['files'].items())
        for i in range(0, len(files), filesPerJob):
            jobs.append({name: {'files': dict(files[i:i + filesPerJob]), 'metadata': entry['metadata']}})
    return jobs


def proxyPath(minHours=24):
    left = int(subprocess.run(['voms-proxy-info', '-timeleft'], capture_output=True, text=True).stdout.strip() or 0)
    if left < minHours * 3600:
        raise SystemExit('grid proxy has %.1f h left; run voms-proxy-init -voms cms -valid 192:00' % (left / 3600))
    return subprocess.run(['voms-proxy-info', '-path'], check=True, capture_output=True, text=True).stdout.strip()


def codeState():
    git = lambda *a: subprocess.run(['git', '-C', ANALYSIS] + list(a), capture_output=True, text=True).stdout.strip()
    return {'commit': git('rev-parse', 'HEAD'), 'dirty': git('status', '--porcelain', '--', '.')}


def snapshot(workDir, configPath):
    """Code and config as they are now: condor transfers inputs only when a job starts."""
    path = os.path.join(workDir, 'inputs', 'analysis.tgz')
    skip = lambda info: None if '__pycache__' in info.name else info
    with tarfile.open(path, 'w:gz') as tar:
        tar.add(os.path.join(ANALYSIS, 'bvana'), arcname='bvana', filter=skip)
        tar.add(os.path.join(ANALYSIS, 'run.py'), arcname='run.py')
        tar.add(configPath, arcname='config.yaml')
    return path


def jdl(workDir, proxy, cpus, memory):
    d = workDir
    return '\n'.join([
        'universe = vanilla',
        'executable = %s/inputs/condor_job.sh' % d,
        'arguments = $(idx) %d $(chunksize)' % cpus,
        '+ApptainerImage = "%s"' % IMAGE,
        'transfer_input_files = %s/inputs/analysis.tgz, %s/inputs/job_$(idx).json' % (d, d),
        'should_transfer_files = YES',
        'when_to_transfer_output = ON_EXIT',
        'transfer_output_files = part_$(idx).coffea',
        'transfer_output_remaps = "part_$(idx).coffea = %s/parts/part_$(idx).coffea"' % d,
        'x509userproxy = %s' % proxy,
        'request_cpus = %d' % cpus,
        'request_memory = %d' % memory,
        'output = %s/logs/job_$(idx)_$(Cluster).out' % d,
        'error = %s/logs/job_$(idx)_$(Cluster).err' % d,
        'log = %s/logs/condor.log' % d,
        'queue idx, chunksize from %s/inputs/queue.txt' % d,
        ''])


def queue(workDir, state, jobs, dryrun):
    with open(os.path.join(workDir, 'inputs', 'queue.txt'), 'w') as f:
        f.write(''.join('%d %d\n' % (j, state['chunksize']) for j in jobs))
    with open(os.path.join(workDir, 'submit.jdl'), 'w') as f:
        f.write(jdl(workDir, state['proxy'], state['cpus'], state['memory']))
    if not dryrun:
        c = parseSubmit(condorCommand('condor_submit', os.path.join(workDir, 'submit.jdl')))
        c['jobs'] = list(jobs)   # process k of the cluster runs job jobs[k]
        state['clusters'].append(c)
    with open(os.path.join(workDir, 'state.json'), 'w') as f:
        json.dump(state, f, indent=1)


def submit(fileset, args):
    """run.py --backend condor: writes work/<name>/ and submits (unless --dryrun); returns the work directory."""
    name = args.condor_name or os.path.splitext(os.path.basename(args.output))[0]
    workDir = os.path.join(WORK, name)
    if os.path.exists(workDir):
        raise SystemExit('%s exists; pick another --condor-name' % workDir)
    for sub in ('inputs', 'parts', 'logs'):
        os.makedirs(os.path.join(workDir, sub))
    jobs = split(fileset, args.files_per_job)
    for k, js in enumerate(jobs):
        with open(os.path.join(workDir, 'inputs', 'job_%d.json' % k), 'w') as f:
            json.dump(js, f)
    snapshot(workDir, args.config)
    with open(os.path.join(ANALYSIS, 'condor_job.sh')) as src, \
            open(os.path.join(workDir, 'inputs', 'condor_job.sh'), 'w') as dst:
        dst.write(src.read())
    os.chmod(os.path.join(workDir, 'inputs', 'condor_job.sh'), 0o755)
    state = {'config': args.config, 'output': os.path.abspath(args.output), 'tag': args.tag, 'lumi': args.lumi,
             'nJobs': len(jobs), 'filesPerJob': args.files_per_job, 'cpus': args.cpus, 'memory': args.memory,
             'chunksize': args.chunksize, 'proxy': proxyPath(), 'image': IMAGE, 'code': codeState(), 'clusters': []}
    queue(workDir, state, range(len(jobs)), args.dryrun)
    print('%s: %d jobs %s' % (workDir, len(jobs), '(dry run)' if args.dryrun else 'submitted'))
    return workDir


def load(workDir):
    with open(os.path.join(workDir, 'state.json')) as f:
        return json.load(f)


def logStatus(workDir, state):
    """{job: 'done' | 'failed' | 'running' | 'idle'} from the condor user log (last event per job wins)."""
    jobOf = {(c['cluster'], p): j for c in state['clusters'] for p, j in enumerate(c['jobs'])}
    out = {}
    path = os.path.join(workDir, 'logs', 'condor.log')
    if not os.path.exists(path):
        return out
    with open(path) as f:
        text = f.read()
    for m in re.finditer(r'^(\d{3}) \((\d+)\.(\d+)\.\d+\)[^\n]*\n(.*?)^\.\.\.', text, re.M | re.S):
        code, key = m.group(1), (int(m.group(2)), int(m.group(3)))
        if key not in jobOf:
            continue
        if code == '005':
            rv = re.search(r'return value (\d+)', m.group(4))
            out[jobOf[key]] = 'done' if rv and rv.group(1) == '0' else 'failed'
        elif code in ('009', '012'):      # aborted, held
            out[jobOf[key]] = 'failed'
        elif code == '001':
            out[jobOf[key]] = 'running'
        elif code == '000':
            out[jobOf[key]] = 'idle'
    return out


def status(workDir):
    """{job: state}; a job is complete only when its part file exists, whatever the log says."""
    state = load(workDir)
    log = logStatus(workDir, state)
    out = {}
    for j in range(state['nJobs']):
        if os.path.exists(os.path.join(workDir, 'parts', 'part_%d.coffea' % j)):
            out[j] = 'complete'
        else:
            out[j] = {'done': 'failed', None: 'unsubmitted'}.get(log.get(j), log.get(j))
    return out


def collect(parts, allowMissing=False):
    """Accumulated output of the part files; refuses missing parts unless allowMissing."""
    from coffea.processor import accumulate
    from coffea.util import load as loadCoffea
    present = [p for p in parts if os.path.exists(p)]
    missing = [p for p in parts if not os.path.exists(p)]
    if missing and not allowMissing:
        raise SystemExit('%d of %d parts missing, e.g. %s (use --allow-missing)' % (len(missing), len(parts), missing[0]))
    out = accumulate(loadCoffea(p) for p in present)
    return out, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('action', choices=['status', 'resubmit', 'collect'])
    ap.add_argument('workdir')
    ap.add_argument('--allow-missing', action='store_true')
    ap.add_argument('--dryrun', action='store_true', help='resubmit: write the JDL, submit nothing')
    a = ap.parse_args()
    state = load(a.workdir)
    st = status(a.workdir)
    if a.action == 'status':
        counts = {}
        for s in st.values():
            counts[s] = counts.get(s, 0) + 1
        print(', '.join('%s %d' % kv for kv in sorted(counts.items())))
        bad = sorted(j for j, s in st.items() if s == 'failed')
        if bad:
            print('failed jobs:', ' '.join(map(str, bad)))
    elif a.action == 'resubmit':
        jobs = sorted(j for j, s in st.items() if s in ('failed', 'unsubmitted'))
        if not jobs:
            raise SystemExit('nothing to resubmit')
        state['proxy'] = proxyPath()
        queue(a.workdir, state, jobs, a.dryrun)
        print('resubmitted %d jobs: %s' % (len(jobs), ' '.join(map(str, jobs))))
    else:
        from coffea.util import save
        parts = [os.path.join(a.workdir, 'parts', 'part_%d.coffea' % j) for j in range(state['nJobs'])]
        out, missing = collect(parts, a.allow_missing)
        out['config'] = state['config']
        out['condor'] = {'workdir': os.path.abspath(a.workdir), 'missingJobs': [parts.index(p) for p in missing],
                         'code': state['code']}
        save(out, state['output'])
        print('wrote %s from %d/%d parts' % (state['output'], len(parts) - len(missing), len(parts)))


if __name__ == '__main__':
    main()
