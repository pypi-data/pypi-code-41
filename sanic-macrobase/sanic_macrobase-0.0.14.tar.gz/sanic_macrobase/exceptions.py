from sanic.exceptions import SanicException


class RoutingErrorException(SanicException):

    def __init__(self, message, *args, **kwargs):
        super().__init__(message, status_code=500, *args, **kwargs)
