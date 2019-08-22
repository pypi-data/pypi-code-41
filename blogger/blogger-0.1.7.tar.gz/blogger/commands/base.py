import click
from abc import ABC, abstractmethod


class BaseCommand(ABC):
    def __init__(self, ctx, *args, **kwargs):
        """
        Initialize the CLI command object.
        """
        self.ctx = ctx
        self.arguments = args
        self.options = kwargs

    @abstractmethod
    def run(self):
        """
        Runs the CLI command.
        """

    def print_help(self):
        """
        Helper method to print the help screen for the current command.
        """
        return click.echo(self.ctx.get_help())
