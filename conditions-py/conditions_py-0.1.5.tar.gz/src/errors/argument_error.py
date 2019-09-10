class ArgumentError(Exception):
    """

    """

    def __init__(self, message, value, argument_name):
        """

        """
        super().__init__(message)

        self.value = value
        self.argument_name = argument_name