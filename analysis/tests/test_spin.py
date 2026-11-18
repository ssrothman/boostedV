"""Tests of bvana.spin: decay distribution, moment extraction closure, the fermion/antifermion identity and the
helicity-frame angles."""
import unittest

import numpy as np

from bvana import spin


def randomRho(rng):
    """A valid (positive, unit-trace) density matrix: a mixture of two random pure states."""
    vs = rng.normal(size=(2, 3)) + 1j * rng.normal(size=(2, 3))
    vs /= np.linalg.norm(vs, axis=1)[:, None]
    p = rng.uniform(0.2, 0.8)
    return p * np.outer(vs[0], vs[0].conj()) + (1 - p) * np.outer(vs[1], vs[1].conj())


def params(rho):
    return np.array([rho[0, 0].real, rho[1, 1].real, rho[2, 2].real, rho[0, 1].real, rho[0, 1].imag,
                     rho[0, 2].real, rho[0, 2].imag, rho[1, 2].real, rho[1, 2].imag])


def sample(rho, pMinus, n, rng):
    """Accept-reject from W (bounded by 3/(4 pi) * 2 for a density matrix)."""
    out = []
    while sum(len(o[0]) for o in out) < n:
        c, ph = rng.uniform(-1, 1, 4 * n), rng.uniform(-np.pi, np.pi, 4 * n)
        th = np.arccos(c)
        W = spin.decayDistribution(th, ph, rho, pMinus)
        keep = rng.uniform(0, 2 * 3 / (4 * np.pi), len(c)) < W
        out.append((th[keep], ph[keep]))
    th = np.concatenate([o[0] for o in out])[:n]
    ph = np.concatenate([o[1] for o in out])[:n]
    return th, ph


class DecayDistribution(unittest.TestCase):
    def test_normalisation_and_longitudinal_and_transverse_shapes(self):
        rng = np.random.default_rng(1)
        M = spin.momentMatrix(0.7)
        r = params(randomRho(rng))
        self.assertAlmostEqual((M @ r)[0], 1.0, places=12)   # the l = 0 moment is the integral
        th = np.linspace(0.1, 3.0, 7)
        L = spin.decayDistribution(th, 0 * th, spin.rhoMatrix([0, 1, 0, 0, 0, 0, 0, 0, 0]), 0.7)
        np.testing.assert_allclose(L, 3 / (8 * np.pi) * np.sin(th) ** 2, rtol=1e-12)
        # Helicity -1 with a left-handed fermion: the fermion follows the spin, (1 + cos)^2 along the boson direction.
        m = spin.decayDistribution(th, 0 * th, spin.rhoMatrix([0, 0, 1, 0, 0, 0, 0, 0, 0]), 1.0)
        np.testing.assert_allclose(m, 3 / (16 * np.pi) * (1 + np.cos(th)) ** 2, rtol=1e-12)

    def test_rotated_spin_state_points_along_x(self):
        # |psi> = R(0, pi/2, 0)|m = -1>: the helicity -1 state rotated from z to x. With a left-handed fermion,
        # W = 3/(16 pi) (1 + n.x)^2: the off-diagonal phases put the spin along +x (phi = 0), not -x.
        psi = spin.d1(np.pi / 2)[:, 2]
        rho = np.outer(psi, psi.conj())
        rng = np.random.default_rng(4)
        th, ph = np.arccos(rng.uniform(-1, 1, 50)), rng.uniform(-np.pi, np.pi, 50)
        nx = np.sin(th) * np.cos(ph)
        np.testing.assert_allclose(spin.decayDistribution(th, ph, rho, 1.0), 3 / (16 * np.pi) * (1 + nx) ** 2, atol=1e-12)
        r, _ = spin.extract(*sample(rho, 1.0, 50000, rng), 1.0)
        self.assertLess(r[3], 0)   # Re rho_{+0} = d_{+1,-1} d_{0,-1} = (1/2)(-1/sqrt 2): the sign that means +x

    def test_positive_for_a_density_matrix(self):
        rng = np.random.default_rng(2)
        th, ph = np.arccos(rng.uniform(-1, 1, 5000)), rng.uniform(-np.pi, np.pi, 5000)
        for _ in range(5):
            self.assertGreaterEqual(spin.decayDistribution(th, ph, randomRho(rng), 0.8).min(), -1e-15)


