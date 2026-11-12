"""Locating and pairing per-job outputs (nano_<i>.root, hists_<i>.root) under a sample's output directory."""
import json
import os
import re
import subprocess

JOB_RE = re.compile(r'/(nano|hists)_(\d+)\.root$')


def listRoot(outDir):
    """Every .root file below outDir (an xrootd URL root://host//path, or a local directory)."""
    if outDir.startswith('root://'):
        m = re.match(r'^(root://[^/]+)/(/.*)$', outDir)
        if not m:
            raise ValueError('not an xrootd URL with an absolute path: %s' % outDir)
        host, path = m.groups()
        res = subprocess.run(['xrdfs', host, 'ls', '-R', path], capture_output=True, text=True)
        if res.returncode != 0:
            if 'No such file' in res.stderr:
                return []
            raise RuntimeError(res.stderr)
        return sorted(host + '/' + p for p in res.stdout.split() if p.endswith('.root'))
    return sorted(os.path.join(d, f) for d, _, fs in os.walk(outDir) for f in fs if f.endswith('.root'))


def pairJobs(paths):
    """({index: {'nano': path, 'hists': path}} for complete jobs, sorted incomplete indices).
    Files under a merged/ directory are ignored; an index seen twice for the same kind is an error."""
    jobs = {}
    for p in paths:
        if '/merged/' in p:
            continue
        m = JOB_RE.search(p)
        if not m:
            continue
        kind, idx = m.group(1), int(m.group(2))
        if kind in jobs.setdefault(idx, {}):
            raise RuntimeError('job %d has two %s files: %s, %s' % (idx, kind, jobs[idx][kind], p))
        jobs[idx][kind] = p
    complete = {i: j for i, j in jobs.items() if len(j) == 2}
    return complete, sorted(set(jobs) - set(complete))


def expectedJobs(workDir):
    """Job indices the submission created, or None if unknown (CRAB: from the last status, see status.py)."""
    condor = os.path.join(workDir, 'jobs.txt')
    if os.path.exists(condor):
        with open(condor) as f:
            return [int(l.split()[0]) for l in f if l.strip()]
    crab = os.path.join(workDir, 'crabJobs.json')
    if os.path.exists(crab):
        with open(crab) as f:
            return json.load(f)
    return None


def submission(workDir):
    """The submission record (backend, outDir, isMC, ...) written by submit.py."""
    for name in ('condor.json', 'crab.json'):
        p = os.path.join(workDir, name)
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)
    raise RuntimeError('%s: no submission record' % workDir)
