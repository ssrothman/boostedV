"""Example coffea processor for the ZX_test NANO: per channel and level, the boson, the jets passing the channel's
veto, and the unbinned EECs histogrammed (E2C in dR, E1C in theta and phi).

Event weight: genWeight (MC) times metadata['lumiScale'] (xsec * lumi / genEventSumw, see samples.py) if given, else 1.
"""
import awkward as ak
import hist
import numpy as np
from coffea import processor

import eec

LEVELS = {'reco': ('Selection', '', 'Reco', 'RecoJet'), 'gen': ('GenSelection', 'Gen', 'Gen', 'GenJet')}
E2C = ('E2Cn1', 'E2Cn2')
E1C = ('E1CLab', 'E1CHelicity', 'E1CCS')


def axes():
    return dict(
        bosonPt=hist.axis.Regular(60, 0, 1200, name='pt', label='boson $p_T$ [GeV]'),
        jetPt=hist.axis.Regular(60, 200, 1400, name='pt', label='jet $p_T$ [GeV]'),
        dR=hist.axis.Regular(50, -3, 0, name='log10dR', label=r'$\log_{10}\Delta R$'),
        theta=hist.axis.Regular(40, 0, np.pi, name='theta', label=r'$\theta$'),
        logTheta=hist.axis.Regular(40, -3, 0, name='log10theta', label=r'$\log_{10}\theta$'),
        phi=hist.axis.Regular(40, -np.pi, np.pi, name='phi', label=r'$\phi$'))


class ZXProcessor(processor.ProcessorABC):
    def __init__(self, channels=('Zmumu', 'Zee'), levels=('reco', 'gen')):
        self.channels, self.levels = channels, levels

    def process(self, events):
        md = events.metadata
        isMC = md.get('isMC', 'genWeight' in events.fields)
        w = (events.genWeight if isMC else ak.ones_like(events.run, dtype=np.float64)) * md.get('lumiScale', 1.0)
        out = {'sumw': {md['sample']: float(ak.sum(w))}, 'cutflow': {}, 'hists': {}}
        a = axes()
        for level in self.levels:
            if level == 'gen' and not isMC:
                continue
            flags, prefix, coll, jetTable = LEVELS[level]
            jets = events[jetTable]
            for ch in self.channels:
                sel = events[flags][ch]
                key = '%s_%s_%s' % (md['sample'], ch, level)
                ev, wt = events[sel], w[sel]
                good = ~ev[jetTable]['veto' + ch] if 'veto' + ch in jets.fields else ak.ones_like(ev[jetTable].pt, dtype=bool)
                out['cutflow'][key] = {'events': int(ak.sum(sel)), 'jets': int(ak.sum(good))}
                h = out['hists'].setdefault(key, {})
                h['bosonPt'] = hist.Hist(a['bosonPt'], storage='weight').fill(
                    ak.to_numpy(ak.firsts(ev[prefix + ch + 'Boson'].pt)), weight=ak.to_numpy(wt))
                jw = ak.broadcast_arrays(wt, ev[jetTable].pt)[0]
                h['jetPt'] = hist.Hist(a['jetPt'], storage='weight').fill(
                    ak.to_numpy(ak.flatten(ev[jetTable].pt[good])), weight=ak.to_numpy(ak.flatten(jw[good])))
                for obs in E2C + E1C:
                    if coll + obs not in ev.fields:
                        continue
                    nested = eec.entriesByJet(ev, coll, obs)[good]
                    ew = ak.flatten(eec.tupleWeight(nested) * eec.toEntries(jw[good], nested), axis=None)
                    if obs in E2C:
                        hh = hist.Hist(a['dR'], storage='weight')
                        dR = ak.flatten(nested.dR, axis=None)
                        pos = dR > 0  # the i = j entries (dR = 0) are the self-correlation term
                        hh.fill(np.log10(ak.to_numpy(dR[pos])), weight=ak.to_numpy(ew[pos]))
                    else:
                        th = a['logTheta'] if obs == 'E1CLab' else a['theta']
                        theta = ak.to_numpy(ak.flatten(nested.theta, axis=None))
                        hh = hist.Hist(th, a['phi'], storage='weight')
                        hh.fill(np.log10(theta) if obs == 'E1CLab' else theta,
                                ak.to_numpy(ak.flatten(nested.phi, axis=None)), weight=ak.to_numpy(ew))
                    h[obs] = hh
        return out

    def postprocess(self, accumulator):
        return accumulator
