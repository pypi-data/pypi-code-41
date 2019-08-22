from unittest import TestCase


from .test_data import TestDataFactory
from ..validators import FillRateValidator

fakeData = TestDataFactory().defaultRowsToPandasDf([
    TestDataFactory().getDefaultRow().copy(hours_of_operation=""),
    TestDataFactory().getDefaultRow().copy(hours_of_operation=""),
    TestDataFactory().getDefaultRow().copy(hours_of_operation=""),
    TestDataFactory().getDefaultRow().copy(),
    TestDataFactory().getDefaultRow().copy(location_type="", hours_of_operation=""),
    TestDataFactory().getDefaultRow().copy(phone="", location_type=""),
    TestDataFactory().getDefaultRow().copy(phone="", hours_of_operation=""),
    TestDataFactory().getDefaultRow().copy(phone=""),
    TestDataFactory().getDefaultRow().copy(phone=""),
    TestDataFactory().getDefaultRow().copy(phone="")
])

fillRateValidator = FillRateValidator(fakeData)


class TestFillRateValidator(TestCase):
    def testFillRateValidator(self):
        percBlankDf = fakeData.apply(lambda x: x == "", axis=0).mean() * 100
        nullCountsByColumn = fillRateValidator.validateInner(percBlankDf, "blank")
        expectedConcerningCols = sorted(["hours_of_operation", "phone"])
        self.assertEqual(sorted(list(nullCountsByColumn.index)), expectedConcerningCols)
