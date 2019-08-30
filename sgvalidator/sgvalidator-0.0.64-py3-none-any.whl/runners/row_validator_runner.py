from ..types import ValidatorStatus
from ..decorators import ignorable
from ..validators.validator_utils import ValidatorUtils
from .abstract_runner import AbstractRunner
from ..color_printer import ColorPrinter


class RowValidatorRunner(AbstractRunner):
    REASON_COLNAME = "REASON"
    ROW_NUM_COLNAME = "rowNumber"

    def __init__(self, validatorsToIgnore):
        self.validatorsToIgnore = validatorsToIgnore

    @ignorable
    def run(self, func, data, validatorConfig):
        res = RowValidatorRunner.runFunc(func, data, validatorConfig)
        if len(res) > 0:
            displayColumns = self.getDisplayColumns(validatorConfig)
            debugExamples = self.getDebugExamples(res, displayColumns)
            message = "Found {} concerning rows. Examples:\n{}\n".format(len(res), debugExamples)
            if validatorConfig.isWarnOnly():
                return self.warn(message)
            else:
                return self.failAndPotentiallyExit(message, validatorConfig)
        return ValidatorStatus.SUCCESS

    @staticmethod
    def runFunc(tagger, data, config):
        filteredData = RowValidatorRunner.filterData(data, config)
        if filteredData.empty:
            return []

        reasonSeries = filteredData.apply(lambda row: tagger(row, config).getMessage(), axis=1)
        filteredData[RowValidatorRunner.REASON_COLNAME] = reasonSeries
        return filteredData[~filteredData[RowValidatorRunner.REASON_COLNAME].isnull()]

    @staticmethod
    def getDisplayColumns(validatorConfig):
        displayCols = validatorConfig.getDisplayCols()
        if len(displayCols) == 0:
            return [RowValidatorRunner.ROW_NUM_COLNAME, RowValidatorRunner.REASON_COLNAME]
        return displayCols + [RowValidatorRunner.REASON_COLNAME, RowValidatorRunner.ROW_NUM_COLNAME]

    @staticmethod
    def getDebugExamples(df, displayCols, n=5):
        if displayCols is None:
            debugExamples = df.head(n)
        else:
            debugExamples = df.head(n)[displayCols]
        return debugExamples
