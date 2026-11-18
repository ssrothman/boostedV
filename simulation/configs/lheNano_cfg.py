"""MiniAOD -> NANO with only the LHE tables (LHE, LHEPart) and generator weights, for every event (no selection).
Input of the truth spin-density matrix extraction (analysis/truthRho.py), which must not see acceptance cuts.

cmsRun lheNano_cfg.py inputFiles=file:in.root outputFile=lhe.root maxEvents=-1
"""
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

opts = VarParsing('analysis')
opts.parseArguments()

process = cms.Process('LHENANO')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 10000
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring(opts.inputFiles))
process.maxEvents.input = opts.maxEvents
# As in eecNano_cfg.py (the standard NanoAOD lheInfoTable settings).
process.lheInfoTable = cms.EDProducer('LHETablesProducer', lheInfo=cms.VInputTag('externalLHEProducer', 'source'),
                                      precision=cms.int32(14), storeLHEParticles=cms.bool(True))
from PhysicsTools.NanoAOD.globals_cff import genTable
process.genTable = genTable.clone()
task = cms.Task(process.lheInfoTable, process.genTable)
process.out = cms.OutputModule('NanoAODOutputModule', fileName=cms.untracked.string(opts.outputFile),
                               outputCommands=cms.untracked.vstring('drop *', 'keep nanoaodFlatTable_*Table_*_*'))
process.outPath = cms.EndPath(process.out, task)
