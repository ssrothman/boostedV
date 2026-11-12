#!/usr/bin/env python3
"""Submits the manifest's samples to CRAB or LPC condor (run inside cmsenv; source crab-setup.sh for CRAB).

Usage: submit.py samples.yaml --tag YYYYMMDD_desc [--only NAME ...] [--dryrun] [--allow-dirty]

Local bookkeeping goes to work/<tag>/<sample>/ and work/<tag>/provenance/; outputs to
<outputBase>/<tag>/<sample>/ on EOS. A sample already submitted under the tag is refused.
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifest  # noqa: E402

REPO = os.path.dirname(os.path.dirname(HERE))
WORK = os.path.join(HERE, 'work')


def git(*args, cwd=REPO):
    return subprocess.run(['git'] + list(args), cwd=cwd, check=True, capture_output=True, text=True).stdout


def gitState():
    """(description, dirty) of boostedV and its submodules."""
    lines = ['boostedV ' + git('rev-parse', 'HEAD').strip(), git('submodule', 'status').rstrip()]
    dirty = git('status', '--porcelain', '--ignore-submodules=none', '--untracked-files=no').strip()
    return '\n'.join(lines) + '\n', dirty


def writeProvenance(tagDir, manPath, man, names, allowDirty):
    state, dirty = gitState()
    if dirty and not allowDirty:
        raise SystemExit('uncommitted changes (use --allow-dirty to submit anyway):\n' + dirty)
    prov = os.path.join(tagDir, 'provenance')
    os.makedirs(os.path.join(prov, 'configs'), exist_ok=True)
    n = len([d for d in os.listdir(prov) if d.startswith('submission_')])
    with open(os.path.join(prov, 'submission_%d.txt' % n), 'w') as f:
        f.write('samples: %s\nCMSSW: %s\n%s' % (' '.join(names), os.environ.get('CMSSW_BASE', ''), state))
        if dirty:
            f.write('DIRTY:\n%s\n%s%s' % (dirty, git('diff'), git('submodule', 'foreach', '--quiet', 'git diff')))
    shutil.copy(manPath, os.path.join(prov, 'samples_%d.yaml' % n))
    for name in names:
        shutil.copy(man['samples'][name]['config'], os.path.join(prov, 'configs', name + '.yaml'))


def proxyPath(minHours=24):
    left = int(subprocess.run(['voms-proxy-info', '-timeleft'], capture_output=True, text=True).stdout.strip() or 0)
    if left < minHours * 3600:
        raise SystemExit('grid proxy has %.1f h left; run voms-proxy-init -voms cms -valid 192:00' % (left / 3600))
    return subprocess.run(['voms-proxy-info', '-path'], check=True, capture_output=True, text=True).stdout.strip()


def condorTarball(tagDir, man, tag, dryrun):
    """Builds the CMSSW tarball once per tag and copies it to EOS; returns its URL."""
    import condorBackend
    local = os.path.join(tagDir, 'cmssw.tgz')
    remote = '%s/%s/%s/cmssw.tgz' % (man['eosRedirector'], man['outputBase'], tag)
    if not os.path.exists(local):
        print('building %s' % local)
        condorBackend.makeTarball(os.environ['CMSSW_BASE'], local + '.part')
        os.rename(local + '.part', local)
    host, path = remote.split('//', 2)[1], '/' + remote.split('//', 2)[2]
    stat = subprocess.run(['xrdfs', 'root://' + host, 'stat', path], capture_output=True)
    if not dryrun and stat.returncode != 0:
        subprocess.run(['xrdcp', '-f', local, remote], check=True)
    return remote


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('manifest')
    ap.add_argument('--tag', required=True)
    ap.add_argument('--only', nargs='+', metavar='NAME')
    ap.add_argument('--dryrun', action='store_true', help='prepare everything, submit nothing')
    ap.add_argument('--allow-dirty', action='store_true')
    args = ap.parse_args()
    tag = manifest.checkTag(args.tag)
    man = manifest.load(args.manifest)
    names = args.only or list(man['samples'])
    unknown = set(names) - set(man['samples'])
    if unknown:
        raise SystemExit('unknown samples: %s' % sorted(unknown))
    # Dry runs live apart so that they never block the real submission.
    tagDir = os.path.join(WORK, 'dryrun', tag) if args.dryrun else os.path.join(WORK, tag)
    if args.dryrun:
        for n in names:
            shutil.rmtree(os.path.join(tagDir, n), ignore_errors=True)
    done = [n for n in names if os.path.exists(os.path.join(tagDir, n))]
    if done:
        raise SystemExit('already submitted under %s: %s' % (tag, done))
    for n in names:
        s = man['samples'][n]
        dsGT = manifest.datasetGlobalTag(s['input'].get('dataset', '/x/x/x'))
        if s['isMC'] and dsGT and dsGT != s['globalTag']:
            print('WARNING %s: globalTag %s differs from the dataset GT %s' % (n, s['globalTag'], dsGT))
    proxy = proxyPath()
    writeProvenance(tagDir, args.manifest, man, names, args.allow_dirty)
    for n in names:
        s, workDir = man['samples'][n], os.path.join(tagDir, n)
        try:
            submitSample(s, n, workDir, tagDir, man, tag, proxy, args.dryrun)
        except BaseException:
            if os.path.exists(workDir):
                k = len([d for d in os.listdir(tagDir) if d.startswith(n + '.failed')])
                os.rename(workDir, '%s.failed%d' % (workDir, k))
                print('%s: submission failed; its work directory was moved to %s.failed%d' % (n, workDir, k))
            raise


def submitSample(s, n, workDir, tagDir, man, tag, proxy, dryrun):
    if s['backend'] == 'condor':
        import condorBackend
        tarball = condorTarball(tagDir, man, tag, dryrun)
        nJobs = condorBackend.submit(s, n, workDir, tag, man, tarball, proxy, dryrun)
        print('%s: %d condor jobs %s' % (n, nJobs, '(dry run)' if dryrun else 'submitted'))
    else:
        import crabBackend
        crabBackend.submit(s, n, workDir, tag, man, dryrun)
        print('%s: CRAB task %s' % (n, 'dry run done' if dryrun else 'submitted'))

if __name__ == '__main__':
    main()
