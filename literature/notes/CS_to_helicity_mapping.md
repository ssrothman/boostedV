# Collins-Soper to helicity frame mapping

## Overview

This note documents the mapping between Collins-Soper (CS) frame angular coefficients A_0–A_7 and helicity-frame spin density matrix elements ρ_λλ′ (or helicity fractions f_0, f_L, f_R).

## Exact mapping for W bosons (1203.2165)

The exact conversion formulas were derived by ATLAS in **1203.2165** (Eq. 4-5, Sec. 2.2):

| Quantity | Formula | Notes |
|----------|---------|-------|
| f_0 (longitudinal) | f_0 = (1/2)A_0 | Direct proportionality |
| f_L (left-handed) | f_L = (1/4)(2 − A_0 ∓ A_4) | Upper sign for W⁺, lower for W⁻ |
| f_R (right-handed) | f_R = (1/4)(2 − A_0 ± A_4) | Upper sign for W⁺, lower for W⁻ |
| f_L − f_R | f_L − f_R = ∓A_4/2 | Same sign convention as above |

**Sign convention:** The upper sign (∓) applies to W⁺, the lower sign (∓) to W⁻.

## Derivation from helicity cross sections

The mapping is derived from the relationship between angular coefficients and helicity cross sections in **Mirkes & Ohnemus (1994), hep-ph/9406381**:

### Angular distribution (CS frame)
```
(3/16π) dσ^{U+L}/dp_T² dy [(1+cos²θ) + ½A_0(1−3cos²θ) + A_1 sin2θ cosφ + ½A_2 sin²θ cos2φ
                            + A_3 sinθ cosφ + A_4 cosθ + A_5 sin²θ sin2φ + A_6 sin2θ sinφ + A_7 sinθ sinφ]
```

### Helicity cross sections
- σ^{U+L} ∼ H_00 + H_{++} + H_{--}
- σ^L ∼ H_00
- σ^T ∼ ½(H_{+-} + H_{-+})
- σ^P ∼ H_{++} − H_{--}
- σ^A ∼ ¼(H_{+0} + H_{0+} − H_{-0} − H_{0-})
- σ^I ∼ ¼(H_{+0} + H_{0+} + H_{-0} + H_{0-})
- σ^7, σ^8, σ^9 ∼ related to off-diagonal elements (not standard notation)

### Coefficient definitions (Eq. 26, Mirkes & Ohnemus)
- A_0 = 2σ^L / σ^{U+L}
- A_2 = 4σ^T / σ^{U+L}
- A_4 = 2σ^P / σ^{U+L}
- A_3 = 4√2 σ^A / σ^{U+L}
- A_1 = 2√2 σ^I / σ^{U+L}
- A_5 = 2σ^7 / σ^{U+L}
- A_6 = 2√2 σ^8 / σ^{U+L}
- A_7 = 4√2 σ^9 / σ^{U+L}

### Relation to helicity fractions
The helicity fractions are defined as normalised helicity cross sections:
- f_0 = σ^L / σ^{U+L}
- f_L = σ^L_L / σ^{U+L} (left-handed)
- f_R = σ^L_R / σ^{U+L} (right-handed)

With σ^{U+L} = σ^L + σ^T + σ^P/2 and the decomposition of transverse cross sections into left/right components, the exact mapping follows.

## Off-diagonal elements mapping

The off-diagonal elements of the spin density matrix are related to the angular coefficients A_1, A_3, A_5, A_6, A_7.

### Parity decomposition (2610.38688 App. D)

The angular coefficients split into parity-even and parity-odd combinations:
- **Parity-even:** A_0, A_2, A_4 (proportional to longitudinal and parity-conserving transverse)
- **Parity-odd:** A_1, A_3, A_5, A_6, A_7 (related to interference and CP-violating terms)

The energy-flow and charge-flux one-point traces (EEC) probe ρ in terms of these parities:

