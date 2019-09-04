"""Custom exceptions for rest multi factor."""

__all__ = (
    "MultiFactorException",
    "MultiFactorWarning",
    "RFCGuidanceException",
    "RFCGuidanceWarning",
)


class MultiFactorException(Exception):
    """Main general exception class for this package."""


class MultiFactorWarning(Warning):
    """Main general warning class for this package."""


class RFCGuidanceException(MultiFactorException):
    """Exception for RFC guidance dissatisfactions."""


class RFCGuidanceWarning(MultiFactorWarning):
    """Warning for RFC guidance dissatisfactions."""

