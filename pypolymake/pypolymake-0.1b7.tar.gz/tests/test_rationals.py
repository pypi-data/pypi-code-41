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

class TestPolymakeRational(unittest.TestCase):
    def test_init(self):
        self.assertTrue(polymake.Rational(-2,4) ==
                        polymake.Rational(2,-4) ==
                        polymake.Rational(-1,2) ==
                        polymake.Rational(1,-2))

        with self.assertRaises(ValueError):
             polymake.Rational(0,0)
        with self.assertRaises(ValueError):
            polymake.Rational(2,0)

        for num in [-1, 0, 1, 2**32, 2**32-1, 2**32+1,
                2**64, 2**64-1, 2**64+1]:
            polymake.Rational(num)
            for den in [1, 2**32, 2**32-1, 2**32+1, 2**64, 2**64-1, 2**64+1]:
                polymake.Rational(num, den)

    def test_init_with_sage_input(self):
        if sage is None:
            return

        from sage.all import Integer, Rational
        self.assertEqual(polymake.Rational(Integer(5)), polymake.Rational(5))
        self.assertEqual(polymake.Rational(Rational((2,3))), polymake.Rational(2,3))

    def test_init_with_gmpy2_input(self):
        if gmpy2 is None:
            return

        self.assertEqual(polymake.Rational(gmpy2.mpz(3), gmpy2.mpz(5)), polymake.Rational(3, 5))
        self.assertEqual(polymake.Rational(gmpy2.mpq(3, 4)), polymake.Rational(3, 4))

    def test_bool(self):
        self.assertEqual(bool(polymake.Rational(0,1)), False)
        self.assertEqual(bool(polymake.Rational(1,1)), True)
        self.assertEqual(bool(polymake.Rational(-1,2)), True)
        self.assertEqual(bool(polymake.Rational(2,3)), True)
        self.assertEqual(bool(polymake.Rational(-2,1)), True)

    def test_idempotent(self):
        for a in [(1,3),(0,1),(2**100+1, 3**100-2)]:
            b = polymake.Rational(a)
            self.assertEqual(polymake.Rational(b), b)

    def test_sage(self):
        if sage is None:
            return

        # sage bug...
        #for a in [(-1,3), (2**100,3**60)]:
        for a in [(-1,3)]:
            b = polymake.Rational(a).sage()
            c = sage.all.Rational(a)
            self.assertEqual(type(b), type(c))
            self.assertEqual(b, c)

    def test_gmpy2(self):
        if gmpy2 is None:
            return

        for num, den in [(-1,3), (2**100,3**60)]:
            b = gmpy2.mpq(polymake.Rational(num, den))
            c = gmpy2.mpq(num, den)
            self.assertEqual(type(b), type(c))
            self.assertEqual(b, c)

    def test_big(self):
        num = 2**97 - 1
        den = 3**100 + 1
        a = polymake.Rational(num, den)
        self.assertEqual(a.numerator(), num)
        self.assertEqual(a.denominator(), den)

    def test_num_den(self):
        self.assertEqual(polymake.Rational(2, 5).numerator(), 2)
        self.assertEqual(polymake.Rational(2, 5).denominator(), 5)

    def test_cmp(self):
        a = 2
        b = 3
        pa = polymake.integer.Integer(2)
        pb = polymake.integer.Integer(3)
        qa = polymake.Rational(2)
        qb = polymake.Rational(3)
        self.assertTrue(qa == qa and pa == qa and qa == pa and qa == a and a == qa)

        self.assertTrue(qa != qb and pa != qb and qa != pb and qa != b and a != qb)
        self.assertTrue(qa <  qb and pa <  qb and qa <  pb and qa <  b and a <  qb)
        self.assertTrue(qa <= qb and pa <= qb and qa <= pb and qa <= b and a <  qb)

        self.assertTrue(qb >= qa and pb >= qa and qb >= pa and qb >= a and b >= qa)
        self.assertTrue(qb >  qa and pb >  qa and qb >  pa and qb >  a and b >= qa)

        self.assertFalse(qa != qa or pa != qa or qa != pa or qa != a or a != qa)

        self.assertFalse(qa == qb or pa == qb or qa == pb or qa == b or a == qb)
        self.assertFalse(qa >= qb or pa >= pb or pa >= pb or qa >= b or a >= qb)
        self.assertFalse(qa >  qb or pa >  pb or pa >  pb or qa >  b or a >  qb)

        self.assertFalse(qb <= qa or pb <= qa or qb <= pa or qb <= a or b <= qa)
        self.assertFalse(qb <  qa or pb <  qa or qb <  pa or qb <  a or b <  qa)

    def test_binop(self):
        a = polymake.Rational(1,2)
        b = polymake.Rational(2,3)
        self.assertTrue(a + b == polymake.Rational(7,6))

        for _ in range(100):
            anum = random.randint(-10,10)
            aden = random.randint(1,10)
            bnum = random.randint(-10,10)
            bden = random.randint(1,10)
            a = polymake.Rational(anum, aden)
            b = polymake.Rational(bnum, bden)
            self.assertTrue(a + b == polymake.Rational(anum*bden + bnum*aden, aden*bden))
            self.assertTrue(a - b == polymake.Rational(anum*bden - bnum*aden, aden*bden))
            self.assertTrue(a * b == polymake.Rational(anum*bnum, aden*bden))
            if bnum:
                self.assertTrue(a / b == polymake.Rational(anum*bden, aden*bnum))

            ones = [1, polymake.integer.Integer(1)]
            if sage is not None:
                ones.append(sage.all.Integer(1))
                ones.append(sage.all.Rational(1))
            # Note: gmpy2.mpq seems a bit broken... see also
            # https://trac.sagemath.org/ticket/28394
            # if gmpy2 is not None:
            #     ones.append(gmpy2.mpz(1))
            #     ones.append(gmpy2.mpq(1))
            for o in ones:
                msg = "a = {}  type(o) = {}".format(a, type(o))
                self.assertEqual(a + o, polymake.Rational(anum+aden, aden), msg)
                self.assertEqual(o + a, polymake.Rational(anum+aden, aden), msg)
                self.assertEqual(a - o, polymake.Rational(anum-aden, aden), msg)
                self.assertEqual(o - a, polymake.Rational(aden-anum, aden), msg)
            twos = [2, polymake.integer.Integer(2)]
            for t in twos:
                msg = "a = {}  type(t) = {}".format(a, type(t))
                self.assertEqual(a * t, polymake.Rational(2*anum, aden), msg)
                self.assertEqual(t * a, polymake.Rational(anum*2, aden), msg)
                self.assertEqual(a / t, polymake.Rational(anum, aden*2), msg)
                if anum:
                    self.assertTrue(t / a == polymake.Rational(2*aden, anum), msg)

    def test_zero_division(self):
        zeros = [0, polymake.integer.Integer(0), polymake.Rational(0)]
        rats = [polymake.Rational(0,1), polymake.Rational(1,1)]
        for z in zeros:
            for r in rats:
                with self.assertRaises(ZeroDivisionError):
                    r / z

if __name__ == '__main__':
    unittest.main()
