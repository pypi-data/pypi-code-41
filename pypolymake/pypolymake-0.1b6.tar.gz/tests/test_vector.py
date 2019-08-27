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

try:
    import gmpy2
except ImportError:
    gmpy2 = None

class TestVector(unittest.TestCase):
    vecs = [polymake.VectorInteger, polymake.VectorRational]

    def test_init(self):
        polymake.VectorInteger([])
        polymake.VectorInteger([0,1,3])
        polymake.VectorRational([0,-3])

        polymake.VectorRational([(2,1),(-1,3)])
        polymake.VectorRational([2,(-1,3)])
        polymake.VectorRational([(2,5),-1])

    def test_cmp(self):
        for t in self.vecs:
            self.assertTrue(t() == t())
            self.assertFalse(t() != t())
            self.assertEqual(t([0,1]), t([0,1]))

            self.assertFalse(t() == t([0]))
            self.assertTrue(t() != t([0]))
            self.assertNotEqual(t([0]), t())

            self.assertNotEqual(t([0]), t([1]))
            self.assertNotEqual(t([1]), t([0]))

        for t1 in self.vecs:
            for t2 in self.vecs:
                self.assertEqual(t1(), t2())
                self.assertEqual(t1([0,0]), t2([0,0]))
                self.assertNotEqual(t1(), t2([0]))
                self.assertNotEqual(t1([0]), t2())

    def test_neg(self): 
        for t in self.vecs:
            self.assertEqual(-t([1,2]), t([-1,-2]))

    def test_binop(self):
        for t in self.vecs:
            self.assertEqual(t([1]) + t([3]), t([4]))

        for t1 in self.vecs:
            for t2 in self.vecs:
                for t3 in self.vecs:
                    self.assertEqual(t1([1]) + t2([3]), t3([4]))

