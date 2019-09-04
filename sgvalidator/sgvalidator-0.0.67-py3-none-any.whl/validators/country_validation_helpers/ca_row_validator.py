from .abstract_country_validator import AbstractCountryValidator
from .country_detector import CountryDetector
from ..validator_utils import ValidatorUtils
from ...types import *


class CaRowValidator(AbstractCountryValidator):
    def __init__(self):
        pass

    def validate(self, row):
        res1 = self.validateZip(row)
        res2 = self.validateState(row)
        res3 = self.validatePhone(row)
        if res1.getStatus() != ValidatorStatus.SUCCESS:
            return res1
        elif res2.getStatus() != ValidatorStatus.SUCCESS:
            return res2
        elif res3.getStatus() != ValidatorStatus.SUCCESS:
            return res3
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    def validateState(self, row):
        state = row["state"]
        if not ValidatorUtils.is_blank(state) and not CountryDetector.isCaState(state):
            return ValidatorResponse(ValidatorStatus.FAIL, "INVALID_CA_PROVINCE")
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    def validatePhone(self, row):
        phone = row["phone"]
        if not ValidatorUtils.is_blank(phone) and not ValidatorUtils.is_valid_phone_number(phone, "CA"):
            return ValidatorResponse(ValidatorStatus.FAIL, "INVALID_CA_PHONE")
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    def validateZip(self, row):
        zip_code = row["zip"]
        if not ValidatorUtils.is_blank(zip_code) and not CountryDetector.isCaZip(zip_code):
            return ValidatorResponse(ValidatorStatus.FAIL, "INVALID_CA_POSTAL_CODE")
        return ValidatorResponse(ValidatorStatus.SUCCESS)
