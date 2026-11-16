**Table 3 (Section 4)**: It would make more sense if we set it up so that <c>Sel is the dilepton selection, <c>B2B is the back-to-back requirement, and <c> is all of <c>Sel and <c>Trigger and <c>B2B and goodVertex and metFilters (i.e. the B2B should be included in the AND, and named consistently with everything else). This will also require a bit of re-plumbing of the analysis python code (Section 12)

**Section 5.2**: 
 - we should double-check that the `goodVertex` requirement aligns with the central `goodVertex` requirement (check against the configuration of the central NANO?)
 - we should double-check that the MET filter list aligns with the central list (needs SSO access to the JME wiki)

**Section 5.3**:
 - we should check with the muon POG the various details here (c.f. the check-with-pog list elsewhere in the repo). In particular I wonder if the high-pT momentum corrections should threshold on the tuneP momentum or the original momentum. 
 - We will want to study in detail the impact of the various corrections (and the associated systematics)

 **Section 5.4**:
  - We will need to implement the EGM POG recommendations for electrons, but can defer that for now. 

 **Section 5.5**:
  - We probably will want to study in detail the impact of dressing (and the associated systematics). But we can defer for now.

  **Section 6**:
 - We should check with the POG whether it is recommended to drop gen electrons in the barrel/endcap gap

 **Section 7**:
 - Again we need to check this against central POG recommendations.
 - We should list exactly which JEC levels we apply
 - Is there a central JEC producer, or did we need a custom one for our setup? We should probably prefer a central implementation if available (and validated)
 - The jet selection should use the tight+lepton veto ID requirement, not just the tight requirement. 
 - Do the GenJets contain the gen-level flavor information? If not, they should. We should also probably attempt to associate the GenJets with the generated bosons when appropriate. 
 - We should check how other analyses have handled the back-to-back requirement (what paremeters? do we allow fallback to softer jets?)

 **Section 8**:
  - We should also implement a projective lab frame for the E1C where $\theta$ is the delta-R w.r.t. the jet axis, and $\phi$ is the angle in the ($\eta, \phi$) plane formed by the line between the particle and the jet axis, with $\phi=0$ aligned with whichever beam proton is closer to the jet. 
  - In the `jetAxis` frame, we should chose the beam closest to the jet
  - Same for the `jetHelicity` frame
  - Similar for the `CS` frame, which I didn't understand you description of, but I think may already be correct.
  - We may want to experiment with other jet axis definitions for the E1C... 

  **Section 9**:
  - M2: clarification question: should we use the momentum direction from the tuneP track? Is it clear from the muon POG wiki? Or should we ask? (Or do we even have access to the tuneP direction?)
  - J3: We should perform JER smearing ***BEFORE*** selections. 


 **Table 7**:
  - It would be nice to have a more detailed breakdown of the cutflow than just `channel flag`. Why is the efficiecy so low for ZZ, and do we expect it? Is it just the low-pT events, and the other-lepton-flavor events?
  - I'm surprised the $\geq 1$ jet requirement has such poor efficiency. Surely all events with boson $p_T$ at least 150 GeV are recoiling against a hard jet? What is the explanation for this? 

  **Table 8**:
  - We should not have the delta R(jet, Z) requirement. And the jet $p_T$ requirement should agree with the boson pT requirement. 

  **Cross-sections**:

The total cross-sections for each channel are as follows. Please incorporate these:
 - DY Jets -> LL (M_ll > 50 GeV): cross-section is 6077.22 pb, as evaluated by FEWZ 3.1, including NNLO QCD terms and NLO EW terms. 
 - The total ZZ (without any decay mode selections) cross-section is 16.523 pb
 - The total WZ (without any decay mode selections) cross-section is 47.13 pb
 - The total WW (without any decay mode selections) cross-section is 118.7 pb
 - The total $t\bar{t} \to 2\ell 2\nu$ cross-section is 88.51