import unittest
from TriangularNumbers import TriangularNumbers


class TriangularNumbersTest(unittest.TestCase):
    """Triangular numbers tests"""
    def test_calculate_term_(self):
        """Calculate term test"""
        tn = TriangularNumbers()
        res = tn.calculate_term(5)
        self.assertEqual(res, 15)

    def test_about_test(self):
        """About test"""
        tn = TriangularNumbers()
        res = tn.about()
        self.assertTrue(res.startswith("A triangular number"))
