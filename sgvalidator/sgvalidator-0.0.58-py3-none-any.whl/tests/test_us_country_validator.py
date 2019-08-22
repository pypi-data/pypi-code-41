from unittest import TestCase

from sgvalidator.sgvalidator.types.validator_status import ValidatorStatus
from ..validators import UsRowValidator

usRowValidator = UsRowValidator()


class TestUsCountryChecker(TestCase):
    def testCheckUsState(self):
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateState({"state": None}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateState({"state": "ca"}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateState({"state": "CA"}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateState({"state": "California"}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateState({"state": "TX"}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateState({"state": "texas"}))

        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validateState({"state": "tsxs"}))
        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validateState({"state": "asds"}))
        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validateState({"state": "cali"}))
        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validateState({"state": "sada"}))

    def testCheckUsZip(self):
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateZip({"zip": "94103"}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateZip({"zip": "94103-1234"}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateZip({"zip": None}))

        # note - currently, this zip code doesn't fail because we're
        # not checking against a database of real US zips
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validateZip({"zip": "00000"}))

        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validateZip({"zip": "9104"}))
        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validateZip({"zip": "910421-1234"}))
        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validateZip({"zip": "342131"}))

    def testCheckUsPhone(self):
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validatePhone({"phone": "2149260428"}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validatePhone({"phone": "+12149260428"}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validatePhone({"phone": None}))
        self.assertTrue(ValidatorStatus.SUCCESS == usRowValidator.validatePhone({"phone": "+1 (214) 926-0428"}))

        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validatePhone({"phone": "960428"}))
        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validatePhone({"phone": "214-926!0428"}))
        self.assertTrue(ValidatorStatus.FAIL == usRowValidator.validatePhone({"phone": "2149260428 null"}))
