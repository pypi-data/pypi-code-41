from .validator_runner import ValidatorRunner
from .validator_io import ValidatorIO
from .color_printer import ColorPrinter
import sys


def validate(dataLocation, debug=False):
    # deprecating debug as of version 0.0.49, but not going to update validate.py because it requires
    # contractors to pull. so validate() will still receive it, but we won't do anything with it
    validatePythonVersion()
    ColorPrinter.printGreenBanner("========== Validating data ==========")
    validatorIo = ValidatorIO()
    data = validatorIo.readDataFromLocation(dataLocation)
    classesToIgnore = validatorIo.getClassesToIgnore()
    numFailures = ValidatorRunner(data, classesToIgnore=classesToIgnore).run()
    validatorIo.optionallyWriteSuccessFile(numFailures)


def validatePythonVersion():
    version = sys.version_info[0]
    if version == 2:
        ColorPrinter.printRedBanner("This script can only run on Python3, but you're running on Python2. "
                                    "Please re-run using Python3. For help installing and running Python3, "
                                    "see wsvincent.com/install-python3-mac or "
                                    "wsvincent.com/install-python3-windows depending on your OS.")
        exit(0)
