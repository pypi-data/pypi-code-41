"""
Unittests for the class Vector4
"""

import unittest
import numpy as np
import cmath
import math
from pylorentz import Vector4, Momentum4


class Vector4TestCase(unittest.TestCase):
    """
    Test the implementation of Vector4.
    """

    def test_repr(self):
        """
        Check that the representation returns a string that recreates the
        object.
        """
        vec = Vector4(1, 2, 3, 4)
        self.assertEqual(repr(vec), "Vector4(1, 2, 3, 4)")

    def test_init_numbers(self):
        """
        Check that objects can be created using four values.
        """
        vec = Vector4(1, 2, 3, 4)
        self.assertEqual(list(vec._values), [1, 2, 3, 4])
        self.assertIsInstance(vec._values, np.ndarray)

    def test_init_not_four(self):
        """
        Check that init raises an error if the number of arguments is not
        four.
        """
        self.assertRaises(TypeError, Vector4, 1, 2, 3)
        self.assertRaises(TypeError, Vector4, 1, 2, 3, 4, 5)

    def test_init_copy(self):
        """
        Check that objects can be copied.
        """
        vec = Vector4(1, 2, 3, 4)
        vec2 = Vector4(vec)

        vec._values = [0, 0, 0, 0]

        self.assertEqual(list(vec._values), [0, 0, 0, 0])
        self.assertEqual(list(vec2._values), [1, 2, 3, 4])

    def test_add(self):
        """
        Check that two 4-vectors can be added.
        """
        vec = Vector4(1, 2, 3, 4)
        vec2 = Vector4(3, 4, 5, 10)

        self.assertEqual(str(vec + vec2),
                         "Vector4(4, 6, 8, 14)") 

    def test_add_types(self):
        """
        Check that a 4-vectors and numbers cannot be added.
        """
        vec = Vector4(1, 2, 3, 4)
        self.assertRaises(TypeError, lambda: vec + 4)

    def test_iadd(self):
        """
        Check that two 4-vectors can be added in-place.
        """
        vec = Vector4(1, 2, 3, 4)
        vec2 = Vector4(3, 4, 5, 10)

        vec2 += vec

        self.assertEqual(str(vec2), "Vector4(4, 6, 8, 14)") 

    def test_iadd_types(self):
        """
        Check that a 4-vectors and numbers cannot be added in-place.
        """
        def func1():
            vec = Vector4(1, 2, 3, 4)
            vec += 4

        self.assertRaises(TypeError, func1)

    def test_sub(self):
        """
        Check that two 4-vectors can be subtracted.
        """
        vec = Vector4(1, 2, 3, 4)
        vec2 = Vector4(3, 4, 5, 10)

        self.assertEqual(str(vec - vec2),
                         "Vector4(-2, -2, -2, -6)") 

    def test_sub_types(self):
        """
        Check that a 4-vectors and numbers cannot be subtracted.
        """
        vec = Vector4(1, 2, 3, 4)
        self.assertRaises(TypeError, lambda: vec - 4)

    def test_isub(self):
        """
        Check that two 4-vectors can be subtracted in-place.
        """
        vec = Vector4(1, 2, 3, 4)
        vec2 = Vector4(3, 4, 5, 10)

        vec -= vec2

        self.assertEqual(str(vec), "Vector4(-2, -2, -2, -6)") 

    def test_isub_types(self):
        """
        Check that a 4-vectors and numbers cannot be subtracted in-place.
        """
        def func2():
            vec = Vector4(1, 2, 3, 4)
            vec -= 4

        self.assertRaises(TypeError, func2)

    def test_mul_scalar(self):
        """
        Check that multiplying the vector by a scalar, scales the vector.
        """
        vec = Vector4(1, 0, 4, 5)
        self.assertEqual(str(vec * 2), 'Vector4(2, 0, 8, 10)')

    def test_mul_dot_product(self):
        """
        Check that multiplying two vectors, returns the dot product.
        """
        vec = Vector4(2, 0, 4, 5)
        vec2 = Vector4(7, 0, -1, 3)

        self.assertEqual(vec * vec2, 14 - 0 + 4 - 15)

    def test_rmul_scalar(self):
        """
        Check that multiplying the vector by a scalar from left, scales the vector.
        """
        vec = Vector4(1, 0, 4, 5)
        self.assertEqual(str(2 * vec), 'Vector4(2, 0, 8, 10)')

    def test_imul_dot_product(self):
        """
        Check that multiplying a vector by a vector in-place, raises an error.
        """
        def func3():
            vec = Vector4(2, 0, 4, 5)
            vec2 = Vector4(7, 0, -1, 3)

            vec *= vec2

        self.assertRaises(TypeError, func3)

    def test_imul_scalar(self):
        """
        Check that multiplying a vector by a scaler in-place, scales the vector.
        """
        vec = Vector4(1, 0, 4, 5)
        vec *= 2

        self.assertEqual(str(vec), 'Vector4(2, 0, 8, 10)')

    def test_div_scalar(self):
        """
        Check that dividing a vector by a scalar, scales the vector.
        """
        vec = Vector4(1, 0, 4, 5)
        self.assertEqual(str(vec / 2.0), 'Vector4(0.5, 0, 2, 2.5)')

    def test_floordiv_scalar(self):
        """
        Check that dividing a vector by a scalar, scales the vector.
        """
        vec = Vector4(1, 0, 4, 5)
        self.assertEqual(str(vec // 3), 'Vector4(0, 0, 1, 1)')

    def test_ifloordiv_scalar(self):
        """
        Check that dividing a vector by a scalar in-place, scales the vector.
        """
        vec = Vector4(1, 0, 4, 5)
        vec //= 3
        self.assertEqual(str(vec), 'Vector4(0, 0, 1, 1)')

    def test_div_types(self):
        """
        Check that dividing two vectors, raises an exception.
        """
        vec = Vector4(2, 0, 4, 5)
        vec2 = Vector4(7, 0, -1, 3)

        self.assertRaises(TypeError, lambda: vec / vec2)

    def test_floordiv_types(self):
        """
        Check that dividing two vectors, raises an exception.
        """
        vec = Vector4(2, 0, 4, 5)
        vec2 = Vector4(7, 0, -1, 3)

        self.assertRaises(TypeError, lambda: vec // vec2)

    def test_rdiv_scalar(self):
        """
        Check that dividing a scalar by vector raises an exception.
        """
        vec = Vector4(1, 0, 4, 5)
        self.assertRaises(TypeError, lambda: 1 / vec)

    def test_rdiv_types(self):
        """
        Check that dividing two vectors raises an exception.
        """
        vec = Vector4(1, 0, 4, 5)
        vec2 = Vector4(1, 0, 4, 5)
        self.assertRaises(TypeError, lambda: vec2 / vec)

    def test_idiv_types(self):
        """
        Check that dividing a vector by a vector in-place, raises an error.
        """
        def func4():
            vec = Vector4(2, 0, 4, 5)
            vec2 = Vector4(7, 0, -1, 3)

            vec /= vec2

        self.assertRaises(TypeError, func4)

    def test_idiv_scalar(self):
        """
        Check that dividing a vector by a scalar in-place, scales the vector.
        """
        vec = Vector4(1, 0, 4, 5)
        vec /= 2.0

        self.assertEqual(str(vec), 'Vector4(0.5, 0, 2, 2.5)')

    def test_mag(self):
        """
        Check that mag returns the magnitude of the vectors respecting the
        metric.
        """
        vec = Vector4(4, 0, 3, 4)
        self.assertEqual(vec.mag, 3j)

        vec = Vector4(7, 2, 3, 4)
        self.assertEqual(vec.mag, cmath.sqrt(49 - 4 - 9 - 16))

    def test_mag2(self):
        """
        Check that mag returns the square magnitude of the vectors respecting
        the metric.
        """
        vec = Vector4(4, 0, 3, 4)
        self.assertEqual(vec.mag2, -9)

        vec = Vector4(7, 2, 3, 4)
        self.assertEqual(vec.mag2, 49 - 4 - 9 - 16)

    def test_eta(self):
        """
        Check that eta returns the pseudo-rapidity of a vector.
        """
        # Forward
        vector = Vector4(1, 0, 0, 1)
        self.assertEqual(vector.eta, float('inf'))
        vector = Vector4(0, 0, 0, 1)
        self.assertEqual(vector.eta, float('inf'))

        # Backward
        vector = Vector4(1, 0, 0, -1)
        self.assertEqual(vector.eta, float('-inf'))

        # Center
        vector = Vector4(1, 0, 1, 0)
        self.assertAlmostEqual(vector.eta, 0)
        vector = Vector4(1, 1, 0, 0)
        self.assertAlmostEqual(vector.eta, 0)

        # 45 deg
        vector = Vector4(1, 0, 1, 1)
        self.assertAlmostEqual(vector.eta, 0.8813735870195428)
        vector = Vector4(1, 1, 0, 1)
        self.assertAlmostEqual(vector.eta, 0.8813735870195428)
        vector = Vector4(10, 0, 1, 1)
        self.assertAlmostEqual(vector.eta, 0.8813735870195428)
        vector = Vector4(0, 0, 1, 1)
        self.assertAlmostEqual(vector.eta, 0.8813735870195428)

    def test_theta(self):
        """
        Check that theta returns the azimuthal angle of the vector.
        """
        # Forward
        vector = Vector4(1, 0, 0, 1)
        self.assertEqual(vector.theta, 0)
        vector = Vector4(0, 0, 0, 1)
        self.assertEqual(vector.theta, 0)

        # Backward
        vector = Vector4(1, 0, 0, -1)
        self.assertEqual(vector.theta, cmath.pi)

        # Center
        vector = Vector4(1, 0, 1, 0)
        self.assertEqual(vector.theta, cmath.pi / 2)
        vector = Vector4(1, 1, 0, 0)
        self.assertEqual(vector.theta, cmath.pi / 2)

        # 45 deg
        vector = Vector4(1, 0, 1, 1)
        self.assertAlmostEqual(vector.theta, cmath.pi / 4)
        vector = Vector4(1, 1, 0, 1)
        self.assertAlmostEqual(vector.theta, cmath.pi / 4)
        vector = Vector4(10, 0, 1, 1)
        self.assertAlmostEqual(vector.theta, cmath.pi / 4)
        vector = Vector4(0, 0, 1, 1)
        self.assertAlmostEqual(vector.theta, cmath.pi / 4)

    def test_phi(self):
        """
        Check that phi returns the polar angle of the vector.
        """
        vector = Vector4(1, 1, 0, 1)
        self.assertEqual(vector.phi, 0)
        vector = Vector4(1, 0, 1, 1)
        self.assertAlmostEqual(vector.phi, cmath.pi / 2)

        vector = Vector4(0, -1, 0, 1)
        self.assertAlmostEqual(vector.phi, cmath.pi)
        vector = Vector4(1, -1, 0, 1)
        self.assertAlmostEqual(vector.phi, cmath.pi)
        vector = Vector4(1, -1, 0, 10)
        self.assertAlmostEqual(vector.phi, cmath.pi)

        vector = Vector4(1, 0, -1, 1)
        self.assertAlmostEqual(vector.phi, -cmath.pi / 2)

    def test_trans(self):
        """
        Check that trans returns the length of the transverse vector.
        """
        vector = Vector4(1, 1, 0, 1)
        self.assertEqual(vector.trans, 1)
        vector = Vector4(1, 0, 1, 1)
        self.assertAlmostEqual(vector.trans, 1)

        vector = Vector4(0, -1, 0, 1)
        self.assertAlmostEqual(vector.trans, 1)
        vector = Vector4(1, -1, 0, 1)
        self.assertAlmostEqual(vector.trans, 1)
        vector = Vector4(1, -1, 0, 10)
        self.assertAlmostEqual(vector.trans, 1)

        vector = Vector4(1, 3, 4, 1)
        self.assertAlmostEqual(vector.trans, 5)

class BoostTestCase(unittest.TestCase):
    """
    Test the implementation of Lorentz boosts.
    """

    def test_beta_simple(self):
        """
        Check that a simple, regular boost with beta parameter returns the
        boosted vector.
        """
        vector = Vector4(20, 40, 0, 0)
        boosted = vector.boost(1, 0, 0, beta=3./5)

        self.assertAlmostEqual(boosted[0], -5)
        self.assertAlmostEqual(boosted[1], 35)
        self.assertAlmostEqual(boosted[2], 0)
        self.assertAlmostEqual(boosted[3], 0)

    def test_beta(self):
        """
        Check that a regular boost with beta parameter returns the boosted
        vector.
        """
        vector = Vector4(1, 2, 3, 4)
        boosted = vector.boost(5, 3, 4, beta=0.5)

        self.assertAlmostEqual(boosted[0], -1.7030374948677893)
        self.assertAlmostEqual(boosted[1], 2.1332035938635183)
        self.assertAlmostEqual(boosted[2], 3.0799221563181116)
        self.assertAlmostEqual(boosted[3], 4.106562875090814)


    def test_beta_rest(self):
        """
        Check that a regular boost with beta=0 returns the same vector.
        """
        vector = Vector4(1, 2, 3, 4)
        boosted = vector.boost(5, 3, 4, beta=0)

        self.assertAlmostEqual(boosted[0], 1)
        self.assertAlmostEqual(boosted[1], 2)
        self.assertAlmostEqual(boosted[2], 3)
        self.assertAlmostEqual(boosted[3], 4)

    def test_gamma_simple(self):
        """
        Check that a simple, regular boost with gamma parameter returns the
        boosted vector.
        """
        vector = Vector4(20, 40, 0, 0)
        boosted = vector.boost(1, 0, 0, gamma=5./4)

        self.assertAlmostEqual(boosted[0], -5)
        self.assertAlmostEqual(boosted[1], 35)
        self.assertAlmostEqual(boosted[2], 0)
        self.assertAlmostEqual(boosted[3], 0)

    def test_gamma(self):
        """
        Check that a regular boost with gamma parameter returns the boosted
        vector.
        """
        vector = Vector4(1, 2, 3, 4)
        boosted = vector.boost(5, 3, 4, gamma=1/math.sqrt(0.75))

        self.assertAlmostEqual(boosted[0], -1.7030374948677893)
        self.assertAlmostEqual(boosted[1], 2.1332035938635183)
        self.assertAlmostEqual(boosted[2], 3.0799221563181116)
        self.assertAlmostEqual(boosted[3], 4.106562875090814)


    def test_gamma_rest(self):
        """
        Check that a regular boost with gamma=0 returns the same vector.
        """
        vector = Vector4(1, 2, 3, 4)
        boosted = vector.boost(5, 3, 4, gamma=1)

        self.assertAlmostEqual(boosted[0], 1)
        self.assertAlmostEqual(boosted[1], 2)
        self.assertAlmostEqual(boosted[2], 3)
        self.assertAlmostEqual(boosted[3], 4)

    def assertBetween(self, min, actual, max):
        self.assertLess(min, actual)
        self.assertLess(actual, max)

    def test_particle(self):
        """
        Check that a boost from a moving particle returns the correct vector.
        """
        m = 125.0

        # Pair of taus in the y-z-plane
        tau_1 = Momentum4.e_m_eta_phi(m / 2, 1.777, 2, math.pi / 2)
        tau_2 = Momentum4.e_m_eta_phi(m / 2, 1.777, -2, -math.pi / 2)

        # Higgs boosted in ~x direction
        higgs = Momentum4.m_eta_phi_pt(m, 0.1, 0.1, 345.6)

        tau_1 = tau_1.boost_particle(higgs)
        tau_2 = tau_2.boost_particle(higgs)

        self.assertBetween(0, tau_1.eta, 2)
        self.assertBetween(0, tau_1.phi, math.pi/2)

        self.assertBetween(-2, tau_2.eta, 0)
        self.assertBetween(-math.pi/2, tau_2.phi, 0)

        delta_R = math.sqrt((tau_1.eta - tau_2.eta)**2
                            + (tau_1.phi - tau_2.phi)**2)

        # approximation: dR = 2 * m / pT
        self.assertAlmostEqual(delta_R, 2 * higgs.m / higgs.p_t, 1)

