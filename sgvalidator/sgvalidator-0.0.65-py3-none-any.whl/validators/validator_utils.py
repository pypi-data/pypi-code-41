import phonenumbers
import pkg_resources
from ..color_printer import ColorPrinter


class ValidatorUtils:
    IGNORE_MESSAGE_PATH = pkg_resources.resource_filename("sgvalidator", "validators/data/IGNORE_MESSAGE.txt")

    @staticmethod
    def fail(message):
        ColorPrinter.printRed(message)

    @staticmethod
    def printIgnoreMessage(className):
        with open(ValidatorUtils.IGNORE_MESSAGE_PATH, "r") as f:
            ColorPrinter.printCyan(f.read().format(className))

    @staticmethod
    def shouldClassBeIgnored(className, ignoreFlags):
        if ignoreFlags and className in ignoreFlags:
            return True
        return False

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_phone_number(phone, country):
        try:
            return phonenumbers.is_possible_number(phonenumbers.parse(phone, country))
        except:
            return False

    @staticmethod
    def is_blank(field):
        if field in ['<MISSING>', '<INACCESSIBLE>']:
            return True
        return not bool(field)

    @staticmethod
    def is_missing_or_inaccessible(field):
        if field in ['<MISSING>', '<INACCESSIBLE>']:
            return True
        return False

    @staticmethod
    def is_not_blank(field):
        return not ValidatorUtils.is_blank(field)

    @staticmethod
    def cleanState(state):
        if state is None:
            return None
        return state.lower().strip().replace(".", "")
