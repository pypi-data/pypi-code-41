from .country_validation_helpers.ca_row_validator import CaRowValidator
from .country_validation_helpers.us_row_validator import UsRowValidator
from ..data_preprocessor import DataPreprocessor
from ..types import *


class CountryValidator:
    @staticmethod
    def validateCountrySpecificValues(row, config):
        countryCode = row[DataPreprocessor.DETECTED_CC]
        if countryCode == CountryCode.US:
            return UsRowValidator().validate(row)
        elif countryCode == CountryCode.CA:
            return CaRowValidator().validate(row)
        return ValidatorResponse(ValidatorStatus.SUCCESS)
