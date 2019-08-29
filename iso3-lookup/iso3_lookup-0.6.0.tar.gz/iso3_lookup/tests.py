import unittest
from iso3_lookup import get_iso3, get_country


class MyTest(unittest.TestCase):
    def test1(self):
        self.assertEqual(get_country("AFG"), "Afghanistan")

    def test2(self):
        self.assertEqual(get_iso3("Albania"), "ALB")

    def test3(self):
        self.assertRaises(ValueError, get_iso3, "sdfsf")


def run():
    unittest.main()


if __name__ == "__main__":
    run()
