import sys


class Logger:
    """Logging utility"""

    verbosity = 0

    @classmethod
    def log(cls, message: str, level: int = 0):
        if cls.verbosity >= level:
            print(message, file=sys.stdout if level >= 0 else sys.stderr)

    @classmethod
    def set_verbosity(cls, verbose: int):
        cls.verbosity = verbose
