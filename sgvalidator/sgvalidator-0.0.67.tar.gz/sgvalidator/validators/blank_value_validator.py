from ..types import *


class BlankValueValidator:
    @staticmethod
    def validateBlankValues(data, config):
        numBlankValues = data.apply(BlankValueValidator.rowHasAnyBlankValues, axis=1).sum().sum()
        if numBlankValues > 0:
            message = "Data contains blank values or empty strings. Per the documentation, " \
                      "please use <MISSING> or <INACCESSIBLE> if you can't populate a given cell." \
                      "\nFailing because the remainder of the checks won't be able to complete without this " \
                      "invariant satisfied."
            return ValidatorResponse(ValidatorStatus.FAIL, message)
        return ValidatorResponse(ValidatorStatus.SUCCESS, numBlankValues)

    @staticmethod
    def rowHasAnyBlankValues(row):
        for key, value, in row.items():
            if str(value) == "":
                return True
        return False

