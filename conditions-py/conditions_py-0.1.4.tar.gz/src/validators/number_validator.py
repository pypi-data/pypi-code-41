from __future__ import annotations

from typing import TypeVar
from .validator import Validator
from ..errors.argument_error import ArgumentError
from ..errors.argument_null_error import ArgumentNullError
from ..errors.argument_out_of_range_error import ArgumentOutOfRangeError


number = TypeVar('number', int, float)


class NumberValidator(Validator):
    """
    Contains all the number (int and float) validation conditions.
    """


    def __init__(self, value: str, argument_name: str):
        """
        Initializes the validator base class with the `value` and `argument_name`.
        """
        super().__init__(value, argument_name)


    def get_value(self) -> str:
        """
        Returns the validator value.
        """
        return super().get_value()


    def is_in_range(self, min_value: number, max_value: number) -> NumberValidator:
        """
        Checks whether the given value is between `min_value` and `max_value` (including those values).
        An exception is thrown otherwise.
        """
        if self.value < min_value or self.value > max_value:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` is out of the range `{min_value}-{max_value}`, was `{self.value}`',
                self.value,
                self.argument_name,
                min_value,
                max_value
            )

        return self


    def is_not_in_range(self, min_value: number, max_value: number) -> NumberValidator:
        """
        Checks whether the given value is not between `min_value` and `max_value` (including those values).
        An exception is thrown otherwise.
        """
        if self.value >= min_value and self.value <= max_value:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` is not out of the range `{min_value}-{max_value}`, was `{self.value}`',
                self.value,
                self.argument_name,
                min_value,
                max_value
            )

        return self


    def is_greater_than(self, min_value: number) -> NumberValidator:
        """
        Checks whether the given value is greater than the specified `min_value`.
        An exception is thrown otherwise.
        """
        if self.value <= min_value:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` should be greater than `{min_value}`, but was `{self.value}`',
                self.value,
                self.argument_name,
                min_value=min_value
            )

        return self


    def is_greater_or_equal(self, min_value: number) -> NumberValidator:
        """
        Checks whether the given value is greater or equal to the specified `min_value`.
        An exception is thrown otherwise.
        """
        if self.value < min_value:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` should be greater or equal to `{min_value}`, but was `{self.value}`',
                self.value,
                self.argument_name,
                min_value=min_value
            )

        return self


    def is_less_than(self, max_value: number) -> NumberValidator:
        """
        Checks whether the given value is less than the specified `max_value`.
        An exception is thrown otherwise.
        """
        if self.value >= max_value:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` should be less than `{max_value}`, but was `{self.value}`',
                self.value,
                self.argument_name,
                max_value=max_value
            )

        return self


    def is_less_or_equal(self, max_value: number) -> NumberValidator:
        """
        Checks whether the given value is less or equal to the specified `max_value`.
        An exception is thrown otherwise.
        """
        if self.value > max_value:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` should be less or equal to `{max_value}`, but was `{self.value}`',
                self.value,
                self.argument_name,
                max_value=max_value
            )

        return self


    def is_equal_to(self, value: number) -> NumberValidator:
        """
        Checks whether the given value is equal to the specified `value`.
        An exception is thrown otherwise.
        """
        if self.value != value:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` should be equal to `{value}`, but was `{self.value}`',
                self.value,
                self.argument_name,
                equal_to=value
            )

        return self


    def is_not_equal_to(self, value: number) -> NumberValidator:
        """
        Checks whether the given value is not equal to the specified `value`.
        An exception is thrown otherwise.
        """
        if self.value == value:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` should not be equal to `{value}`, but was `{self.value}`',
                self.value,
                self.argument_name,
                equal_to=value
            )

        return self


    def is_positive(self) -> NumberValidator:
        """
        Checks to see whether the given value is positive or not.
        An exception is thrown otherwise.
        """
        if self.value < 0:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` should be positive (or 0), but was `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def is_negative(self) -> NumberValidator:
        """
        Checks to see whether the given value is positive or not.
        An exception is thrown otherwise.
        """
        if self.value >= 0:
            raise ArgumentOutOfRangeError(
                f'The argument `{self.argument_name}` should be negative, but was `{self.value}`',
                self.value,
                self.argument_name
            )

        return self