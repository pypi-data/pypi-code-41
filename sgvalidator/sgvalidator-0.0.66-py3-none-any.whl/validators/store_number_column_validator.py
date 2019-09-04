from ..types import *
from .validator_utils import ValidatorUtils


class StoreNumberColumnValidator:
    @staticmethod
    def validateStoreNumberColumn(series, config):
        if StoreNumberColumnValidator.isColumnPartiallyFilled(series):
            return ValidatorResponse(ValidatorStatus.FAIL, "Store number column is only partially filled. "
                                                           "Please make sure you're capturing store numbers for all "
                                                           "POI on the store locator.")
        elif not StoreNumberColumnValidator.isColumnTotallyBlank(series):
            duplicateStoreNumbers = StoreNumberColumnValidator.getDuplicateStoreNumbers(series)
            if len(duplicateStoreNumbers) > 0:
                return ValidatorResponse(ValidatorStatus.FAIL, "Store number column contains {} duplicates. "
                                                               "Here are a few examples of store numbers which appear "
                                                               "at least twice in your data: {}"
                                         .format(len(duplicateStoreNumbers), duplicateStoreNumbers.unique()[:5]))
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def countNumBlanks(series):
        return series.apply(ValidatorUtils.is_missing_or_inaccessible).sum()

    @staticmethod
    def isColumnTotallyBlank(series):
        return StoreNumberColumnValidator.countNumBlanks(series) == len(series)

    @staticmethod
    def isColumnPartiallyFilled(series):
        return 0 < StoreNumberColumnValidator.countNumBlanks(series) < len(series)

    @staticmethod
    def getDuplicateStoreNumbers(series):
        duplicateRows = StoreNumberColumnValidator.getDuplicateRows(series)
        return duplicateRows

    @staticmethod
    def getDuplicateRows(df):
        return df[df.duplicated()]
