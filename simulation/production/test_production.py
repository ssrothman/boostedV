"""Unit tests of the production tooling (inside cmsenv, with crab-setup.sh sourced for the CRAB tests):
python3 -m unittest -v test_production"""
import copy
import os
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import condorBackend  # noqa: E402
import manifest  # noqa: E402
import merge  # noqa: E402
import outputs  # noqa: E402
import status  # noqa: E402

SAMPLES = os.path.join(HERE, 'samples.yaml')
MC, DATA = 'DYto2L-4Jets_MLM_PTLL-400to600', 'Muon_Run2022F-22Sep2023'


def loadRaw():
    with open(SAMPLES) as f:
        return yaml.safe_load(f)


def writeManifest(man, dirname=HERE):
    """Written next to samples.yaml so that relative config paths still resolve."""
    f = tempfile.NamedTemporaryFile('w', suffix='.yaml', dir=dirname, delete=False)
    yaml.safe_dump(man, f)
    f.close()
    return f.name


class Manifest(unittest.TestCase):
    def assertRejected(self, mutate, *fragments):
        man = loadRaw()
        mutate(man)
        path = writeManifest(man)
        try:
            with self.assertRaises(manifest.ManifestError) as ctx:
                manifest.load(path)
        finally:
            os.unlink(path)
        for frag in fragments:
            self.assertIn(frag, str(ctx.exception))

    def test_default_is_valid(self):
        man = manifest.load(SAMPLES)
        self.assertTrue(os.path.isabs(man['samples'][MC]['config']))
        self.assertTrue(os.path.isfile(man['samples'][DATA]['lumiMask']))

    def test_schema(self):
        self.assertRejected(lambda m: m.update(extra=1), 'Additional properties')
        self.assertRejected(lambda m: m['samples'][MC].update(extra=1), 'samples/%s' % MC)
        self.assertRejected(lambda m: m['samples'][MC].pop('globalTag'), 'globalTag')
        self.assertRejected(lambda m: m['samples'][MC].update(backend='slurm'), 'backend')
        self.assertRejected(lambda m: m['samples'][MC].update(maxJobs=0), 'maxJobs')
        self.assertRejected(lambda m: m['samples'].update({'bad/name': m['samples'][MC]}), 'bad/name')
        self.assertRejected(lambda m: m.update(outputBase='/eos/uscms/store/user/x'), 'outputBase')

    def test_cross_checks(self):
        self.assertRejected(lambda m: m['samples'][DATA].update(lumiMask=''), 'data needs a lumiMask')
        self.assertRejected(lambda m: m['samples'][MC].update(lumiMask=m['samples'][DATA]['lumiMask']),
                            'lumiMask is for data only')
        self.assertRejected(lambda m: m['samples'][DATA].update(lumiMask='nope.json'), 'not found')
        self.assertRejected(lambda m: m['samples'][MC]['splitting'].update(mode='events'),
                            'condor supports only files')
        self.assertRejected(lambda m: m['samples'][DATA].update(input={'fileList': SAMPLES}),
                            'fileList input needs the condor backend')
        self.assertRejected(lambda m: m['samples'][MC].update(config='nope.yaml'), 'config')

    def test_gen_only_config_for_data(self):
        with open(os.path.join(manifest.CONFIGS, 'default.yaml')) as f:
            cfg = yaml.safe_load(f)
        cfg['selection']['levels'] = ['gen']
        with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False) as f:
            yaml.safe_dump(cfg, f)
        self.assertRejected(lambda m: m['samples'][DATA].update(config=f.name), 'need gen')
        man = loadRaw()
        man['samples'][MC]['config'] = f.name
        path = writeManifest(man)
        try:
            manifest.load(path)  # gen-only is fine for MC
        finally:
            os.unlink(path)

    def test_dataset_global_tag(self):
        gt = '130X_mcRun3_2022_realistic_postEE_v6'
        for proc in ('Run3Summer22EEMiniAODv4-%s-v3' % gt, 'Run3Summer22EEMiniAODv4-%s_ext1-v3' % gt,
                     'Run3Summer22EEMiniAODv4-FS22_%s-v3' % gt):
            self.assertEqual(manifest.datasetGlobalTag('/DY/%s/MINIAODSIM' % proc), gt)
        self.assertIsNone(manifest.datasetGlobalTag('/Muon/Run2022F-22Sep2023-v2/MINIAOD'))

    def test_tag(self):
        self.assertEqual(manifest.checkTag('20261112_dy-test'), '20261112_dy-test')
        for bad in ('dy', '2026111_x', '20261112_', '20261112_a/b', '20261112_a_b'):
            with self.assertRaises(manifest.ManifestError):
                manifest.checkTag(bad)


