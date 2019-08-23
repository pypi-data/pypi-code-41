# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import sys
import traceback


class AzureMLException(Exception):
    """
    Base class for all azureml exceptions.
    Extends Exception, if trying to catch only azureml exceptions
    then catch this class.
    """

    def __init__(self, exception_message, inner_exception=None, target=None, details=None, **kwargs):
        Exception.__init__(self, exception_message, **kwargs)
        self._exception_message = exception_message
        self._inner_exception = inner_exception
        self._exc_info = sys.exc_info()
        self._target = target
        self._details = details

    def __repr__(self):
        return "{}:\n\tMessage: {}\n\tInnerException {}\n\tErrorResponse \n{}".format(
            self.__class__.__name__,
            self.message,
            self.inner_exception,
            self._serialize_json(indent=4))

    def __str__(self):
        return self.__repr__()

    @property
    def message(self):
        return self._exception_message

    @message.setter
    def message(self, value):
        self._exception_message = value

    @property
    def inner_exception(self):
        return self._inner_exception

    @inner_exception.setter
    def inner_exception(self, value):
        self._inner_exception = value

    def print_stacktrace(self):
        traceback.print_exception(*self._exc_info)

    def _serialize_json(self, indent=None):
        """
        Serialize this exception as an ErrorResponse json.
        :return: json string
        """
        error_ret = {}
        error_out = {}
        for super_class in self.__class__.mro():
            if super_class.__name__ == AzureMLException.__name__:
                break
            if not hasattr(super_class, '_error_code'):
                break
            if error_out != {}:
                error_out = {"code": super_class._error_code, "inner_error": error_out}
            else:
                error_out = {"code": super_class._error_code}

        error_out['message'] = self._exception_message
        if self._target is not None:
            error_out['target'] = self._target
        if self._details is not None:
            error_out['details'] = self._details
        error_ret['error'] = error_out

        return json.dumps(error_ret, indent=indent)

    def _contains_code(self, code_hierarchy):
        """
        Determine whether this error exists within the hierarchy provided.
        :param code_hierarchy: List of strings sorted by hierarchy
        :return: bool
        """
        error_response = json.loads(self._serialize_json())
        inner_error = error_response.get('error')
        response_hierarchy = []
        while inner_error is not None:
            response_hierarchy.append(inner_error.get('code'))
            inner_error = inner_error.get('inner_error')

        # Compare only the first K codes, allow more granular codes to be defined
        return code_hierarchy == response_hierarchy[:len(code_hierarchy)]
