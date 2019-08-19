class RequestSchemaException(Exception):
    """Request validation error, check the request data"""
    def __init__(self, message, resource, errors):
        super().__init__(
            "[Resource: {}]: {}\n\t{}".format(
                resource, message, errors
            )
        )
        self.resource = resource
        self.errors = errors

class AuthenticationException(Exception):
    """Authentication error, check authorization key"""
    def __init__(self, message, resource, errors):
        super().__init__(
            "[Resource: {}]: {}\n\t{}".format(
                resource, message, errors
            )
        )
        self.resource = resource
        self.errors = errors
