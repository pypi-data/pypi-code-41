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

try:
    import gmpy2
except ImportError:
    gmpy2 = None

class TestQuadraticExtension(unittest.TestCase):
    def random(self, r=None):
        anum = random.randint(-10, 10)
        aden = random.randint(1, 10)
        a = polymake.Rational(anum, aden)
        bnum = random.randint(-10, 10)
        bden = random.randint(1, 10)
        b = polymake.Rational(bnum, bden)

        if r is None:
            rnum = random.randint(1, 100)
            rden = random.randint(1, 100)
            r = polymake.Rational(rnum, rden)

        return polymake.QuadraticExtension(a, b, r)

    def test_cmp(self):
        self.assertEqual(polymake.QuadraticExtension(1,1,5), polymake.QuadraticExtension(1,1,5))
        self.assertNotEqual(polymake.QuadraticExtension(1,1,5), polymake.QuadraticExtension(-1,1,5))
        self.assertNotEqual(polymake.QuadraticExtension(1,1,5), polymake.QuadraticExtension(1,-1,5))
        self.assertNotEqual(polymake.QuadraticExtension(0,1,3), polymake.QuadraticExtension(0,1,5))

    def test_idempotent(self):
        for a,b,r in [(1,2,3),(3,0,3),(0,3,0),(1,1,1),(2,2,2)]:
            z = polymake.QuadraticExtension(a,b,r)
            self.assertEqual(polymake.QuadraticExtension(z),  z)

    def test_with_sage_input(self):
        if sage is None:
            return

        from sage.all import Integer, Rational

        self.assertEqual(polymake.QuadraticExtension(Integer(1), Integer(1), Integer(5)),
                         polymake.QuadraticExtension(1, 1, 5))
        self.assertEqual(polymake.QuadraticExtension(Rational((2,3)), Rational((-1,3)), Rational((23,7))),
                         polymake.QuadraticExtension(polymake.Rational((2,3)),
                                                     polymake.Rational((-1,3)),
                                                     polymake.Rational((23,7))))
    def test_to_sage(self):
        if sage is None:
            return

        from sage.all import Integer, Rational, QQ, AA, polygen, NumberField, QuadraticField

        z = polymake.QuadraticExtension(2, 3, 5)
        t = z.sage()
        self.assertEqual((t - 2)**2, 45)

        a = polymake.QuadraticExtension(polymake.Rational(2,5),
                                        polymake.Rational(5,7),
                                        polymake.Rational(18,17))
        b = a.sage()
        self.assertEqual((b - QQ((2,5))) * (b - QQ((2,5))), QQ((450, 833)))
    
        # With a number field argument
        x = polygen(QQ)
        b = a.sage(NumberField(2*x**2 - 17, 't'))
        self.assertEqual((b - QQ((2,5))) * (b - QQ((2,5))), QQ((450,833)))
        b = a.sage(NumberField(x**2 + QQ((8,3))*x - QQ((290,9)), 't'))
        self.assertEqual((b - QQ((2,5))) * (b - QQ((2,5))), QQ((450,833)))

        # Check that embedding is taken into account
        a = polymake.QuadraticExtension(polymake.Rational(1,2),
                                        polymake.Rational(1,2),
                                        5)
        K = QuadraticField(5, embedding=AA(5).sqrt())
        self.assertEqual(a.sage(K), (1 + K.gen())/2)
        K = QuadraticField(5, embedding=-AA(5).sqrt())
        self.assertEqual(a.sage(K), (1 - K.gen())/2)

        # Test with rationals
        a = polymake.QuadraticExtension(1, 3, 4)
        self.assertEqual(a.sage(), 7)
        self.assertEqual(type(a.sage()), Rational)
        self.assertEqual(a.sage(QQ), QQ(7))
        a = polymake.QuadraticExtension(1, 0, 5)
        self.assertEqual(a.sage(), QQ(1))
        self.assertEqual(type(a.sage()), Rational)
        self.assertEqual(a.sage(QuadraticField(5)), 1)
        self.assertEqual(type(a.sage(QuadraticField(5))),
                sage.rings.number_field.number_field_element_quadratic.NumberFieldElement_quadratic)

    def test_from_sage(self):
        if sage is None:
            return

        from sage.all import QuadraticField, NumberField, polygen, AA, QQ
        from polymake.sage_conversion import SageQuadraticFieldToPolymake

        K1 = QuadraticField(5, embedding=AA(5).sqrt())
        K2 = QuadraticField(5, embedding=-AA(5).sqrt())

        f1 = SageQuadraticFieldToPolymake(K1)
        f2 = SageQuadraticFieldToPolymake(K2)
        self.assertEqual(f1(K1.gen()), polymake.QuadraticExtension(0,1,5))
        self.assertEqual(f2(K2.gen()), polymake.QuadraticExtension(0,-1,5))

        for _ in range(10):
            a = K1.random_element()
            b = K1.random_element()
            self.assertEqual(f1(a+b), f1(a) + f1(b))
            self.assertEqual(f1(a*b), f1(a) * f1(b))

            a = K2.random_element()
            b = K2.random_element()
            self.assertEqual(f2(a+b), f2(a) + f2(b))
            self.assertEqual(f2(a*b), f2(a) * f2(b))

        x = polygen(QQ)
        K = NumberField(x**2 - x - 1, 'a', embedding=(1 + AA(5).sqrt())/2)
        a = K.gen()
        self.assertEqual(polymake.polymake(a), polymake.QuadraticExtension((1,2),(1,2),5))

        f = SageQuadraticFieldToPolymake(K)
        for _ in range(10):
            a = K.random_element()
            b = K.random_element()
            self.assertEqual(f(a+b), f(a) + f(b))
            self.assertEqual(f(a*b), f(a) * f(b))

    def test_bool(self):
        self.assertTrue(polymake.QuadraticExtension(1))
        self.assertTrue(polymake.QuadraticExtension(0,1,2))
        self.assertFalse(polymake.QuadraticExtension(0))

    def test_init(self):
        self.assertTrue(
                polymake.QuadraticExtension(1) ==
                polymake.QuadraticExtension(1,0,1) ==
                polymake.QuadraticExtension(1,1,0))

        with self.assertRaises(ValueError):
            polymake.QuadraticExtension(1,1,-1)

        self.assertTrue(
                polymake.QuadraticExtension((1,2,5)) ==
                polymake.QuadraticExtension(1, 2, 5))
        self.assertTrue(
                polymake.QuadraticExtension(((1,7), 2, 3)) ==
                polymake.QuadraticExtension(polymake.Rational(1,7), 2, 3))

    def test_abr(self):
        z = polymake.QuadraticExtension(2, 5, 7)
        self.assertEqual(z.a(), 2)
        self.assertEqual(z.b(), 5)
        self.assertEqual(z.r(), 7)

    def test_binop(self):
        # just check that we don't get error
        for _ in range(10):
            z1 = self.random()
            z2 = self.random(r=z1.r())
            z1 + z2
            z1 - z1
            z1 * z2

            z1 + 2
            2 + z1
            2 - z1
            z1 - 2
            z1 * 2
            2 * z1
            z1 / 2
            if z1:
                2 / z1

        with self.assertRaises(ZeroDivisionError):
            z1 / polymake.QuadraticExtension(0)
        with self.assertRaises(ZeroDivisionError):
            z1 / 0

        with self.assertRaises(ValueError):
            polymake.QuadraticExtension(0,1,2) + polymake.QuadraticExtension(0,1,3)
        with self.assertRaises(ValueError):
            polymake.QuadraticExtension(0,1,2) - polymake.QuadraticExtension(0,1,3)
        with self.assertRaises(ValueError):
            polymake.QuadraticExtension(0,1,2) * polymake.QuadraticExtension(0,1,3)
        with self.assertRaises(ValueError):
            polymake.QuadraticExtension(0,1,2) / polymake.QuadraticExtension(0,1,3)

if __name__ == '__main__':
    unittest.main()
