import os
import numpy as np
import pandas as pd
import pkg_resources
from ..types import *


class CountValidator:
    MAXIMUM_COUNT_DIFF_THRESHOLD = 5
    MAXIMUM_PERC_DIFF_THRESHOLD = 10.0
    TRUTHSET_PATH = pkg_resources.resource_filename("sgvalidator", "validators/data/brand_count_truthset.csv")

    @staticmethod
    def validatePoiCountAgainstRawCount(data, config):
        poiCount, trueCount = CountValidator.getPoiCountAndRawCount(data)
        if trueCount and not CountValidator.isPoiCountWithinRangeOfTruthsetCount(poiCount, trueCount, config):
            message = "We think there should be around {} POI, but your file has {} POI. " \
                      "Are you sure you scraped correctly?".format(trueCount, poiCount)
            return ValidatorResponse(ValidatorStatus.FAIL, message)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def getPoiCountAndRawCount(data, domain=None):
        truthset = CountValidator.loadTruthset()
        if not domain:
            domain = CountValidator.getDomain()
        else:
            domain = domain

        dataLen = len(data)
        res = truthset[truthset["domain"] == domain]["raw_count"]
        if len(res) == 0:
            return dataLen, None
        elif len(res) == 1:
            return dataLen, res.item()
        elif len(res) == 2:  # if we have counts from both mobius and mozenda
            return dataLen, res.mean()

    @staticmethod
    def isPoiCountWithinRangeOfTruthsetCount(poiCount, rawCount, config):
        MAXIMUM_PERC_DIFF_THRESHOLD = config.getArgs()["MAXIMUM_PERC_DIFF_THRESHOLD"]
        MAXIMUM_COUNT_DIFF_THRESHOLD = config.getArgs()["MAXIMUM_COUNT_DIFF_THRESHOLD"]
        upperPerc = 1.0 + MAXIMUM_PERC_DIFF_THRESHOLD / 100.0
        lowerPerc = 1.0 - MAXIMUM_PERC_DIFF_THRESHOLD / 100.0
        isPoiCountWithinPercRange = int(rawCount * upperPerc) >= poiCount >= int(rawCount * lowerPerc)
        isPoiCountWithinAbsRange = np.abs(poiCount - rawCount) <= MAXIMUM_COUNT_DIFF_THRESHOLD
        return isPoiCountWithinPercRange or isPoiCountWithinAbsRange

    @staticmethod
    def getDomain():
        encodedDomain = os.getcwd().split("/")[-1]
        return encodedDomain.replace("_", ".")

    @staticmethod
    def loadTruthset():
        return pd.read_csv(CountValidator.TRUTHSET_PATH)
