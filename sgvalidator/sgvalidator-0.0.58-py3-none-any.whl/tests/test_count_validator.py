import pandas as pd
from .test_data import getFakeData
from unittest import TestCase

from ..validators import CountValidator
data = pd.DataFrame(getFakeData())
countValidator = CountValidator(data)


class TestCountValidation(TestCase):
    def testCountValidation(self):
        self.assertTrue(countValidator.isPoiCountWithinRangeOfTruthsetCount(123, 128))
        self.assertTrue(countValidator.isPoiCountWithinRangeOfTruthsetCount(10, 15))
        self.assertTrue(countValidator.isPoiCountWithinRangeOfTruthsetCount(1, 2))
        self.assertTrue(countValidator.isPoiCountWithinRangeOfTruthsetCount(550, 500))
        self.assertTrue(countValidator.isPoiCountWithinRangeOfTruthsetCount(100, 93))

        self.assertFalse(countValidator.isPoiCountWithinRangeOfTruthsetCount(100, 90))
        self.assertFalse(countValidator.isPoiCountWithinRangeOfTruthsetCount(121, 136))
        self.assertFalse(countValidator.isPoiCountWithinRangeOfTruthsetCount(500, 340))
        self.assertFalse(countValidator.isPoiCountWithinRangeOfTruthsetCount(10, 20))
        self.assertFalse(countValidator.isPoiCountWithinRangeOfTruthsetCount(10, 16))
        self.assertFalse(countValidator.isPoiCountWithinRangeOfTruthsetCount(8, 14))
        self.assertFalse(countValidator.isPoiCountWithinRangeOfTruthsetCount(571, 500))

    def testGetPoiCountAndRawCount(self):
        poiCount, rawCount = countValidator.getPoiCountAndRawCount(domain="1stcb.com")
        self.assertTrue(poiCount == 8)
        self.assertTrue(rawCount == 317)

        poiCount, rawCount = countValidator.getPoiCountAndRawCount(domain="advantage.com")
        self.assertTrue(poiCount == 8)
        self.assertTrue(rawCount == 19)

        self.assertTrue(countValidator.getPoiCountAndRawCount(domain="fakedomain.com") == (8, None))

    def testCountValidationAcrossCounties(self):
        newData = pd.DataFrame(getFakeData('sample_data_half_us_half_ca.csv'))
        self.assertTrue(len(newData) == 13)
        cntValidator2 = CountValidator(newData, False)
        self.assertTrue(len(cntValidator2.data) == 13)
        filtered = cntValidator2.filterToUsOnly()
        self.assertTrue(len(filtered) == 8)
