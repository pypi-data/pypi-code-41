"""Error classes for NQontrol."""


class NQontrolError(Exception):
    """Base Error Class."""

    def __init__(self, message):
        self.message = message


class ConfigurationError(NQontrolError):
    """Errors due to misconfiguration."""

    pass


class UserInputError(NQontrolError):
    """Wrong user input."""

    pass


class Bug(NQontrolError):
    """Found a bug."""

    pass
