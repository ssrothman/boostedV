#!/usr/bin/env python3
"""Status of a tag's samples, and resubmission of failed jobs (inside cmsenv; source crab-setup.sh for CRAB).

Usage: status.py --tag T [SAMPLE ...] [--resubmit]

condor: a job is done when both outputs exist on EOS; --resubmit queues the missing jobs that are no longer in
        condor_q (one new cluster, recorded in condor.json).
CRAB:   crab status (job indices saved to crabJobs.json for merge.py); --resubmit runs crab resubmit.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import outputs  # noqa: E402

WORK = os.path.join(HERE, 'work')


HELD = 5


def condorQueued(clusters):
    """{job index (the args' first field): (JobStatus, schedd)} of the jobs still in the given clusters."""
    if not clusters:
        return {}
    import condorBackend
    # The cluster ids must precede -af, which takes every later argument as an attribute.
    res = condorBackend.condorCommand('condor_q', *[str(c) for c in clusters], '-af', 'JobStatus', 'GlobalJobId',
                                      'Args')
    out = {}
    for l in res.splitlines():
        if l.strip():
            st, gid, idx = l.split()[:3]
            out[int(idx)] = (int(st), gid.split('#')[0])
    return out


def heldConstraint(clusters):
    """Held jobs of these clusters only."""
    return 'JobStatus == %d && (%s)' % (HELD, ' || '.join('ClusterId == %d' % c for c in clusters))


def condorMissing(expected, done, queued):
    """Expected jobs with no complete output that are not queued any more."""
    return sorted(set(expected) - set(done) - set(queued))


def condorStatus(workDir, resubmit):
    import condorBackend
    rec = outputs.submission(workDir)
    expected = outputs.expectedJobs(workDir)
    done, _ = outputs.pairJobs(outputs.listRoot(rec['outDir']))
    queued = condorQueued(rec['clusters'])
    held = sorted(i for i, (st, _) in queued.items() if st == HELD)
    lost = condorMissing(expected, done, queued)
    print('  %d jobs: %d done, %d idle/running, %d held, %d failed or lost'
          % (len(expected), len(set(done) & set(expected)), len(queued) - len(held), len(held), len(lost)))
    missing = lost
    if resubmit and held:
        # A held job never finishes by itself, so it is removed and resubmitted with the failed ones.
        # The LPC wrapper needs the schedd named for a -constraint removal.
        for schedd in sorted({queued[i][1] for i in held}):
            condorBackend.condorCommand('condor_rm', '-name', schedd, '-constraint', heldConstraint(rec['clusters']))
        missing = sorted(lost + held)
    if resubmit and missing:
        with open(os.path.join(workDir, 'jobs.txt')) as f:
            lines = {int(l.split()[0]): l for l in f if l.strip()}
        n = len(rec['clusters'])
        argsFile = os.path.join(workDir, 'jobs_resub%d.txt' % n)
        with open(argsFile, 'w') as f:
            f.writelines(lines[i] for i in missing)
        with open(os.path.join(workDir, 'submit.jdl')) as f:
            jdl = f.read().replace(os.path.join(workDir, 'jobs.txt'), argsFile)
        jdlPath = os.path.join(workDir, 'submit_resub%d.jdl' % n)
        with open(jdlPath, 'w') as f:
            f.write(jdl)
        rec['clusters'].append(condorBackend.condorSubmit(jdlPath))
        with open(os.path.join(workDir, 'condor.json'), 'w') as f:
            json.dump(rec, f, indent=1)
        print('  resubmitted %s' % missing)


def crabStatus(workDir, resubmit):
    from CRABAPI.RawCommand import crabCommand
    rec = outputs.submission(workDir)
    res = crabCommand('status', dir=rec['projDir'])
    jobs = res.get('jobs', {})
    states = {}
    for j in jobs.values():
        states[j['State']] = states.get(j['State'], 0) + 1
    print('  task %s: %s' % (res.get('status'), states))
    if jobs:
        with open(os.path.join(workDir, 'crabJobs.json'), 'w') as f:
            json.dump(sorted(int(i) for i in jobs), f)
    if resubmit and states.get('failed'):
        crabCommand('resubmit', dir=rec['projDir'])
        print('  resubmitted %d failed jobs' % states['failed'])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tag', required=True)
    ap.add_argument('samples', nargs='*')
    ap.add_argument('--resubmit', action='store_true')
    args = ap.parse_args()
    tagDir = os.path.join(WORK, args.tag)
    names = args.samples or sorted(d for d in os.listdir(tagDir) if d != 'provenance' and '.failed' not in d and
                                   os.path.isdir(os.path.join(tagDir, d)))
    for name in names:
        workDir = os.path.join(tagDir, name)
        print(name)
        if outputs.submission(workDir)['backend'] == 'condor':
            condorStatus(workDir, args.resubmit)
        else:
            crabStatus(workDir, args.resubmit)


if __name__ == '__main__':
    main()
