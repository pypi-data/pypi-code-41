from typing import TypeVar, Generic
from .validators.validator import Validator
from .validators.string_validator import StringValidator
from .validators.object_validator import ObjectValidator
from .validators.number_validator import NumberValidator
from .validators.boolean_validator import BooleanValidator


number = TypeVar('number', int, float)


class Condition:
    """
    Base condition class to create the validator which corresponds to the value type.
    """


    @staticmethod
    def requires_obj(value: object, argument_name: str) -> ObjectValidator:
        """
        Initializes the conditions framework using the `number (float, int)` validator.
        """
        return ObjectValidator(value, argument_name)


    @staticmethod
    def requires_num(value: number, argument_name: str) -> NumberValidator:
        """
        Initializes the conditions framework using the `number (float, int)` validator.
        """
        return NumberValidator(value, argument_name)


    @staticmethod
    def requires_bool(value: bool, argument_name: str) -> BooleanValidator:
        """
        Initializes the conditions framework using the `boolean` validator.
        """
        return BooleanValidator(value, argument_name)


    @staticmethod
    def requires_str(value: object, argument_name: str) -> StringValidator:
        """
        Initializes the conditions framework using the `string` validator.
        """
        return StringValidator(value, argument_name)