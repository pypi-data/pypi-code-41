from unittest import TestCase

from ..validators import CountryDetector


class TestCountryDetection(TestCase):
    def testInferCountryCode(self):
        self.assertTrue(CountryDetector.inferCountryCode("US") == CountryDetector.US_COUNTRY_CODE)
        self.assertTrue(CountryDetector.inferCountryCode("united states") == CountryDetector.US_COUNTRY_CODE)

        self.assertTrue(CountryDetector.inferCountryCode("CA") == CountryDetector.CA_COUNTRY_CODE)
        self.assertTrue(CountryDetector.inferCountryCode("can") == CountryDetector.CA_COUNTRY_CODE)

        self.assertTrue(CountryDetector.inferCountryCode("") == None)
        self.assertTrue(CountryDetector.inferCountryCode(None) == None)
        self.assertTrue(CountryDetector.inferCountryCode("Fake  ") == None)

    def testIsUsZip(self):
        self.assertTrue(CountryDetector.isUsZip("94103"))
        self.assertTrue(CountryDetector.isUsZip("94103-1234"))
        self.assertTrue(CountryDetector.isUsZip("00000"))

        self.assertFalse(CountryDetector.isUsZip("9104"))
        self.assertFalse(CountryDetector.isUsZip(None))
        self.assertFalse(CountryDetector.isUsZip("910421-1234"))
        self.assertFalse(CountryDetector.isUsZip("342131"))

    def testIsCountry(self):
        self.assertTrue(CountryDetector.US_COUNTRY_CODE == CountryDetector.detect(
            {"country_code": "united states", "state": None, "zip": None}))
        self.assertTrue(CountryDetector.US_COUNTRY_CODE == CountryDetector.detect(
            {"country_code": None, "state": None, "zip": "12345"}))
        self.assertTrue(CountryDetector.US_COUNTRY_CODE == CountryDetector.detect(
            {"country_code": None, "zip": None, "state": "tx"}))

        self.assertIsNone(CountryDetector.detect(
            {"country_code": None, "zip": "67J 3J7", "state": "Ont"}))

        self.assertTrue(CountryDetector.CA_COUNTRY_CODE == CountryDetector.detect(
            {"country_code": "can", "state": None, "zip": None}))
        self.assertTrue(CountryDetector.CA_COUNTRY_CODE == CountryDetector.detect(
            {"country_code": None, "state": None, "zip": "A1A 1A1"}))
        self.assertTrue(CountryDetector.CA_COUNTRY_CODE == CountryDetector.detect(
            {"country_code": None, "zip": None, "state": "ab"}))
