import enum


class ErrorCodes(enum.Enum):
    DATE_START = 1
    DATE_END = 2


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class DateStartError(Error):
    """Exception raised when a date is below an expected value."""

    def __init__(self):
        self.message = "date is below the expected start time"
        self.code = ErrorCodes.DATE_START


class DateEndError(Error):
    """Exception raised when a date is above an expected value."""

    def __init__(self):
        self.message = "date is above the expected start time"
        self.code = ErrorCodes.DATE_END
