"""MiniAOD -> minimal custom NANO with EEC tables, plus per-channel aggregated EEC histograms with covariance.

cmsRun eecNano_cfg.py inputFiles=file:in.root outputFile=nano.root histFile=hists.root isMC=1 maxEvents=-1
  writeConstituents=0|1   also store jet constituents (for validation)
  aggregateChannels=Zmumu,Zee

Physics settings below (jet cuts, observables, binning, constituent-variation sizes) are development defaults.
"""
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from SRothman.EventSelection.eventSelection_cff import addAllChannels, CHANNELS
from SRothman.JetSetup.eecJets_cff import setupJets, CONSTITUENT_VARIATIONS
from SRothman.EECs.eecTools import addPENC, addE1C, addAggregator, logAxis, regularAxis
import math

opts = VarParsing('analysis')
opts.register('isMC', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, 'MC (1) or data (0)')
opts.register('histFile', 'eecHists.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'TFileService output')
opts.register('writeConstituents', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, 'store jet constituents')
opts.register('aggregateChannels', 'Zmumu,Zee', VarParsing.multiplicity.singleton, VarParsing.varType.string,
              'comma-separated channels with aggregated histograms')
opts.parseArguments()
isMC = bool(opts.isMC)

process = cms.Process('EECNANO')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(opts.inputFiles))
process.maxEvents.input = opts.maxEvents
process.TFileService = cms.Service('TFileService', fileName=cms.string(opts.histFile))
task = cms.Task()

# ---- event selection ----
# Defaults live in SRothman/EventSelection/python/eventSelection_cff.py (OBJECT_CUTS, MET_FILTERS, TRIGGERS and the
# selector defaults in addChannel). Override here, e.g.
#   objectCuts=dict(tightMuons="pt > 20 && ..."), metFilters=[...], triggers=dict(Zmumu=['HLT_IsoMu27_v*']),
#   channelCuts=dict(Zmumu=dict(massMin=81.0, massMax=101.0), Wmunu=dict(mtMin=60.0))
addAllChannels(process, task, objectCuts=None, metFilters=None, triggers=None, channelCuts=None)
process.anyChannelPath = cms.Path(process.anyChannelFilter, task)

# ---- jets ----
vetoes = ['ZmumuSel:leptons', 'ZeeSel:leptons', 'WmunuSel:leptons', 'WenuSel:leptons', 'GammaJetsSel:objects']
jetCuts = dict(ptMin=200.0, absEtaMax=2.4, idMask=1, minConstituents=1)
variations = {}
if isMC:
    variations = {'JESUp': dict(type='jes', direction='up'), 'JESDown': dict(type='jes', direction='down'),
                  'JERUp': dict(type='jer', direction='up'), 'JERDown': dict(type='jer', direction='down')}
    variations.update(CONSTITUENT_VARIATIONS)  # placeholder sizes, see eecJets_cff.py
collections = []  # (EEC name prefix, jet collection label)
reco = setupJets(process, 'recoJets', level='reco', mode='pat', R=0.8, ptMin=180.0, isMC=isMC, jetCuts=jetCuts,
                 vetoSrcs=vetoes, variations=variations, tableName='RecoJet',
                 writeConstituents=bool(opts.writeConstituents), task=task)
collections += [('Reco' + v, label) for v, label in reco.items()]
if isMC:
    gen = setupJets(process, 'genJets', level='gen', mode='pat', R=0.8, ptMin=180.0,
                    jetCuts=dict(ptMin=200.0, absEtaMax=2.4, minConstituents=1), vetoSrcs=vetoes, tableName='GenJet',
                    writeConstituents=bool(opts.writeConstituents), task=task)
    collections.append(('Gen', gen['']))

# ---- EECs ----
dRAxis = [logAxis(50, 1e-3, 1.0)]
e1cAxes = [regularAxis(20, 0.0, math.pi), regularAxis(20, -math.pi, math.pi)]
genInfo = 'generator' if isMC else ''
aggregated = []  # (label, src, output, axes)
for prefix, jets in collections:
    for N in (2, 3):
        lab = 'eec%sE%dC' % (prefix, N)
        addPENC(process, lab, jets, N, weight='Pt', angle='DeltaR', output='SparseMerged', norm='sumPt',
                axes=dRAxis, tableName='%sE%dC' % (prefix, N), task=task)
        aggregated.append((lab, 'SparseMerged', dRAxis))
    lab = 'eec%sE1C' % prefix
    addE1C(process, lab, jets, weight='Pt', output='SparseMerged', norm='sumPt', frame='jetHelicity',
           axes=e1cAxes, tableName='%sE1C' % prefix, task=task)
    aggregated.append((lab, 'SparseMerged', e1cAxes))

for ch in [c for c in opts.aggregateChannels.split(',') if c]:
    if ch not in CHANNELS:
        raise ValueError('unknown channel ' + ch)
    aggs = [addAggregator(process, '%s_%s' % (ch, lab), lab, out, axes, genInfo) for lab, out, axes in aggregated]
    seq = getattr(process, ch + 'Filter')
    for a in aggs:
        seq = seq + a
    setattr(process, ch + 'AggPath', cms.Path(seq, task))

# ---- event-level tables ----
if isMC:
    from PhysicsTools.NanoAOD.genWeightsTable_cfi import genWeightsTable
    from PhysicsTools.NanoAOD.globals_cff import puTable, genTable
    process.genWeightsTable = genWeightsTable.clone()
    process.puTable = puTable.clone()
    process.genTable = genTable.clone()
    task.add(process.puTable, process.genTable)
    # Scheduled on its own path so that the Runs-tree sums of weights include every processed event.
    process.genWeightsPath = cms.Path(process.genWeightsTable)

process.out = cms.OutputModule('NanoAODOutputModule', fileName=cms.untracked.string(opts.outputFile),
                               SelectEvents=cms.untracked.PSet(SelectEvents=cms.vstring('anyChannelPath')),
                               outputCommands=cms.untracked.vstring('drop *', 'keep nanoaodFlatTable_*Table_*_*',
                                                                    'keep edmTriggerResults_*_*_HLT',
                                                                    'keep nanoaodMergeableCounterTable_*Table_*_*',
                                                                    'keep nanoaodUniqueString_nanoMetadata_*_*'))
process.outPath = cms.EndPath(process.out, task)