| EEC observable | Probes in ρ basis |
|---------------|-------------------|
| Energy flow (parity-even) | ρ_00 (longitudinal fraction) |
| cos 2Φ, sin 2Φ (parity-even) | ρ_+- + ρ_-+ (alignment) |
| cos Φ, sin Φ (parity-odd) | ρ_+0 − ρ_0- (interference) |

### Mapping summary

| Angular coefficient | Related ρ element | Parity | Notes |
|---------------------|-------------------|--------|-------|
| A_0 | ρ_00 = f_0 | even | Diagonal, longitudinal |
| A_1, A_3 | ρ_+- combinations | even | Off-diagonal (Δλ=±2) |
| A_4 | f_L − f_R | even | Diagonal difference |
| A_5, A_7 | ρ_+- combinations | odd | Off-diagonal (Δλ=±2) |
| A_6 | ρ_+0 − ρ_0- | odd | Off-diagonal interference |

**Note:** The exact proportionality constants between A_i and ρ_λλ′ for i=1,3,5,6,7 depend on the frame convention and are typically quoted as "proportional to" in experimental papers. The literature consistently states A_0 ∝ f_0 and A_4 ∝ ∓(f_L − f_R) but the off-diagonal relations are not as commonly tabulated.

## Inverse mapping

Given helicity fractions f_0, f_L, f_R:

| Quantity | Formula |
|----------|---------|
| A_0 | A_0 = 2f_0 |
| A_4 | A_4 = ∓2(f_L − f_R) |

Given spin density matrix elements ρ_λλ′ (unnormalised helicity cross sections H_λλ′):

| Quantity | Formula |
|----------|---------|
| H_00 | H_00 = f_0 H_{U+L} |
| H_{++} − H_{--} | = ½(f_L − f_R) H_{U+L} |
| H_{++} + H_{--} | = ½(1 − f_0) H_{U+L} − H_00 |

## Z boson mapping

For Z bosons, the same relationship holds between A_0 and f_0:
- A_0 = 2f_0 = 2ρ_00

The full mapping for Z involves all eight coefficients. The key differences from W bosons are:
- Different electroweak couplings for left/right-handed fermions (g_V, g_A)
- A_1, A_3, A_5, A_6, A_7 are predicted to be non-zero at NLO and NNLO

## Summary of literature coverage

| Paper | Frame | Map provided | Equation |
|-------|-------|--------------|----------|
| 1203.2165 | CS → helicity | Exact for W diagonal | Eqs. 4–5 |
| 1606.00689 | CS → H_mm′ | Unnormalised hadronic tensor | App. A, Eq. 16 |
| 2008.04174 | CS → helicity | Proportionalities only | Eq. 3 |
| 1104.3829 | helicity → CS | Proportionalities only | Sec. 2 |
| 2610.38688 | helicity → energy flow | ρ → EEC structure functions | Eqs. 9–10, 82 |
| 2409.16731 | tensor basis → joint ρ | α, γ → f_λλ′ | Eqs. 11, 16 |
| hep-ph/9406381 | CS → H_mm′ | Full helicity cross sections | Eq. 26 |

## Open issues

1. The exact mapping between A_5–A_7 and off-diagonal ρ elements (ρ_+−, ρ_+0, ρ_−0) is not explicitly stated in 1203.2165; the literature consistently states proportionalities without constants.
2. The Z boson mapping requires additional treatment due to the different SU(2)×U(1) couplings for left/right-handed fermions.
3. The relation between A_1, A_3 (parity-even) and A_5, A_6, A_7 (parity-odd) and their specific combinations of ρ elements needs further documentation.

## References

1. ATLAS, Eur. Phys. J. C (2012) arXiv:1203.2165
2. Mirkes & Ohnemus, Phys. Rev. D 50 (1994) 5692, arXiv:hep-ph/9406381
3. ATLAS, JHEP 10 (2016) 052, arXiv:1606.00689
4. CMS, JHEP 02 (2021) 067, arXiv:2008.04174
5. Gao, Lee & Zhang, arXiv:2610.38688 (2026)
6. Grossi, Pelliccioli & Vicini, arXiv:2409.16731 (2024)
