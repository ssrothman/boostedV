"""Final-selection efficiencies of a merged ZX_test production, for the last rows of the AN cutflow tables.

Usage: python3 final_rows.py OUT.json NAME=work/<tag>/<sample>/merged/sample.json [...]
Per sample: events passing <c> (Selection_<c>, GenSelection_<c>) per level and channel and in any of them, unweighted and
as a genWeight-weighted fraction of the processed events of the merged jobs (sample.json genEventSumw). NANOs are read
over xrootd (only the flags and genWeight).
"""
import json
import sys

import numpy as np
import uproot

CHANNELS = ('Zmumu', 'Zee')
LEVELS = {'reco': 'Selection_', 'gen': 'GenSelection_'}


def rows(sample):
    flags = [p + c for p in LEVELS.values() for c in CHANNELS]
    n = {f: 0 for f in flags + ['any']}
    w = {f: 0.0 for f in flags + ['any']}
    for f in sample['nanoFiles']:
        t = uproot.open(f)['Events']
        if t.num_entries == 0:   # a job without selected events writes a tree without branches
            continue
        ev = t.arrays(flags + ['genWeight'], library='np')
        anyPass = np.zeros(len(ev['genWeight']), dtype=bool)
        for k in flags:
            p = ev[k].astype(bool)
            anyPass |= p
            n[k] += int(p.sum())
            w[k] += float(ev['genWeight'][p].sum())
        n['any'] += int(anyPass.sum())
        w['any'] += float(ev['genWeight'][anyPass].sum())
    sw = sample['genEventSumw']
    return {'genEventCount': sample['genEventCount'], 'genEventSumw': sw, 'nanoFiles': len(sample['nanoFiles']),
            'missingJobs': len(sample['missing']), 'eventsWritten': sample['eventsWritten'],
            'pass': {k: {'n': n[k], 'frac': w[k] / sw} for k in n}}


def main():
    out, pairs = sys.argv[1], [a.split('=', 1) for a in sys.argv[2:]]
    res = {}
    for name, path in pairs:
        res[name] = rows(json.load(open(path)))
        assert res[name]['pass']['any']['n'] == res[name]['eventsWritten'], name   # ZX_test writes exactly these
        print(name, {k: (v['n'], '%.4g%%' % (100 * v['frac'])) for k, v in res[name]['pass'].items()})
    json.dump(res, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
