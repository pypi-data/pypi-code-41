from unittest import TestCase
from .test_data import TestDataFactory
from ..validators import CentroidValidator

dataWithBadCentroids = TestDataFactory().defaultRowsToPandasDf([
    TestDataFactory().getDefaultRow(),
    TestDataFactory().getDefaultRow().copy(latitude=None),
    TestDataFactory().getDefaultRow().copy(latitude="<span>122</span>"),
    TestDataFactory().getDefaultRow().copy(longitude="91213123")
])

centroidValidator = CentroidValidator(dataWithBadCentroids)


class TestCentroidValidator(TestCase):
    def testEitherLatOrLngIsEmptyButNotBoth(self):
        self.assertFalse(centroidValidator.eitherLatOrLngIsEmptyButNotBoth(None, None))
        self.assertTrue(centroidValidator.eitherLatOrLngIsEmptyButNotBoth("1,0", None))
        self.assertTrue(centroidValidator.eitherLatOrLngIsEmptyButNotBoth(None, "1.0"))
        self.assertFalse(centroidValidator.eitherLatOrLngIsEmptyButNotBoth("1.0", "1.0"))

    def testGetBadCentroidReason(self):
        self.assertTrue(
            centroidValidator.getBadCentroidReason({"latitude": "37.12334", "longitude": "122.123213"}) == 0)
        self.assertTrue(
            centroidValidator.getBadCentroidReason({"latitude": "-29.12334", "longitude": "122.123213"}) == 0)
        self.assertTrue(
            centroidValidator.getBadCentroidReason({"latitude": "29.12334", "longitude": "-122.123213"}) == 0)
        self.assertTrue(
            centroidValidator.getBadCentroidReason({"latitude": "-37.12334", "longitude": "-122.123213"}) == 0)
        self.assertTrue(
            centroidValidator.getBadCentroidReason({"latitude": "-37.12123", "longitude": "-122.12123"}) == 0)

        self.assertTrue(centroidValidator.getBadCentroidReason(
            {"latitude": "-37.12", "longitude": "-122.12"}) == centroidValidator.EITHER_LAT_OR_LNG_IS_IMPRECISE)
        self.assertTrue(centroidValidator.getBadCentroidReason(
            {"latitude": "0.0", "longitude": None}) == centroidValidator.EITHER_LAT_OR_LNG_IS_EMPTY)
        self.assertTrue(centroidValidator.getBadCentroidReason(
            {"latitude": None, "longitude": "0.0"}) == centroidValidator.EITHER_LAT_OR_LNG_IS_EMPTY)
        self.assertTrue(centroidValidator.getBadCentroidReason(
            {"latitude": "37 lat", "longitude": "-122.1234123"}) == centroidValidator.EITHER_LAT_OR_LNG_NON_NUMERIC)
        self.assertTrue(centroidValidator.getBadCentroidReason({"latitude": "-91.1234123",
                                                                "longitude": "-122.12312312"}) ==
                        centroidValidator.EITHER_LAT_OR_LNG_IS_OUTSIDE_OF_RANGE)
        self.assertTrue(centroidValidator.getBadCentroidReason({"latitude": "-89.123123123",
                                                                "longitude": "-181.123123"}) ==
                        centroidValidator.EITHER_LAT_OR_LNG_IS_OUTSIDE_OF_RANGE)

    def testGetRowsWithBadCentroids(self):
        rowsWithBadCentroids = centroidValidator.getRowsWithBadCentroids()
        self.assertTrue(len(rowsWithBadCentroids) == 2)
