from __future__ import annotations

from .validator import Validator
from ..errors.argument_error import ArgumentError


class BooleanValidator(Validator):
    """
    Contains all the boolean validation conditions.
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


    def is_true(self) -> BooleanValidator:
        """
        Checks whether the given value is `True`. An exception is thrown otherwise.
        """
        if not self.value == True:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be True but was `{self.value}`',
                self.value,
                self.argument_name
            )

        return self


    def is_false(self) -> BooleanValidator:
        """
        Checks whether the given value is `True`. An exception is thrown otherwise.
        """
        if not self.value == False:
            raise ArgumentError(
                f'The argument `{self.argument_name}` should be False but was `{self.value}`',
                self.value,
                self.argument_name
            )

        return self