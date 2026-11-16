"""Generator-level breakdown of the dilepton channel acceptance on MiniAOD (prunedGenParticles), in the order of the
ZX_test dilepton selection. Leptons are the bare hard-process final-state electrons and muons (no photon dressing, unlike
the Rivet particle level of the gen channels), so the counts approximate the gen channel flags.

Usage: python3 gen_breakdown.py OUT.json NAME=file.root [NAME=file.root ...] [--maxEvents N]
Per sample: the Z -> ee / mumu / tautau fractions of hard-process Z bosons, then per channel the cumulative,
genWeight-weighted fractions of all events.
"""
import json
import math
import sys

from DataFormats.FWLite import Events, Handle

MZ = 91.1876
CUTS = {'Zmumu': dict(pdg=13, etaMax=2.4, lead=26.0), 'Zee': dict(pdg=11, etaMax=2.5, lead=35.0)}
STEPS = ['Z -> ll of the flavour', '2 leptons |eta|', 'lead/sublead pT', 'opposite charge', 'm_ll window',
         'pT_ll >= 150', 'pT_ll >= 200']


def accepted(p, c):
    a = abs(p.eta())
    gap = c['pdg'] == 11 and 1.4442 < a < 1.566
    return p.pt() > 15.0 and a < c['etaMax'] and not gap


def run(path, maxEvents):
    gp, info = Handle('std::vector<reco::GenParticle>'), Handle('GenEventInfoProduct')
    n, sumw, flav = 0, 0.0, {'ee': 0.0, 'mumu': 0.0, 'tautau': 0.0, 'other': 0.0}
    steps = {ch: [0.0] * len(STEPS) for ch in CUTS}
    for i, ev in enumerate(Events(path)):
        if 0 <= maxEvents <= i:
            break
        ev.getByLabel('prunedGenParticles', gp)
        ev.getByLabel('generator', info)
        w = info.product().weight()
        n += 1
        sumw += w
        parts = gp.product()
        zFlav = set()
        for p in parts:
            if p.pdgId() == 23 and p.isLastCopy():
                ids = sorted(abs(p.daughter(k).pdgId()) for k in range(p.numberOfDaughters()))
                zFlav.add({(11, 11): 'ee', (13, 13): 'mumu', (15, 15): 'tautau'}.get(tuple(ids), 'other'))
        for f in zFlav:
            flav[f] += w
        for ch, c in CUTS.items():
            if ('ee' if c['pdg'] == 11 else 'mumu') not in zFlav:
                continue
            leps = [p for p in parts if abs(p.pdgId()) == c['pdg'] and p.fromHardProcessFinalState()]
            ok = [True]
            acc = sorted((p for p in leps if accepted(p, c)), key=lambda p: -p.pt())
            ok.append(len(acc) >= 2)
            pairs = [(a, b) for k, a in enumerate(acc) for b in acc[k + 1:]]
            pairs = [(a, b) for a, b in pairs if a.pt() >= c['lead']]
            ok.append(ok[-1] and bool(pairs))
            pairs = [(a, b) for a, b in pairs if a.charge() * b.charge() < 0]
            ok.append(ok[-1] and bool(pairs))

            def mass(a, b):
                return (a.p4() + b.p4()).M()
            pairs = [(a, b) for a, b in pairs if MZ - 30 <= mass(a, b) <= MZ + 30]
            ok.append(ok[-1] and bool(pairs))
            best = min(pairs, key=lambda ab: abs(mass(*ab) - MZ)) if pairs else None
            ptll = (best[0].p4() + best[1].p4()).Pt() if best else -1
            ok.append(ok[-1] and ptll >= 150)
            ok.append(ok[-1] and ptll >= 200)
            for k, passed in enumerate(ok):
                steps[ch][k] += w * passed
    return dict(events=n, sumw=sumw,
                zFlavour={k: v / sumw for k, v in flav.items()},
                channels={ch: dict(zip(STEPS, [v / sumw for v in s])) for ch, s in steps.items()})


def main():
    args = sys.argv[1:]
    maxEvents = -1
    if '--maxEvents' in args:
        k = args.index('--maxEvents')
        maxEvents = int(args[k + 1])
        del args[k:k + 2]
    out, pairs = args[0], [a.split('=', 1) for a in args[1:]]
    res = {}
    for name, path in pairs:
        res[name] = run(path, maxEvents)
        print(name, json.dumps(res[name], indent=1))
    with open(out, 'w') as f:
        json.dump(res, f, indent=1)


if __name__ == '__main__':
    main()
