from functools import wraps
from .types import *
from .color_printer import ColorPrinter
from .validators.validator_utils import ValidatorUtils


def ignorable(evaluateFunc):
    @wraps(evaluateFunc)
    def wrapper(self, tagger, data, validatorConfig):
        validatorName = validatorConfig.getName()
        if validatorConfig.isIgnorable() and validatorName in self.validatorsToIgnore:
            ColorPrinter.printRedBanner("!!!!!!! Ignoring {} !!!!!!!".format(validatorName))
            return ValidatorResponse(ValidatorStatus.IGNORED)
        status = evaluateFunc(self, tagger, data, validatorConfig)
        if validatorConfig.isIgnorable() and status == ValidatorStatus.FAIL:
            ValidatorUtils.printIgnoreMessage(validatorName)
        elif status == ValidatorStatus.FAIL:
            print("This check is not ignorable.")
        return status
    return wrapper
