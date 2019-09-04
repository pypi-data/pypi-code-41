from marshmallow import ValidationError as BaseValidationError


class ImmediateResponseError(Exception):
    def __init__(self, response):
        self.response = response


class ValidationError(BaseValidationError):
    """Base error for all of query param validation/parsing errors."""