class Condor(unittest.TestCase):
    def setUp(self):
        self.sample = manifest.load(SAMPLES)['samples']

    def test_chunks_cover_files_once(self):
        files = ['/store/f%d.root' % i for i in range(23)]
        for n in (1, 5, 23, 40):
            c = condorBackend.chunks(files, n, -1)
            self.assertEqual(sum(c, []), files)
            self.assertTrue(all(1 <= len(x) <= n for x in c))
            self.assertEqual(len(c), -(-23 // n))
        self.assertEqual(condorBackend.chunks(files, 5, 2), [files[:5], files[5:10]])

    def test_job_args(self):
        files = ['/store/a.root', '/store/b.root', 'root://other//store/c.root']
        s = copy.deepcopy(self.sample[DATA])
        s['splitting']['unitsPerJob'] = 2
        lines = condorBackend.jobArgs(s, files, 'root://eos//store/user/x/T/S', 'root://eos//t.tgz',
                                      'root://in')
        self.assertEqual(lines, [
            '0 root://in//store/a.root,root://in//store/b.root root://eos//store/user/x/T/S root://eos//t.tgz '
            'default.yaml 130X_dataRun3_PromptAnalysis_v1 0 Cert_Collisions2022_eraF_360390_362167_Golden.json',
            '1 root://other//store/c.root root://eos//store/user/x/T/S root://eos//t.tgz '
            'default.yaml 130X_dataRun3_PromptAnalysis_v1 0 Cert_Collisions2022_eraF_360390_362167_Golden.json'])
        mc = condorBackend.jobArgs(self.sample[MC], files[:1], 'o', 't', 'root://in')
        self.assertEqual(mc[0].split()[5:], ['130X_mcRun3_2022_realistic_postEE_v6', '1', 'none'])

    def test_jdl_ships_cfg_and_mask(self):
        w = tempfile.mkdtemp()
        inputs = condorBackend.snapshotInputs(self.sample[DATA], w)
        self.assertEqual(sorted(os.listdir(os.path.join(w, 'inputs'))),
                         sorted([os.path.basename(f) for f in inputs] + ['job.sh']))
        self.assertTrue(os.access(os.path.join(w, 'inputs', 'job.sh'), os.X_OK))
        for f in inputs:
            self.assertTrue(f.startswith(os.path.join(w, 'inputs') + '/'))
        j = condorBackend.jdl('/w', inputs, '/w/jobs.txt', '/proxy')
        inputs = [l for l in j.splitlines() if l.startswith('transfer_input_files')][0]
        for f in ('eecNano_cfg.py', 'analysisConfig.py', 'analysis.schema.yaml', 'default.yaml',
                  'Cert_Collisions2022_eraF_360390_362167_Golden.json'):
            self.assertIn('/' + f, inputs)
        self.assertIn('queue args from /w/jobs.txt', j)
        self.assertIn('x509userproxy = /proxy', j)
        self.assertIn('executable = /w/inputs/job.sh', j)

    def test_tarball_dereferences_src_only(self):
        d = tempfile.mkdtemp()
        base, pkg = os.path.join(d, 'CMSSW_X'), os.path.join(d, 'repo', 'Pkg')
        for sub in ('python', 'build', 'interface'):
            os.makedirs(os.path.join(pkg, sub))
        with open(os.path.join(pkg, 'python', 'mod.py'), 'w') as f:
            f.write('x = 1\n')
        os.symlink(pkg, os.path.join(pkg, 'build', 'loop'))  # like EECs/build
        os.makedirs(os.path.join(base, 'src', 'Grp'))
        os.symlink(pkg, os.path.join(base, 'src', 'Grp', 'Pkg'))
        os.makedirs(os.path.join(base, 'lib'))
        with open(os.path.join(base, 'lib', 'libX.so'), 'w') as f:
            f.write('so')
        os.makedirs(os.path.join(base, 'external'))
        os.symlink('/cvmfs/somewhere', os.path.join(base, 'external', 'ext'))
        os.makedirs(os.path.join(base, 'tmp', 'big'))
        tgz = condorBackend.makeTarball(base, os.path.join(d, 'x.tgz'))
        with tarfile.open(tgz) as t:
            m = {i.name: i for i in t.getmembers()}
            self.assertTrue(m['CMSSW_X/src/Grp/Pkg'].isdir())
            self.assertEqual(t.extractfile('CMSSW_X/src/Grp/Pkg/python/mod.py').read(), b'x = 1\n')
            self.assertIn('CMSSW_X/src/Grp/Pkg/interface', m)
            self.assertIn('CMSSW_X/lib/libX.so', m)
            self.assertTrue(m['CMSSW_X/external/ext'].issym())
            self.assertFalse([n for n in m if '/build' in n or '/tmp' in n])

    def test_parse_submit(self):
        out = ('Querying the CMS LPC pool and trying to find an available schedd...\n\n'
               'Attempting to submit jobs to lpcschedd4.fnal.gov\n\n'
               'Submitting job(s)...\n3 job(s) submitted to cluster 4242.\n')
        self.assertEqual(condorBackend.parseSubmit(out), {'cluster': 4242, 'schedd': 'lpcschedd4.fnal.gov'})
        with self.assertRaisesRegex(RuntimeError, 'not understood'):
            condorBackend.parseSubmit('3 job(s) submitted to cluster 4242.\n')


class Tarball(unittest.TestCase):
    """submit.condorTarball with the build, git and EOS calls replaced."""

    def setUp(self):
        import submit
        self.submit = submit
        self.dir = tempfile.mkdtemp()
        self.man = {'eosRedirector': 'root://eos', 'outputBase': '/store/user/x'}
        self.state, self.onEOS, self.copied = 'commit A\n', None, []

    def build(self, base, path):
        with open(path, 'w') as f:
            f.write('tarball')

    def call(self, dryrun=False):
        def run(cmd, **kw):
            self.copied.append(cmd)
        with mock.patch.object(self.submit, 'codeState', lambda: self.state), \
                mock.patch.object(self.submit, 'remoteAdler32', lambda host, path: self.onEOS), \
                mock.patch.object(condorBackend, 'makeTarball', self.build), \
                mock.patch.object(self.submit.subprocess, 'run', run), \
                mock.patch.dict(os.environ, {'CMSSW_BASE': '/cmssw'}):
            return self.submit.condorTarball(self.dir, self.man, 'T', dryrun)

    def test_adler32(self):
        p = os.path.join(self.dir, 'w')
        with open(p, 'w') as f:
            f.write('Wikipedia')
        self.assertEqual(self.submit.adler32(p), '11e60398')

    def test_build_upload_reuse(self):
        url, checksum = self.call(dryrun=True)
        self.assertEqual(url, 'root://eos//store/user/x/T/cmssw.tgz')
        self.assertEqual(checksum, self.submit.adler32(os.path.join(self.dir, 'cmssw.tgz')))
        self.assertEqual(self.copied, [])
        self.call()
        self.assertEqual(self.copied, [['xrdcp', os.path.join(self.dir, 'cmssw.tgz'), url]])
        self.onEOS = checksum
        self.assertEqual(self.call(), (url, checksum))
        self.assertEqual(len(self.copied), 1)

    def test_refuses_other_code(self):
        self.call()
        self.state = 'commit B\n'
        with self.assertRaisesRegex(SystemExit, 'built from other code'):
            self.call()
        os.unlink(os.path.join(self.dir, 'cmssw.tgz.state'))
        self.state = 'commit A\n'
        with self.assertRaisesRegex(SystemExit, 'built from other code'):
            self.call()

    def test_refuses_other_eos_copy(self):
        self.onEOS = 'deadbeef'
        with self.assertRaisesRegex(SystemExit, 'is not'):
            self.call()
        self.assertEqual(self.copied, [])


class Outputs(unittest.TestCase):
    def test_pairing(self):
        paths = ['/o/a/0000/nano_1.root', '/o/a/0000/hists_1.root', '/o/a/0000/nano_2.root',
                 '/o/b/hists_3.root', '/o/b/nano_3.root', '/o/merged/hists_9.root', '/o/merged/nano_9.root',
                 '/o/log/other.root']
        jobs, incomplete = outputs.pairJobs(paths)
        self.assertEqual(jobs, {1: {'nano': '/o/a/0000/nano_1.root', 'hists': '/o/a/0000/hists_1.root'},
                                3: {'nano': '/o/b/nano_3.root', 'hists': '/o/b/hists_3.root'}})
        self.assertEqual(incomplete, [2])
        with self.assertRaisesRegex(RuntimeError, 'two nano'):
            outputs.pairJobs(paths + ['/o/c/nano_1.root'])

    def test_local_listing_and_expected(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, 'x', '0000'))
        for f in ('x/0000/nano_1.root', 'x/0000/hists_1.root', 'x/0000/log.txt'):
            open(os.path.join(d, f), 'w').close()
        self.assertEqual([os.path.relpath(p, d) for p in outputs.listRoot(d)],
                         ['x/0000/hists_1.root', 'x/0000/nano_1.root'])
        self.assertIsNone(outputs.expectedJobs(d))
        with open(os.path.join(d, 'jobs.txt'), 'w') as f:
            f.write('0 a o t c g 1 none\n1 b o t c g 1 none\n')
        self.assertEqual(outputs.expectedJobs(d), [0, 1])

    def test_condor_missing(self):
        self.assertEqual(status.condorMissing(range(6), {0: 0, 2: 0}, {3}), [1, 4, 5])
        self.assertEqual(status.condorMissing(range(6), {0: 0}, {3: (2, 's'), 4: (status.HELD, 's')}), [1, 2, 5])
        clusters = [{'cluster': 7, 'schedd': 'a'}, {'cluster': 8, 'schedd': 'b'}, {'cluster': 9, 'schedd': 'a'}]
        self.assertEqual(status.heldConstraint(clusters, 'a'), 'JobStatus == 5 && (ClusterId == 7 || ClusterId == 9)')
        self.assertEqual(status.heldConstraint(clusters, 'b'), 'JobStatus == 5 && (ClusterId == 8)')

    def test_queue_keeps_recorded_schedd_cluster_pairs(self):
        # Cluster 7 exists on both schedds; only the one on s1 is ours.
        res = ('1 s1.fnal.gov#7.0#1700000000 0 a o t c g 1 none\n'
               '5 s1.fnal.gov#7.1#1700000000 1 a o t c g 1 none\n'
               '2 s2.fnal.gov#7.0#1700000001 2 a o t c g 1 none\n'
               '2 s2.fnal.gov#8.0#1700000002 3 a o t c g 1 none\n')
        clusters = [{'cluster': 7, 'schedd': 's1.fnal.gov'}, {'cluster': 8, 'schedd': 's2.fnal.gov'}]
        self.assertEqual(status.parseQueue(res, clusters),
                         {0: (1, 's1.fnal.gov'), 1: (5, 's1.fnal.gov'), 3: (2, 's2.fnal.gov')})

    def test_merge_needs_job_list(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, 'crab.json'), 'w') as f:
            f.write('{"backend": "crab"}')
        with self.assertRaisesRegex(RuntimeError, 'no job list'):
            merge.expectedOrFail(d)
        with open(os.path.join(d, 'crabJobs.json'), 'w') as f:
            f.write('[1, 2, 3]')
        self.assertEqual(merge.expectedOrFail(d), [1, 2, 3])

    def test_lumi_ranges(self):
        self.assertEqual(merge.lumiRanges([(2, 5), (1, 3), (1, 1), (1, 2), (1, 2), (2, 7), (2, 6)]),
                         {'1': [[1, 3]], '2': [[5, 7]]})
        self.assertEqual(merge.lumiRanges([(1, 1), (1, 3)]), {'1': [[1, 1], [3, 3]]})


