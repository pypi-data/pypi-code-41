from ..types import ValidatorTypes
from . import ColumnValidatorRunner
from . import RowValidatorRunner
from . import DataframeValidatorRunner


class RunnerFactory:
    def __init__(self, classesToIgnore):
        self.classesToIngore = classesToIgnore

    def getRunner(self, validatorType):
        if validatorType == ValidatorTypes.ROW_VALIDATOR:
            return RowValidatorRunner(self.classesToIngore)
        elif validatorType == ValidatorTypes.COLUMN_VALIDATOR:
            return ColumnValidatorRunner(self.classesToIngore)
        elif validatorType == ValidatorTypes.DATAFRAME_VALIDATOR:
            return DataframeValidatorRunner(self.classesToIngore)
        else:
            print("Shouldn't have to get a runner for {}".format(validatorType))
            exit(0)
