"""
aws-okta-processor

Usage:
  aws-okta-processor [options] <command> <subcommand> [<subcommand> ...] [parameters]

Options:
  -h --help                                                  Show this screen.
  --version                                                  Show version.

Help:
  Use "aws-okta-processor <command> --help" for more information on a specific command.
  
  For additional support please reach out to our Slack channel :
  https://godaddy-oss-slack.herokuapp.com/
"""  # noqa


from docopt import docopt

from . import __version__ as VERSION

from . import commands


def main():
    options = docopt(
        __doc__,
        version=VERSION,
        options_first=True
    )

    command_name = options.pop('<command>').capitalize()
    command_options = options.pop('<subcommand>')

    if command_options is None:
        command_options = {}

    try:
        command_class = getattr(commands, command_name)
        command = command_class(command_options)
        command.execute()
    except AttributeError:
        exit("aws-okta-processor: error: argument command: Invalid choice")
