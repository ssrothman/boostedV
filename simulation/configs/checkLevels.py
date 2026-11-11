"""Checks the selection-level modes of eecNano_cfg.py (MC).
Usage: python3 checkLevels.py reco.root gen.root or.root [miniaod.root]
 - each file's events pass at least one channel at its enabled level(s); OR = union of reco-only and gen-only
 - every written event has EEC tables for all jet collections (also events selected at only one level)
 - gen dileptons are in the mass window
 - (with MiniAOD) gen Z->mumu vs an FWLite selection with bare prompt final-state muons (no dressing)
"""
import sys

import numpy as np
import uproot

CHANNELS = ['Zmumu', 'Zee', 'Wmunu', 'Wenu', 'Hadronic', 'GammaJets']
ok = True


def report(name, cond, detail):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + name + ': ' + detail)


def load(path):
    return uproot.open(path)['Events'].arrays(library='np')


def anyFlag(a, table):
    return np.logical_or.reduce([a['%s_%s' % (table, c)] for c in CHANNELS])


files = dict(reco=load(sys.argv[1]), gen=load(sys.argv[2]), OR=load(sys.argv[3]))
ev = {k: set(a['event'].tolist()) for k, a in files.items()}
for mode, tables in (('reco', ['Selection']), ('gen', ['GenSelection']), ('OR', ['Selection', 'GenSelection'])):
    a = files[mode]
    passes = np.logical_or.reduce([anyFlag(a, t) for t in tables])
    report('%s: every written event passes an enabled level' % mode, passes.all() and len(passes) > 0,
           'written %d' % len(passes))
    both = all('%s_%s' % (t, c) in a for t in ('Selection', 'GenSelection') for c in CHANNELS)
    report('%s: flags of both levels stored' % mode, both, '')
    nj = {lvl: np.array([len(x) for x in a[lvl + 'Jet_pt']]) for lvl in ('Reco', 'Gen')}
    tabs = all(np.array_equal(nj[lvl], a['n%s%s' % (lvl, o)]) for lvl in ('Reco', 'Gen') for o in ('E2C', 'E3C', 'E1C'))
    report('%s: EEC tables for every jet in every written event' % mode, tabs,
           'reco jets %d, gen jets %d' % (nj['Reco'].sum(), nj['Gen'].sum()))

a = files['OR']
recoAny, genAny = anyFlag(a, 'Selection'), anyFlag(a, 'GenSelection')
orEv = a['event']
report('OR = reco-only U gen-only', ev['OR'] == ev['reco'] | ev['gen'],
       'reco %d, gen %d, both %d, OR %d' % (len(ev['reco']), len(ev['gen']), len(ev['reco'] & ev['gen']), len(ev['OR'])))
report('OR events with a reco flag = reco-only file', set(orEv[recoAny].tolist()) == ev['reco'], '')
report('OR events with a gen flag = gen-only file', set(orEv[genAny].tolist()) == ev['gen'], '')
for c in ('Zmumu', 'Zee'):
    m = np.concatenate([x for x in a['Gen%sBoson_mass' % c]]) if len(a['Gen%sBoson_mass' % c]) else np.array([])
    report('gen %s boson mass window' % c, len(m) > 0 and np.all((m >= 71) & (m <= 111)),
           'n=%d mean %.2f; reco&gen %d, reco only %d, gen only %d' % (
               len(m), m.mean() if len(m) else 0, (a['Selection_' + c] & a['GenSelection_' + c]).sum(),
               (a['Selection_' + c] & ~a['GenSelection_' + c]).sum(), (~a['Selection_' + c] & a['GenSelection_' + c]).sum()))

if len(sys.argv) > 4:
    import ROOT
    from DataFormats.FWLite import Events, Handle
    h = Handle('std::vector<reco::GenParticle>')
    bare = {}
    for e in Events(sys.argv[4]):
        e.getByLabel('prunedGenParticles', h)
        mus = [p for p in h.product() if abs(p.pdgId()) == 13 and p.status() == 1 and p.isPromptFinalState()
               and p.pt() > 15 and abs(p.eta()) < 2.4]
        best = None
        for i in range(len(mus)):
            for j in range(i + 1, len(mus)):
                x, y = mus[i], mus[j]
                if x.charge() * y.charge() >= 0 or max(x.pt(), y.pt()) < 26 or min(x.pt(), y.pt()) < 15:
                    continue
                mass = (x.p4() + y.p4()).M()
                if 71 <= mass <= 111:
                    best = mass
        bare[e.eventAuxiliary().event()] = best is not None
    genSel = {int(n): bool(f) for n, f in zip(a['event'], a['GenSelection_Zmumu'])}
    nBare = sum(bare.values())
    nOurs = sum(genSel.values())
    agree = sum(1 for n, f in bare.items() if f == genSel.get(n, False))
    # Dressing moves some leptons across the pt and mass cuts, so only near-agreement is expected.
    report('gen Zmumu vs bare prompt muons (FWLite)', abs(nOurs - nBare) <= 0.05 * nBare and agree >= 0.95 * len(bare),
           'dressed %d, bare %d, events agreeing %d / %d' % (nOurs, nBare, agree, len(bare)))
sys.exit(0 if ok else 1)
