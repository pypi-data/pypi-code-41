import unittest
import string
from mandarina.randomdata import *


class RandomdataTests(unittest.TestCase):
    def test(self):
        pass

    def test_random_string(self):
        size = random.randint(0, 10 ** 6)
        charset = string.ascii_letters
        random_str = random_string(size)
        # Check if string has the correct size
        self.assertEqual(len(random_str), size)
        # Check if only allowed characters are in the random string
        self.assertTrue(set(random_str) <= set(charset))

    def test_random_datetime(self):
        from_date = datetime.datetime(year=2019, month=7, day=1)
        to_date = datetime.datetime.now()
        random_dt = random_datetime(from_date, to_date)
        self.assertGreaterEqual(random_dt, from_date)
        self.assertLessEqual(random_dt, to_date)
