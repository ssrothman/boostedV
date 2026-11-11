"""MiniAOD -> minimal custom NANO with EEC tables, plus per-channel aggregated EEC histograms with covariance.

cmsRun eecNano_cfg.py config=default.yaml inputFiles=file:in.root outputFile=nano.root histFile=hists.root \\
    isMC=1 maxEvents=-1 [writeConstituents=1]

All physics settings come from the YAML `config` (validated by analysisConfig.py); a relative path is resolved
against the current directory first, then this file's directory.
"""
import inspect
import os
import sys

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from SRothman.EECs.eecTools import addAggregator, addObservable
from SRothman.EventSelection.eventSelection_cff import addSelection, selectedObjects
from SRothman.JetSetup.eecJets_cff import setupJets

# edmConfigDump does not define __file__; the code object's filename is set by every loader.
HERE = os.path.dirname(os.path.abspath(inspect.currentframe().f_code.co_filename))
sys.path.insert(0, HERE)
import analysisConfig  # noqa: E402

opts = VarParsing('analysis')
opts.register('config', 'default.yaml', VarParsing.multiplicity.singleton, VarParsing.varType.string,
              'analysis configuration YAML')
opts.register('isMC', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, 'MC (1) or data (0)')
opts.register('histFile', 'eecHists.root', VarParsing.multiplicity.singleton, VarParsing.varType.string,
              'TFileService output')
opts.register('writeConstituents', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int,
              'store jet constituents')
opts.parseArguments()
isMC = bool(opts.isMC)
cfgPath = opts.config if os.path.exists(opts.config) else os.path.join(HERE, opts.config)
cfg = analysisConfig.load(cfgPath)
inputs = cfg['inputs']

process = cms.Process('EECNANO')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(opts.inputFiles))
process.maxEvents.input = opts.maxEvents
process.TFileService = cms.Service('TFileService', fileName=cms.string(opts.histFile))
task = cms.Task()

# ---- event selection ----
addSelection(process, cfg['selection'], inputs, task)
process.anyChannelPath = cms.Path(process.anyChannelFilter, task)

# ---- jets ----
vetoes = selectedObjects(cfg['selection'], cfg['jets']['cleaning']['channels'])
collections = []  # (EEC name prefix, jet collection label)
for name, spec in cfg['jets']['collections'].items():
    if spec['mcOnly'] and not isMC:
        continue
    labels = setupJets(process, 'jets' + name, spec, isMC, vetoSrcs=vetoes,
                       writeConstituents=bool(opts.writeConstituents), task=task)
    collections += [(name + v, label) for v, label in labels.items()]

# ---- EECs ----
for prefix, jets in collections:
    for obs, spec in cfg['observables'].items():
        addObservable(process, 'eec%s%s' % (prefix, obs), jets, spec, prefix + obs, task)

agg = cfg['aggregation']
genInfo = inputs['genEventInfo'] if isMC else ''
for ch in agg['channels']:
    seq = getattr(process, ch + 'Filter')
    for prefix, _ in collections:
        for obs in agg['observables']:
            lab = 'eec%s%s' % (prefix, obs)
            seq = seq + addAggregator(process, '%s_%s' % (ch, lab), lab, cfg['observables'][obs], genInfo,
                                      agg['maxBins'])
    setattr(process, ch + 'AggPath', cms.Path(seq, task))

# ---- event-level tables ----
if isMC and cfg['output']['mcEventTables']:
    from PhysicsTools.NanoAOD.genWeightsTable_cfi import genWeightsTable
    from PhysicsTools.NanoAOD.globals_cff import puTable, genTable
    process.genWeightsTable = genWeightsTable.clone()
    process.puTable = puTable.clone()
    process.genTable = genTable.clone()
    task.add(process.puTable, process.genTable)
    # Scheduled on its own path so that the Runs-tree sums of weights include every processed event.
    process.genWeightsPath = cms.Path(process.genWeightsTable)

keep = ['drop *', 'keep nanoaodFlatTable_*Table_*_*', 'keep nanoaodMergeableCounterTable_*Table_*_*',
        'keep nanoaodUniqueString_nanoMetadata_*_*']
if cfg['output']['keepHLTBits']:
    keep.append('keep edmTriggerResults_*_*_%s' % inputs['hltProcess'])
process.out = cms.OutputModule('NanoAODOutputModule', fileName=cms.untracked.string(opts.outputFile),
                               SelectEvents=cms.untracked.PSet(SelectEvents=cms.vstring('anyChannelPath')),
                               outputCommands=cms.untracked.vstring(*keep))
process.outPath = cms.EndPath(process.out, task)
