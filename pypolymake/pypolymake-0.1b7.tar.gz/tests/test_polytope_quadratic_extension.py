import unittest

# NOTE: apparently this has to be done *before* importing polymake.
# Otherwise it produces segfault...
try:
    import sage.all
    import sage
except:
    sage = None

import polymake

class TestPolytopeQuadraticExtension(unittest.TestCase):
    def test_from_sage(self):
        if sage is None:
            return

        from sage.all import polytopes
        for p_sage in [polytopes.dodecahedron(), polytopes.icosahedron()]:
            p_pm = polymake.polymake(p_sage)
            self.assertEqual(p_pm.F_VECTOR.python(), list(p_sage.f_vector())[1:-1])

if __name__ == '__main__':
    unittest.main()
