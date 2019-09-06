from unittest import TestCase

from girepo.extractor import calculate_star_per


class TestExtractor(TestCase):

    def test_calculate_star_per(self):
        created_at, updated_at, star_count, day_duration, round_n = \
            ["2014-09-11T17:12:01Z", "2014-09-18T16:12:01Z", 14, 1, 2]
        actual = calculate_star_per(created_at, updated_at, star_count, day_duration, round_n)
        self.assertEqual(2.00, actual)

    def test_calculate_star_per_case_zero_division(self):
        created_at, updated_at, star_count, day_duration, round_n = \
            ["2014-09-18T16:12:01Z", "2014-09-18T16:12:01Z", 0, 1, 2]
        actual = calculate_star_per(created_at, updated_at, star_count, day_duration, round_n)
        self.assertEqual(0.00, actual)

    def test_calculate_star_per_case_same_date(self):
        created_at, updated_at, star_count, day_duration, round_n = \
            ["2014-09-18T16:12:01Z", "2014-09-18T16:12:01Z", 1, 1, 2]
        actual = calculate_star_per(created_at, updated_at, star_count, day_duration, round_n)
        self.assertEqual(1.00, actual)
