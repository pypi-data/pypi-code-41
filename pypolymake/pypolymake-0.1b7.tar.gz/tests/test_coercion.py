import unittest
import random
import operator

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


class TestCoercion(unittest.TestCase):
    def assertCoerceBinop(self, a, b, res, op):
        ans = op(a, b)
        self.assertEqual(type(ans), type(res))
        self.assertEqual(ans, res)

    def assertCoerceBinopCommutative(self, a, b, res, op):
        self.assertCoerceBinop(a, b, res, op)
        self.assertCoerceBinop(b, a, res, op)

    def randint(self):
        if random.random() < 0.5:
            return random.choice([0, -1, 1, 2**32, -2**32, 2**64, -2**64,
                2**32-1, 2**32+1, -2**32-1, -2**32+1,
                2**64-1, 2**64+1, -2**64-1, -2**64+1])
        else:
            return random.randint(-2**100, 2**100)

    def randint_nonzero(self):
        if random.random() < 0.5:
            return random.choice([-1, 1, 2**32, -2**32, 2**64, -2**64,
                2**32-1, 2**32+1, -2**32-1, -2**32+1,
                2**64-1, 2**64+1, -2**64-1, -2**64+1])
        else:
            z = random.randint(-2**100, 2**100)
            if not z:
                return 1

    def randint_positive(self):
        if random.random() < 0.5:
            return random.choice([1, 2**32, 2**64,
                2**32-1, 2**32+1, 2**64-1, 2**64+1])
        else:
            z = random.randint(1, 2**100)
            if not z:
                return 1

    def test_int_integer(self):
        for _ in range(20):
            a = self.randint()
            b = self.randint()
            c = a + b
            self.assertCoerceBinopCommutative(polymake.Integer(a), b, polymake.Integer(a+b), operator.add)
            self.assertCoerceBinopCommutative(polymake.Integer(a), b, polymake.Integer(a*b), operator.mul)
            self.assertCoerceBinop(polymake.Integer(a), b, polymake.Integer(a-b), operator.sub)
            self.assertCoerceBinop(a, polymake.Integer(b), polymake.Integer(a-b), operator.sub)
            # TODO: not working for negative b
            if a >= 0 and b > 0:
                self.assertCoerceBinop(polymake.Integer(a), b, polymake.Integer(a//b), operator.floordiv)
                self.assertCoerceBinop(a, polymake.Integer(b), polymake.Integer(a//b), operator.floordiv)

    def test_integer_rational(self):
        for _ in range(20):
            a = polymake.Integer(self.randint())
            b = polymake.Rational(self.randint(), self.randint_positive())

            s = polymake.Rational(a*b.denominator() + b.numerator(), b.denominator())
            self.assertCoerceBinopCommutative(a, b, s, operator.add)

            p = polymake.Rational(a * b.numerator(), b.denominator())
            self.assertCoerceBinopCommutative(a, b, p, operator.mul)

            d = polymake.Rational(a*b.denominator() - b.numerator(), b.denominator())
            self.assertCoerceBinop(a, b, d, operator.sub)
            d = polymake.Rational(b.numerator() - a*b.denominator(), b.denominator())
            self.assertCoerceBinop(b, a, d, operator.sub)

    def test_integer_quadratic_extension(self):
        self.assertCoerceBinopCommutative(polymake.Integer(2),
                                          polymake.QuadraticExtension(1,2,3),
                                          polymake.QuadraticExtension(3,2,3),
                                          operator.add)

    def test_rational_quadratic_extension(self):
        self.assertCoerceBinopCommutative(polymake.Rational(2,3),
                         polymake.QuadraticExtension(1,2,3),
                         polymake.QuadraticExtension(polymake.Rational(5,3), 2, 3),
                         operator.add)

    def test_pm_conversion(self):
        from polymake.coercion import as_pm_object
        self.assertEqual(type(as_pm_object(3)), polymake.Integer)
        self.assertEqual(type(as_pm_object(2**100)), polymake.Integer)

if __name__ == '__main__':
    unittest.main()
