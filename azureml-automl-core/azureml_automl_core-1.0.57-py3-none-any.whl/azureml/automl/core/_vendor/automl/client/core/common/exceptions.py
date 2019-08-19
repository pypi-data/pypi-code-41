# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by AutoML."""
import json
from typing import cast, Optional, Type, TypeVar, Any
from ._error_response_constants import ErrorCodes


ExceptionT = TypeVar('ExceptionT', bound=BaseException)


class ErrorTypes:
    """Possible types of errors."""

    User = 'User'
    Service = 'Service'
    Client = 'Client'
    Resource = 'Resource'
    Unclassified = 'Unclassified'
    All = {User, Service, Client, Resource, Unclassified}


class AutoMLException(Exception):
    """Exception with an additional field specifying what type of error it is."""

    error_type = ErrorTypes.Unclassified

    def __init__(self, message="", error_type=ErrorTypes.Unclassified, target=None, details=None):
        """
        Construct a new AutoMLException.

        :param error_type: type of the exception.
        :param message: details on the exception.
        """
        super().__init__(message)
        self.error_type = error_type
        self._target = target
        self._details = details
        self._error_hierarchy = self._serialize_json(message=message)

    def __repr__(self) -> str:
        """Return string representation of the exception."""
        return "{}:\n\tErrorResponse {}".format(
            self.__class__.__name__,
            self._error_hierarchy)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        return self.__repr__()

    @classmethod
    def from_exception(cls: 'Type[ExceptionT]', e: BaseException, msg: Optional[str] = None) -> ExceptionT:
        """Convert an arbitrary exception to this exception type."""
        if not msg and isinstance(e, cls):
            return cast(ExceptionT, e)
        return cast(ExceptionT, cls(msg or str(e)).with_traceback(e.__traceback__))

    def get_error_type(self):
        """Get the error code for this exception."""
        return getattr(self, "_error_code", self.error_type)

    def _serialize_json(self, message: str) -> str:
        """
        Serialize this exception as an ErrorResponse json.

        :return: json string
        """
        error_ret = {}
        error_out = {}  # type: Any
        for super_class in self.__class__.mro():
            if super_class.__name__ == AutoMLException.__name__:
                break
            try:
                error_code = getattr(super_class, '_error_code', None)
                if error_out != {}:
                    error_out = {"code": error_code, "inner_error": error_out}
                else:
                    error_out = {"code": error_code}
            except AttributeError:
                break

        error_out['message'] = message
        if self._target is not None:
            error_out['target'] = self._target
        if self._details is not None:
            error_out['details'] = self._details
        error_ret['error'] = error_out

        return json.dumps(error_ret, indent=4, sort_keys=True)


class DataException(AutoMLException):
    """
    Exception related to data validations.

    :param message: Details on the exception.
    """

    _error_code = ErrorCodes.INVALIDDATA_ERROR

    def __init__(self, message="", target=None):
        """
        Construct a new DataException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.User, target)


class UserException(AutoMLException):
    """
    Exception related to user error.

    :param message: Details on the exception.
    """

    _error_code = ErrorCodes.USER_ERROR

    def __init__(self, message="", target=None):
        """
        Construct a new UserException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.User, target)


class UntrainedModelException(UserException):
    """UntrainedModelException."""

    def __init__(self, message="Fit need to be called before predict."):
        """Create a UntrainedModelException."""
        super().__init__("UntrainedModelException: {0}".format(message))


class ConfigException(AutoMLException):
    """
    Exception related to invalid user config.

    :param message: Details on the exception.
    """

    _error_code = ErrorCodes.VALIDATION_ERROR

    def __init__(self, message="", target=None):
        """
        Construct a new ConfigException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.User, target)


class ArgumentException(AutoMLException):
    """
    Exception related to invalid user config.

    :param message: Details on the exception.
    """

    _error_code = ErrorCodes.VALIDATION_ERROR

    def __init__(self, message="", target=None):
        """
        Construct a new ConfigException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.User, target)


class ServiceException(AutoMLException):
    """
    Exception related to JOS.

    :param message: Details on the exception.
    """

    _error_code = ErrorCodes.SYSTEM_ERROR

    def __init__(self, message="", target=None):
        """
        Construct a new ServiceException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.Service, target)


class ClientException(AutoMLException):
    """
    Exception related to client.

    :param message: Details on the exception.
    """

    _error_code = ErrorCodes.SYSTEM_ERROR

    def __init__(self, message="", target=None):
        """
        Construct a new ClientException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.Client, target)


class DataErrorException(AutoMLException):
    """
    Exception related to errors seen while processing data at training or inference time.

    :param message: Details on the exception.
    """

    _error_code = ErrorCodes.DATA_ERROR

    def __init__(self, message="", target=None):
        """
        Construct a new DataErrorException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.Client, target)


class RawDataSnapshotException(AutoMLException):
    """
    Exception related to capturing the raw data snapshot to be used at the inference time.

    :param message: Details on the exception.
    """

    _error_code = ErrorCodes.RAWDATASNAPSHOT_ERROR

    def __init__(self, message="", target=None):
        """
        Construct a new RawDataSnapshotException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.Client, target)


class ResourceException(AutoMLException):
    """
    Exception related to resource usage.

    :param message: Details on the exception.
    """

    def __init__(self, message="", target=None):
        """
        Construct a new ResourceException.

        :param message: details on the exception.
        """
        super().__init__(message, ErrorTypes.Resource, target)


class OnnxConvertException(ClientException):
    """Exception related to ONNX convert."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.ONNX_ERROR


class DataprepException(ClientException):
    """Exceptions related to Dataprep."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.DATAPREPVALIDATION_ERROR
