"""Spin-density matrix of a vector boson from the angles of its decay fermion (helicity frame).

Decay V(lambda) -> f fbar with massless fermions: for fermion helicity difference sigma = lambda_f - lambda_fbar = -1
(left-handed f, probability pMinus = (1 + A_f)/2) or +1,
    W(theta, phi) = 3/(4 pi) sum_sigma P_sigma sum_{l,l'} rho_{l l'} conj(D_{l sigma}) D_{l' sigma},
D_{l sigma} = exp(-i l phi) d^1_{l sigma}(theta) (Wigner, Condon-Shortley), lambda ordered (+1, 0, -1), and
(theta, phi) the fermion direction in the V rest frame. The off-diagonal phases depend on the x-axis convention.
rho is extracted with the moments of the nine real spherical harmonics with l <= 2, inverted with the matrix M of
their integrals against the decay distribution of each real parameter (exact quadrature).

Parameters, in order: rho_{++}, rho_{00}, rho_{--}, Re/Im rho_{+0}, Re/Im rho_{+-}, Re/Im rho_{0-}.
"""
import numpy as np

from .frames import axisKinematics

PARAMS = ['rho_pp', 'rho_00', 'rho_mm', 'Re_rho_p0', 'Im_rho_p0', 'Re_rho_pm', 'Im_rho_pm', 'Re_rho_0m', 'Im_rho_0m']


def d1(theta):
    """d^1_{l s}(theta) as an array [l][s][...], l and s ordered (+1, 0, -1)."""
    c, s = np.cos(theta), np.sin(theta)
    r = np.sqrt(2.0)
    return np.array([[(1 + c) / 2, -s / r, (1 - c) / 2],
                     [s / r, c, -s / r],
                     [(1 - c) / 2, s / r, (1 + c) / 2]])


def rhoMatrix(r):
    """Hermitian 3x3 matrix from the nine real parameters."""
    pp, zz, mm, rp0, ip0, rpm, ipm, r0m, i0m = r
    p0, pm, zm = rp0 + 1j * ip0, rpm + 1j * ipm, r0m + 1j * i0m
    return np.array([[pp, p0, pm], [np.conj(p0), zz, zm], [np.conj(pm), np.conj(zm), mm]])


def decayDistribution(theta, phi, rho, pMinus):
    """W(theta, phi) for the density matrix rho (3x3) and P(sigma = -1) = pMinus; normalised to tr(rho)."""
    d = d1(theta)
    phi = np.asarray(phi, dtype=float)
    lam = np.array([1, 0, -1]).reshape((3,) + (1,) * phi.ndim)
    D = np.exp(-1j * lam * phi)[:, None] * d  # [l][s][...]
    out = 0
    for si, P in ((0, 1 - pMinus), (2, pMinus)):   # s = +1, s = -1
        Ds = D[:, si, :]
        out = out + P * np.real(np.einsum('i...,ij,j...->...', np.conj(Ds), rho, Ds))
    return 3 / (4 * np.pi) * out


def testFunctions(theta, phi):
    """The nine real spherical harmonics with l <= 2 (unnormalised), shape [9][...]."""
    c, s = np.cos(theta), np.sin(theta)
    one = np.ones_like(c)
    return np.array([one, c, s * np.cos(phi), s * np.sin(phi), 3 * c * c - 1, s * c * np.cos(phi), s * c * np.sin(phi),
                     s * s * np.cos(2 * phi), s * s * np.sin(2 * phi)])


def momentMatrix(pMinus, nTheta=24, nPhi=48):
    """M[k][a] = integral of testFunction_k times the decay distribution of unit parameter a (exact quadrature)."""
    x, wx = np.polynomial.legendre.leggauss(nTheta)
    phi = (np.arange(nPhi) + 0.5) * 2 * np.pi / nPhi
    T, P = np.meshgrid(np.arccos(x), phi, indexing='ij')
    wgt = np.outer(wx, np.full(nPhi, 2 * np.pi / nPhi))
    g = testFunctions(T, P)
    M = np.empty((9, 9))
    for a in range(9):
        e = np.zeros(9)
        e[a] = 1.0
        W = decayDistribution(T, P, rhoMatrix(e), pMinus)
        M[:, a] = np.sum(g * W * wgt, axis=(1, 2))
    return M


def extract(theta, phi, pMinus, weights=None):
    """(parameters, covariance) of rho from fermion angles; weights are event weights (may be negative). pMinus may
    vary per event (e.g. quark flavours): M is affine in pMinus, so its weighted mean is exact."""
    w = np.ones_like(theta) if weights is None else np.asarray(weights, dtype=float)
    pMinus = float(np.sum(w * np.broadcast_to(pMinus, w.shape)) / np.sum(w))
    g = testFunctions(theta, phi)
    sw = w.sum()
    mean = (g * w).sum(axis=1) / sw
    dev = g - mean[:, None]
    cov = (dev * w ** 2) @ dev.T / sw ** 2
    Minv = np.linalg.inv(momentMatrix(pMinus))
    return Minv @ mean, Minv @ cov @ Minv.T


