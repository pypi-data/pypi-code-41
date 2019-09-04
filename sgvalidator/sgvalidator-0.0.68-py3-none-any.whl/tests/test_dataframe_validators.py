from unittest import TestCase
from ..types import *
import pandas as pd
import numpy as np
from .test_data_factory import TestDataFactory as tdf
from .test_utils import getMethodAndValidatorConfigFromName
from ..validators import CountValidator


class TestDataframeValidators(TestCase):
    def testSchemaValidator(self):
        method, conf = getMethodAndValidatorConfigFromName("SchemaValidator")
        dfGoodSchema1 = tdf.row().toPdDf()

        dfGoodSchema2 = tdf.row().toPdDf()
        dfGoodSchema2["extra_col"] = "4"

        dfBadSchema1 = tdf.row().toPdDf()
        dfBadSchema1 = dfBadSchema1.rename({"zip": "zip_code"}, axis=1)

        dfBadSchema2 = tdf.row().toPdDf()
        dfBadSchema2 = dfBadSchema2.drop("location_name", axis=1)

        self.assertTrue(method(dfGoodSchema1, conf).getStatus() == ValidatorStatus.SUCCESS)
        self.assertTrue(method(dfGoodSchema2, conf).getStatus() == ValidatorStatus.SUCCESS)
        self.assertTrue(method(dfBadSchema1, conf).getStatus() == ValidatorStatus.FAIL)
        self.assertTrue(method(dfBadSchema2, conf).getStatus() == ValidatorStatus.FAIL)

    def testBlankValueChecker(self):
        method, conf = getMethodAndValidatorConfigFromName("BlankValueChecker")
        goodDf = pd.DataFrame({1: [1, 2, 3], 2: [4, 5, "<MISSING>"]})
        badDf = pd.DataFrame({1: [1, 2, 3, ""], 2: [4, 5, 2, 2]})

        self.assertTrue(method(goodDf, conf).getStatus() == ValidatorStatus.SUCCESS)
        self.assertTrue(method(badDf, conf).getStatus() == ValidatorStatus.FAIL)

    def testCountValidator(self):
        method, conf = getMethodAndValidatorConfigFromName("CountValidator")

        conf.args = {
            "MAXIMUM_COUNT_DIFF_THRESHOLD":  5,
            "MAXIMUM_PERC_DIFF_THRESHOLD": 10.0
        }

        self.assertTrue(CountValidator.isPoiCountWithinRangeOfTruthsetCount(123, 128, conf))
        self.assertTrue(CountValidator.isPoiCountWithinRangeOfTruthsetCount(10, 15, conf))
        self.assertTrue(CountValidator.isPoiCountWithinRangeOfTruthsetCount(1, 2, conf))
        self.assertTrue(CountValidator.isPoiCountWithinRangeOfTruthsetCount(550, 500, conf))
        self.assertTrue(CountValidator.isPoiCountWithinRangeOfTruthsetCount(100, 93, conf))

        self.assertFalse(CountValidator.isPoiCountWithinRangeOfTruthsetCount(100, 90, conf))
        self.assertFalse(CountValidator.isPoiCountWithinRangeOfTruthsetCount(121, 136, conf))
        self.assertFalse(CountValidator.isPoiCountWithinRangeOfTruthsetCount(500, 340, conf))
        self.assertFalse(CountValidator.isPoiCountWithinRangeOfTruthsetCount(10, 20, conf))
        self.assertFalse(CountValidator.isPoiCountWithinRangeOfTruthsetCount(10, 16, conf))
        self.assertFalse(CountValidator.isPoiCountWithinRangeOfTruthsetCount(8, 14, conf))
        self.assertFalse(CountValidator.isPoiCountWithinRangeOfTruthsetCount(571, 500, conf))

        trueCount = CountValidator.getExpectedCountFromTruthset(domain="1stcb.com")
        self.assertTrue(trueCount == 327)

        trueCount = CountValidator.getExpectedCountFromTruthset(domain="advantage.com")
        self.assertTrue(trueCount == 40)

        trueCount = CountValidator.getExpectedCountFromTruthset(domain="fakedomain.com")
        self.assertTrue(trueCount is None)

    def testIdentityDuplicationValidator(self):
        method, conf = getMethodAndValidatorConfigFromName("IdentityDuplicationValidator")
        self.assertTrue(1 == 1)

    def testLatLngDuplicationValidator(self):
        method, conf = getMethodAndValidatorConfigFromName("LatLngDuplicationValidator")

        dfGood = pd.DataFrame({
            "latitude": [1.0, 2.0, 3.0, 7.0],
            "longitude": [1.0, 3.0, 2.0, 1.0],
            "street_address": ["1543 mission", "123 main st", "4532 broadway", "1544 mission"]
        })

        dfBad = pd.DataFrame({
            "latitude": [1.0, 2.0, 3.0, 7.0],
            "longitude": [1.0, 3.0, 2.0, 1.0],
            "street_address": ["1543 mission", "123 main st", "4532 broadway", "1543 mission"]
        })

    def testAddrWithMultipleCoordinatesValidator(self):
        method, conf = getMethodAndValidatorConfigFromName("AddrWithMultipleCoordinatesValidator")
        self.assertTrue(1 == 1)

    def testStrangeRowCountValidator(self):
        method, conf = getMethodAndValidatorConfigFromName("StrangeRowCountValidator")
        self.assertTrue(method(self.getFakeDfWithNRows(10), conf).getStatus() == ValidatorStatus.FAIL)
        self.assertTrue(method(self.getFakeDfWithNRows(50), conf).getStatus() == ValidatorStatus.FAIL)
        self.assertTrue(method(self.getFakeDfWithNRows(80), conf).getStatus() == ValidatorStatus.FAIL)
        self.assertTrue(method(self.getFakeDfWithNRows(123), conf).getStatus() == ValidatorStatus.SUCCESS)
        self.assertTrue(method(self.getFakeDfWithNRows(74), conf).getStatus() == ValidatorStatus.SUCCESS)
        self.assertTrue(method(self.getFakeDfWithNRows(12), conf).getStatus() == ValidatorStatus.SUCCESS)

    def testStateLevelCountValidator(self):
        method, conf = getMethodAndValidatorConfigFromName("StateLevelCountValidator")
        poiAndTruth = pd.DataFrame({
            "canonicalized_state": ["ny", "tx", "ma", "wy"],
            "count_expected": [12, 532, np.nan, 800],
            "count_scraped": [np.nan, 536, 10, 500]
        })

        self.assertTrue(CountValidator.getUnexpectedStatesFoundInData(poiAndTruth) == ["ma"])
        self.assertTrue(CountValidator.getExpectedStatesNotFoundInData(poiAndTruth) == ["ny"])
        self.assertTrue(CountValidator.getStatesThatDifferSignificantlyByCount(poiAndTruth, conf)["canonicalized_state"].values == ["wy"])

        truthSetZumiez = CountValidator.getExpectedCountsByStateFromTruthset(domain="zumiez.com")
        self.assertTrue(len(truthSetZumiez) == 50)
        self.assertTrue(set(truthSetZumiez.columns).difference(["website", "state", "count"]) == set([]))

        truthSetFake = CountValidator.getExpectedCountsByStateFromTruthset(domain="fakedomain.com")
        self.assertTrue(truthSetFake.empty)

    @staticmethod
    def getFakeDfWithNRows(n):
        return pd.DataFrame([[1, 2, 3]] * n)
