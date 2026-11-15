# Back-to-back jet selection: plan

Status: implemented 2026-11-14 for nominal jets (JOURNAL.md); per-variation selection deferred (last section).

Optional requirement that the event has a leading jet back to back with, and balanced against, the channel's triggering
object; only that jet is written.

## User decisions (2026-11-14)
- Leading jet: highest-pT jet among those passing `jetCuts` and not vetoed for the channel (`veto<ch>`, ΔR <
  `cleaningDR` from the channel's selected objects). Other jets are dropped: not written, no EECs computed.
- Geometry: Δφ(jet, V) > `dPhiMin`.
- Balance: |pT_jet − pT_V| / (pT_jet + pT_V) < `asymmetryMax`.
- Reco jet variations (JES, JER, constituent, cuts): each variation should pick its own leading jet and apply the cuts
  itself, the event written if any (level, channel, variation) passes. Deferred (see the last section).
- Cuts whole events: an event passes a channel only if the channel's own selection and the back-to-back requirement
  both pass.

## Design (approved 2026-11-14)
1. **Config**: per channel, schema-required in every channel spec (reco and gen), e.g.
   ```yaml
   backToBack: {enabled: true, dPhiMin: 2.8, asymmetryMax: 0.3}
   ```
   `enabled: false` gives today's behaviour exactly (no new modules). ZX_test: enabled with these values in its four
   channels. default.yaml: disabled everywhere.
2. **Triggering object V**: the channel's `boson` product: the dilepton for `dilepton`, the leading object for
   `singleObject`. `leptonMET` channels (W, p_z = 0 placeholder) are rejected by config validation when enabled; the W
   selection is to be refined later (TODO.md).
3. **Per (channel, level)** a new `BackToBackSelector` (JetSetup): inputs = channel flag, channel boson, the level's
   nominal jets and their `veto<ch>` flags; outputs = bool and the selected jet (or none).
   Framework-free core (`jetsetup::selectBackToBack`) unit-tested, including Δφ wrap-around and the leading jet being
   the one that fails (no fallback to the second jet).
4. **Jet output**: per jet collection, a filter keeps the union over channels of the selected jets (normally one) →
   `<label>B2B`. Tables, extension tables, veto tables and EEC producers read this collection. New per-jet bool
   column `b2b<ch>` marks which channel selected the jet.
5. **Event tables**: per (channel, level) a bool `B2B<ch>` (gen: `GenB2B<ch>`) for the nominal jets.
6. **Event filter**: `anySelected` becomes OR over (level, channel) of [channel flag AND B2B]. The
   existing channel flags stay as written (pre-b2b), so offline cutflows still work.
7. **Aggregated histograms** (default.yaml path, unused in ZX_test): channel ch fills only if B2B(ch).

## Validation
- Unit tests of the core with mutations (Δφ direction, asymmetry definition, fallback to next jet, veto ignored).
- Config tests: disabled = identical module list to today; enabled wiring reaches the modules.
- End to end (2000 DY + 1000 PTLL-400to600 events): every written jet is the leading non-vetoed jet passing both cuts,
  recomputed in Python from an enabled=false run; disabled run bit-identical to today's output.

## Deferred: per-variation re-evaluation (user decision 2026-11-14)
Neither config has gen-jet variations and ZX_test has no reco-jet variations, so the first implementation uses the
nominal jets of each level only, and validation rejects `backToBack.enabled` together with any `variations` on a
collection of that level. To lift it (needed before enabling back-to-back with default.yaml's 11 reco variations):
- one `BackToBackSelector` per (channel, variant), reading the variant's jets and its `veto<ch>` flags;
- one filtered collection `<label><V>B2B` per variant, feeding that variant's tables and EECs;
- per-event flags `B2B<ch><variant>`, and the event filter ORing over variants;
- aggregators of variant V filling only if B2B(ch, V);
- remove the validation rule, and extend the tests to a variation whose leading jet differs from the nominal one.
