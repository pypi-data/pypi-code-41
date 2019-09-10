from .argument_error import ArgumentError

class ArgumentPatternError(ArgumentError):
    """

    """


    def __init__(
        self,
        message: str,
        value: str,
        argument_name: str,
        pattern: str
    ):
        """

        """
        super().__init__(
            message,
            value,
            argument_name
        )
        self.pattern = pattern