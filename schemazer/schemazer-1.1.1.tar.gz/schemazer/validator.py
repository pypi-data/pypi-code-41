import re

from typing import List
from flask import request

from schemazer.base import SchemazerParameter
from schemazer.messages import (ERROR_WRONG, ERROR_INTERVAL, ERROR_TYPE,
                                ERROR_MISSING)
from .commons.errors import RequestErrors


class RequestValidator:
    """
    The class implements methods for verifying the query parameters for API
    """

    @staticmethod
    def validate_required(parameter: SchemazerParameter) -> bool:
        """
        Check in request required parameter
        :param SchemazerParameter parameter: Schema parameter
        """
        if not request.args.get(parameter.name) and parameter.required:
            return RequestErrors.BadRequest.json_abort(
                failure_field=parameter.name,
                extend_msg=ERROR_MISSING.format(parameter.name))

        return True

    def validate_parameters(
            self, parameters: List[SchemazerParameter]) -> bool:
        """
        Validate request parameters by schema.
        Check required parameters and parameter format.
        :param List[SchemazerParameter] parameters: Schema parameters
        :return bool: True if all parameters is correct, or abort response.
        """
        for parameter in parameters or []:
            result = self.validate_required(parameter)
            if result is not True:
                return result

            result = parameter.validator.check(parameter)
            if result is not True:
                return result

        return True

    @staticmethod
    def validate_interval(parameters: List[SchemazerParameter]) -> bool:
        """
        Validate request parameters by available values interval
        :param List[SchemazerParameter] parameters: Schema parameters
        """
        for parameter in parameters or list():
            value = request.query.args.get(parameter.name)
            if callable(parameter.interval) and not parameter.interval(value):
                return RequestErrors.BadRequest.json_abort(
                    param=parameter.name,
                    msg=ERROR_INTERVAL.format(parameter.name))
        return True

    @staticmethod
    def set_default_values(parameters: List[SchemazerParameter]):
        for parameter in parameters:
            value = request.query.args.get(parameter.name)
            value = str(value) if value is not None else None

            try:
                if value or parameter.default:
                    request.query.args[parameter.name] = \
                        parameter.type(value) or parameter.default
            except ValueError:
                return RequestErrors.BadRequest.json_abort(
                    param=parameter.name,
                    msg=ERROR_TYPE.format(parameter.name))

    def process(self, parameters: List[SchemazerParameter]) -> bool:
        """
        Validate request parameters by schema.
        - validate required parameters
        - validate format pattern of parameters
        - validate parameters interval
        - validate params types, convert from string query params by schema
          parameter types.
        :param parameters: Schema parameters
        """
        for func in [self.validate_parameters, self.validate_interval,
                     self.set_default_values]:
            result = func(parameters)
            if result is not bool:
                return result

        return True


class Validator:
    """
    Base validator representation.
    """
    def check(self, **kwargs):
        raise NotImplementedError()


class PatternValidator(Validator):
    """
    Regex validator.
    """
    def __init__(self, pattern: str):
        """
        Init by regex pattern.
        :param str pattern:
        """
        self.pattern = pattern

    @staticmethod
    def _regular_check(value, expression):
        process = re.compile(expression)

        if type(value) in [bool, int, float]:
            value = str(value).lower()
        result = process.match(value)

        return bool(result)

    def check(self, parameter: SchemazerParameter) -> bool:
        """
        Check request parameter by pattern.
        :param SchemazerParameter parameter: SchemazerParameter schema
        """
        str_value = str(request.query.args.get(parameter.name))

        if not self._regular_check(str_value, self.pattern):
            return RequestErrors.BadRequest.json_abort(
                param=parameter.name,
                msg=ERROR_WRONG.format(parameter.name))

        return True
