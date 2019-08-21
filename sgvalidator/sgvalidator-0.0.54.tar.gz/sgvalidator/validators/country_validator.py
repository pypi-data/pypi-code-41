from .country_validation_helpers.ca_row_validator import CaRowValidator
from .country_validation_helpers.us_row_validator import UsRowValidator
from ..types import CountryCode
from ..data_preprocessor import DataPreprocessor


class CountryValidator:
    @staticmethod
    def validateCountrySpecificValues(row, config):
        countryCode = row[DataPreprocessor.DETECTED_CC]
        if countryCode == CountryCode.US:
            return UsRowValidator().validate(row)
        elif countryCode == CountryCode.CA:
            return CaRowValidator().validate(row)
        return 0
