#!/usr/bin/env python

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

class TestPolymakeInteger(unittest.TestCase):
    def test_init(self):
        for a in [-1,0,1, 2**32, 2**32-1, 2**32+1,
                2**64, 2**64-1, 2**64+1, -2**32, -2**32-1, -2**32+1,
                -2**64, -2**64-1, -2**64+1]:
            polymake.Integer(a)

    def test_bool(self):
        self.assertEqual(bool(polymake.Integer(0)), False)
        self.assertEqual(bool(polymake.Integer(1)), True)
        self.assertEqual(bool(polymake.Integer(-1)), True)
        self.assertEqual(bool(polymake.Integer(2)), True)
        self.assertEqual(bool(polymake.Integer(-2)), True)

    def test_idempotent(self):
        for a in [0, -2, 2**100+3]:
            b = polymake.Integer(a)
            self.assertEqual(polymake.Integer(b), b)

    def test_sage(self):
        if sage is None:
            return

        for a in [0, -2, 2**100+3]:
            b1 = polymake.Integer(a).sage()
            b2 = sage.all.Integer(polymake.Integer(a))
            c = sage.all.Integer(a)
            self.assertEqual(type(b1), type(c))
            self.assertEqual(type(b2), type(c))
            self.assertEqual(b1, c)
            self.assertEqual(b2, c)

    def test_gmpy2(self):
        if gmpy2 is None:
            return

        for a in [-2, 2**100+3]:
            b = gmpy2.mpz(polymake.Integer(a))
            c = gmpy2.mpz(a)
            self.assertEqual(type(b), type(c))
            self.assertEqual(b, c)

    def test_index(self):
        self.assertTrue([0,1,5,3][polymake.Integer(2)], 5)

    def test_num_den(self):
        one = polymake.Integer(1)
        for _ in range(10):
            a = polymake.Integer(random.randint(-2**100, 2**100))
            self.assertEqual(a.numerator(), a)
            self.assertEqual(a.denominator(), one)

    def test_int(self):
        for a in [1, -2, 2**100+3]:
            self.assertEqual(int(polymake.Integer(a)), a)

    def test_float(self):
        for a in [0, 1, -4]:
            self.assertEqual(float(polymake.Integer(a)), float(a))

    def test_big(self):
        a = 3**100
        b = polymake.Integer(a)
        self.assertEqual(a, b.__index__())

    def test_pow(self):
        for _ in range(20):
            a = random.randint(-100, 100)
            b = random.randint(0, 10)

            ans = polymake.Integer(a**b)
            self.assertEqual(polymake.Integer(a)**b, ans)
            self.assertEqual(polymake.Integer(a)**polymake.Integer(b), ans)

        with self.assertRaises(ValueError):
            polymake.Integer(2) ** (-3)
        with self.assertRaises(OverflowError):
            polymake.Integer(2) ** (2**100)

    def test_pow_other(self):
        for _ in range(20):
            a = random.randint(-100, 100)
            b = random.randint(0, 10)

            B = [b]
            if sage is not None:
                B.append(sage.all.Integer(b))
            if gmpy2 is not None:
                B.append(gmpy2.mpz(b))

            ans = polymake.Integer(a**b)
            for bb in B:
                self.assertTrue(isinstance(polymake.Integer(a)**bb, polymake.Integer))
                self.assertEqual(polymake.Integer(a)**bb, ans)

        with self.assertRaises(ValueError):
            polymake.Integer(2) ** (-3)
        with self.assertRaises(OverflowError):
            polymake.Integer(2) ** (2**100)


    def test_cmp(self):
        for _ in range(10):
            a = random.randint(-10, 10)
            b = a + random.randint(1, 10)
            pa = polymake.Integer(a)
            pb = polymake.Integer(b)
            self.assertTrue(pa == pa and a == pa and pa == a)
            self.assertTrue(pa != pb and a != pb and pa != b)
            self.assertTrue(pa <  pb and a <  pb and pa <  b)
            self.assertTrue(pa <= pb and a <= pb and pa <= b)

            self.assertTrue(pb >= pa and b >= pa and pb >= a)
            self.assertTrue(pb >  pa and b >  pa and pb >  a)

            self.assertFalse(pa != pa or a != pa or pa != a)
            self.assertFalse(pa == pb or a == pb or pa == b)
            self.assertFalse(pa >= pb or a >= pb or pa >= b)
            self.assertFalse(pa >  pb or a >  pb or pa >  b)

            self.assertFalse(pb <= pa or b <= pa or pb <= a)
            self.assertFalse(pb <  pa or b <  pa or pb <  a)

    def test_cmp_other(self):
        for _ in range(20):
            a = random.randint(-2**100, 2**100)
            b = a + random.randint(1, 2**100)
            pa = polymake.Integer(a)
            pb = polymake.Integer(b)
            A = [a]
            B = [b]
            if sage is not None:
                A.append(sage.all.Integer(a))
                B.append(sage.all.Integer(b))
            if gmpy2 is not None:
                A.append(gmpy2.mpz(a))
                B.append(gmpy2.mpz(b))
            for aa in A:
                self.assertTrue(aa == pa and aa <= pa and pa <= aa and aa >= pa and pa >= aa)
                self.assertFalse(aa != pa or aa < pa or aa > pa)
            for bb in B:
                self.assertTrue(pa < bb and bb > pa and pa != bb and bb != pa)
                self.assertFalse(pa >= bb or bb <= pa or pa == bb or bb == pa)

    def test_binop(self):
        for _ in range(30):
            a = random.randint(-100, 100)
            b = random.randint(-100, 100)
            pa = polymake.Integer(a)
            pb = polymake.Integer(b)

            s = polymake.Integer(a+b)
            p = polymake.Integer(a*b)
            d = polymake.Integer(a-b)
            if b:
                q = polymake.Integer(a // b)
            else:
                q = None

            A = [a]
            B = [b]
            if sage is not None:
                A.append(sage.all.Integer(a))
                B.append(sage.all.Integer(b))
            if gmpy2 is not None:
                A.append(gmpy2.mpz(a))
                B.append(gmpy2.mpz(b))

            # Integer op Integer
            self.assertEqual(pa+pb, s)
            self.assertEqual(pa*pb, p)
            self.assertEqual(pa-pb, d)
            # TODO: don't agree for negative values
            if a >= 0 and b > 0:
                self.assertEqual(pa//pb, q)

            # Integer op int
            for bb in B:
                self.assertEqual(pa+bb, s)
                self.assertEqual(pa*bb, p)
                self.assertEqual(pa-bb, d)
                # TODO: don't agree for negative values
                if a >= 0 and b > 0:
                    self.assertEqual(pa//bb, q)

            # int op Integer
            for aa in A:
                self.assertEqual(aa+pb, s)
                self.assertEqual(aa*pb, p)
                self.assertEqual(aa-pb, d)
                # TODO: don't agree for negative values
                if a >= 0 and b > 0:
                    self.assertEqual(aa//pb, q)

    def test_neg(self):
        for _ in range(10):
            a = random.randint(-10, 10)
            pa = polymake.Integer(a)
            self.assertEqual(-pa, polymake.Integer(-a))

    def test_zero_division(self):
        zeros = [0, polymake.Integer(0), polymake.rational.Rational(0)]
        if sage is not None:
            zeros.append(sage.all.Integer(0))
            zeros.append(sage.all.Rational(0))
        if gmpy2 is not None:
            zeros.append(gmpy2.mpz(0))
            zeros.append(gmpy2.mpq(0))
        rats = [polymake.Integer(0), polymake.Integer(1)]
        if sage is not None:
            rats.append(sage.all.Integer(1))
        for z in zeros:
            for r in rats:
                with self.assertRaises(ZeroDivisionError):
                    r / z
                with self.assertRaises(ZeroDivisionError):
                    r // z

if __name__ == '__main__':
    unittest.main()
