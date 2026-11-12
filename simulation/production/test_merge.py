"""Integration test of merge.py (inside cmsenv; about 5 min): python3 -m unittest -v test_merge

Each test file in testdata/ is split in two halves; eecNano_cfg.py runs once on both halves together and once per
half as two jobs. Merging the two jobs must reproduce the single job. Outputs are cached in $MERGE_TEST_DIR
(default: a new temporary directory).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compareOutputs  # noqa: E402
import merge  # noqa: E402

REPO = os.path.dirname(os.path.dirname(HERE))
CFG = os.path.join(os.path.dirname(HERE), 'configs', 'eecNano_cfg.py')
TESTDATA = os.path.join(REPO, 'testdata')
INPUTS = {
    'mc': ('DYto2L-4Jets_MLL-50_PTLL-400to600_MLM_Summer22EE_1000ev.root', 500, 1,
           '130X_mcRun3_2022_realistic_postEE_v6', ''),
    # 250 events in each of 8 lumis, so the halves hold disjoint lumis; 2 of the 8 are not golden.
    'data': ('Muon_Run2022F-22Sep2023_8lumis_2000ev.root', 1000, 0, '130X_dataRun3_PromptAnalysis_v1',
             '/cvmfs/cms-griddata.cern.ch/cat/metadata/DC/Collisions22/2026-05-28/'
             'Cert_Collisions2022_eraF_360390_362167_Golden.json'),
}
SPLIT_CFG = '''import FWCore.ParameterSet.Config as cms
process = cms.Process('SPLIT')
process.source = cms.Source('PoolSource', fileNames=cms.untracked.vstring('file:%s'),
                            skipEvents=cms.untracked.uint32(%d))
process.maxEvents.input = %d
process.out = cms.OutputModule('PoolOutputModule', fileName=cms.untracked.string('%s'))
process.e = cms.EndPath(process.out)
'''


def run(cmds, cwd):
    """Runs the commands in parallel; raises if any fails."""
    procs = [(c, subprocess.Popen(c, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True))
             for c in cmds]
    for c, p in procs:
        _, err = p.communicate()
        if p.returncode:
            raise RuntimeError('%s failed:\n%s' % (' '.join(c), err[-3000:]))


def produce(work):
    """Fills work/<kind>/{single,jobs/0000}/ unless already there."""
    for kind, (name, half, isMC, gt, mask) in INPUTS.items():
        d = os.path.join(work, kind)
        if os.path.exists(os.path.join(d, 'done')):
            continue
        os.makedirs(os.path.join(d, 'jobs', '0000'), exist_ok=True)
        os.makedirs(os.path.join(d, 'single'), exist_ok=True)
        for i, (skip, n) in enumerate(((0, half), (half, -1))):
            with open(os.path.join(d, 'split%d_cfg.py' % i), 'w') as f:
                f.write(SPLIT_CFG % (os.path.join(TESTDATA, name), skip, n, os.path.join(d, 'half%d.root' % i)))
        run([['cmsRun', 'split0_cfg.py'], ['cmsRun', 'split1_cfg.py']], d)
        common = ['config=default.yaml', 'globalTag=' + gt, 'isMC=%d' % isMC] + (['lumiMask=' + mask] if mask else [])
        jobs = [['cmsRun', CFG, 'inputFiles=file:half0.root,file:half1.root', 'outputFile=single/nano.root',
                 'histFile=single/hists.root'] + common]
        for i in range(2):
            jobs.append(['cmsRun', CFG, 'inputFiles=file:half%d.root' % i, 'outputFile=jobs/0000/nano_%d.root' % (i + 1),
                         'histFile=jobs/0000/hists_%d.root' % (i + 1)] + common)
        run(jobs, d)
        open(os.path.join(d, 'done'), 'w').close()


class Merge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = os.environ.get('MERGE_TEST_DIR') or tempfile.mkdtemp()
        produce(cls.work)

    def merged(self, kind, **kw):
        out = tempfile.mkdtemp()
        info = merge.merge(os.path.join(self.work, kind, 'jobs'), out, INPUTS[kind][2] == 1, **kw)
        return out, info

    def single(self, kind, f):
        return os.path.join(self.work, kind, 'single', f)

    def assertMergeReproducesSingle(self, kind):
        out, info = self.merged(kind, expected=[1, 2])
        self.assertEqual(info['jobs'], [1, 2])
        self.assertEqual(info['missing'], [])
        diffs = compareOutputs.compareHists(self.single(kind, 'hists.root'), os.path.join(out, 'hists.root'),
                                            rtol=1e-12)
        self.assertEqual(diffs, [])
        import uproot
        with uproot.open(self.single(kind, 'nano.root')) as nano:
            self.assertEqual(info['eventsWritten'], nano['Events'].num_entries)
            self.assertGreater(info['eventsWritten'], 50)
            if kind == 'mc':
                runs = nano['Runs'].arrays(list(merge.GEN_SUMS), library='np')
                self.assertEqual(info['genEventCount'], 1000)
                for k in merge.GEN_SUMS:
                    self.assertAlmostEqual(info[k], runs[k].sum().item(), delta=1e-9 * abs(info[k]))
            else:
                lb = nano['LuminosityBlocks'].arrays(['run', 'luminosityBlock'], library='np')
                with open(os.path.join(out, 'processedLumis.json')) as f:
                    self.assertEqual(json.load(f), merge.lumiRanges(zip(lb['run'].tolist(),
                                                                       lb['luminosityBlock'].tolist())))
        return out, info

    def test_mc(self):
        self.assertMergeReproducesSingle('mc')

    def test_data(self):
        out, _ = self.assertMergeReproducesSingle('data')
        with open(os.path.join(out, 'processedLumis.json')) as f:
            # golden lumis of the skim (225 and 226 of run 360458 are not certified)
            self.assertEqual(json.load(f), {'360458': [[215, 215], [236, 237], [241, 241]], '360459': [[4, 4], [6, 6]]})

    def test_one_job_is_not_the_single_run(self):
        """Discrimination: merging only one half differs from the single run."""
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, '0000'))
        for f in ('nano_1.root', 'hists_1.root'):
            shutil.copy(os.path.join(self.work, 'mc', 'jobs', '0000', f), os.path.join(d, '0000', f))
        out = tempfile.mkdtemp()
        info = merge.merge(d, out, True)
        self.assertLess(info['genEventCount'], 1000)
        diffs = compareOutputs.compareHists(self.single('mc', 'hists.root'), os.path.join(out, 'hists.root'),
                                            rtol=1e-12)
        self.assertGreater(len(diffs), 100)
        self.assertTrue(any(x.split(':')[0].endswith('/nEvents') for x in diffs))

    def test_missing_and_unexpected_jobs(self):
        with self.assertRaisesRegex(RuntimeError, '1 jobs missing'):
            self.merged('mc', expected=[1, 2, 3])
        _, info = self.merged('mc', expected=[1, 2, 3], allowMissing=True)
        self.assertEqual(info['missing'], [3])
        with self.assertRaisesRegex(RuntimeError, 'not submitted: \\[2\\]'):
            self.merged('mc', expected=[1])


if __name__ == '__main__':
    unittest.main()
