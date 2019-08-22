from unittest import TestCase

from ..validators import CentroidValidator


class TestLatLngCountryChecker(TestCase):
    def testLatitudeAndLongitude(self):
        countryChecker = CentroidValidator(None, debug=False)
        countryChecker.validateRow({"latitude": "37.12334", "longitude": "122.123213"})
        countryChecker.validateRow({"latitude": "-29.12334", "longitude": "122.123213"})
        countryChecker.validateRow({"latitude": "29.12334", "longitude": "-122.123213"})
        countryChecker.validateRow({"latitude": "-37.12334", "longitude": "-122.123213"})

        with self.assertRaises(AssertionError):
            countryChecker.validateRow({"latitude": "0.0", "longitude": None})

        with self.assertRaises(AssertionError):
            countryChecker.validateRow({"latitude": None, "longitude": "0.0"})

        with self.assertRaises(AssertionError):
            countryChecker.validateRow({"latitude": "37", "longitude": "-122 longitude"})

        with self.assertRaises(AssertionError):
            countryChecker.validateRow({"latitude": "37 lat", "longitude": "-122"})

        with self.assertRaises(AssertionError):
            countryChecker.validateRow({"latitude": "-91", "longitude": "-122"})

        with self.assertRaises(AssertionError):
            countryChecker.validateRow({"latitude": "-89", "longitude": "-181"})
