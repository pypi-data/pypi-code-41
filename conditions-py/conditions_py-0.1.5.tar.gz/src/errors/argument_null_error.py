from typing import TypeVar
from .argument_error import ArgumentError


object_class = TypeVar('object_class', object, type)


class ArgumentNullError(ArgumentError):
    """

    """


    def __init__(
        self,
        message: str,
        value: object_class,
        argument_name: str
    ):
        """

        """
        super().__init__(
            message,
            value,
            argument_name
        )