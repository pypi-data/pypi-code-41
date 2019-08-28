import us

from .abstract_country_validator import AbstractCountryValidator
from .country_detector import CountryDetector
from ..validator_utils import ValidatorUtils
from ...types import *


class UsRowValidator(AbstractCountryValidator):
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
        # todo - make a clean state method
        if not ValidatorUtils.is_blank(state) and not us.states.lookup(ValidatorUtils.cleanState(state)):
            return ValidatorResponse(ValidatorStatus.FAIL, "INVALID_US_STATE")
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    def validateZip(self, row):
        zip_code = row["zip"]
        if ValidatorUtils.is_not_blank(zip_code) and not CountryDetector.isUsZip(zip_code):
            return ValidatorResponse(ValidatorStatus.FAIL, "INVALID_US_ZIP")
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    def validatePhone(self, row):
        phone = row["phone"]
        if not ValidatorUtils.is_blank(phone) and not ValidatorUtils.is_valid_phone_number(phone, "US"):
            return ValidatorResponse(ValidatorStatus.FAIL, "INVALID_US_PHONE")
        return ValidatorResponse(ValidatorStatus.SUCCESS)
