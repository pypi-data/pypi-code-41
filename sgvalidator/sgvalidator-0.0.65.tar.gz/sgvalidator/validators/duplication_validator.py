from ..types import *
from .validator_utils import ValidatorUtils


class DuplicationValidator:
    @staticmethod
    def validateIdentityDuplicates(data, config):
        duplicateRows = DuplicationValidator.getDuplicateRows(data, config.getArgs()["IDENTITY_KEYS"])
        debugExamples = duplicateRows[config.getArgs()["IDENTITY_KEYS"]].head(5)
        if len(duplicateRows) > 0:
            message = "Found {} duplicate rows in the data. Each example below is a row that exists at least " \
                      "twice in the dataset:\n{}\n".format(len(duplicateRows), debugExamples)
            return ValidatorResponse(ValidatorStatus.FAIL, message)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def validateLatLngDuplicates(data, config):
        resUnfiltered = data.groupby(["latitude", "longitude"])["street_address"].apply(set).reset_index()
        resUnfiltered["num_addrs"] = resUnfiltered["street_address"].apply(len)
        blankMask = resUnfiltered["latitude"].apply(ValidatorUtils.is_not_blank) & resUnfiltered["longitude"] \
            .apply(ValidatorUtils.is_not_blank)
        res = resUnfiltered[blankMask & (resUnfiltered["num_addrs"] > 1)].sort_values("num_addrs", ascending=False)
        if len(res) > 0:
            message = "Found {} <lat, lng> pair(s) that belong to multiple addresses. Examples:\n{}\n"\
                .format(len(res), res.head(10))
            return ValidatorResponse(ValidatorStatus.FAIL, message)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def getAddrsWithMultipleLatLngs(data, config):
        data = data.loc[(data["street_address"] != "<MISSING>") & (data["street_address"] != "<INACCESSIBLE>")]
        resUnfiltered = data.groupby(["street_address"])[["latitude", "longitude"]].nunique().reset_index()
        res = resUnfiltered[(resUnfiltered["latitude"] > 1) | (resUnfiltered["longitude"] > 1)] \
            .sort_values("latitude", ascending=False) \
            .rename({"latitude": "same_lat_count", "longitude": "same_lng_count"}, axis="columns")
        if len(res) > 0:
            message = "WARNING: We found {} cases where a single address has multiple <lat, lngs>. Are you sure you" \
                      " scraped correctly? Examples:\n{}\n".format(len(res), res.head(10))
            return ValidatorResponse(ValidatorStatus.FAIL, message)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def getDuplicateRows(df, keys):
        return df[df.duplicated(subset=keys)]
