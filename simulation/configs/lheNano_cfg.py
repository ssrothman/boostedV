"""MiniAOD -> NANO with only the LHE tables (LHE, LHEPart) and generator weights, for every event (no selection).
Input of the truth spin-density matrix extraction (analysis/truthRho.py), which must not see acceptance cuts.

cmsRun lheNano_cfg.py inputFiles=file:in.root outputFile=lhe.root [histFile=hists.root] maxEvents=-1
config, globalTag and isMC are accepted, and ignored, so that the production (cmsswConfig: lheNano_cfg.py) can run it
like eecNano_cfg.py; histFile is an empty file that the production's job bookkeeping expects.
"""
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

opts = VarParsing('analysis')
for name, default in (('config', ''), ('globalTag', ''), ('histFile', 'lheHists.root')):
    opts.register(name, default, VarParsing.multiplicity.singleton, VarParsing.varType.string)
opts.register('isMC', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int)
opts.parseArguments()

process = cms.Process('LHENANO')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 10000
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(opts.inputFiles))
process.maxEvents.input = opts.maxEvents
process.TFileService = cms.Service('TFileService', fileName=cms.string(opts.histFile))
# As in eecNano_cfg.py (the standard NanoAOD lheInfoTable settings).
process.lheInfoTable = cms.EDProducer('LHETablesProducer', lheInfo=cms.VInputTag('externalLHEProducer', 'source'),
                                      precision=cms.int32(14), storeLHEParticles=cms.bool(True))
from PhysicsTools.NanoAOD.globals_cff import genTable
from PhysicsTools.NanoAOD.genWeightsTable_cfi import genWeightsTable
process.genTable = genTable.clone()
process.genWeightsTable = genWeightsTable.clone()
task = cms.Task(process.lheInfoTable, process.genTable)
# Runs-tree sums of weights (genEventCount, genEventSumw), which merge.py records; its per-event tables are dropped
# (PDF and scale weights, 10 times the size of the rest; Generator_weight is the event weight).
process.genWeightsPath = cms.Path(process.genWeightsTable)
process.out = cms.OutputModule('NanoAODOutputModule', fileName=cms.untracked.string(opts.outputFile),
                               outputCommands=cms.untracked.vstring('drop *', 'keep nanoaodFlatTable_*Table_*_*',
                                                                    'drop nanoaodFlatTable_genWeightsTable_*_*',
                                                                    'keep nanoaodMergeableCounterTable_*Table_*_*'))
process.outPath = cms.EndPath(process.out, task)
