"""LPC HTCondor backend: file chunks of a dataset, a CMSSW tarball on EOS, one condor job per chunk."""
import json
import os
import re
import shutil
import subprocess
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIGS = os.path.join(os.path.dirname(HERE), 'configs')
CFG_FILES = [os.path.join(CONFIGS, f) for f in ('eecNano_cfg.py', 'analysisConfig.py', 'analysis.schema.yaml')]
# Not needed at run time; EECs/build also contains symlink loops back into the package.
TAR_EXCLUDE = {'tmp', '.git', 'build', '__pycache__', 'test', 'bench', 'docs'}


def inputFiles(sample):
    """Sorted input files: DAS LFNs of the dataset, or the lines of fileList."""
    if 'fileList' in sample['input']:
        with open(sample['input']['fileList']) as f:
            files = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    else:
        out = subprocess.run(['dasgoclient', '-query', 'file dataset=%s' % sample['input']['dataset']],
                             check=True, capture_output=True, text=True).stdout
        files = out.split()
    if not files:
        raise RuntimeError('no input files for %s' % sample['input'])
    return sorted(files)


def chunks(files, unitsPerJob, maxJobs):
    """Consecutive chunks of unitsPerJob files; only the first maxJobs unless maxJobs is -1."""
    out = [files[i:i + unitsPerJob] for i in range(0, len(files), unitsPerJob)]
    return out if maxJobs == -1 else out[:maxJobs]


def url(f, redirector):
    return redirector + '/' + f if f.startswith('/store/') else f


def makeTarball(cmsswBase, path):
    """Tarball of the CMSSW area with src/ symlinks (the SRothman packages) dereferenced and links in
    external/ kept as links."""
    release = os.path.basename(cmsswBase.rstrip('/'))

    def skip(info):
        return None if os.path.basename(info.name) in TAR_EXCLUDE else info

    with tarfile.open(path, 'w:gz') as tar:
        for entry in sorted(os.listdir(cmsswBase)):
            if entry in TAR_EXCLUDE:
                continue
            full = os.path.join(cmsswBase, entry)
            if entry == 'src':
                tar.add(full, arcname=os.path.join(release, 'src'), recursive=False)
                for pkgGroup in sorted(os.listdir(full)):
                    _addDeref(tar, os.path.join(full, pkgGroup), os.path.join(release, 'src', pkgGroup), skip)
            else:
                tar.add(full, arcname=os.path.join(release, entry), filter=skip)
    return path


def _addDeref(tar, path, arcname, skip):
    """Adds path recursively, following symlinks."""
    info = tar.gettarinfo(os.path.realpath(path), arcname)
    if skip(info) is None:
        return
    if os.path.isdir(path):
        tar.addfile(info)
        for e in sorted(os.listdir(path)):
            _addDeref(tar, os.path.join(path, e), os.path.join(arcname, e), skip)
    else:
        with open(os.path.realpath(path), 'rb') as f:
            tar.addfile(info, f)


def jobArgs(sample, files, outDir, tarballUrl, redirector):
    """One argument line per job, in job.sh's order."""
    mask = os.path.basename(sample['lumiMask']) if sample['lumiMask'] else 'none'
    lines = []
    for i, chunk in enumerate(chunks(files, sample['splitting']['unitsPerJob'], sample['maxJobs'])):
        lines.append(' '.join([str(i), ','.join(url(f, redirector) for f in chunk), outDir, tarballUrl,
                               os.path.basename(sample['config']), sample['globalTag'], str(int(sample['isMC'])),
                               mask]))
    return lines


def jobInputs(sample):
    return CFG_FILES + [sample['config']] + ([sample['lumiMask']] if sample['lumiMask'] else [])


def snapshotInputs(sample, workDir):
    """Copies the job inputs into workDir/inputs/, because condor transfers them only when each job starts."""
    d = os.path.join(workDir, 'inputs')
    os.makedirs(d)
    for f in jobInputs(sample) + [os.path.join(HERE, 'job.sh')]:
        shutil.copy(f, d)
    return [os.path.join(d, os.path.basename(f)) for f in jobInputs(sample)]


def jdl(workDir, inputs, argsFile, proxy):
    return '\n'.join([
        'universe = vanilla',
        'executable = %s' % os.path.join(workDir, 'inputs', 'job.sh'),
        'arguments = $(args)',
        'transfer_input_files = %s' % ','.join(inputs),
        'should_transfer_files = YES',
        'when_to_transfer_output = ON_EXIT',
        'x509userproxy = %s' % proxy,
        'request_memory = 2500',
        'output = %s/logs/job_$(Cluster)_$(Process).out' % workDir,
        'error = %s/logs/job_$(Cluster)_$(Process).err' % workDir,
        'log = %s/logs/condor.log' % workDir,
        'queue args from %s' % argsFile,
        ''])


def submit(sample, name, workDir, tag, man, tarballUrl, proxy, dryrun):
    """Writes jobs.txt and the JDL into workDir and submits unless dryrun; returns the job count."""
    outDir = '%s/%s/%s/%s' % (man['eosRedirector'], man['outputBase'], tag, name)
    files = inputFiles(sample)
    lines = jobArgs(sample, files, outDir, tarballUrl, man['inputRedirector'])
    os.makedirs(os.path.join(workDir, 'logs'))
    inputs = snapshotInputs(sample, workDir)
    argsFile = os.path.join(workDir, 'jobs.txt')
    with open(argsFile, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(workDir, 'submit.jdl'), 'w') as f:
        f.write(jdl(workDir, inputs, argsFile, proxy))
    info = {'backend': 'condor', 'nJobs': len(lines), 'nFiles': sum(len(l.split()[1].split(',')) for l in lines),
            'outDir': outDir, 'isMC': sample['isMC'], 'clusters': []}
    if not dryrun:
        info['clusters'].append(condorSubmit(os.path.join(workDir, 'submit.jdl')))
    with open(os.path.join(workDir, 'condor.json'), 'w') as f:
        json.dump(info, f, indent=1)
    return len(lines)


def condorCommand(*args):
    """stdout of an HTCondor command; run via sh because the LPC wrappers have no shebang line."""
    return subprocess.run(['sh', '-c', '"$0" "$@"'] + list(args), check=True, capture_output=True, text=True).stdout


def condorSubmit(jdlPath):
    out = condorCommand('condor_submit', jdlPath)
    m = re.search(r'submitted to cluster (\d+)', out)
    if not m:
        raise RuntimeError('condor_submit output not understood:\n' + out)
    return int(m.group(1))
