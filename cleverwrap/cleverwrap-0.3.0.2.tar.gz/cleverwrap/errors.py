__all__ = ('CleverWrapError', 'UnknownAPIError')


class CleverWrapError(Exception):
    pass


class UnknownAPIError(CleverWrapError):
    pass
