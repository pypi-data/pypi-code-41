import us
from uszipcode import SearchEngine
from .validator_utils import ValidatorUtils
from ..types import *


class GeoConsistencyValidator:
    zipsearch = SearchEngine(simple_zipcode=True)
    ZIPCODE_NOT_IN_STATE = "ZIPCODE_NOT_IN_STATE"

    @staticmethod
    def getBadGeoConsistencyReason(row, config):
        """
        Return a bad consistency reason if there is one, otherwise return 0
        """
        zipcode, city, state, lat, lng = row["zip"], row["city"], row["state"], row["latitude"], row["longitude"]
        if not GeoConsistencyValidator.zipcodeInsideState(zipcode, state):
            return ValidatorResponse(ValidatorStatus.FAIL, GeoConsistencyValidator.ZIPCODE_NOT_IN_STATE)
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def zipcodeInsideState(zipcode, state):
        if ValidatorUtils.is_blank(zipcode) or ValidatorUtils.is_blank(state):
            return True

        cleanedZipcode = GeoConsistencyValidator.cleanZip(zipcode)
        inferredState = GeoConsistencyValidator.zipsearch.by_zipcode(cleanedZipcode).state
        lookedUp = us.states.lookup(ValidatorUtils.cleanState(state))
        if inferredState and lookedUp:
            if lookedUp.abbr != inferredState:
                return False
            else:
                return True
        return False

    @staticmethod
    def cleanZip(zipcode):
        stripped = zipcode.strip()
        if len(stripped) > 5:
            return stripped[:5]
        return stripped