def writeHists(path, change=None):
    """A TFileService-like file; change names the one thing to alter."""
    import ROOT
    f = ROOT.TFile(path, 'RECREATE')
    d = f.mkdir('ch_reco_obs')
    d.cd()
    h = ROOT.TH1D('values', '', 3, -0.5, 2.5)
    for i, (v, e) in enumerate([(1.0, 0.5), (2.0, 0.25), (3.0, 1.0)]):
        h.SetBinContent(i + 1, v + (1e-6 if change == 'content' and i == 1 else 0))
        h.SetBinError(i + 1, e * (2 if change == 'error' and i == 2 else 1))
    c = ROOT.TH2D('covariance', '', 2, 0, 2, 2, 0, 2)
    c.SetBinContent(1, 2, 7.0 if change != 'cov' else 7.5)
    edges = [0.0, 1.0, 3.0] if change != 'edges' else [0.0, 1.5, 3.0]
    import array
    ROOT.TH1D('axis0', '', 2, array.array('d', edges)).Write()
    ROOT.TParameter('double')('sumW', 4.0 if change != 'sumW' else 4.5).Write()
    ROOT.TNamed('axisTypes', 'log' if change != 'type' else 'regular').Write()
    h.Write()
    c.Write()
    f.Close()


class Compare(unittest.TestCase):
    def test_hists(self):
        import compareOutputs
        d = tempfile.mkdtemp()
        ref = os.path.join(d, 'ref.root')
        writeHists(ref)
        writeHists(os.path.join(d, 'same.root'))
        self.assertEqual(compareOutputs.compareHists(ref, os.path.join(d, 'same.root')), [])
        for change, obj in (('content', 'values'), ('error', 'values'), ('cov', 'covariance'), ('edges', 'axis0'),
                            ('sumW', 'sumW'), ('type', 'axisTypes')):
            p = os.path.join(d, change + '.root')
            writeHists(p, change)
            diffs = compareOutputs.compareHists(ref, p)
            self.assertEqual(len(diffs), 1, (change, diffs))
            self.assertTrue(diffs[0].startswith('ch_reco_obs/' + obj), diffs)
        self.assertEqual(compareOutputs.compareHists(ref, os.path.join(d, 'content.root'), rtol=1e-3), [])
        self.assertEqual(len(compareOutputs.compareHists(ref, os.path.join(d, 'content.root'), rtol=1e-9)), 1)

    def test_nano(self):
        import numpy as np
        import uproot
        import compareOutputs
        d = tempfile.mkdtemp()

        def write(name, x, jag):
            with uproot.recreate(os.path.join(d, name)) as f:
                import awkward as ak
                f['Events'] = {'x': np.array(x), 'j': ak.Array(jag)}
                f['Runs'] = {'run': np.array([1])}
                f['LuminosityBlocks'] = {'run': np.array([1]), 'luminosityBlock': np.array([2])}
            return os.path.join(d, name)
        a = write('a.root', [1.0, 2.0], [[1.0], [2.0, 3.0]])
        self.assertEqual(compareOutputs.compareNano(a, write('b.root', [1.0, 2.0], [[1.0], [2.0, 3.0]])), [])
        self.assertEqual(compareOutputs.compareNano(a, write('c.root', [1.0, 2.5], [[1.0], [2.0, 3.0]])),
                         ['Events/x differs'])
        self.assertEqual(compareOutputs.compareNano(a, write('e.root', [1.0, 2.0], [[1.0], [2.0, 3.5]])),
                         ['Events/j differs'])
        self.assertEqual(compareOutputs.compareNano(a, write('f.root', [1.0], [[1.0]])), ['Events: 2 vs 1 entries'])


