from .validator_utils import ValidatorUtils
from ..types import *

class BadCentroidTagger:
    EITHER_LAT_OR_LNG_IS_EMPTY = "EITHER_LAT_OR_LNG_EMPTY"
    EITHER_LAT_OR_LNG_NON_NUMERIC = "EITHER_LAT_OR_LNG_NON_NUMERIC"
    EITHER_LAT_OR_LNG_IS_OUTSIDE_OF_RANGE = "EITHER_LAT_OR_LNG_OUTSIDE_OF_RANGE"
    EITHER_LAT_OR_LNG_IS_IMPRECISE = "EITHER_LAT_OR_LNG_IMPRECISE"

    @staticmethod
    def tag(row, config):
        latitude, longitude = row["latitude"], row["longitude"]
        if BadCentroidTagger.bothBlank(latitude, longitude):
            return ValidatorResponse(ValidatorStatus.SUCCESS)
        elif BadCentroidTagger.eitherLatOrLngIsEmptyButNotBoth(latitude, longitude):
            return ValidatorResponse(ValidatorStatus.FAIL, BadCentroidTagger.EITHER_LAT_OR_LNG_IS_EMPTY)
        elif BadCentroidTagger.eitherNonNumeric(latitude, longitude):
            return ValidatorResponse(ValidatorStatus.FAIL, BadCentroidTagger.EITHER_LAT_OR_LNG_NON_NUMERIC)
        elif BadCentroidTagger.eitherOutsideOfRange(latitude, longitude):
            return ValidatorResponse(ValidatorStatus.FAIL, BadCentroidTagger.EITHER_LAT_OR_LNG_IS_OUTSIDE_OF_RANGE)
        elif BadCentroidTagger.eitherImprecise(latitude, longitude,
                                               config.getArgs()["MINIMUM_NUMBER_SIGNIFICANT_DIGITS_FOR_LAT_LNG"]):
            return ValidatorResponse(ValidatorStatus.FAIL, BadCentroidTagger.EITHER_LAT_OR_LNG_IS_IMPRECISE)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def eitherImprecise(latitude, longitude, MINIMUM_NUMBER_SIGNIFICANT_DIGITS_FOR_LAT_LNG):
        return not BadCentroidTagger.isPreciseEnough(latitude, MINIMUM_NUMBER_SIGNIFICANT_DIGITS_FOR_LAT_LNG) \
               or not BadCentroidTagger.isPreciseEnough(longitude, MINIMUM_NUMBER_SIGNIFICANT_DIGITS_FOR_LAT_LNG)

    @staticmethod
    def isPreciseEnough(val, MINIMUM_NUMBER_SIGNIFICANT_DIGITS_FOR_LAT_LNG):
        splitted = str(val).split(".")
        if len(splitted) == 1:
            return False
        else:
            numSigfigs = len(splitted[1])
            return numSigfigs >= MINIMUM_NUMBER_SIGNIFICANT_DIGITS_FOR_LAT_LNG

    @staticmethod
    def bothBlank(latitude, longitude):
        return ValidatorUtils.is_blank(latitude) and ValidatorUtils.is_blank(longitude)

    @staticmethod
    def eitherLatOrLngIsEmptyButNotBoth(latitude, longitude):
        return (ValidatorUtils.is_blank(latitude) and ValidatorUtils.is_not_blank(longitude)) or \
               (ValidatorUtils.is_not_blank(latitude) and ValidatorUtils.is_blank(longitude))

    @staticmethod
    def eitherOutsideOfRange(latitude, longitude):
        return not (-90.0 <= float(latitude) <= 90.0) or not (-180.0 <= float(longitude) <= 180.0)

    @staticmethod
    def eitherNonNumeric(latitude, longitude):
        return not ValidatorUtils.is_number(longitude) or not ValidatorUtils.is_number(latitude)
