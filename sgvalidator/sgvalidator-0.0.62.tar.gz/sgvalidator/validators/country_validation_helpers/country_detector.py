# -*- coding: utf-8 -*-

import re
import us
from ..validator_utils import ValidatorUtils
from ...types import CountryCode


class CountryDetector:
    CANADA_STATE_VARIATIONS = {'ab', 'alberta', 'bc', 'british columbia', 'mb', 'manitoba', 'nb', 'new brunswick', 'nl',
                               'newfoundland and labrador', 'nt', 'northwest territories', 'ns', 'nova scotia', 'nu',
                               'nunavut', 'on', 'ontario', 'pe', 'prince edward island', 'qc', 'quebec', 'sk',
                               'saskatchewan', 'yt', 'yukon', u'québec', 'newfoundland', 'b.c.'}

    US_COUNTRY_CODE_VARIATIONS = {"us", "usa", "united states", "united states of america"}
    CA_COUNTRY_CODE_VARIATIONS = {"ca", "can", "canada"}

    @staticmethod
    def detect(row):
        state = row["state"]
        zipcode = row["zip"]
        country = row["country_code"]
        inferredCountryCode = CountryDetector.inferCountryCode(country)
        if inferredCountryCode == CountryCode.US or CountryDetector.isUsZip(
                zipcode) or CountryDetector.isUsState(state):
            return CountryCode.US
        elif inferredCountryCode == CountryCode.CA or CountryDetector.isCaZip(
                zipcode) or CountryDetector.isCaState(state):
            return CountryCode.CA
        else:
            return "<MISSING>"

    @staticmethod
    def inferCountryCode(raw_country):
        if ValidatorUtils.is_blank(raw_country):
            return None

        normalized = raw_country.strip().lower()
        if normalized in CountryDetector.US_COUNTRY_CODE_VARIATIONS:
            return CountryCode.US
        elif normalized in CountryDetector.CA_COUNTRY_CODE_VARIATIONS:
            return CountryCode.CA
        return None

    @staticmethod
    def isUsZip(zipcode):
        if ValidatorUtils.is_blank(zipcode):
            return False

        cleaned_zip = str(zipcode).strip()
        firstpart = cleaned_zip.split("-")[0]
        if len(firstpart) == 5 and ValidatorUtils.is_number(firstpart):
            return True
        else:
            return False

    @staticmethod
    def isUsState(state):
        if ValidatorUtils.is_blank(state):
            return False

        cleanedState = state.strip().lower()
        return bool(us.states.lookup(cleanedState))

    @staticmethod
    def isCaZip(zipcode):
        pattern = re.compile("^[ABCEGHJ-NPRSTVXY][0-9][ABCEGHJ-NPRSTV-Z] ?[0-9][ABCEGHJ-NPRSTV-Z][0-9]$")
        return ValidatorUtils.is_not_blank(zipcode) and pattern.match(zipcode.strip())

    @staticmethod
    def isCaState(state):
        if ValidatorUtils.is_blank(state):
            return False

        cleanedState = state.strip().lower()
        return cleanedState in CountryDetector.CANADA_STATE_VARIATIONS
