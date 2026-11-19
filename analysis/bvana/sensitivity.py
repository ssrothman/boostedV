"""Stat-only significance of a signal in the per-jet E2C, and the distortion of the background shape by a cut.

A jet's E2C row v_j (bins in Delta R) is placed in the block of its jet-pT slice. With expected yields w_j (MC weight
scaled to the luminosity) and one jet per event, the total histogram H = sum_j v_j of a Poisson data set has
covariance C = sum_j w_j v_j v_j^T, built here from MC. EEC bins of one jet are correlated, so C is not diagonal.
  Z_tot^2   = s^T C^+ s            (C of the background-only hypothesis)
  Z_shape^2 = Z_tot^2 - (s^T C^+ b)^2 / (b^T C^+ b)   (background normalisation profiled)
C^+ is the pseudo-inverse on the bins with non-zero variance.
"""
import numpy as np

PT_SLICES = np.array([200.0, 300.0, 400.0, 600.0, 1000.0, np.inf])
EIG_CUTOFF = 1e-12
CHUNK = 200000


class Stats:
    """H (sum w v), C (sum w v v^T) and Cmc (sum w^2 v v^T) over jets, block-diagonal in the pT slices."""

    def __init__(self, V, w, pt, slices=PT_SLICES):
        k, nS = V.shape[1], len(slices) - 1
        self.H = np.zeros(nS * k)
        self.C = np.zeros((nS * k, nS * k))
        self.Cmc = np.zeros((nS * k, nS * k))
        sl = np.searchsorted(slices, pt, side='right') - 1
        for i in range(nS):
            idx = np.flatnonzero(sl == i)
            b = slice(i * k, (i + 1) * k)
            for c in range(0, len(idx), CHUNK):   # bounded float64 copies
                j = idx[c:c + CHUNK]
                Vi, wi = V[j].astype(np.float64), w[j]
                self.H[b] += wi @ Vi
                self.C[b, b] += Vi.T @ (Vi * wi[:, None])
                self.Cmc[b, b] += Vi.T @ (Vi * (wi ** 2)[:, None])

    def __add__(self, other):
        out = object.__new__(Stats)
        out.H, out.C, out.Cmc = self.H + other.H, self.C + other.C, self.Cmc + other.Cmc
        return out


def pinv(C):
    """Pseudo-inverse on the bins with positive variance; eigenvalues below EIG_CUTOFF x the largest are dropped."""
    keep = np.diag(C) > 0
    out = np.zeros_like(C)
    if not keep.any():
        return out
    e, U = np.linalg.eigh(C[np.ix_(keep, keep)])
    good = e > EIG_CUTOFF * e.max()
    out[np.ix_(keep, keep)] = (U[:, good] / e[good]) @ U[:, good].T
    return out


def significance(s, b, C):
    """(Z_tot, Z_shape) of signal vector s over background vector b with covariance C."""
    P = pinv(C)
    z2 = s @ P @ s
    bb = b @ P @ b
    shape = z2 - (s @ P @ b) ** 2 / bb if bb > 0 else z2
    return np.sqrt(max(z2, 0.0)), np.sqrt(max(shape, 0.0))


def shapeChi2(Hpass, Cpass, Href):
    """chi2 and ndf of the unit-normalised Hpass against the unit-normalised Href, with the covariance of the
    normalised Hpass propagated from Cpass (the reference is taken as exact)."""
    n = Hpass.sum()
    p, q = Hpass / n, Href / Href.sum()
    J = (np.eye(len(p)) - np.outer(p, np.ones(len(p)))) / n
    Cp = J @ Cpass @ J.T
    keep = np.diag(Cpass) > 0
    ndf = int(keep.sum()) - 1
    d = p - q
    return float(d @ pinv(Cp) @ d), ndf


def slicedShapeChi2(Hpass, Cpass, Href, nSlices):
    """shapeChi2 summed over the pT-slice blocks, each normalised on its own, so that a change of the jet-pT spectrum
    alone gives 0. Blocks empty in Hpass or Href are skipped. Returns (chi2, ndf)."""
    k = len(Hpass) // nSlices
    chi2, ndf = 0.0, 0
    for i in range(nSlices):
        b = slice(i * k, (i + 1) * k)
        if Hpass[b].sum() > 0 and Href[b].sum() > 0:
            c, n = shapeChi2(Hpass[b], Cpass[b, b], Href[b])
            chi2, ndf = chi2 + c, ndf + n
    return chi2, ndf


def peakWindow(binCenters, pt, mass, lo=0.55, hi=1.65):
    """(jets, bins) mask of the bins whose Delta R lies in [lo, hi] x 2 m / pT of each jet."""
    x = binCenters[None, :] * pt[:, None] / (2.0 * mass)
    return (x >= lo) & (x <= hi)


def cosThetaHelicity(lPt, lEta, lPhi, zPt, zEta, zPhi, zMass):
    """cos of the angle between a massless lepton in the Z rest frame and the Z direction in the lab."""
    def p3(pt, eta, phi):
        return np.stack([pt * np.cos(phi), pt * np.sin(phi), pt * np.sinh(eta)], axis=-1)
    pl, pz = p3(lPt, lEta, lPhi), p3(zPt, zEta, zPhi)
    El = np.linalg.norm(pl, axis=-1)
    Ez = np.sqrt(np.sum(pz ** 2, axis=-1) + zMass ** 2)
    beta = pz / Ez[:, None]
    b2 = np.sum(beta ** 2, axis=-1)
    gamma = 1.0 / np.sqrt(1.0 - b2)
    bp = np.sum(beta * pl, axis=-1)
    plRest = pl + ((gamma - 1.0) * bp / b2 - gamma * El)[:, None] * beta
    zHat = pz / np.linalg.norm(pz, axis=-1)[:, None]
    return np.sum(plRest * zHat, axis=-1) / np.linalg.norm(plRest, axis=-1)
