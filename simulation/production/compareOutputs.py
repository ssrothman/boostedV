#!/usr/bin/env python3
"""Compares two eecNano outputs object by object (run inside cmsenv).

Usage: compareOutputs.py [--rtol R] [--nano A.root B.root] [--hists A.root B.root]

NANO: every branch of the Events, Runs and LuminosityBlocks trees (Events entries compared in order).
Hists: every object in every directory; TH1/TH2 contents and variances including flow, binning, TParameter
values, TNamed titles. Exit status 1 on any difference.
"""
import argparse
import sys

import numpy as np


def _close(a, b, rtol):
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape:
        return False
    if rtol == 0 or a.dtype.kind not in 'fc':
        return np.array_equal(a, b)
    return np.allclose(a, b, rtol=rtol, atol=0.0)


def compareNano(fa, fb, rtol=0.0):
    """Returns a list of difference descriptions between two NANO files."""
    import uproot
    diffs = []
    with uproot.open(fa) as A, uproot.open(fb) as B:
        for tree in ('Events', 'Runs', 'LuminosityBlocks'):
            ta, tb = A[tree], B[tree]
            if ta.num_entries != tb.num_entries:
                diffs.append('%s: %d vs %d entries' % (tree, ta.num_entries, tb.num_entries))
                continue
            ka, kb = set(ta.keys()), set(tb.keys())
            diffs += ['%s/%s only in first' % (tree, k) for k in sorted(ka - kb)]
            diffs += ['%s/%s only in second' % (tree, k) for k in sorted(kb - ka)]
            for k in sorted(ka & kb):
                va, vb = ta[k].array(library='np'), tb[k].array(library='np')
                if va.dtype == object:
                    same = len(va) == len(vb) and all(_close(x, y, rtol) for x, y in zip(va, vb))
                else:
                    same = _close(va, vb, rtol)
                if not same:
                    diffs.append('%s/%s differs' % (tree, k))
    return diffs


def _buffer(ptr, n):
    ptr.reshape((n,))
    return np.array(ptr, dtype=np.float64)


def _histArrays(h):
    """(contents, variances, axis edges), flow bins included."""
    n = h.GetNcells()
    vals = _buffer(h.GetArray(), n)
    sw2 = h.GetSumw2()
    var = _buffer(sw2.GetArray(), n) if sw2.GetSize() else vals.copy()
    edges = []
    for ax in (h.GetXaxis(), h.GetYaxis()):
        xb = ax.GetXbins()
        edges.append(_buffer(xb.GetArray(), xb.GetSize()) if xb.GetSize()
                     else np.array([ax.GetXmin(), ax.GetXmax(), ax.GetNbins()]))
    return vals, var, edges


def _objects(f):
    """{path: TObject} for every non-directory key, recursively."""
    import ROOT
    out = {}

    def walk(d, prefix):
        for key in d.GetListOfKeys():
            obj = key.ReadObj()
            path = prefix + key.GetName()
            if isinstance(obj, ROOT.TDirectory):
                walk(obj, path + '/')
            else:
                out[path] = obj
    walk(f, '')
    return out


def compareHists(fa, fb, rtol=0.0):
    """Returns a list of difference descriptions between two TFileService histogram files."""
    import ROOT
    A, B = ROOT.TFile.Open(fa), ROOT.TFile.Open(fb)
    oa, ob = _objects(A), _objects(B)
    diffs = ['%s only in first' % k for k in sorted(set(oa) - set(ob))]
    diffs += ['%s only in second' % k for k in sorted(set(ob) - set(oa))]
    for k in sorted(set(oa) & set(ob)):
        a, b = oa[k], ob[k]
        if a.ClassName() != b.ClassName():
            diffs.append('%s: class %s vs %s' % (k, a.ClassName(), b.ClassName()))
        elif isinstance(a, ROOT.TH1):
            (va, ea, xa), (vb, eb, xb) = _histArrays(a), _histArrays(b)
            if not all(np.array_equal(x, y) for x, y in zip(xa, xb)):
                diffs.append('%s: binning differs' % k)
            elif not (_close(va, vb, rtol) and _close(ea, eb, rtol)):
                diffs.append('%s: contents differ' % k)
        elif a.ClassName().startswith('TParameter'):
            if not _close(a.GetVal(), b.GetVal(), rtol):
                diffs.append('%s: %r vs %r' % (k, a.GetVal(), b.GetVal()))
        elif isinstance(a, ROOT.TNamed):
            if a.GetTitle() != b.GetTitle():
                diffs.append('%s: title %r vs %r' % (k, a.GetTitle(), b.GetTitle()))
        else:
            diffs.append('%s: unsupported class %s' % (k, a.ClassName()))
    return diffs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--rtol', type=float, default=0.0, help='relative tolerance on floats (0: exact)')
    ap.add_argument('--nano', nargs=2, metavar='ROOT')
    ap.add_argument('--hists', nargs=2, metavar='ROOT')
    args = ap.parse_args()
    diffs = []
    if args.nano:
        diffs += compareNano(*args.nano, rtol=args.rtol)
    if args.hists:
        diffs += compareHists(*args.hists, rtol=args.rtol)
    for d in diffs:
        print(d)
    print('%d differences' % len(diffs))
    sys.exit(1 if diffs else 0)


if __name__ == '__main__':
    main()
