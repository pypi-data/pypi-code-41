from ..types import *
from ..color_printer import ColorPrinter
from ..decorators import ignorable
from ..validators.validator_utils import ValidatorUtils
from .abstract_runner import AbstractRunner


class ColumnValidatorRunner(AbstractRunner):
    def __init__(self, validatorsToIgnore):
        self.validatorsToIgnore = validatorsToIgnore

    @ignorable
    def run(self, func, data, validatorConfig):
        validatorResponse = ColumnValidatorRunner.validateColumns(func, data, validatorConfig)
        return self.handleResponse(validatorResponse, validatorConfig)

    @staticmethod
    def validateColumns(func, data, config):
        filteredData = ColumnValidatorRunner.filterData(data, config)
        for column in config.getColumnsToOperateOn():
            validatorResponse = func(filteredData[column], config)
            if validatorResponse.getStatus() == ValidatorStatus.FAIL:
                return validatorResponse
        return ValidatorResponse(ValidatorStatus.SUCCESS)
