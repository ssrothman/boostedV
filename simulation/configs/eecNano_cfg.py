"""MiniAOD -> minimal custom NANO with EEC tables, plus per-channel aggregated EEC histograms with covariance.

cmsRun eecNano_cfg.py config=default.yaml globalTag=<GT> inputFiles=file:in.root outputFile=nano.root \\
    histFile=hists.root isMC=1 maxEvents=-1 [lumiMask=golden.json] [writeConstituents=1]

All physics settings come from the YAML `config` (validated by analysisConfig.py); a relative path is resolved
against the current directory first, then this file's directory.
"""
import inspect
import os
import sys

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from SRothman.EECs.eecTools import addAggregator, addObservable
from SRothman.EventSelection.eventSelection_cff import (addSelection, bosonTag, label, muonSFLabel, processModifiers,
                                                        selectedObjects)
from SRothman.EventSelection.eventTables_cff import addAK4Jets, addEventTables
from SRothman.JetSetup.eecJets_cff import backToBackFlag, setupJets

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
opts.register('globalTag', '', VarParsing.multiplicity.singleton, VarParsing.varType.string,
              'conditions GlobalTag (required)')
opts.register('lumiMask', '', VarParsing.multiplicity.singleton, VarParsing.varType.string,
              'certification JSON restricting the processed lumisections (empty: all)')
opts.register('writeConstituents', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int,
              'store jet constituents')
opts.parseArguments()
isMC = bool(opts.isMC)
if not opts.globalTag:
    raise analysisConfig.ConfigError('globalTag is required')
cfgPath = opts.config if os.path.exists(opts.config) else os.path.join(HERE, opts.config)
cfg = analysisConfig.load(cfgPath)
inputs = cfg['inputs']

process = cms.Process('EECNANO', *processModifiers(inputs['eras']))
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(opts.inputFiles))
process.maxEvents.input = opts.maxEvents
if opts.lumiMask:
    from FWCore.PythonUtilities.LumiList import LumiList
    process.source.lumisToProcess = LumiList(filename=opts.lumiMask).getVLuminosityBlockRange()
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag  # noqa: E402
process.GlobalTag = GlobalTag(process.GlobalTag, opts.globalTag, '')
process.TFileService = cms.Service('TFileService', fileName=cms.string(opts.histFile))
task = cms.Task()

# ---- event selection ----
# Events passing any channel at any enabled level are written; data has no gen level.
levels = [l for l in cfg['selection']['levels'] if isMC or l == 'reco']
if not levels:
    raise analysisConfig.ConfigError('%s: selection/levels %s has no level available in data'
                                     % (cfgPath, cfg['selection']['levels']))
sel = cfg['selection']
muCorr = sel['reco']['muonCorrections']
if not isMC and muCorr['variation'] != 'nominal':
    raise analysisConfig.ConfigError('%s: selection/reco/muonCorrections/variation %s is for MC only'
                                     % (cfgPath, muCorr['variation']))
selFlags = addSelection(process, sel, inputs, levels, isMC, task)
process.anySelectedPath = cms.Path(process.anySelectedFilter, task)

# ---- jets ----
cleaning = cfg['jets']['cleaning']['channels']
collections = []  # (EEC name prefix, jet collection label)
b2bFlags = {}  # (level, channel) -> flag: the channel's dilepton/object selection passes and has a back-to-back jet
for name, spec in cfg['jets']['collections'].items():
    if spec['mcOnly'] and not isMC:
        continue
    lev = spec['level']
    # Each level's jets are cleaned against that level's selected objects.
    vetoes = dict(zip(cleaning, selectedObjects(sel[lev], lev, cleaning)))
    b2b = {ch: dict(flag=label(lev, ch) + 'Sel', objects=bosonTag(lev, ch, c),
                    dPhiMin=c['backToBack']['dPhiMin'], asymmetryMax=c['backToBack']['asymmetryMax'])
           for ch, c in sel[lev]['channels'].items() if c['backToBack']['enabled']}
    labels = setupJets(process, 'jets' + name, spec, isMC, vetoSrcs=vetoes,
                       writeConstituents=bool(opts.writeConstituents), task=task, backToBack=b2b)
    collections += [(name + v, lab) for v, lab in labels.items()]
    b2bFlags.update({(lev, ch): backToBackFlag('jets' + name, ch) for ch in b2b})

