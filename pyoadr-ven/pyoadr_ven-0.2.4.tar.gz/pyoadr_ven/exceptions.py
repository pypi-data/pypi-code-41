class OpenADRException(Exception):
    """Abstract superclass for exceptions in the Open ADR VEN agent."""

    def __init__(self, message, error_code, *args):
        super(OpenADRException, self).__init__(message, *args)
        self.error_code = error_code


class OpenADRInterfaceException(OpenADRException):
    """Use this exception when an error should be sent to the VTN as an OadrResponse payload."""

    def __init__(self, message, error_code, *args):
        super(OpenADRInterfaceException, self).__init__(message, error_code, *args)


class OpenADRInternalException(OpenADRException):
    """Use this exception when an error should be logged but not sent to the VTN."""

    def __init__(self, message, error_code, *args):
        super(OpenADRInternalException, self).__init__(message, error_code, *args)


class InvalidStatusException(Exception):
    def __init__(self, message):
        super(InvalidStatusException, self).__init__(message)
