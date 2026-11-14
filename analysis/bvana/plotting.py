"""Plotting of Processor outputs (hists[hist][region][sample]) with mplhep, CMS Simulation Work in progress style.

reduce() slices and projects by axis name; plot1d() overlays or stacks 1D histograms with an optional ratio panel;
plot2d() draws one 2D histogram. Normalisations: 'none', 'area' (unit integral over the visible bins);
bin-width division: 'none', 'linear' (per unit x) or 'log' (per unit ln x, e.g. dSigma/dln(dR)).
"""
import hist
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import mplhep as hep  # noqa: E402
import numpy as np  # noqa: E402

LABEL = 'Work in progress'


def parseSlice(text):
    """'axis=lo:hi' (either bound may be empty) -> (axis, lo, hi)."""
    name, rng = text.split('=', 1)
    lo, hi = rng.split(':', 1)
    return name, (float(lo) if lo else None), (float(hi) if hi else None)


def reduce(h, slices=(), project=None):
    """Sum over [lo, hi) of each sliced axis (bin edges must match), then keep only the `project` axes (in order)."""
    idx = {}
    for name, lo, hi in slices:
        ax = h.axes[name]
        for v in (lo, hi):
            if v is not None and not np.any(np.isclose(ax.edges, v)):
                raise ValueError('slice %s: %g is not a bin edge of %s' % (name, v, list(ax.edges)))
        idx[name] = slice(hist.loc(lo) if lo is not None else None, hist.loc(hi) if hi is not None else None, sum)
    if idx:
        h = h[idx]
    if project:
        h = h.project(*project)
    return h


def values(h, norm='none', width='none'):
    """(values, errors) of a 1D histogram after the requested normalisation and bin-width division."""
    v, var = h.values(), h.variances()
    e = np.sqrt(var) if var is not None else np.sqrt(np.abs(v))
    if norm == 'area':
        tot = v.sum()
        if tot:
            v, e = v / tot, e / tot
    elif norm != 'none':
        raise ValueError('norm must be none or area')
    edges = h.axes[0].edges
    if width == 'linear':
        d = np.diff(edges)
    elif width == 'log':
        d = np.diff(np.log(edges))
    elif width == 'none':
        d = np.ones(len(edges) - 1)
    else:
        raise ValueError('width must be none, linear or log')
    return v / d, e / d


def label(ax, lumi=None, fontsize=None):
    hep.cms.label(LABEL, data=False, lumi=lumi, com=13.6, ax=ax, fontsize=fontsize)


def plot1d(hists, norm='none', width='none', stack=False, ratio=None, logx=False, logy=False, xlabel=None,
           ylabel=None, lumi=None):
    """hists: {legend: 1D Hist}, all with the same binning; ratio: legend of the denominator, or None."""
    hep.style.use('CMS')
    if ratio is not None:
        fig, (ax, rax) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.05})
    else:
        fig, ax = plt.subplots()
        rax = None
    names = list(hists)
    first = hists[names[0]]
    edges = first.axes[0].edges
    vals = {n: values(hists[n], norm, width) for n in names}
    if stack:
        hep.histplot([vals[n][0] for n in names], edges, yerr=None, stack=True, histtype='fill', label=names, ax=ax)
    else:
        for n in names:
            hep.histplot(vals[n][0], edges, yerr=vals[n][1], label=n, ax=ax)
    if rax is not None:
        den = vals[ratio][0]
        for n in names:
            if n == ratio:
                continue
            with np.errstate(divide='ignore', invalid='ignore'):
                hep.histplot(vals[n][0] / den, edges, yerr=vals[n][1] / np.abs(den), ax=rax, label=n)
        rax.axhline(1, color='gray', lw=1)
        rax.set_ylabel('ratio to %s' % ratio)
        rax.set_xlabel(xlabel or first.axes[0].label)
    else:
        ax.set_xlabel(xlabel or first.axes[0].label)
    ax.set_ylabel(ylabel or defaultYLabel(norm, width))
    for a in (ax, rax):
        if a is not None and logx:
            a.set_xscale('log')
    if logy:
        ax.set_yscale('log')
    ax.legend()
    label(ax, lumi)
    return fig


def plot2d(h, norm='none', logz=False, lumi=None):
    hep.style.use('CMS')
    fig, ax = plt.subplots()
    v = h.values()
    if norm == 'area' and v.sum():
        v = v / v.sum()
    x, y = h.axes[0].edges, h.axes[1].edges
    mesh = ax.pcolormesh(x, y, v.T, norm=matplotlib.colors.LogNorm() if logz else None)
    fig.colorbar(mesh, ax=ax)
    ax.set_xlabel(h.axes[0].label)
    ax.set_ylabel(h.axes[1].label)
    if x[0] > 0 and np.allclose(np.diff(np.log(x)), np.diff(np.log(x))[0]) and not np.allclose(np.diff(x), np.diff(x)[0]):
        ax.set_xscale('log')
    label(ax, lumi, fontsize=16)
    return fig


def defaultYLabel(norm, width):
    base = 'fraction' if norm == 'area' else 'weighted entries'
    return base + {'none': '', 'linear': ' / bin width', 'log': r' / $\Delta\ln x$'}[width]
