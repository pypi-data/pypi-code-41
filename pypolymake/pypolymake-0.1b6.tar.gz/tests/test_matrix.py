#!/usr/bin/env python3

import unittest
import random

# NOTE: apparently this has to be done *before* importing polymake.
# Otherwise it produces segfault...
try:
    import sage.all
    import sage
except ImportError:
    sage = None

import polymake
import polymake.matrix

try:
    import gmpy2
except ImportError:
    gmpy2 = None

class TestMatrix(unittest.TestCase):
    mats = [(int, polymake.matrix.MatrixInt),
            (float, polymake.matrix.MatrixFloat),
            (polymake.Integer, polymake.matrix.MatrixInteger),
            (polymake.Rational, polymake.matrix.MatrixRational),
            (polymake.QuadraticExtension, polymake.matrix.MatrixQuadraticExtension)]

    def test_init(self):
        m1 = polymake.matrix.MatrixInt([[1,2], [3,4]])
        m2 = polymake.matrix.MatrixInt(2, 2, [1,2,3,4])
        self.assertEqual(m1, m2)

        m1 = polymake.matrix.MatrixFloat([[1.3, 2.5, 0.2], [-1.3, 1, -1.3]])
        m2 = polymake.matrix.MatrixFloat(2, 3, [1.3, 2.5, 0.2, -1.3, 1, -1.3])
        self.assertEqual(m1, m2)

        polymake.matrix.MatrixInteger([[1,2], [-3,2**100]])
        polymake.matrix.MatrixRational([[(1,2), polymake.Rational(3,4)], [5, (-6,7)]])
        polymake.matrix.MatrixQuadraticExtension([[(1,2,3), polymake.QuadraticExtension(1,1,5)],
                                           [polymake.Integer(-3), 5**100]])

    def test_binop(self):
        m1 = polymake.matrix.MatrixInt([[1,2,3],[4,5,6]])
        m2 = polymake.matrix.MatrixInt([[-1,-1,-1],[-2,-2,-2]])
        s = polymake.matrix.MatrixInt([[0,1,2],[2,3,4]])
        self.assertEqual(type(m1 + m2), type(s))
        self.assertEqual(m1 + m2, s)

    def test_getitem(self):
        for scal_typ, mat_typ in self.mats:
            m = mat_typ([[1,2],[3,4]])
            self.assertEqual(type(m[0,0]), scal_typ)
            self.assertEqual(m[0,0], scal_typ(1))

    def test_sage(self):
        if sage is None:
            return

        for scal_typ, mat_typ in self.mats:
            m = mat_typ([[1,2],[3,4]])
            m.sage()

        m = polymake.matrix.MatrixQuadraticExtension([
            [(1,2,3),((2,3),-1,3)],[(1,1,3),2]])
        m.sage()


        m = polymake.matrix.MatrixQuadraticExtension([[(0,1,5),(1,(-1,5),5)]])
        mm = m.sage()
        self.assertEqual(mm[0,0]**2, 5)
        self.assertEqual(5*(mm[0,1]-1)**2, 1)
