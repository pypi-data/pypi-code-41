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
            if displayColumns is None:
                debugExamples = res.head(5)
            else:
                debugExamples = res.head(5)[displayColumns]
            message = "Found {} concerning rows. Examples:\n{}\n".format(len(res), debugExamples)
            if not validatorConfig.isWarnOnly():
                ValidatorUtils.fail(message)
                if validatorConfig.shouldExitAfterFailure():
                    exit(0)
            else:
                ColorPrinter.printYellow(message)
                return ValidatorStatus.WARN
            return ValidatorStatus.FAIL
        return ValidatorStatus.SUCCESS

    @staticmethod
    def runFunc(tagger, data, config):
        filteredData = RowValidatorRunner.filterData(data, config)
        if filteredData.empty:
            return []
        reasonSeries = filteredData.apply(lambda row: tagger(row, config), axis=1)
        filteredData[RowValidatorRunner.REASON_COLNAME] = reasonSeries
        mask = reasonSeries.astype("bool")
        return filteredData[mask]

    @staticmethod
    def getDisplayColumns(validatorConfig):
        displayCols = validatorConfig.getDisplayCols()
        if len(displayCols) == 0:
            return [RowValidatorRunner.ROW_NUM_COLNAME, RowValidatorRunner.REASON_COLNAME]
        return displayCols + [RowValidatorRunner.REASON_COLNAME, RowValidatorRunner.ROW_NUM_COLNAME]
