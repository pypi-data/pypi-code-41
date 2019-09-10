import re

class RegexHelper:
    """
    Defines regex helper methods.
    """

    @staticmethod
    def is_match(pattern: str, string: str) -> bool:
        """
        Returns `True` or `False` if a regex match has been found in the string.
        """
        if re.match(pattern, string) is not None:
            return True
        else:
            return False