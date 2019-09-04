from ..decorators import ignorable
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