class Extraction(unittest.TestCase):
    def test_closure_on_sampled_decays(self):
        rng = np.random.default_rng(7)
        for pMinus in (0.85, 0.57):   # quark-like and lepton-like analysing powers
            rho = randomRho(rng)
            th, ph = sample(rho, pMinus, 200000, rng)
            r, cov = spin.extract(th, ph, pMinus)
            pull = (r - params(rho)) / np.sqrt(np.maximum(np.diag(cov), 1e-30))
            self.assertAlmostEqual(r[0] + r[1] + r[2], 1.0, places=10)
            self.assertLess(np.max(np.abs(pull[1:])), 4.5, (pMinus, pull))
            # A wrong analysing power biases the parity-odd entries (rho_pp - rho_mm), so the test discriminates it.
            rw, covw = spin.extract(th, ph, 1 - pMinus)
            d = (rw[0] - rw[2]) - (r[0] - r[2])
            self.assertGreater(abs(d), 5 * np.sqrt(cov[0, 0] + cov[2, 2] - 2 * cov[0, 2]) if abs(r[0] - r[2]) > 0.05 else -1)

    def test_antifermion_with_swapped_helicity_gives_the_same_rho(self):
        rng = np.random.default_rng(3)
        th, ph = sample(randomRho(rng), 0.8, 20000, rng)
        r, _ = spin.extract(th, ph, 0.8)
        rbar, _ = spin.extract(np.pi - th, ph + np.pi, 0.2)
        np.testing.assert_allclose(rbar, r, atol=1e-12)


def sampleJoint(psi, pMinus1, pMinus2, n, rng):
    """Accept-reject from the joint decay distribution of the two-boson pure state psi[l1][l2]."""
    out = []
    while sum(len(o[0]) for o in out) < n:
        m = 40 * n
        th1, th2 = np.arccos(rng.uniform(-1, 1, m)), np.arccos(rng.uniform(-1, 1, m))
        ph1, ph2 = rng.uniform(-np.pi, np.pi, m), rng.uniform(-np.pi, np.pi, m)
        lam = np.array([1, 0, -1])[:, None]
        D1 = np.exp(-1j * lam[:, :, None] * ph1) * spin.d1(th1)   # [l][s][...]
        D2 = np.exp(-1j * lam[:, :, None] * ph2) * spin.d1(th2)
        W = 0
        for s1, P1 in ((0, 1 - pMinus1), (2, pMinus1)):
            for s2, P2 in ((0, 1 - pMinus2), (2, pMinus2)):
                W = W + P1 * P2 * np.abs(np.einsum('ij,i...,j...->...', psi, np.conj(D1[:, s1]), np.conj(D2[:, s2]))) ** 2
        keep = rng.uniform(0, 9, m) < W   # |amplitude|^2 <= (sum |psi|)^2 <= 9
        out.append((th1[keep], ph1[keep], th2[keep], ph2[keep]))
    return [np.concatenate([o[k] for o in out])[:n] for k in range(4)]


class JointDiagonal(unittest.TestCase):
    def test_entangled_state_diagonal(self):
        rng = np.random.default_rng(11)
        psi = np.zeros((3, 3), complex)
        psi[0, 2], psi[2, 0], psi[1, 1], psi[0, 1] = 0.6, 0.3j, -0.5, 0.4 + 0.2j
        psi /= np.linalg.norm(psi)
        pM1, pM2 = 0.97, 0.6
        th1, ph1, th2, ph2 = sampleJoint(psi, pM1, pM2, 200000, rng)
        P, cov = spin.jointDiagonal(spin.helicityWeights(th1, 2 * pM1 - 1), spin.helicityWeights(th2, 2 * pM2 - 1))
        err = np.sqrt(np.diag(cov)).reshape(3, 3)
        self.assertAlmostEqual(P.sum(), 1.0, places=10)
        self.assertLess(np.max(np.abs((P - np.abs(psi) ** 2) / err)), 4.5, (P, np.abs(psi) ** 2, err))
        # The marginals agree with the single-boson extraction.
        r1, _ = spin.extract(th1, ph1, pM1)
        np.testing.assert_allclose(P.sum(axis=1), r1[:3], atol=1e-10)
        # Discriminating: the product of the marginals (no correlation) is far from it (here (+,-): 0.47 vs 0.25).
        prod = np.outer(P.sum(axis=1), P.sum(axis=0))
        self.assertGreater(np.max(np.abs((prod - np.abs(psi) ** 2) / err)), 10)


