class AlfaError(Exception):
    template = "An unspecified error occurred"

    def __init__(self, **kwargs):
        if "template" in kwargs:
            self.template = kwargs.get("template")

        message = self.template.format(**kwargs)
        Exception.__init__(self, message)
        self.kwargs = kwargs

    def __reduce__(self):
        return _unpickle_exception, (self.__class__, None, self.kwargs)


def _unpickle_exception(exception_class, args=(), kwargs={}):
    return exception_class(*args, **kwargs)


#


class CredentialsError(AlfaError):
    template = "Authentication credentials not found / invalid"


class TokenNotFoundError(CredentialsError):
    template = "Authentication tokens not found"


class AuthenticationError(AlfaError):
    template = "Error encountered during authentication: {error}"


class AuthorizationError(AlfaError):
    template = "Not authorized for request to {url}: {error}"


class RequestError(AlfaError):
    template = "Error encountered during request to {url} ({status}): {error}"


class ResourceError(AlfaError):
    template = "Error encountered for resource {resource}: {error}"


class ResourceNotFoundError(ResourceError):
    template = "Error encountered during resource initialization: Resource not found in ({url})"


class ResourceDeletionError(ResourceError):
    template = "Cannot delete {resource}: {error}"


class UnknownServiceError(AlfaError):
    template = "Unknown service: '{service_name}'. Valid service names are: {known_service_names}"


class ServiceEnvironmentError(AlfaError):
    template = "Environment '{environment}' does not exist for service '{service_name}'"


class SemanticVersionError(AlfaError):
    template = "Version '{version}' does not comply with Semantic Versioning."


class AlfaConfigError(AlfaError):
    template = "{message} ({error})"
