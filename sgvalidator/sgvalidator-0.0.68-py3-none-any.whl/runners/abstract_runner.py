from abc import ABCMeta
from ..data_preprocessor import DataPreprocessor
from ..types import *
from ..validators.validator_utils import ValidatorUtils
from ..color_printer import ColorPrinter


class AbstractRunner:
    __metaclass__ = ABCMeta

    @staticmethod
    def filterData(data, config):
        countryFilter = config.getCountryFilter()
        if data.empty or countryFilter is None:
            return data
        return data.loc[data[DataPreprocessor.DETECTED_CC] == countryFilter].copy()

    @staticmethod
    def handleResponse(validatorResponse, validatorConfig):
        status = validatorResponse.getStatus()
        message = validatorResponse.getMessage()
        if status == ValidatorStatus.FAIL:
            if validatorConfig.isWarnOnly():
                return AbstractRunner.warn(message)
            return AbstractRunner.failAndPotentiallyExit(message, validatorConfig)
        return status

    @staticmethod
    def warn(message):
        ColorPrinter.printYellow(message)
        return ValidatorStatus.WARN

    @staticmethod
    def failAndPotentiallyExit(message, validatorConfig):
        ValidatorUtils.fail(message)
        if validatorConfig.shouldExitAfterFailure():
            exit(0)
        return ValidatorStatus.FAIL
