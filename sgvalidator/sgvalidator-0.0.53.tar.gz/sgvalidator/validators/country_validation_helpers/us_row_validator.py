import us

from .abstract_country_validator import AbstractCountryValidator
from .country_detector import CountryDetector
from ..validator_utils import ValidatorUtils


class UsRowValidator(AbstractCountryValidator):
    def __init__(self):
        pass

    def validate(self, row):
        res1 = self.validateZip(row)
        res2 = self.validateState(row)
        res3 = self.validatePhone(row)
        if res1 != 0:
            return res1
        elif res2 != 0:
            return res2
        elif res3 != 0:
            return res3
        return 0

    def validateState(self, row):
        state = row["state"]
        if not ValidatorUtils.is_blank(state) and not us.states.lookup(state.strip()):
            # ValidatorUtils.fail("Invalid state: {}".format(state))
            return "INVALID_US_STATE"
        return 0

    def validateZip(self, row):
        zip_code = row["zip"]
        if ValidatorUtils.is_not_blank(zip_code) and not CountryDetector.isUsZip(zip_code):
            # ValidatorUtils.fail("Invalid zip code: {}".format(zip_code))
            return "INVALID_US_ZIP"
        return 0

    def validatePhone(self, row):
        phone = row["phone"]
        if not ValidatorUtils.is_blank(phone) and not ValidatorUtils.is_valid_phone_number(phone, "US"):
            # ValidatorUtils.fail("Invalid phone number: {}".format(phone))
            return "INVALID_US_PHONE"
        return 0
