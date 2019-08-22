from .validator_utils import ValidatorUtils
from ..color_printer import ColorPrinter
from .validator_status import ValidatorStatus
from functools import wraps


def ignorable(subvalidator):
    @wraps(subvalidator)
    def wrapper(self):
        subvalidatorName = self.subvalidatorName(subvalidator)
        if self.classesToIgnore and subvalidatorName in self.classesToIgnore:
            ColorPrinter.printRedBanner("!!!!!!! Ignoring {} !!!!!!!".format(subvalidatorName))
            return
        status = subvalidator(self)
        if status == ValidatorStatus.FAIL:
            ValidatorUtils.printIgnoreMessage(subvalidatorName)
        return status
    return wrapper
