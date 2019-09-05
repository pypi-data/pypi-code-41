class NonCriticalCLIException(Exception):
    """
    An exception that is caught by certain operations in core module
    """
    pass


class UserDefinedError(Exception):
    """
    For use in situations where developers might want to distinguish an
    error in try-except blocks. (Just to provide you with one so you
    don't have to write your own when prototyping.)
    """
    pass
