from enum import Enum

from ucp9.conversion import CP932Conversion
from ucp9.environment import CP932


class Option(Enum):
    REMOVE = 'remove'
    KEEP = 'keep'
    REPLACE = 'replace'


def convert(string: str, option: str = 'replace') -> str:
    """
    Iterate through each character in the input string,
    attempt to convert any characters which cannot be encoded to cp932.
    :param string: a string of text.
    :param option: keep/replace/remove = action to be performed on inconvertible characters. Default is replace
    :return: a cp932-encodable version of the input string.
    """
    # Convert string to enum
    option = Option(option)
    output = ""
    if type(string) is not str:
        return string

    for c in string:
        try:
            c.encode(CP932)
            output += c
        except UnicodeEncodeError:
            output += _replacer(c, option)

    return output


def _replacer(character: str, option: Option) -> str:
    """
    :param character: a single character
    :return: cp932-compatible version of the input character
    """
    try:
        cp = CP932Conversion()
        return cp.convert(character)
    except KeyError:
        if option == Option.REMOVE:
            return ""
        elif option == Option.KEEP:
            return character
        else:
            return "?"
