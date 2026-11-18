"""Boost of lab-frame one-point correlator entries into the rest frame of a jet axis.

Input: an unbinned E1C with weight Pt, n = 1 and frame jetAxis about the axis (theta' = 3D angle to the axis, phi the
azimuth about it with x toward the beam on the axis side), so each entry's transverse momentum is weight * E_jet.
Every particle is given the mass `particleMass` (default m_pi+-, as PF charged hadrons), at reco and gen level alike.
The boost is along the axis with the axis momentum and the boson-mass hypothesis M; phi is unchanged by it.
"""
import awkward as ak
import numpy as np

M_PION = 0.13957039  # GeV, PDG


def axisKinematics(pt, eta, phi):
    """Unit vector of the axis and the frame x axis (beam on the axis side, orthogonalised), as (3, n) arrays."""
    a = np.stack([np.cos(phi) / np.cosh(eta), np.sin(phi) / np.cosh(eta), np.tanh(eta)])
    beam = np.stack([np.zeros_like(eta), np.zeros_like(eta), np.where(eta < 0, -1.0, 1.0)])
    x = beam - np.sum(beam * a, axis=0) * a
    x /= np.linalg.norm(x, axis=0)
    return a, x


def restFrame(theta, phi, pt, axisPt, axisEta, axisPhi, M, particleMass=M_PION):
    """Flat numpy arrays (one value per entry; axis quantities broadcast per entry) -> dict of
    thetaRest, phiRest, cosThetaRest and ERest (= E*/M). theta, phi: lab angles about the axis; pt: particle pt."""
    a, x = axisKinematics(axisPt, axisEta, axisPhi)
    y = np.cross(a, x, axis=0)
    st, ct = np.sin(theta), np.cos(theta)
    n = st * np.cos(phi) * x + st * np.sin(phi) * y + ct * a
    p = pt / np.hypot(n[0], n[1])
    m2 = particleMass ** 2
    E = np.sqrt(p * p + m2)
    P = axisPt * np.cosh(axisEta)
    Ea = np.sqrt(P * P + M * M)
    gamma, beta = Ea / M, P / Ea
    oneMinusBeta = M * M / (Ea * (Ea + P))
    # gamma * (p_par - beta E), with E - p_par = m^2/(E+p) + 2p sin^2(theta/2) to avoid the cancellation at beta -> 1.
    pParRest = gamma * (oneMinusBeta * E - m2 / (E + p) - 2 * p * np.sin(theta / 2) ** 2)
    ERest = gamma * (E - beta * p * ct)
    thetaRest = np.arctan2(p * st, pParRest)
    return {'thetaRest': thetaRest, 'phiRest': np.asarray(phi, dtype=float), 'cosThetaRest': np.cos(thetaRest),
            'ERest': ERest / M}


def addRestFrame(entries, perJet, jets, axis, mass, particleMass=M_PION):
    """entries [event][jet][entry] (fields theta, phi, weight), the per-jet table (E_jet, n) and jets aligned with them.
    axis: 'jet' or an axis name (jet columns <axis>Pt/Eta/Phi/Mass); mass: 'axis' (the axis' own mass), a number
    (GeV) or a per-jet array; it must be >= 2 particleMass for every jet with entries. Returns entries with the restFrame()
    fields added."""
    if not ak.all(ak.flatten(perJet.n) == 1):
        raise ValueError('restFrame needs E1C weights with n = 1')
    if axis == 'jet':
        apt, aeta, aphi, am = jets.pt, jets.eta, jets.phi, jets.mass
    else:
        apt, aeta, aphi, am = (jets[axis + c] for c in ('Pt', 'Eta', 'Phi', 'Mass'))
    M = am if isinstance(mass, str) and mass == 'axis' else ak.ones_like(apt) * mass

    def perEntry(x):
        return ak.to_numpy(ak.flatten(ak.broadcast_arrays(x, entries.weight)[0], axis=None)).astype(float)

    flat = lambda f: ak.to_numpy(ak.flatten(entries[f], axis=None)).astype(float)
    Mflat = perEntry(M)
    # Below two particle masses no system of these particles has this rest frame (e.g. a massless parton axis).
    if np.any(~(Mflat >= 2 * particleMass)):
        raise ValueError('restFrame: boost mass below 2 x particleMass (%g GeV) for axis %s; use a fixed mass hypothesis'
                         % (particleMass, axis))
    pt = flat('weight') * perEntry(perJet.E_jet)
    out = restFrame(flat('theta'), flat('phi'), pt, perEntry(apt), perEntry(aeta), perEntry(aphi), Mflat, particleMass)
    counts1, counts2 = ak.num(entries.weight, axis=1), ak.flatten(ak.num(entries.weight, axis=2))
    for k, v in out.items():
        entries = ak.with_field(entries, ak.unflatten(ak.unflatten(v, counts2), counts1), k)
    return entries
