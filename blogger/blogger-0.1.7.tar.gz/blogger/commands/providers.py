import click

from .base import BaseCommand
from blogger.providers import supported_providers


class ProvidersCommand(BaseCommand):
    def run(self):
        """
        Entry point for `blogger providers`.
        """
        if self.options.get("list", False):
            return self.print_list()
        return self.print_help()

    def print_list(self):
        """
        Iterates the list of supported providers to print both the provider
        key and the description of the provider to the user.
        """
        for provider in supported_providers():
            click.echo("{key} {description}".format(key=click.style(provider[0], fg="green"), description=provider[1]))
