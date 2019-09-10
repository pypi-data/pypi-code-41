from __future__ import annotations

from .validator import Validator
from ..helpers.regex_helper import RegexHelper
from ..errors.argument_error import ArgumentError
from ..errors.argument_null_error import ArgumentNullError
from ..errors.argument_pattern_error import ArgumentPatternError


class StringValidator(Validator):
    """
    Contains all the string validation conditions.
    """


    EMPTY_STRING = ''


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


    def is_null(self) -> StringValidator:
        """
        Checks whether the given value is none (null). An exception is thrown otherwise.
        """
        if self.value is not None:
            raise ArgumentNullError(
                f'The argument `{self.argument_name}` should be NULL',
                self.value,
                self.argument_name
            )

        return self


    def is_not_null(self) -> StringValidator:
        """
        Checks whether the given value is NOT none (null). An exception is thrown otherwise.
        """
        if self.value is None:
            raise ArgumentNullError(
                f'The argument `{self.argument_name}` should not be NONE (NULL)',
                self.value,
                self.argument_name
            )

        return self


    def is_null_or_empty(self) -> StringValidator:
        """
        Checks whether the given value is none (null) or an empty string. An exception is thrown otherwise.
        """
        if self.value is not None\
        and self.value != self.EMPTY_STRING:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be either EMPTY or NULL but was `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def is_not_null_or_empty(self) -> StringValidator:
        """
        Checks whether the given value is NOT none (null) or NOT an empty string. An exception is thrown otherwise.
        """
        if self.value is None\
        or self.value == self.EMPTY_STRING:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not be EMPTY',
                self.value,
                self.argument_name
            )

        return self


    def is_null_or_whitespace(self) -> StringValidator:
        """
        Checks whether the given value is none (null), empty, or consists only of white-space characters.
        An exception is thrown otherwise.
        """
        if self.value is not None\
        and self.value != self.EMPTY_STRING\
        and not str(self.value).isspace():
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be NULL or WHITESPACE but was `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def is_not_null_or_whitespace(self) -> StringValidator:
        """
        Checks whether the given value is NOT none (null), NOT empty, and does NOT consist only of white-space characters.
        An exception is thrown otherwise.
        """
        if self.value is None\
        or self.value == self.EMPTY_STRING\
        or str(self.value).isspace():
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not have WHITESPACE',
                self.value,
                self.argument_name
            )

        return self


    def is_shorter_than(self, max_length: int) -> StringValidator:
        """
        Checks whether the given value is shorter in length, than the specified `max_length`.
        An exception is thrown otherwise.
        """
        if len(self.value) >= max_length:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be shorter than `{max_length}` but is `{len(self.value)}`',
                self.value,
                self.argument_name
            )

        return self


    def is_shorter_or_equal(self, max_length: int) -> StringValidator:
        """
        Checks whether the given value is shorter or equal in length, than the specified `max_length`.
        An exception is thrown otherwise.
        """
        if len(self.value) > max_length:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be shorter than or equal to `{max_length}` but is `{len(self.value)}`',
                self.value,
                self.argument_name
            )

        return self


    def is_longer_than(self, min_length: int) -> StringValidator:
        """
        Checks whether the given value is longer in length, than the specified `min_length`.
        An exception is thrown otherwise.
        """
        if len(self.value) <= min_length:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be longer than `{min_length}` but is `{len(self.value)}`',
                self.value,
                self.argument_name
            )

        return self


    def is_longer_or_equal(self, min_length: int) -> StringValidator:
        """
        Checks whether the given value is longer or equal in length, than the specified `min_length`.
        An exception is thrown otherwise.
        """
        if len(self.value) < min_length:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be longer than or equal to `{min_length}` but is `{len(self.value)}`',
                self.value,
                self.argument_name
            )

        return self


    def has_length(self, length: int) -> StringValidator:
        """
        Checks whether the given value is equal in length to the specified `length`. An exception is thrown otherwise.
        """
        if len(self.value) != length:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should have a length of `{length}` but is `{len(self.value)}`',
                self.value,
                self.argument_name
            )

        return self


    def does_not_have_length(self, length: int) -> StringValidator:
        """
        Checks whether the given value is unequal in length to the specified `length`. An exception is thrown otherwise.
        """
        if len(self.value) == length:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not have a length of `{length}` but is `{len(self.value)}`',
                self.value,
                self.argument_name
            )

        return self


    def equals(self, value: str) -> StringValidator:
        """
        Checks whether the given value equals the specified `value`. An exception is thrown otherwise.
        """
        if self.value != value:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should equal `{value}` but was actually `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def does_not_equal(self, value: str) -> StringValidator:
        """
        Checks whether the given value equals the specified `value`. An exception is thrown otherwise.
        """
        if self.value == value:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should equal `{value}` but was actually `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def starts_with(self, value: str) -> StringValidator:
        """
        Checks whether the given value starts with the specified `value`. An exception is thrown otherwise.
        """
        if not str(self.value).startswith(value):
            raise ArgumentError(
                f'The argument `{self.argument_name}` should start with `{value}` but was actually `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def does_not_start_with(self, value: str) -> StringValidator:
        """
        Checks whether the given value does not start with the specified `value`. An exception is thrown otherwise.
        """
        if str(self.value).startswith(value):
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not start with `{value}` but was actually `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def ends_with(self, value: str) -> StringValidator:
        """
        Checks whether the given value ends with the specified `value`. An exception is thrown otherwise.
        """
        if not str(self.value).endswith(value):
            raise ArgumentError(
                f'The argument `{self.argument_name}` should end with `{value}` but was actually `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def does_not_end_with(self, value: str) -> StringValidator:
        """
        Checks whether the given value does not end with the specified `value`. An exception is thrown otherwise.
        """
        if str(self.value).endswith(value):
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not end with `{value}` but was actually `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def contains(self, value: str) -> StringValidator:
        """
        Checks whether the given value contains the specified `value`. An exception is thrown otherwise.
        """
        if value not in self.value:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should contain `{value}` but was actually `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def does_not_contain(self, value: str) -> StringValidator:
        """
        Checks whether the given value does not contain the specified `value`. An exception is thrown otherwise.
        """
        if value in self.value:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not contain `{value}` but was actually `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def is_regex_match(self, pattern: str) -> StringValidator:
        """
        Checks wether the given value matches the supplied `pattern`. An exception is thrown otherwise.
        """
        if not RegexHelper.is_match(pattern, self.value):
            raise ArgumentPatternError(
                f'The argument `{self.argument_name}` should match the pattern `{pattern}`',
                self.value,
                self.argument_name,
                pattern
            )

        return self


    def is_not_regex_match(self, pattern: str) -> StringValidator:
        """
        Checks whether the given value does not match the supplied `pattern`. An exception is thrown otherwise.
        """
        if RegexHelper.is_match(pattern, self.value):
            raise ArgumentPatternError(
                f'The argument `{self.argument_name}` should match the pattern `{pattern}`',
                self.value,
                self.argument_name,
                pattern
            )

        return self


    def is_in_set(self, set: list) -> StringValidator:
        """
        Checks to see if the given value matches any of the values in the supplied set. An exception is thrown otherwise.
        """
        if not self.value in set:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should match a value specified in the set.',
                self.value,
                self.argument_name
            )

        return self


    def is_in_set_case_insensitive(self, set: list) -> StringValidator:
        """
        Checks to see if the given value matches any of the values in the supplied set.
        Case insensitive.
        An exception is thrown otherwise.
        """
        if not self.value.lower() in (item.lower() for item in set):
            raise ArgumentError(
                f'The argument `{self.argument_name}` should match a value specified in the set.',
                self.value,
                self.argument_name
            )

        return self


    def is_not_in_set(self, set: list) -> StringValidator:
        """
        Checks to see if the given value matches any of the values is not in the supplied set. An exception is thrown otherwise.
        """
        if self.value in set:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not match a value specified in the set.',
                self.value,
                self.argument_name
            )

        return self


    def is_not_in_set_case_insensitive(self, set: list) -> StringValidator:
        """
        Checks to see if the given value matches any of the values is not in the supplied set.
        Case insensitive.
        An exception is thrown otherwise.
        """
        if self.value.lower() in (item.lower() for item in set):
            raise ArgumentError(
                f'The argument `{self.argument_name}` should not match a value specified in the set.',
                self.value,
                self.argument_name
            )

        return self