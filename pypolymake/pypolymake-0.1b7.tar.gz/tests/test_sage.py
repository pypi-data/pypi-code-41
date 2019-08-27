import unittest
import random

try:
    import sage.all
    import sage
except ImportError:
    sage = None

import polymake

class TestPolymakeRational(unittest.TestCase):
    def test_is_sage_type(self):
        if sage is None:
            return

        from polymake.coercion import is_sage_type

        for a in [1, 'hello', int, polymake.Integer(3)]:
            self.assertFalse(is_sage_type(type(a)))

        for a in [sage.all.Integer(1),
                  sage.all.Rational(1), 
                  sage.all.ZZ,
                  sage.all.QQ,
                  sage.all.AA,
                  sage.all.matrix(sage.all.ZZ, 2),
                  sage.all.vector(sage.all.ZZ, 2),
                  sage.all.polytopes.cube()]:
            self.assertTrue(is_sage_type(type(a)))

    def test_sage_polymake_sage(self):
        if sage is None:
            return

        # round trip: sage -> polymake -> sage
        for obj in [sage.all.Integer(1),
                    sage.all.Integer(2**32),
                    sage.all.Rational((-3, 5)),
                    sage.all.vector(sage.all.ZZ, [1,2,3]),
                    sage.all.vector(sage.all.QQ, [1,2,sage.all.QQ((3,5))]),
                    sage.all.polytopes.cube(),
                    sage.all.polytopes.associahedron(['B',4]),
                    sage.all.Polyhedron(vertices=[(0,0)], rays=[(1,0),(1,1)]),
                    sage.all.polytopes.dodecahedron()]:

            self.assertEqual(polymake.polymake(obj).sage(), obj)

    def test_polymake_sage_polymake(self):
        if sage is None:
            return

        # round trip: polymake -> sage -> polymake
        # TODO: polymake comparison for polytope is not what you might expect...
        # how do we compare them? (eg, vertices are not sorted)
        for obj in [polymake.Integer(1),
                    polymake.Integer(2**32),
                    polymake.Rational(-3, 5),
                    polymake.VectorInteger([1,2,3]),
                    polymake.VectorRational([1, (2,3), -5])]:

            self.assertEqual(polymake.polymake(obj.sage()), obj)

if __name__ == '__main__':
    unittest.main()
