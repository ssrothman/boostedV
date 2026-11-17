# Plan: faster histogram filling (shared per-region computation)

Status: approved 2026-11-17. Stage 1 done: per-chunk processing 7.32 s → 4.72 s on the profiled file; outputs
bit-identical to the previous code (98 histograms and all cutflows, `zxtest.yaml` and `zxtest_boosted.yaml`). Of the
remaining 4.7 s: zlib decompression ≈1.7 s, `hist.fill` ≈1.5 s, awkward work ≈1 s, so stage 2 can save at most about
1 s per chunk. Stage 2 not started.

## Contents
- Evidence
- Where the repeated work is
- Proposed change (two stages)
- Validation
- Risks and open questions

## Evidence
Profile of one chunk (one DY PTLL-200to400 file, 33,116 events, `configs/zxtest_boosted.yaml`, single process;
script: scratchpad `prof/prof.py`):
- processing 7.3 s, the same for a remote EOS file and a local copy, so input reading is not the bottleneck;
- reading and decompressing the 62 branches used: 1.45 s (about 20%);
- the 16 E2C histograms: about 5.9 s, i.e. 0.30–0.37 s each, apart from the first two, which include the reads;
- by function (cProfile): awkward indexing, masking and broadcasting about 3–4 s, `hist.fill` 1.6 s, zlib 1.7 s.

## Where the repeated work is
`HistDef.fill` (`bvana/histograms.py`) works from scratch for every histogram:
1. `view.namespace(obs)` rebuilds `jets = ev[jetTable][jetIdx]`, which is a jagged gather, on every call;
2. it broadcasts the event weight to the entry level and multiplies it by `weight * symfactor`;
3. it evaluates and broadcasts every cut (e.g. `eec.dR > 0`, shared by 12 of the 16 E2C histograms);
4. for each axis it evaluates the expression (`eec.dR` and `jets.pt` appear in most of them), broadcasts it to the
   entry level, applies the mask, flattens it and converts it to numpy.
Of these, only the axis values that differ (e.g. `abs(jets.eta)`, `jets.msoftdrop`) and `hist.fill` itself are
specific to each histogram.

## Proposed change (two stages; measure after each)
**Stage 1: cache per view (small, low risk).**
- `View.namespace(obs)` is built once per (view, observable) and reused.
- Expression results are memoised per namespace, keyed by expression text (variables included).
- Entry-level event weights (event weight × weight × symfactor, before any renormalisation) are cached per observable,
  and cut masks are cached keyed by the tuple of cut texts.
- The fill logic, the expression semantics and the outputs are unchanged.

**Stage 2: flat numpy gathers instead of jagged broadcasts (only if stage 1 is not enough).**
- Once per (view, observable), compute flat index arrays: entry → event row and entry → kept-jet row.
- Event- and jet-level quantities are then turned into per-entry numpy arrays with one integer gather each, instead
  of `ak.broadcast_arrays` + mask + `ak.flatten`. Cuts become numpy boolean masks.
- Missing values (`None`, e.g. `max()` over no jets) still become NaN before the gather, so they still go to overflow.

The cache lives on the `View`, so it is freed when the region's chunk is done; nothing is shared across chunks.

## Validation
- Equivalence: for one DY file, run `configs/zxtest.yaml` (all reco and gen regions, E1C included) and
  `configs/zxtest_boosted.yaml` with the current commit and with the change. Every histogram's values and variances
  must agree (exactly for stage 1, to float rounding for stage 2), and so must the cutflows.
- Unit tests: the existing suite, plus a test that the same expression requested by two histograms is evaluated
  once and that the outputs match the uncached path (it must fail if the cache returns a stale or wrong-shape array).
- Speed: rerun `prof.py` and report the per-chunk time and the per-histogram fills.

## Risks and open questions
- Memory: the cached flat per-entry arrays add roughly (number of entries × 8 bytes) per cached column per chunk.
  With 200k-event chunks this may be several hundred MB per worker; if it is too much, lower `--chunksize`.
- Memoising by expression text assumes expressions have no side effects and that the namespace is not modified
  between histograms. Both hold in the current code.
- Out of scope here: the HTCondor scale-out (a separate plan), and why the 4 local workers sit at about 60% CPU
  (not explained by input reading; not yet measured).
