from ..types import ValidatorStatus
from ..color_printer import ColorPrinter
from ..decorators import ignorable
from ..validators.validator_utils import ValidatorUtils
from .abstract_runner import AbstractRunner


class DataframeValidatorRunner(AbstractRunner):
    def __init__(self, validatorsToIgnore):
        self.validatorsToIgnore = validatorsToIgnore

    @ignorable
    def run(self, func, data, validatorConfig):
        validatorResponse = DataframeValidatorRunner.validateData(func, data, validatorConfig)
        return self.handleResponse(validatorResponse, validatorConfig)

    @staticmethod
    def validateData(func, data, config):
        filteredData = DataframeValidatorRunner.filterData(data, config)
        return func(filteredData, config)
