"""
Unittests for the class Momentum4
"""

import unittest
import numpy as np
import cmath
from pylorentz import Momentum4


class Momentum4TestCase(unittest.TestCase):
    """
    Test the implementation of Momentum4.
    """

    def test_init(self):
        """
        Check that a instantiation with all four componentes returns the
        correct vector.
        """
        momentum = Momentum4(100, 2.5, 1.23, 1.777)
        self.assertAlmostEqual(momentum.e, 100)
        self.assertAlmostEqual(momentum.p_x, 2.5)
        self.assertAlmostEqual(momentum.p_y, 1.23)
        self.assertAlmostEqual(momentum.p_z, 1.777)

    def test_e_eta_phi_pt(self):
        """
        Check that instantiation with e_eta_phi_pt() returns the correct
        object.
        """
        momentum = Momentum4.e_eta_phi_pt(100, 2.5, 1.23, 1.777)
        self.assertAlmostEqual(momentum.e, 100)
        self.assertAlmostEqual(momentum.eta, 2.5)
        self.assertAlmostEqual(momentum.phi, 1.23)
        self.assertAlmostEqual(momentum.p_t, 1.777)

        self.assertAlmostEqual(momentum.e**2, momentum.p**2 + momentum.m**2)

    def test_m_eta_phi_pt(self):
        """
        Check that instantiation with m_eta_phi_pt() returns the correct
        object.
        """
        momentum = Momentum4.m_eta_phi_pt(0.105, 2.5, 1.23, 1.777)
        self.assertAlmostEqual(momentum.m, 0.105)
        self.assertAlmostEqual(momentum.eta, 2.5)
        self.assertAlmostEqual(momentum.phi, 1.23)
        self.assertAlmostEqual(momentum.p_t, 1.777)
        self.assertAlmostEqual(momentum.e**2, momentum.p**2 + momentum.m**2)

    def test_m_eta_phi_p(self):
        """
        Check that instantiation with m_eta_phi_p() returns the correct
        object.
        """
        momentum = Momentum4.m_eta_phi_p(0.105, 2.5, 1.23, 1.777)
        self.assertAlmostEqual(momentum.m, 0.105)
        self.assertAlmostEqual(momentum.eta, 2.5)
        self.assertAlmostEqual(momentum.phi, 1.23)
        self.assertAlmostEqual(momentum.p, 1.777)
        self.assertAlmostEqual(momentum.e**2, momentum.p**2 + momentum.m**2)

    def test_e_eta_phi_p(self):
        """
        Check that instantiation with e_eta_phi_p() returns the correct
        object.
        """
        momentum = Momentum4.e_eta_phi_p(2, 2.5, 1.23, 1.777)
        self.assertAlmostEqual(momentum.e, 2)
        self.assertAlmostEqual(momentum.eta, 2.5)
        self.assertAlmostEqual(momentum.phi, 1.23)
        self.assertAlmostEqual(momentum.p, 1.777)
        self.assertAlmostEqual(momentum.e**2, momentum.p**2 + momentum.m**2)

    def test_e_m_eta_phi(self):
        """
        Check that instantiation with e_m_eta_phi() returns the correct
        object.
        """
        momentum = Momentum4.e_m_eta_phi(2, 1.777, 2.5, 1.23)
        self.assertAlmostEqual(momentum.e, 2)
        self.assertAlmostEqual(momentum.eta, 2.5)
        self.assertAlmostEqual(momentum.phi, 1.23)
        self.assertAlmostEqual(momentum.m, 1.777)
        self.assertAlmostEqual(momentum.e**2, momentum.p**2 + momentum.m**2)
