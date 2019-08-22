import click

from .base import BaseCommand
from blogger.converters import supported_converters


class ConvertersCommand(BaseCommand):
    def run(self):
        """
        Entry point for `blogger converters`.
        """
        if self.options.get("list", False):
            return self.print_list()
        return self.print_help()

    def print_list(self):
        """
        Iterates the list of supported converters to print both the converter
        key and the description of the converter to the user.
        """
        for converter in supported_converters():
            click.echo(
                "{key} {description}".format(key=click.style(converter[0], fg="green"), description=converter[1])
            )
