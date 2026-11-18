"""Jet (eta, phi) occupancy before and after the jet veto map, for the JME documentation requirement.

    python3 jetVetoMapOccupancy.py nano1.root [nano2.root ...] -o outdir
Input: ZX_test production NANOs (local copies, e.g. made with xrdcp). Events: those passing a gen channel
(GenSelection_Zmumu or _Zee), which does not depend on the reco veto map; "after": those also passing
Selection_jetVetoMap. Jets: AK4Jet (pt > 20 GeV as stored) and RecoJet (the selected AK8 jets). Unweighted counts.
Output: outdir/vetoMapOccupancy.pdf (per collection: before, after, and the fraction removed) and vetoMap.md.
"""
import argparse
import os

import awkward as ak
import matplotlib
import numpy as np
import uproot

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

COLLECTIONS = {'AK4Jet': 'AK4 PUPPI jets ($p_T > 20$ GeV)', 'RecoJet': 'selected AK8 jets'}
ETA = np.linspace(-4.7, 4.7, 95)
PHI = np.linspace(-np.pi, np.pi, 73)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('-o', '--outdir', required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    files = a.files
    H = {c: {k: np.zeros((len(ETA) - 1, len(PHI) - 1)) for k in ('before', 'after')} for c in COLLECTIONS}
    nEv = {'before': 0, 'after': 0}
    branches = ['GenSelection_Zmumu', 'GenSelection_Zee', 'Selection_jetVetoMap'] + \
        [c + '_' + v for c in COLLECTIONS for v in ('eta', 'phi')]
    for f in files:
        for ev in uproot.iterate(f + ':Events', branches, step_size='200 MB'):
            gen = ev.GenSelection_Zmumu | ev.GenSelection_Zee
            for k, m in (('before', gen), ('after', gen & ev.Selection_jetVetoMap)):
                nEv[k] += int(ak.sum(m))
                for c in COLLECTIONS:
                    h, _, _ = np.histogram2d(ak.to_numpy(ak.flatten(ev[c + '_eta'][m])),
                                             ak.to_numpy(ak.flatten(ev[c + '_phi'][m])), bins=(ETA, PHI))
                    H[c][k] += h
    fig, axs = plt.subplots(len(COLLECTIONS), 3, figsize=(21, 6 * len(COLLECTIONS)), squeeze=False)
    lines = ['# Jet veto map: occupancy before and after', '', '%d files; events passing a gen channel: %d, of which %d '
             'pass Selection_jetVetoMap (%.2f%% removed).' % (len(files), nEv['before'], nEv['after'],
                                                             100 * (1 - nEv['after'] / max(nEv['before'], 1))), '']
    for r, (c, title) in enumerate(COLLECTIONS.items()):
        b, af = H[c]['before'], H[c]['after']
        lines.append('- %s: %d jets before, %d after (%.2f%% removed)' % (c, b.sum(), af.sum(),
                                                                          100 * (1 - af.sum() / max(b.sum(), 1))))
        frac = np.divide(b - af, b, out=np.full_like(b, np.nan), where=b > 0)
        for col, (img, lab, kw) in enumerate(((b, 'before', {}), (af, 'after', {}),
                                              (frac, 'fraction removed', dict(vmin=0, vmax=1)))):
            ax = axs[r, col]
            m = ax.pcolormesh(ETA, PHI, img.T, shading='flat', edgecolors='face', rasterized=True, **kw)
            fig.colorbar(m, ax=ax, label='jets' if col < 2 else 'fraction')
            ax.set_xlabel(r'$\eta$')
            ax.set_ylabel(r'$\phi$')
            ax.set_title('%s, %s' % (title, lab))
    fig.tight_layout()
    fig.savefig(os.path.join(a.outdir, 'vetoMapOccupancy.pdf'))
    open(os.path.join(a.outdir, 'vetoMap.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
