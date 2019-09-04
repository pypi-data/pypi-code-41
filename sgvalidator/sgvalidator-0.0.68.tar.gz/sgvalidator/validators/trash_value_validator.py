from ..types import *


class TrashValueValidator:
    @staticmethod
    def findTrashValues(row, config):
        for key, value, in row.items():
            badTokensIncludeFilter = set(filter(lambda x: x in str(value), config.getArgs()["BAD_TOKENS_INCLUDE"]))
            badTokensExcludeFilter = set(filter(lambda x: x in str(value), config.getArgs()["BAD_TOKENS_EXCLUDE"]))
            if len(badTokensIncludeFilter) > 0 and len(badTokensExcludeFilter) == 0:
                return ValidatorResponse(ValidatorStatus.FAIL, TrashValueValidator.getReason(key))
        return ValidatorResponse(ValidatorStatus.SUCCESS)

    @staticmethod
    def getReason(key):
        return key.upper() + "_CONTAINS_GARBAGE_VALUE"
