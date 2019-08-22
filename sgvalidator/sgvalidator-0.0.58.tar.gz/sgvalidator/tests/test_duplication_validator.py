from unittest import TestCase

import pandas as pd

from sgvalidator.sgvalidator.types.validator_status import ValidatorStatus
from .test_data import getFakeData
from ..validators import DuplicationValidator

data = pd.DataFrame(getFakeData())
debugChecker = DuplicationValidator(data)


class TestDuplicationChecker(TestCase):
    def testCheckIdentityDuplication(self):
        self.assertTrue(len(debugChecker.getIdentityDuplicates() == 3))

    def testCheckLatLngDuplication(self):
        self.assertTrue(len(debugChecker.getAddrsWithMultipleLatLngs() == 1))
        self.assertTrue(ValidatorStatus.FAIL == debugChecker.validate())

    def testWarnIfSameAddrHasMultipleLatLngs(self):
        res = debugChecker.getAddrsWithMultipleLatLngs()
        self.assertTrue(len(res) == 2)
