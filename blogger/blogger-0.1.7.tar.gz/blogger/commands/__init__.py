import click
from click import ClickException

from .audio import AudioCommand
from .converters import ConvertersCommand
from .providers import ProvidersCommand
from .voices import VoicesCommand


class handler:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if isinstance(exc_type, type(ValueError)):
                raise ClickException(click.style(str(exc_val), fg="red"))
            raise ClickException(
                click.style("There was a problem. Please report a problem to the issue repository.", fg="red")
            )
