import unittest
from TriangularNumbers import TriangularNumber


class TriangularNumberTest(unittest.TestCase):
    """Triangular numbers tests"""
    def test_calculate_term_(self):
        """Calculate term test"""
        res = TriangularNumber.calculate_term(5)
        self.assertEqual(res, 15)

    def test_about_test(self):
        """About test"""
        res = TriangularNumber.about()
        self.assertTrue(res.startswith("A triangular number"))
