"""CRAB backend: one task per sample. Needs crab-setup.sh sourced after cmsenv for submission."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(os.path.dirname(HERE), 'configs', 'eecNano_cfg.py')
SPLITTING = {'files': 'FileBased', 'events': 'EventAwareLumiBased'}


def makeConfig(sample, name, tag, man, workArea):
    from CRABClient.UserUtilities import config as crabConfig
    c = crabConfig()
    c.General.requestName = name
    c.General.workArea = workArea
    c.General.transferOutputs = True
    c.General.transferLogs = False
    c.JobType.pluginName = 'Analysis'
    c.JobType.psetName = CFG
    # The cfg is evaluated here at submission, so the YAML is read locally; CRAB applies Data.lumiMask itself.
    c.JobType.pyCfgParams = ['config=' + sample['config'], 'globalTag=' + sample['globalTag'],
                             'isMC=%d' % sample['isMC'], 'outputFile=nano.root', 'histFile=hists.root']
    c.JobType.maxMemoryMB = 2500
    c.Data.inputDataset = sample['input']['dataset']
    c.Data.splitting = SPLITTING[sample['splitting']['mode']]
    c.Data.unitsPerJob = sample['splitting']['unitsPerJob']
    if sample['maxJobs'] != -1:
        c.Data.totalUnits = sample['maxJobs'] * sample['splitting']['unitsPerJob']
    if sample['lumiMask']:
        c.Data.lumiMask = sample['lumiMask']
    c.Data.publication = False
    c.Data.outLFNDirBase = '%s/%s/%s' % (man['outputBase'], tag, name)
    c.Data.outputDatasetTag = tag
    c.Site.storageSite = man['storageSite']
    return c


def submit(sample, name, workDir, tag, man, dryrun):
    """Submits (or dry-runs) the CRAB task; the CRAB project directory is workDir/crab_<name>."""
    from CRABAPI.RawCommand import crabCommand as cc
    os.makedirs(workDir)
    c = makeConfig(sample, name, tag, man, workDir)
    res = cc('submit', config=c, dryrun=True) if dryrun else cc('submit', config=c)
    with open(os.path.join(workDir, 'crab.json'), 'w') as f:
        json.dump({'backend': 'crab', 'projDir': os.path.join(workDir, 'crab_' + name),
                   'outDir': '%s/%s' % (man['eosRedirector'], c.Data.outLFNDirBase), 'dryrun': dryrun, 'isMC': sample['isMC'],
                   'result': str(res)}, f, indent=1)
