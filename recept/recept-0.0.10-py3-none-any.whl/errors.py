import click


class ReceptError(click.ClickException):
    pass
    # TODO: Revert when we replace click.
    # def __init__(self, message):
    #     self.message = message
    #
    # @property
    # def name(self):
    #     return self.__class__.__name__
    #
    # def __str__(self):
    #     return f"{self.name}({self.message})"
    #
    # __repr__ = __str__


class ImproperlyConfigured(ReceptError):
    pass