class Crab(unittest.TestCase):
    def setUp(self):
        try:
            import crabBackend
            import CRABClient.UserUtilities  # noqa: F401
        except ImportError:
            self.fail('source /cvmfs/cms.cern.ch/common/crab-setup.sh first')
        self.crab = crabBackend
        self.man = manifest.load(SAMPLES)

    def test_mc_config(self):
        s = self.man['samples']['DYto2L-4Jets_MLM_PTLL-600']
        c = self.crab.makeConfig(s, 'S', '20261112_t', self.man, '/w')
        self.assertEqual(c.General.requestName, 'S')
        self.assertEqual(c.Data.inputDataset, s['input']['dataset'])
        self.assertEqual(c.Data.splitting, 'FileBased')
        self.assertEqual(c.Data.unitsPerJob, 5)
        self.assertFalse(hasattr(c.Data, 'totalUnits'))
        self.assertFalse(hasattr(c.Data, 'lumiMask'))
        self.assertEqual(c.Data.outLFNDirBase, '/store/user/srothman/boostedV/20261112_t/S')
        self.assertEqual(c.Site.storageSite, 'T3_US_FNALLPC')
        self.assertEqual(c.JobType.pyCfgParams, ['config=' + s['config'],
                                                 'globalTag=130X_mcRun3_2022_realistic_postEE_v6', 'isMC=1',
                                                 'outputFile=nano.root', 'histFile=hists.root'])

    def test_data_config(self):
        s = copy.deepcopy(self.man['samples'][DATA])
        s.update(maxJobs=3, splitting={'mode': 'events', 'unitsPerJob': 1000})
        c = self.crab.makeConfig(s, 'D', '20261112_t', self.man, '/w')
        self.assertEqual(c.Data.lumiMask, s['lumiMask'])
        self.assertEqual(c.Data.splitting, 'EventAwareLumiBased')
        self.assertEqual(c.Data.totalUnits, 3000)
        self.assertIn('isMC=0', c.JobType.pyCfgParams)
        self.assertFalse([p for p in c.JobType.pyCfgParams if p.startswith('lumiMask')])


if __name__ == '__main__':
    unittest.main()
