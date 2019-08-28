from .color_printer import ColorPrinter
from .config import validators
from .data_preprocessor import DataPreprocessor
from .types import ValidatorStatus
from .validator_config import ValidatorConfig
from .runners import RunnerFactory


class ValidatorRunner:
    def __init__(self, data, classesToIgnore):
        self.rawData = data
        self.data = DataPreprocessor.preprocess(data)
        self.classesToIgnore = classesToIgnore

    def run(self):
        results = []
        runnerFactory = RunnerFactory(self.classesToIgnore)
        for validator in validators:
            validatorConfig = ValidatorConfig().parse(validator)
            runner = runnerFactory.getRunner(validatorConfig.getValidatorType())
            ColorPrinter.printBlueBanner(validatorConfig.getAnnouncement())
            res = runner.run(validatorConfig.getMethod(), self.data, validatorConfig)
            results.append(res)
            if res == ValidatorStatus.SUCCESS:
                ColorPrinter.printGreenBanner("========== Looks good! ==========")

        numSuccesses = ValidatorRunner.getNumResultsWithStatus(results, ValidatorStatus.SUCCESS)
        numIgnored = ValidatorRunner.getNumResultsWithStatus(results, ValidatorStatus.IGNORED)
        numFailures = ValidatorRunner.getNumResultsWithStatus(results, ValidatorStatus.FAIL)
        numWarnings = ValidatorRunner.getNumResultsWithStatus(results, ValidatorStatus.WARN)
        self.printStatus(numSuccesses, numIgnored, numFailures, numWarnings)
        return numFailures

    @staticmethod
    def printStatus(numSuccesses, numIgnored, numFailures, numWarnings):
        ColorPrinter.printWhiteBanner("\n============= Results =============")
        ColorPrinter.printGreenBanner("======== {} checks passing ========".format(numSuccesses))
        ColorPrinter.printYellowBanner("======== {} checks ignored ========".format(numIgnored))
        ColorPrinter.printCyanBanner("======== {} checks warning ========".format(numWarnings))
        ColorPrinter.printRedBanner("======== {} checks failing ========".format(numFailures))
        ColorPrinter.printWhiteBanner("===================================\n")
        if numFailures > 0:
            ColorPrinter.printYellowBanner("Close! You still have {} check(s) that need to pass.".format(numFailures))
        else:
            ColorPrinter.printGreenBanner("Congratulations! All your checks passed.")

    @staticmethod
    def getNumResultsWithStatus(results, status):
        return len(list(filter(lambda x: x == status, results)))
