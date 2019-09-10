from .argument_error import ArgumentError

class ArgumentOutOfRangeError(ArgumentError):
    """

    """


    def __init__(
        self,
        message: str,
        value: int,
        argument_name: str,
        equal_to: int = None,
        min_value: int = None,
        max_value: int = None
    ):
        """

        """
        super().__init__(
            message,
            value,
            argument_name
        )
        self.equal_to = equal_to
        self.min_value = min_value
        self.max_value = max_value