class Shape(unittest.TestCase):
    def test_higher_moments_vanish_for_spin_one_and_not_after_an_acceptance_cut(self):
        rng = np.random.default_rng(5)
        th, ph = sample(randomRho(rng), 0.8, 100000, rng)
        m, cov = spin.higherMoments(th, ph)
        self.assertLess(m @ np.linalg.solve(cov, m), 45)   # chi^2(16) > 45 has p < 2e-4
        cut = np.abs(np.cos(th)) < 0.8
        m, cov = spin.higherMoments(th[cut], ph[cut])
        self.assertGreater(m @ np.linalg.solve(cov, m), 500)

    def test_binned_prediction(self):
        ce, pe = np.linspace(-1, 1, 5), np.linspace(-np.pi, np.pi, 7)
        L = spin.binnedPrediction([0, 1, 0, 0, 0, 0, 0, 0, 0], 0.7, ce, pe)
        F = lambda c: 0.75 * (c - c ** 3 / 3)   # cos theta CDF of sin^2 theta, flat in phi
        np.testing.assert_allclose(L.sum(axis=1), F(ce[1:]) - F(ce[:-1]), rtol=1e-12)
        np.testing.assert_allclose(L.sum(axis=0), np.full(6, 1 / 6), rtol=1e-12)
        rng = np.random.default_rng(6)
        r = params(randomRho(rng))
        P = spin.binnedPrediction(r, 0.8, ce, pe)
        self.assertAlmostEqual(P.sum(), 1.0, places=12)
        th, ph = sample(spin.rhoMatrix(r), 0.8, 100000, rng)
        h, _, _ = np.histogram2d(np.cos(th), ph, [ce, pe])
        self.assertLess(np.sum((h - 1e5 * P) ** 2 / (1e5 * P)), 60)   # 24 bins
        # Discriminating: the wrong analysing power fails.
        Pw = spin.binnedPrediction(r, 0.2, ce, pe)
        self.assertGreater(np.sum((h - 1e5 * Pw) ** 2 / (1e5 * Pw)), 200)


class Couplings(unittest.TestCase):
    def test_asymmetry_parameters_match_the_pdg_values(self):
        # PDG (Electroweak model review) at sin^2 theta_eff = 0.2315: A_l = 0.147, A_u = 0.67, A_d = 0.94.
        self.assertAlmostEqual(spin.asymmetryParameter(11, 23, 0.23153), 0.147, places=3)
        self.assertAlmostEqual(spin.asymmetryParameter(2, 23, 0.23153), 0.668, places=2)
        self.assertAlmostEqual(spin.asymmetryParameter(1, 23, 0.23153), 0.936, places=2)
        self.assertEqual(spin.asymmetryParameter(13, 24, 0.23153), 1.0)
        self.assertEqual(spin.asymmetryParameter(12, 23, 0.2229), 1.0)   # neutrinos are purely left-handed


class HelicityAngles(unittest.TestCase):
    def test_hand_computed_frame(self):
        # V along +x at eta 0: z = +x_lab, x = +z_lab (beam on the V side, sign +), y = z cross x = -y_lab.
        m, pt, gamma = 91.19, 300.0, None
        V = tuple(np.array([v]) for v in (pt, 0.0, 0.0, m))
        E = np.sqrt(pt * pt + m * m)
        b, g = pt / E, E / m
        for (rest, theta, phi) in (((0, 0, 1), np.pi / 2, 0.0), ((0, -1, 0), np.pi / 2, np.pi / 2),
                                   ((1, 0, 0), 0.0, None), ((-1 / np.sqrt(2), 0, 1 / np.sqrt(2)), 3 * np.pi / 4, 0.0)):
            p = 10.0
            px, py, pz = (p * c for c in rest)
            Elab, pxlab = g * (p + b * px), g * (px + b * p)   # massless fermion boosted along +x
            ptl = np.hypot(pxlab, py)
            f = (np.array([ptl]), np.array([np.arcsinh(pz / ptl)]), np.array([np.arctan2(py, pxlab)]), np.array([0.0]))
            th, ph = spin.helicityAngles(V, f)
            self.assertAlmostEqual(th[0], theta, places=9)
            if phi is not None:
                self.assertAlmostEqual(ph[0], phi, places=9)


if __name__ == '__main__':
    unittest.main()
