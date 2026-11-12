# JRV2 JER SF uncertainty: the reference combination does not reproduce JRV1 (to report to JME)

## Summary
- `Run3-22EFGSep23-Summer22EE-NanoAODv12/2026-06-05` (= `latest` on 2026-11-12) splits the JER scale factor into
  `Summer22EE_22Sep2023_JRV2_MC_ScaleFactor_AK8PFPuppi` (nominal) and `..._JRV2_MC_SFUncertainty_AK8PFPuppi`.
- JRDatabase PR #30 describes JRV2 as the JRV1 file split into SF and SFUncertainty, and the nominal values are identical.
- The reference implementation (cms-cat nanoAOD-tools-modules PR #32, `jetCorr.py`) uses `SF_up/down = SF * (1 ± unc)`.
- The stored `unc` instead matches the JRV1 **absolute** shift `up − nom`. So `SF * (1 ± unc)` gives variations SF times
  larger than JRV1's (SF is 1.02–1.26 for |η| < 2.4 and 1.19–1.87 for 2.4 < |η| < 4.7).
- We follow the reference, `SF * (1 ± unc)` (`JetSetup/plugins/EECJetVariationProducer.cc`), pending JME's answer.

## Evidence (AK8PFPuppi, 2025-07-15 JRV1 vs 2026-06-05 JRV2)
On a 50 η × 40 pT grid (pT 50–3000 GeV, log-spaced), maximum absolute differences:

| quantity | \|η\| < 2.4 | 2.4 < \|η\| < 4.7 |
|---|---|---|
| SF(JRV2) − nom(JRV1) | 0 | 0 |
| (up − nom)(JRV1) − unc | 0.0046 | 0.022 |
| (nom − down)(JRV1) − unc | 0.0046 | 0.022 |
| (up − nom)(JRV1) − SF·unc | 0.012 | 0.14 |
| (up − nom)/nom (JRV1) − unc | 0.010 | 0.076 |

The residual for `up − nom` is consistent with `unc` being a smooth fit in pT to binned JRV1 values. Example at η = 0.3,
pT = 450: JRV1 nom/up/down = 1.0830/1.0930/1.0730, JRV2 unc = 0.0100, SF·(1+unc) = 1.0938, SF+unc = 1.0930.

## Reproduce (inside cmsenv)
```python
import correctionlib, numpy as np
D = '/cvmfs/cms-griddata.cern.ch/cat/metadata/JME/Run3-22EFGSep23-Summer22EE-NanoAODv12/'
old = correctionlib.CorrectionSet.from_file(D + '2025-07-15/fatJet_jerc.json.gz')
new = correctionlib.CorrectionSet.from_file(D + '2026-06-05/fatJet_jerc.json.gz')
o = old['Summer22EE_22Sep2023_JRV1_MC_ScaleFactor_AK8PFPuppi']
sf = new['Summer22EE_22Sep2023_JRV2_MC_ScaleFactor_AK8PFPuppi']
u = new['Summer22EE_22Sep2023_JRV2_MC_SFUncertainty_AK8PFPuppi']
for eta, pt in [(0.3, 450.), (2.0, 300.), (3.5, 200.)]:
    nom, up = o.evaluate(eta, pt, 'nom'), o.evaluate(eta, pt, 'up')
    s, x = sf.evaluate(eta, pt), u.evaluate(eta, pt)
    print(eta, pt, 'JRV1 up-nom', up - nom, 'unc', x, 'SF*unc', s * x)
```

## References
- JRDatabase PR #30 (the JRV1 → JRV2 split): https://github.com/cms-jet/JRDatabase/pull/30
- cms-cat nanoAOD-tools-modules PR #32 (`SF * (1 ± unc)`): https://github.com/cms-cat/nanoAOD-tools-modules/pull/32
- JME correction MR (CERN login): https://gitlab.cern.ch/cms-analysis-corrections/JME/Run3-22EFGSep23-Summer22EE-NanoAODv12/-/merge_requests/4
- CMS Talk announcement (CERN login): https://cms-talk.web.cern.ch/t/new-jer-smearing-inputs-available-for-2024-and-2025/145723
