"""
Unittests for the class Momentum4
"""

import unittest
import numpy as np
import cmath
from pylorentz import Position4


class Position4TestCase(unittest.TestCase):
    """
    Test the implementation of Position4.
    """

    def test_init(self):
        """
        Check that a instantiation with all four componentes returns the
        correct vector.
        """
        position = Position4(100, 2.5, 1.23, 1.777)
        self.assertAlmostEqual(position.t, 100)
        self.assertAlmostEqual(position.x, 2.5)
        self.assertAlmostEqual(position.y, 1.23)
        self.assertAlmostEqual(position.z, 1.777)
