from .color_printer import ColorPrinter
from .types import ValidatorTypes


class ValidatorConfig:
    def __init__(self, name=None, announcement=None, ignorable=None, validatorType=None, exitAfterFailure=None,
                 displayCols=None, countryFilter=None, method=None, columnsToOperateOn=None, apology=None,
                 warnOnly=None, args=None):
        self.name = name
        self.announcement = announcement
        self.ignorable = ignorable
        self.validatorType = validatorType
        self.exitAfterFailure = exitAfterFailure
        self.displayCols = displayCols
        self.countryFilter = countryFilter
        self.method = method
        self.columnsToOperateOn = columnsToOperateOn
        self.apology = apology
        self.warnOnly = warnOnly
        self.args = args

    def parse(self, configDict):
        self.name = self.getArgIfExists(configDict, "name")
        self.announcement = self.getArgIfExists(configDict, "announcement")
        self.ignorable = self.getArgIfExists(configDict, "ignorable")
        self.validatorType = self.getArgIfExists(configDict, "validatorType")
        self.exitAfterFailure = self.getArgIfExists(configDict, "exitAfterFailure")
        self.displayCols = self.getArgIfExists(configDict, "displayCols")
        self.countryFilter = self.getArgIfExists(configDict, "countryFilter")
        self.method = self.getArgIfExists(configDict, "method")
        self.columnsToOperateOn = self.getArgIfExists(configDict, "columnsToOperateOn")
        self.apology = self.getArgIfExists(configDict, "apology")
        self.warnOnly = self.getArgIfExists(configDict, "warnOnly")
        self.args = self.getArgIfExists(configDict, "args")
        self.validateConfig()
        return self

    @staticmethod
    def getArgIfExists(configDict, key):
        return configDict.get(key, None)

    def validateConfig(self):
        if self.name is None:
            ColorPrinter.printRedBanner("You need to specify a name argument for all configs!")
            exit(0)
        elif self.announcement is None:
            ColorPrinter.printRedBanner("You need to specify an announcement argument for config: {}!".format(self.name))
            exit(0)
        elif self.validatorType is None:
            ColorPrinter.printRedBanner("You need to specify a validatorType argument for all configs: {}!".format(self.name))
            exit(0)
        elif self.method is None:
            ColorPrinter.printRedBanner("You need to specify a method argument for all configs: {}!".format(self.name))
            exit(0)
        elif self.validatorType == ValidatorTypes.COLUMN_VALIDATOR and self.columnsToOperateOn is None:
            ColorPrinter.printRedBanner("You need to specify a columnsToOperateOn argument for config {} because it's"
                                        " a column validator.".format(self.name))
            exit(0)
        elif self.warnOnly is True and self.ignorable is True:
            ColorPrinter.printRedBanner("You specified wanrOnly=True and ignorable=True in the same config. "
                                        "Please resolve.")
            exit(0)

    def isIgnorable(self):
        return self.ignorable is True

    def isWarnOnly(self):
        return self.warnOnly is True

    def getName(self):
        return self.name

    def getMethod(self):
        return self.method

    def getArgs(self):
        return self.args

    def getApology(self):
        return self.apology

    def getColumnsToOperateOn(self):
        return self.columnsToOperateOn

    def shouldExitAfterFailure(self):
        return self.exitAfterFailure is True

    def getCountryFilter(self):
        return self.countryFilter

    def getDisplayCols(self):
        return self.displayCols

    def getValidatorType(self):
        return self.validatorType

    def getAnnouncement(self):
        return self.announcement
