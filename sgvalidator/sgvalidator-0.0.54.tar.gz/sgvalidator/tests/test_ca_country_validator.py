from unittest import TestCase

from sgvalidator.sgvalidator.types.validator_status import ValidatorStatus
from ..validators import CountryValidator, CountryDetector

country_validator = CountryValidator(None)


class TestCaCountryChecker(TestCase):
    def testCheckCaState(self):
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"zip": None, "phone": None, "state": None}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"zip": None, "phone": None, "state": "ab"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"zip": None, "phone": None, "state": "alberta"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"zip": None, "phone": None, "state": " ALBERTA "},CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"zip": None, "phone": None, "state": "quebec"}, CountryDetector.CA_COUNTRY_CODE))

        self.assertTrue(ValidatorStatus.FAIL == country_validator.validateRow({"zip": None, "phone": None, "state": "alberta!"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.FAIL == country_validator.validateRow({"zip": None, "phone": None, "state": "newfoundland"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.FAIL == country_validator.validateRow({"zip": None, "phone": None, "state": "price edwardsd"}, CountryDetector.CA_COUNTRY_CODE))

    def testCheckCaZip(self):
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"phone": None, "state": None, "zip": "A1A 1A1"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"phone": None, "state": None, "zip": "P0M 0B8"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"phone": None, "state": None, "zip": "L0N 1R0"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"phone": None, "state": None, "zip": None}, CountryDetector.CA_COUNTRY_CODE))

        self.assertTrue(ValidatorStatus.FAIL == country_validator.validateRow({"phone": None, "state": None, "zip": "A1A1A1"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.FAIL == country_validator.validateRow({"phone": None, "state": None, "zip": "O1A 1A1"}, CountryDetector.CA_COUNTRY_CODE))

    def testCheckCaPhone(self):
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"state": None, "zip": None, "phone": "2149260428"},CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"state": None, "zip": None, "phone": "+12149260428"},CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"state": None, "zip": None, "phone": None}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.SUCCESS == country_validator.validateRow({"state": None, "zip": None, "phone": "+1 (214) 926-0428"},CountryDetector.CA_COUNTRY_CODE))

        self.assertTrue(ValidatorStatus.FAIL == country_validator.validateRow({"state": None, "zip": None, "phone": "960428"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.FAIL == country_validator.validateRow({"state": None, "zip": None, "phone": "214-926!0428"}, CountryDetector.CA_COUNTRY_CODE))
        self.assertTrue(ValidatorStatus.FAIL == country_validator.validateRow({"state": None, "zip": None, "phone": "2149260428 null"}, CountryDetector.CA_COUNTRY_CODE))
