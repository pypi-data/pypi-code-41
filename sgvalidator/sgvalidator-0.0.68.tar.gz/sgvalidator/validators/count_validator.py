import os

import numpy as np
import pandas as pd
import pkg_resources
import us

from ..types import *
from ..validators.validator_utils import ValidatorUtils


class CountValidator:
    TOTAL_COUNT_TRUTHSET_PATH = pkg_resources.resource_filename("sgvalidator",
                                                                "validators/data/brand_count_truthset_v2.csv")
    COUNTS_BY_STATE_TRUTHSET_PATH = pkg_resources.resource_filename("sgvalidator",
                                                                    "validators/data/brand_count_by_state_truthset.csv")

    @staticmethod
    def checkForSuspiciousRowCount(data, config):
        multiples = config.getArgs()["MULTIPLES"]
        dataLen = len(data)
        for multiple in multiples:
            if dataLen % multiple == 0:
                message = "WARNING: The number of rows in your data ({}) is a multiple of {}. This is sometimes an " \
                          "indication that you didn't correctly paginate through the results on the store locator, " \
                          "though it could also just be a coincidence. Please review the website once more to make sure" \
                          "you're scraping correctly!".format(dataLen, multiple)
                return ValidatorResponse(ValidatorStatus.FAIL, message)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def getUnexpectedStatesFoundInData(df):
        return df[df["count_expected"].isnull()]["canonicalized_state"].values

    @staticmethod
    def getExpectedStatesNotFoundInData(df):
        return df[df["count_scraped"].isnull()]["canonicalized_state"].values

    @staticmethod
    def getStatesThatDifferSignificantlyByCount(df, config):
        stateCountsToCompare = df[df["count_scraped"].notnull() & df["count_expected"].notnull()]
        idxsWithBigDifferences = stateCountsToCompare.apply(
            lambda x: not CountValidator.isPoiCountWithinRangeOfTruthsetCount(x["count_scraped"], x["count_expected"],
                                                                              config), axis=1)
        return stateCountsToCompare[idxsWithBigDifferences]

    @staticmethod
    def mergePoiCountsWithTruthCounts(poiCountsByState, truthset):
        return pd.merge(poiCountsByState, truthset, how='outer', on='canonicalized_state',
                        suffixes=('_scraped', '_expected'))

    @staticmethod
    def validatePoiCountsByState(data, config):
        truthset = CountValidator.getExpectedCountsByStateFromTruthset()
        if data.empty or truthset.empty:
            return ValidatorResponse(ValidatorStatus.SUCCESS)

        truthsetCleaned = CountValidator.cleanStateAndFilterMissing(truthset)
        poiCountsByState = CountValidator.getPoiCountsByState(data)

        merged = CountValidator.mergePoiCountsWithTruthCounts(poiCountsByState, truthsetCleaned)
        unexpectedStatesFoundInData = CountValidator.getUnexpectedStatesFoundInData(merged)
        expectedStatesNotFoundInData = CountValidator.getExpectedStatesNotFoundInData(merged)
        statesWithBigDifferences = CountValidator.getStatesThatDifferSignificantlyByCount(merged, config)
        if not statesWithBigDifferences.empty or len(unexpectedStatesFoundInData) > 0 \
                or len(expectedStatesNotFoundInData) > 0:
            debugExamples = statesWithBigDifferences[["count_expected", "count_scraped", "canonicalized_state"]]\
                .rename({"count_expected": "expected_cnt",
                         "count_scraped": "your_cnt",
                         "canonicalized_state": "state"}, axis=1).head(5)
            message = "When we looked at the number of POI in your data by state, we noticed large differences " \
                      "for {} states in total. This might be because you incorrectly scraped data for these states " \
                      "(though it might also indicate an issue with our truthset or with differences in how we " \
                      "format states. Below are a handful of state for which we noticed issues. Go back to the " \
                      "store locator to ensure you're scraping the correct number of locations. If you think that " \
                      "this is a problem with our truthset or validation code, ignore this check and " \
                      "write down your reasoning for skipping the check in your README.\n" \
                .format(len(statesWithBigDifferences))

            if not statesWithBigDifferences.empty:
                message = message + "\nExample of states in your data that overlap with our truthset but which have " \
                                    "significant differences in counts:\n{}\n".format(debugExamples)

            if len(unexpectedStatesFoundInData) > 0:
                message = message + "\nExamples of states that we saw in your data but didn't expect to see: {}." \
                    .format(unexpectedStatesFoundInData[:5])

            if len(expectedStatesNotFoundInData) > 0:
                message = message + "\nExamples of states that we expected to see in your data but didn't: {}." \
                    .format(expectedStatesNotFoundInData[:5])
            return ValidatorResponse(ValidatorStatus.FAIL, message)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def getPoiCountsByState(data):
        cleanedAndFiltered = CountValidator.cleanStateAndFilterMissing(data)
        valueCounts = cleanedAndFiltered["canonicalized_state"].value_counts()
        return pd.DataFrame(valueCounts).reset_index().rename({"index": "canonicalized_state",
                                                               "canonicalized_state": "count"}, axis=1)

    @staticmethod
    def cleanStateAndFilterMissing(data):
        data["canonicalized_state"] = data["state"].apply(CountValidator.getCanonicalizedState)
        return data[data["canonicalized_state"].apply(lambda s: s is not None)]

    @staticmethod
    def getCanonicalizedState(state):
        if state is None:
            return None
        cleaned = ValidatorUtils.cleanState(state)
        res = us.states.lookup(cleaned)
        if res:
            return res.abbr
        return None

    @staticmethod
    def validatePoiCountAgainstTruthsetCount(data, config):
        poiCount = len(data)
        trueCount = CountValidator.getExpectedCountFromTruthset()
        if trueCount and not CountValidator.isPoiCountWithinRangeOfTruthsetCount(poiCount, trueCount, config):
            message = "We think there should be around {} POI, but your file has {} POI. " \
                      "Are you sure you scraped correctly?".format(trueCount, poiCount)
            return ValidatorResponse(ValidatorStatus.FAIL, message)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def getExpectedCountsByStateFromTruthset(domain=None):
        truthset = CountValidator.loadTruthset(CountValidator.COUNTS_BY_STATE_TRUTHSET_PATH)
        if not domain:
            domain = CountValidator.getDomain()
        else:
            domain = domain
        return truthset[(truthset["website"] == domain) & (truthset["state"].str.len() > 0)]

    @staticmethod
    def getExpectedCountFromTruthset(domain=None):
        truthset = CountValidator.loadTruthset(CountValidator.TOTAL_COUNT_TRUTHSET_PATH)
        if not domain:
            domain = CountValidator.getDomain()
        else:
            domain = domain

        res = truthset[truthset["domain"] == domain]["raw_count"]
        if len(res) == 0:
            return None
        elif len(res) == 1:
            return res.item()
        elif len(res) == 2:  # if we have counts from both mobius and mozenda
            return res.mean()

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
    def loadTruthset(path):
        return pd.read_csv(path)
