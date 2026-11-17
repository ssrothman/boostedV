"""Tests of condor.py: job splitting, status from the condor user log, and collecting the per-job outputs."""
import json
import os
import sys
import tempfile
import unittest

import hist

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import condor  # noqa: E402


def fileset():
    return {'A': {'files': {'a%d.root' % i: 'Events' for i in range(5)}, 'metadata': {'sample': 'A', 'lumiScale': 2.0}},
            'B': {'files': {'b%d.root' % i: 'Events' for i in range(2)}, 'metadata': {'sample': 'B', 'isMC': True}}}


class Split(unittest.TestCase):
    def test_every_file_once_and_metadata_kept(self):
        jobs = condor.split(fileset(), 2)
        self.assertEqual([(list(j)[0], len(j[list(j)[0]]['files'])) for j in jobs], [('A', 2), ('A', 2), ('A', 1), ('B', 2)])
        seen = [f for j in jobs for e in j.values() for f in e['files']]
        self.assertEqual(sorted(seen), sorted(f for e in fileset().values() for f in e['files']))
        self.assertEqual(jobs[2]['A']['metadata'], {'sample': 'A', 'lumiScale': 2.0})


LOG = '''000 (101.000.000) 2026-11-17 17:00:00 Job submitted from host: <1.2.3.4:9618>
...
000 (101.001.000) 2026-11-17 17:00:00 Job submitted from host: <1.2.3.4:9618>
...
000 (101.002.000) 2026-11-17 17:00:00 Job submitted from host: <1.2.3.4:9618>
...
001 (101.000.000) 2026-11-17 17:01:00 Job executing on host: <5.6.7.8:9618>
...
001 (101.001.000) 2026-11-17 17:01:00 Job executing on host: <5.6.7.8:9618>
...
005 (101.000.000) 2026-11-17 17:05:00 Job terminated.
\t(1) Normal termination (return value 0)
...
005 (101.001.000) 2026-11-17 17:05:00 Job terminated.
\t(1) Normal termination (return value 1)
...
000 (102.000.000) 2026-11-17 17:10:00 Job submitted from host: <1.2.3.4:9618>
...
'''


class Status(unittest.TestCase):
    def test_log_and_parts(self):
        with tempfile.TemporaryDirectory() as d:
            for sub in ('logs', 'parts'):
                os.makedirs(os.path.join(d, sub))
            # cluster 101 ran jobs 0, 1, 2; cluster 102 resubmitted job 1
            state = {'nJobs': 4, 'clusters': [{'cluster': 101, 'jobs': [0, 1, 2]}, {'cluster': 102, 'jobs': [1]}]}
            with open(os.path.join(d, 'state.json'), 'w') as f:
                json.dump(state, f)
            with open(os.path.join(d, 'logs', 'condor.log'), 'w') as f:
                f.write(LOG)
            open(os.path.join(d, 'parts', 'part_0.coffea'), 'w').close()
            st = condor.status(d)
            # job 1: failed in 101, then the resubmission's submit event is the latest
            self.assertEqual(st, {0: 'complete', 1: 'idle', 2: 'idle', 3: 'unsubmitted'})
            state['clusters'] = state['clusters'][:1]
            with open(os.path.join(d, 'state.json'), 'w') as f:
                json.dump(state, f)
            self.assertEqual(condor.status(d)[1], 'failed')
            os.remove(os.path.join(d, 'parts', 'part_0.coffea'))
            self.assertEqual(condor.status(d)[0], 'failed')   # ended with 0 but no output came back


def part(value, cut):
    h = hist.Hist(hist.axis.Regular(2, 0, 2, name='x'), storage='weight')
    h.fill([0.5], weight=[value])
    return {'hists': {'h': {'R': {'S': h}}}, 'cutflow': {'R': {'S': {'channel': {'n': cut, 'sumw': 1.0 * cut}}}},
            'sumw': {'S': value}}


class Collect(unittest.TestCase):
    def test_accumulates_and_refuses_missing(self):
        from coffea.util import save
        with tempfile.TemporaryDirectory() as d:
            paths = [os.path.join(d, 'part_%d.coffea' % k) for k in range(3)]
            for k, p in enumerate(paths[:2]):
                save(part(k + 1.0, 10 * (k + 1)), p)
            with self.assertRaises(SystemExit):
                condor.collect(paths)
            out, missing = condor.collect(paths, allowMissing=True)
            self.assertEqual(missing, [paths[2]])
            self.assertEqual(out['hists']['h']['R']['S'].values().tolist(), [3.0, 0.0])
            self.assertEqual(out['cutflow']['R']['S']['channel'], {'n': 30, 'sumw': 30.0})
            self.assertEqual(out['sumw'], {'S': 3.0})


if __name__ == '__main__':
    unittest.main()
