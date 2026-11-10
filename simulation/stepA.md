# Simulation: first step (A)

## A.1 Energy-energy correlators implementation

We need a `c++` library for computation of energy-energy correlators. It should have the following properties:
 - The input types should be the appropriate `fastjet` datatypes. 
 - The output data type should be configurable, with the choice between four options:
     - A pre-binned matrix (e.g., a fixed-length array with floating-point values) representing the EEC histograms. The binning should be controlled by `boost::histogram`, and be configurable at runtime 
     - A zero-suppressed vector of prebinned values (e.g., a variable length vector of `(bin index, weight)` values). When multiple entries fall into the same bin they are merged and their weights summed.
     - A zero-suppressed vector of prebinned values (same as above), with the modification that when multiple entries fall into the same bin they are NOT merged and are instead kept as separate entries.
     - A zero-suppressed vector of *unbinned* values (e.g. a variable-length vector of `(binning coordinate, weight)` pairs). When multiple entries have the same coordinate they are NOT merged and are kept as separate entries. 
 - The implementation of the EEC observables should be highly configurable to enable straightforward implementation of new observables and/or extensions of existing observables. It should be straightforward to define new EEC-style observables. 
 - The EEC calculations should be as fast and optimized as is reasonably achievable.
     - Implementations will be benchmarked and compared to find the best strategy. 
     - When appropriate `c++` templates should be used for compile-time configuration so that the runtime costs of configurability and polymorphism are minimized.
     - When appropriate values will be precomputed and reused.

The baseline EEC implementation must support the following observable definitions:

### A.1.1 projected EECs

The observable is defined as
$$
pENC(\theta) = \sum_{\{p_1 \ldots p_N\} \in jet} \Pi_{i=1}^N \left(\frac{E_{p_i}}{E_{Jet}}\right)^n \delta\left[\theta_{max}(p_1 \ldots p_N) - \theta\right]
$$
where $n$ and $N$ are configurable. The angle $\theta_{max}(p_1 \ldots p_N)$ is defined as the largest of the pairwise angles $\theta_{ij}$. The sum runs over all possible ways to chose $N$ particles from within the jet, ***with replacement***. The delta-function should be implemented with a binning scheme defined by the desired output format (as described above).

The definitions of $E_{p_i}$, $E_{Jet}$, and $\theta_{ij}$ should be straightforward to customize or extend. 

By default we should support the following definitions for $E_{Jet}$:
 - $E_{Jet} = \sum_i E_i$ over all particles in the jet. 
 - $E_{Jet} = $ some value given by the caller on a per-jet basis. 
 - $E_{Jet} = 1 \forall$ jets.

And we should always track which value was used for $E_{Jet}$ so that the weights can be modified later if it needs to be redefined after-the-fact.

By default we should support the following definitions for $E_{p_i}$:
 - The particle energy.
 - The particle transverse momentum.
 - The particle charge.
 - The product of the particle charge and energy.
 - The product of the particle charge and transverse momentum.

By default we should support the following definitions for $\theta_{ij}$:
 - the angle between the three-momenta of particles $i$ and $j$
 - the $\Delta R = \sqrt{(\Delta \phi)^2 + (\Delta \eta)^2}$ between the two particles

We should also support extensions where we bin in arbitrary additional quantities defined as functions of the particle momentum directions. 

### A.1.2 1-point EECs

The observable is defined as
$$
E1C(\theta, \phi) = \sum_{p_i} \left( \frac{E_{p_i}}{E_{Jet}} \right)^n \delta(\theta_i - \theta) \delta (\phi_i - \phi)
$$
where the sum runs over all of the particles in the jet, and $\theta_i$ and $\phi_i$ are the polar and azimuthal angles with respect to a reference frame provided by the caller. As in the projected EECs $n$ should be a configurable parameter. $E_{Jet}$ and $E_{p_i}$ should be configurable just as in the projected EECs (without writing any dubplicate code). The definitions of the angles with respect to the provided reference frame should also be configurable. We will provide a base implementation in which they are simply the polar and azimuthal angles. 

## A.2 Integration into CMSSW & Custom NanoAOD format

In order to process the centrally-produced CMS samples we will need to be able to run our EEC calculation code in the CMSSW framework. This will require three pieces of glue:

1. A producer that translates between the CMSSW jet data formats and the expected input formats for the EEC calculation library
2. A producer that calls the EEC calculation library
3. A producer that takes the EEC calculation library outputs as input and produces NanoAOD FlatTables that can be saved into NanoAOD .root files. 

## A.3 Initial sample processing

The implementation will be validated by running on the centrally-produced leading order (madgraphMLM) inclusive Drell-Yan to dilepton plus jets sample.