def helicityWeights(theta, aF):
    """Per-decay functions f_l (l = +1, 0, -1), shape [3][...], with E[f_l] = rho_ll for every rho, given the decay's own
    analysing power aF (per decay: exact also when rho depends on the flavour). Being the helicity projectors, their
    products over two decays estimate the diagonal of the joint density matrix."""
    c = np.cos(theta)
    f0 = (1 - 5 * (3 * c * c - 1)) / 3
    return np.array([(1 - f0) / 2 - c / aF, f0, (1 - f0) / 2 + c / aF])


def jointDiagonal(f1, f2, weights=None):
    """(P, cov): P[i][j] = probability of helicities (l1, l2) = (i, j) in (+1, 0, -1) order from the helicityWeights of
    the two decays of each event; cov is the 9x9 covariance of P.ravel()."""
    x = (f1[:, None] * f2[None, :]).reshape(9, -1)
    w = np.ones(x.shape[1]) if weights is None else np.asarray(weights, dtype=float)
    sw = w.sum()
    mean = (x * w).sum(axis=1) / sw
    dev = x - mean[:, None]
    return mean.reshape(3, 3), (dev * w ** 2) @ dev.T / sw ** 2


def higherMoments(theta, phi, weights=None):
    """(means, cov) of the 16 real spherical harmonics with l = 3, 4; any spin-1 decay gives zero, so
    means @ inv(cov) @ means is a chi^2 with 16 degrees of freedom for the shape of W."""
    from scipy.special import lpmv
    c = np.cos(theta)
    g = []
    for l in (3, 4):
        g.append(lpmv(0, l, c))
        for m in range(1, l + 1):
            P = lpmv(m, l, c)
            g += [P * np.cos(m * phi), P * np.sin(m * phi)]
    g = np.array(g)
    w = np.ones_like(c) if weights is None else np.asarray(weights, dtype=float)
    sw = w.sum()
    mean = (g * w).sum(axis=1) / sw
    dev = g - mean[:, None]
    return mean, (dev * w ** 2) @ dev.T / sw ** 2


def binnedPrediction(r, pMinus, cosEdges, phiEdges, nq=8):
    """Probability of each (cos theta, phi) bin, shape [nCos][nPhi], for the parameters r (Gauss-Legendre per bin)."""
    x, wx = np.polynomial.legendre.leggauss(nq)
    rho = rhoMatrix(r)
    out = np.empty((len(cosEdges) - 1, len(phiEdges) - 1))
    for i, (c0, c1) in enumerate(zip(cosEdges[:-1], cosEdges[1:])):
        c, wc = (c1 - c0) / 2 * x + (c1 + c0) / 2, (c1 - c0) / 2 * wx
        for j, (p0, p1) in enumerate(zip(phiEdges[:-1], phiEdges[1:])):
            p, wp = (p1 - p0) / 2 * x + (p1 + p0) / 2, (p1 - p0) / 2 * wx
            C, Ph = np.meshgrid(c, p, indexing='ij')
            out[i, j] = np.sum(np.outer(wc, wp) * decayDistribution(np.arccos(C), Ph, rho, pMinus))
    return out


def asymmetryParameter(pdgId, boson, sin2):
    """A_f = (c_L^2 - c_R^2)/(c_L^2 + c_R^2) of fermion pdgId (> 0) from a W (1) or a Z (tree level at sin^2 theta_W =
    sin2, which must be the generator's: A_lepton changes by ~45% between 0.2315 and 0.2226)."""
    if abs(boson) == 24:
        return 1.0
    a = abs(pdgId)
    T3, Q = {1: (-0.5, -1 / 3), 3: (-0.5, -1 / 3), 5: (-0.5, -1 / 3), 2: (0.5, 2 / 3), 4: (0.5, 2 / 3),
             11: (-0.5, -1.0), 13: (-0.5, -1.0), 15: (-0.5, -1.0), 12: (0.5, 0.0), 14: (0.5, 0.0), 16: (0.5, 0.0)}[a]
    gV, gA = T3 - 2 * Q * sin2, T3
    return 2 * gV * gA / (gV * gV + gA * gA)


def p4(pt, eta, phi, mass):
    px, py, pz = pt * np.cos(phi), pt * np.sin(phi), pt * np.sinh(eta)
    return np.stack([np.sqrt(px * px + py * py + pz * pz + mass * mass), px, py, pz])


def helicityAngles(V, f):
    """(theta, phi) of the fermion in the V rest frame: z = V lab direction, x in the (V, beam) plane toward the beam
    on the V side (the bvana/frames.py and EECs jet-frame convention). V, f: (pt, eta, phi, mass) tuples of arrays."""
    PV, Pf = p4(*V), p4(*f)
    beta = PV[1:] / PV[0]
    b2 = np.sum(beta * beta, axis=0)
    gamma = 1 / np.sqrt(1 - b2)
    bp = np.sum(beta * Pf[1:], axis=0)
    # Pure boost by -beta.
    pRest = Pf[1:] + ((gamma - 1) * bp / b2 - gamma * Pf[0]) * beta
    z, x = axisKinematics(V[0], V[1], V[2])
    y = np.cross(z, x, axis=0)
    pz, px, py = np.sum(pRest * z, axis=0), np.sum(pRest * x, axis=0), np.sum(pRest * y, axis=0)
    return np.arctan2(np.hypot(px, py), pz), np.arctan2(py, px)
