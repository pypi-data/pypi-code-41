from unittest import TestCase
from .test_data import TestDataFactory
from ..validators import GeoConsistencyValidator

dataWithInconsistentGeo = TestDataFactory().defaultRowsToPandasDf([
    TestDataFactory().getDefaultRow(),
    TestDataFactory().getDefaultRow().copy(zip="75230", state="CA"),
    TestDataFactory().getDefaultRow().copy(zip="98840", state="WA"),
    TestDataFactory().getDefaultRow().copy(zip="98840", state="OR"),
    TestDataFactory().getDefaultRow().copy(zip="24120", state="VA")
])


geoConsistencyValidator = GeoConsistencyValidator(dataWithInconsistentGeo)


class TestGeoConsistencyValidator(TestCase):
    def testZipcodeInsideState(self):
        self.assertTrue(geoConsistencyValidator.zipcodeInsideState("75230", "TX"))
        self.assertTrue(geoConsistencyValidator.zipcodeInsideState("94103", "CA"))
        self.assertFalse(geoConsistencyValidator.zipcodeInsideState("75230", "AK"))
        self.assertFalse(geoConsistencyValidator.zipcodeInsideState("75230", "CA"))
        self.assertFalse(geoConsistencyValidator.zipcodeInsideState("94103", "NY"))
        self.assertFalse(geoConsistencyValidator.zipcodeInsideState("94103", "DE"))
        self.assertFalse(geoConsistencyValidator.zipcodeInsideState("94103", "MD"))

    def testGetInconsistentGeoRows(self):
        self.assertTrue(len(geoConsistencyValidator.getInconsistentGeoRows()) == 2)
