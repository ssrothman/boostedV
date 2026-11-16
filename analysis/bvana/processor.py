"""coffea processor driven by a Config.

Output (accumulates across chunks and files):
  hists[hist][region][sample]   hist.Hist
  cutflow[region][sample][cut]  {'n', 'sumw', 'jets'}  ('channel', then the region's cuts)
  sumw[sample]                  sum of event weights before any selection
Event weight: genWeight (MC) times metadata['lumiScale'] when given; 1 for data.
"""
import awkward as ak
import numpy as np
from coffea import processor


class Processor(processor.ProcessorABC):
    def __init__(self, config):
        self.config = config

    def process(self, events):
        md = events.metadata
        sample = md['sample']
        isMC = md.get('isMC', 'genWeight' in events.fields)
        w = events.genWeight * md.get('lumiScale', 1.0) if isMC else ak.ones_like(events.run, dtype=np.float64)
        out = {'hists': {}, 'cutflow': {}, 'sumw': {sample: float(ak.sum(w))}}
        for rname, region in self.config.regions.items():
            if region.level == 'gen' and not isMC:
                continue
            view, flow = region.select(events, w)
            out['cutflow'][rname] = {sample: flow}
            for hname, hdef in self.config.histograms.items():
                if rname in self.config.histRegions[hname]:
                    try:
                        h = hdef.fill(view)
                    except Exception as e:
                        raise RuntimeError('histogram %s, region %s, sample %s: %s' % (hname, rname, sample, e)) from e
                    out['hists'].setdefault(hname, {}).setdefault(rname, {})[sample] = h
        return out

    def postprocess(self, accumulator):
        return accumulator
