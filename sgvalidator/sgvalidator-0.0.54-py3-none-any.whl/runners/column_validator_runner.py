from ..types import ValidatorStatus
from ..color_printer import ColorPrinter
from ..decorators import ignorable
from ..validators.validator_utils import ValidatorUtils
from .abstract_runner import AbstractRunner


class ColumnValidatorRunner(AbstractRunner):
    def __init__(self, validatorsToIgnore):
        self.validatorsToIgnore = validatorsToIgnore

    @ignorable
    def run(self, func, data, validatorConfig):
        status, message = ColumnValidatorRunner.validateColumns(func, data, validatorConfig)
        if status == ValidatorStatus.FAIL and not validatorConfig.isWarnOnly():
            ValidatorUtils.fail(message)
            if validatorConfig.shouldExitAfterFailure():
                exit(0)
        elif status == ValidatorStatus.FAIL and validatorConfig.isWarnOnly():
            ColorPrinter.printYellow(message)
            return ValidatorStatus.WARN
        return status

    @staticmethod
    def validateColumns(func, data, config):
        filteredData = ColumnValidatorRunner.filterData(data, config)
        for column in config.getColumnsToOperateOn():
            status, message = func(filteredData[column], config)
            if status == ValidatorStatus.FAIL:
                return status, message
        return ValidatorStatus.SUCCESS, None