# The channel flag <ch> (hence anyChannel, the event filter and <ch>Filter) includes the back-to-back requirement.
for (lev, ch), f in b2bFlags.items():
    getattr(process, label(lev, ch)).srcs.append(f)
    flagTable = getattr(process, label(lev, 'selectionFlags') + 'Table')
    flagTable.names.append(ch + 'B2B')
    flagTable.srcs.append(f)

# ---- EECs ----
# Axis observables exist for the nominal jets only, which are the ones carrying EECJet::axes.
nominalAxes = {name: [d['name'] for d in spec.get('axes', {'definitions': []})['definitions']]
               for name, spec in cfg['jets']['collections'].items()}
for prefix, jets in collections:
    for obs, spec in cfg['observables'].items():
        if 'axis' in spec:
            if prefix not in nominalAxes:
                continue
            addObservable(process, 'eec%s%s' % (prefix, obs), jets, spec, prefix + obs, task,
                          axisIndex=nominalAxes[prefix].index(spec['axis']))
        else:
            addObservable(process, 'eec%s%s' % (prefix, obs), jets, spec, prefix + obs, task)

agg = cfg['aggregation']
genInfo = inputs['genEventInfo'] if isMC else ''
for level in levels:
    for ch in agg['channels']:
        seq = getattr(process, label(level, ch) + 'Filter')
        # Reco-level MC histograms carry the channel's muon efficiency scale factors.
        weights = [muonSFLabel(ch)] if isMC and level == 'reco' and ch in sel['reco']['muonScaleFactors'] else []
        for prefix, jets in collections:
            # Jets overlapping this channel's selected objects are skipped (other channels' vetoes are not applied).
            mask = '%sVetoTable:%s' % (jets, ch) if ch in cleaning else ''
            for obs in agg['observables']:
                lab = 'eec%s%s' % (prefix, obs)
                seq = seq + addAggregator(process, '%s_%s_%s' % (ch, level, lab), lab, cfg['observables'][obs],
                                          genInfo, agg['maxBins'], weights, mask)
        setattr(process, '%s_%s_AggPath' % (ch, level), cms.Path(seq, task))

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
if isMC and cfg['output']['lheTables']:
    # Settings of the standard NanoAOD lheInfoTable (PhysicsTools/NanoAOD/python/particlelevel_cff.py).
    process.lheInfoTable = cms.EDProducer('LHETablesProducer', lheInfo=cms.VInputTag(*inputs['lheInfo']),
                                          precision=cms.int32(14), storeLHEParticles=cms.bool(True))
    task.add(process.lheInfoTable)
addEventTables(process, cfg['output'], inputs, sel['reco']['vertex'], isMC, task)
addAK4Jets(process, cfg['output']['ak4Jets'], isMC, task)

keep = ['drop *', 'keep nanoaodFlatTable_*Table_*_*', 'keep nanoaodMergeableCounterTable_*Table_*_*',
        'keep nanoaodUniqueString_nanoMetadata_*_*']
if cfg['output']['keepHLTBits']:
    keep.append('keep edmTriggerResults_*_*_%s' % inputs['hltProcess'])
process.out = cms.OutputModule('NanoAODOutputModule', fileName=cms.untracked.string(opts.outputFile),
                               SelectEvents=cms.untracked.PSet(SelectEvents=cms.vstring('anySelectedPath')),
                               outputCommands=cms.untracked.vstring(*keep))
process.outPath = cms.EndPath(process.out, task)
