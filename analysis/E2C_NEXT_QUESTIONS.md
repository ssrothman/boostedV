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
signal). Status: open.

 - Two important follow-ups:
     1. Can we somehow modify the selections to more efficiently select the recoiling boson? In events where we have selected an ISR jet, where is the boson? 
     2. Do the non-boson jets have identical properties to the jets from DY+jets? If so, it would make sense to classify them as background

## Q5 Resolved E3C stored as projections (2026-11-19)
The ceec tables store the (R_L, xi) and (R_L, phi) projections (20 R_L x 5 bins each, no flow bins), not the full
3D grid (would be ~2000 floats per jet). Status: open; the full grid is available offline from the bindings.

 - Fine for now, may want deeper examination later. 