# Questions arising while working on E2C_NEXT_PLAN.md

Newest at the end. Each entry: the question, what was done meanwhile (the workaround), status.

## Q1 Resolved E3C at R_S = 0 (2026-11-19)
arXiv:2201.07800 Eq. (3) defines xi = R_S/R_M and phi = arcsin sqrt(1 - (R_L - R_M)^2/R_S^2) but not R_S = 0 (two
coincident particles, e.g. the repeated index of a multiset, or exactly collinear particles).
Meanwhile: such triples get (xi, phi) = (0, 0), i.e. the first shape bin (`eec::triangleShape`, NANO.md 4.6).
Status: open; alternatives are dropping them or a separate bin.

 - If we can, I'd like to track these separately. Somehow define a bin that only gets populated by xi=0? 

Done (2026-11-20): R_S = 0 gives (xi, phi) = (-1, -1), the shape axes' underflow; the ceec shape rows keep it as their
first shape column. Status: resolved (SENSITIVITY_JOURNAL.md, 2026-11-20).

## Q2 AK8 constituents outside the all-particle collection (2026-11-19)
Vertex and PUPPI filters on AK8 constituents take fromPV/dz/dxy/puppiWeightRaw from the all-particle collection by
srcIdx; 0.9% of the constituents (|eta| > 2.4, outside that collection) have none.
Meanwhile: they fail every such filter (`bvana/ceec.py`). Status: open (small effect).

- I think thats perfectly fine (at least for now)

## Q3 Correction: the existing NANOs have no truth axis (2026-11-19)
I told you `axisTruth` was in the existing NANOs; it is not (20261116_zxb2b predates it). Meanwhile the same rules run
offline on GenPart (`bvana/truth.py`), identical to `axisTruth` on 8329 jets. Status: resolved, for information.

 - Cool

## Q4 VV signal jets that are not the boson (2026-11-19)
At the sensitivity baseline only 54% of the VV jets (WZ ~45%, ZZ ~76%) are the hadronic boson; most others are a
hard-process parton (the WZ/ZZ system recoiling against an ISR jet). ZH: 87%. Should the signal template be split
(boson-matched vs not), or the non-boson jets treated as background-like? Meanwhile: unchanged (all VV jets are
signal).

 - Two important follow-ups:
     1. Can we somehow modify the selections to more efficiently select the recoiling boson? In events where we have selected an ISR jet, where is the boson? 
     2. Do the non-boson jets have identical properties to the jets from DY+jets? If so, it would make sense to classify them as background

Follow-ups done (2026-11-20, SENSITIVITY_JOURNAL.md "VV jets that are not the boson"): (1) in those events the V is
soft (median pT ~70-80 GeV), resolved and on the Z side; ~4% (WZ) / 1% (ZZ) would be a boosted candidate, so the
selection can reject but not recover them (n AK4 = 0 raises the boson fraction to 0.83). (2) Closer to DY than to the
boson jets but not identical (E2C chi2/ndf 3.5-7 vs DY, not explained by the q/g mix). Z_shape at gpV 1% DY eff:
13.97 (all signal) vs 13.86 (non-boson as background). Decision (user, 2026-11-20): the non-boson VV jets are background (`sensitivity.py` group `VVother`, truthStatus != 0),
and future productions veto extra AK4 jets (`backToBack.extraJetAlphaMax: 0` in ZX_test/ZX_jetfree). Status: resolved.

## Q5 Resolved E3C stored as projections (2026-11-19)
The ceec tables store the (R_L, xi) and (R_L, phi) projections (20 R_L x 5 bins each, no flow bins), not the full
3D grid (would be ~2000 floats per jet). Status: open; the full grid is available offline from the bindings.

 - Fine for now, may want deeper examination later. 

## Q6 Extra-jet veto thresholds; ZH non-boson jets (2026-11-20)
(a) The production veto now on (alpha 0) uses the existing `selection.<level>.extraJets` cuts: AK4 pt > 20, |eta| < 2.4,
farther than 1.2 from the selected jet and 0.4 from the leptons. The n AK4 = 0 numbers of Q4 used the table cuts
(pt > 30, |eta| < 2.5, dR > 0.8), so the production veto is stricter than what was studied. Keep 20/2.4/1.2, or use
30/2.5/0.8? Meanwhile: unchanged (20/2.4/1.2). (b) Only VV is split; the 13% of ZH jets that are not the boson stay
ZH signal. Split ZH the same way? Meanwhile: no.
Answers (user, 2026-11-20): (a) keep 20/2.4/1.2; (b) yes: ZH jets with truthStatus != 0 are background (`ZHother`).
Status: resolved.
