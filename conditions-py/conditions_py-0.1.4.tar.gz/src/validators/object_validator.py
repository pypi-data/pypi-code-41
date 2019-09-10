from __future__ import annotations

from inspect import isclass
from typing import Type, Union
from .validator import Validator
from ..errors.argument_error import ArgumentError
from ..errors.argument_null_error import ArgumentNullError


class ObjectValidator(Validator):
    """
    Contains all the object validation conditions.
    """


    def __init__(self, value: object, argument_name: str):
        """
        Initializes the validator base class with the `value` and `argument_name`.
        """
        super().__init__(value, argument_name)


    def get_value(self) -> str:
        """
        Returns the validator value.
        """
        return super().get_value()


    def is_of_type_name(self, type: object) -> ObjectValidator:
        """
        Checks whether the Type of the given value is of `type` by comparing the `__name__` attribute.
        An exception is thrown otherwise.
        """
        if isclass(type):
            raise TypeError(
                f'The argument `{self.argument_name}` should be an initialized object rather than a type, did you mean to use `is_of_type()`?.'
            )

        if not self.value.__class__.__name__ == type.__class__.__name__:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be of type `{type.__class__.__name__}` but was `{self.value.__class__.__name__}`',
                self.value,
                self.argument_name
            )

        return self


    def is_not_of_type_name(self, type: object) -> ObjectValidator:
        """
        Checks whether the Type of the given value is not of `type` by comparing the `__name__` attribute.
        An exception is thrown otherwise.
        """
        if isclass(type):
            raise TypeError(
                f'The argument `{self.argument_name}` should be an initialized object rather than a type, did you mean to use `is_not_of_type()`?.'
            )

        if self.value.__class__.__name__ == type.__class__.__name__:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not be of type `{type.__class__.__name__}` but was `{self.value.__class__.__name__}`',
                self.value,
                self.argument_name
            )

        return self


    def is_of_type(self, type: Type) -> ObjectValidator:
        """
        Checks whether the Type of the given value is of `type` by comparing the types using `isinstance()`.
        An exception is thrown otherwise.
        """
        if not isclass(type):
            raise TypeError(
                f'The argument `{self.argument_name}` should be an type rather than an initialized object, did you mean to use `is_of_type_name()`?.'
            )

        if not isinstance(self.value, type):
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be of type `{type.__name__}` but was `{self.value.__class__.__name__}`',
                self.value,
                self.argument_name
            )

        return self


    def is_not_of_type(self, type: Type) -> ObjectValidator:
        """
        Checks whether the Type of the given value is of `type` by comparing the types using `isinstance()`.
        An exception is thrown otherwise.
        """
        if not isclass(type):
            raise TypeError(
                f'The argument `{self.argument_name}` should be an type rather than an initialized object, did you mean to use `is_not_of_type_name()`?.'
            )

        if isinstance(self.value, type):
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not be of type `{type.__name__}` but was `{self.value.__class__.__name__}`',
                self.value,
                self.argument_name
            )

        return self


    def is_null(self) -> ObjectValidator:
        """
        Checks whether the given value is None (Null). An exception is thrown otherwise.
        """
        if not self.value is None:
            raise ArgumentNullError(
                f'The argument `{self.argument_name}` should be NONE (NULL)',
                self.value,
                self.argument_name
            )

        return self


    def is_not_null(self) -> ObjectValidator:
        """
        Checks whether the given value is None (Null). An exception is thrown otherwise.
        """
        if self.value is None:
            raise ArgumentNullError(
                f'The argument `{self.argument_name}` should not be NONE (NULL)',
                self.value,
                self.argument_name
            )

        return self


    def is_equal_to(self, value: object) -> ObjectValidator:
        """
        Checks whether the given value is equal to the object specified in `value` by comparing the internal dictionaries.
        An exception is thrown otherwise.
        """
        if self.value.__dict__ != value.__dict__:
            raise ArgumentError(
                f'The argument `{self.value.__class__.__name__}` should be equal to `{value.__class__.__name__}`',
                self.value,
                self.argument_name
            )

        return self


    def is_not_equal_to(self, value: object) -> ObjectValidator:
        """
        Checks whether the given value is not equal to the object specified in `value` by comparing the internal dictionaries.
        An exception is thrown otherwise.
        """
        if self.value.__dict__ == value.__dict__:
            raise ArgumentError(
                f'The argument `{self.value.__class__.__name__}` should be equal to `{value.__class__.__name__}`',
                self.value,
                self.argument_name
            )

        return self


    def is_equal_to_using_eq(self, value: object) -> ObjectValidator:
        """
        Checks whether the given value is equal to the object specified in `value` by using the `__eq__()` function in object.
        An exception is thrown otherwise.
        """
        if self.value != value:
            raise ArgumentError(
                f'The argument `{self.value.__class__.__name__}` should be equal to `{value.__class__.__name__}`',
                self.value,
                self.argument_name
            )

        return self


    def is_not_equal_to_using_ne(self, value: object) -> ObjectValidator:
        """
        Checks whether the given value is not equal to the object specified in `value` using the `__ne__()` function in the object.
        An exception is thrown otherwise.
        """
        if self.value == value:
            raise ArgumentError(
                f'The argument `{self.value.__class__.__name__}` should be equal to `{value.__class__.__name__}`',
                self.value,
                self.argument_name
            )

        return self