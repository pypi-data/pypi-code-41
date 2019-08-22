from unittest import TestCase

from sgvalidator.sgvalidator.types.validator_status import ValidatorStatus
from .test_data import TestDataFactory
from ..validators import StoreNumberColumnValidator

dataWithFilledAndUniqueStoreNumbers = TestDataFactory().defaultRowsToPandasDf([
    TestDataFactory().getDefaultRow(),
    TestDataFactory().getDefaultRow().copy(store_number="20"),
    TestDataFactory().getDefaultRow().copy(store_number="30")
])

dataWithPartiallyFilledStoreNumbers = TestDataFactory().defaultRowsToPandasDf([
    TestDataFactory().getDefaultRow(),
    TestDataFactory().getDefaultRow().copy(store_number=""),
    TestDataFactory().getDefaultRow().copy(store_number="30")
])

dataWithDuplicateStoreNumbers = TestDataFactory().defaultRowsToPandasDf([
    TestDataFactory().getDefaultRow().copy(store_number="1"),
    TestDataFactory().getDefaultRow().copy(store_number="1"),
    TestDataFactory().getDefaultRow().copy(store_number="2")
])

dataWithAllNullStoreNumbers = TestDataFactory().defaultRowsToPandasDf([
    TestDataFactory().getDefaultRow().copy(store_number=""),
    TestDataFactory().getDefaultRow().copy(store_number=""),
    TestDataFactory().getDefaultRow().copy(store_number="")
])

validatorWithFilledAndUniqueStoreNumbers = StoreNumberColumnValidator(dataWithFilledAndUniqueStoreNumbers)
validatorWithPartiallyFilledStoreNumbers = StoreNumberColumnValidator(dataWithPartiallyFilledStoreNumbers)
validatorWithDuplicateStoreNumbers = StoreNumberColumnValidator(dataWithDuplicateStoreNumbers)
validatorWithAllNullStoreNumbers = StoreNumberColumnValidator(dataWithAllNullStoreNumbers)


class TestStoreNumberColumnValidator(TestCase):
    def testIsColumnPartiallyFilled(self):
        self.assertFalse(validatorWithFilledAndUniqueStoreNumbers.isColumnPartiallyFilled())
        self.assertFalse(validatorWithAllNullStoreNumbers.isColumnPartiallyFilled())
        self.assertTrue(validatorWithPartiallyFilledStoreNumbers.isColumnPartiallyFilled())

    def testGetDuplicateStoreNumbers(self):
        self.assertTrue(len(validatorWithFilledAndUniqueStoreNumbers.getDuplicateStoreNumbers()) == 0)
        self.assertTrue(len(validatorWithDuplicateStoreNumbers.getDuplicateStoreNumbers()) == 1)

    def testValidate(self):
        validatorWithFilledAndUniqueStoreNumbers.validate()
        validatorWithAllNullStoreNumbers.validate()
        self.assertTrue(ValidatorStatus.FAIL == validatorWithPartiallyFilledStoreNumbers.validate())
        self.assertTrue(ValidatorStatus.FAIL == validatorWithDuplicateStoreNumbers.validate())
