"""Analysis configuration (YAML): variables, binning, regions, histograms; see configs/zxtest.yaml.

Top-level keys:
  jetTables   {reco: RecoJet, gen: GenJet} (jet table per level; these are the defaults)
  variables   {name: expression}  derived quantities, usable in later variables, cuts and axes
  binning     {name: binning spec}
  regions     {name: {level, channel, cuts: [...], weights: [...]}}
  histograms  {name: {granularity, axes, cuts, weight, renormalise, regions: [names] (default: all)}}
  anchors     ignored; a place for YAML anchors
"""
import yaml

from .expr import ExprError, compileVariables
from .histograms import HistDef, HistError
from .region import Region, RegionError

KEYS = {'jetTables', 'variables', 'binning', 'regions', 'histograms', 'anchors'}


class ConfigError(ValueError):
    pass


class Config:
    def __init__(self, spec):
        unknown = set(spec) - KEYS
        if unknown:
            raise ConfigError('unknown top-level keys %s' % sorted(unknown))
        try:
            self.jetTables = dict({'reco': 'RecoJet', 'gen': 'GenJet'}, **(spec.get('jetTables') or {}))
            self.variables = compileVariables(spec.get('variables'))
            self.binning = spec.get('binning') or {}
            self.regions = {n: Region(n, r, self.variables, self.jetTables) for n, r in (spec.get('regions') or {}).items()}
            self.histograms = {n: HistDef(n, h, self.binning, self.variables)
                               for n, h in (spec.get('histograms') or {}).items()}
            self.histRegions = {}
            for n, h in (spec.get('histograms') or {}).items():
                regs = h.get('regions', list(self.regions))
                bad = set(regs) - set(self.regions)
                if bad:
                    raise ConfigError('histogram %s: unknown regions %s' % (n, sorted(bad)))
                self.histRegions[n] = regs
        except (ExprError, HistError, RegionError, KeyError) as e:
            raise ConfigError(str(e)) from None
        if not self.regions:
            raise ConfigError('no regions')


def load(path):
    with open(path) as f:
        return Config(yaml.safe_load(f))
