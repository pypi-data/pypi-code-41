from unittest import TestCase
from ..types import *
import pandas as pd
from .test_utils import getMethodAndValidatorConfigFromName


class TestColumnValidators(TestCase):
    def testCountryCodeFillRateChecker(self):
        method, conf = getMethodAndValidatorConfigFromName("CountryCodeFillRateChecker")
        dfWithGoodFillRate = pd.DataFrame({"DETECTED_CC": ["US"] * 22 + ["<MISSING>"] * 6})
        dfWithBadFillRate = pd.DataFrame({"DETECTED_CC": ["CA"] * 10 + ["<MISSING>"] * 5})
        self.assertTrue(method(dfWithGoodFillRate["DETECTED_CC"], conf).getStatus() == ValidatorStatus.SUCCESS)
        self.assertTrue(method(dfWithBadFillRate["DETECTED_CC"], conf).getStatus() == ValidatorStatus.FAIL)

    def testStoreNumberColumnValidator(self):
        method, conf = getMethodAndValidatorConfigFromName("StoreNumberColumnValidator")
        dfWithGoodStoreNumber1 = pd.DataFrame({"store_number": [1, 2, 3, 4,5, 1231, 12323]})
        dfWithGoodStoreNumber2 = pd.DataFrame({"store_number": ["<MISSING>", "<MISSING>", "<MISSING>", "<MISSING>", "<INACCESSIBLE>"]})
        dfWithBadStoreNumber1 = pd.DataFrame({"store_number": [1, 2, 3, "<MISSING>"]})
        dfWithBadStoreNumber2 = pd.DataFrame({"store_number": [1, 2, 3, 1]})

        self.assertTrue(method(dfWithGoodStoreNumber1["store_number"], conf).getStatus() == ValidatorStatus.SUCCESS)
        self.assertTrue(method(dfWithGoodStoreNumber2["store_number"], conf).getStatus() == ValidatorStatus.SUCCESS)

        self.assertTrue(method(dfWithBadStoreNumber1["store_number"], conf).getStatus() == ValidatorStatus.FAIL)
        self.assertTrue(method(dfWithBadStoreNumber2["store_number"], conf).getStatus() == ValidatorStatus.FAIL)

    def testFillRateValidator(self):
        method, conf = getMethodAndValidatorConfigFromName("FillRateValidator")
        dfGood = pd.DataFrame({"col": ["a"] * 10 + ["<MISSING>"] * 5})
        dfBad1 = pd.DataFrame({"col": ["a"] * 10 + ["<INACCESSIBLE>"] * 7})
        dfBad2 = pd.DataFrame({"col": ["a"] * 0 + ["<MISSING>"] * 5})

        self.assertTrue(method(dfGood["col"], conf).getStatus() == ValidatorStatus.SUCCESS)
        self.assertTrue(method(dfBad1["col"], conf).getStatus() == ValidatorStatus.FAIL)
        self.assertTrue(method(dfBad2["col"], conf).getStatus() == ValidatorStatus.FAIL)
