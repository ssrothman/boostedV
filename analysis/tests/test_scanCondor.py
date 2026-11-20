"""Tests of scanCondor.py: job splitting and the merge back into one scan."""
import unittest

import scanCondor as sc


class Split(unittest.TestCase):
    def test_jobs_in_local_section_order(self):
        spec = {'tables': {'a': 'root://x//t.coffea'},
                'scans': {'s1': {'tables': 'a', 'args': ['--scan', 'tagger', '--rebin', 2],
                                 'split': {'taggers': ['VV:gpV', 'ZH:gpV'], 'obs': ['e2cn1', 'both']}},
                          's2': {'tables': 'a', 'args': [], 'split': {'signals': ['VV'], 'obs': ['msd']}}}}
        jobs = sc.jobsOf(spec)
        self.assertEqual([(j['scan'], j['args'][-3], j['args'][-1]) for j in jobs],
                         [('s1', 'VV:gpV', 'e2cn1'), ('s1', 'VV:gpV', 'both'), ('s1', 'ZH:gpV', 'e2cn1'),
                          ('s1', 'ZH:gpV', 'both'), ('s2', 'VV', 'msd')])
        self.assertEqual(jobs[0]['args'], ['--scan', 'tagger', '--rebin', '2', '--taggers', 'VV:gpV', '--obs', 'e2cn1'])
        self.assertEqual(jobs[4]['args'][:2], ['--signals', 'VV'])
        self.assertEqual(jobs[0]['tables'], 'root://x//t.coffea')


class Collect(unittest.TestCase):
    def md(self, signal, obs):
        return ('# Sensitivity scans\n\nheader\n\n## %s, %s\n\n| a |\n|---|\n| 1 |\n\n## Binning, %s, %s (baseline cuts)\n\n'
                '| b |\n' % (signal, obs, signal, obs))

    def test_full_scan_matches_local_order_and_results(self):
        parts = [(self.md(s, o), {s: {o: {'cut': 1}}, 'binning': {s: {o: {'bin': 2}}}}, 'log %s %s\n' % (s, o))
                 for s in ('VV', 'ZH') for o in ('e2cn1', 'both')]
        md, res, log = sc.collectScan(parts)
        heads = [l for l in md.split('\n') if l.startswith('## ')]
        self.assertEqual(heads, ['## VV, e2cn1', '## VV, both', '## ZH, e2cn1', '## ZH, both',
                                 '## Binning, VV, e2cn1 (baseline cuts)', '## Binning, VV, both (baseline cuts)',
                                 '## Binning, ZH, e2cn1 (baseline cuts)', '## Binning, ZH, both (baseline cuts)'])
        self.assertEqual(md.count('# Sensitivity scans'), 1)
        self.assertIn('## VV, e2cn1\n\n| a |\n|---|\n| 1 |\n\n## VV, both', md)
        self.assertEqual(res['binning'], {'VV': {'e2cn1': {'bin': 2}, 'both': {'bin': 2}},
                                          'ZH': {'e2cn1': {'bin': 2}, 'both': {'bin': 2}}})
        self.assertEqual(res['ZH']['both'], {'cut': 1})
        self.assertEqual(log.count('log'), 4)

    def test_conflicting_results_raise(self):
        with self.assertRaises(ValueError):
            sc.merge({'VV': {'e2cn1': {'cut': 1}}}, {'VV': {'e2cn1': {'cut': 2}}})


if __name__ == '__main__':
    unittest.main()
