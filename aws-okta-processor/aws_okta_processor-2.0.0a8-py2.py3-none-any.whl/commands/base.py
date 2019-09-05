import os

from docopt import docopt


ARG_MAP = {
            "--environment": "AWS_OKTA_ENVIRONMENT",
            "--user": "AWS_OKTA_USER",
            "--pass": "AWS_OKTA_PASS",
            "--organization": "AWS_OKTA_ORGANIZATION",
            "--application": "AWS_OKTA_APPLICATION",
            "--role": "AWS_OKTA_ROLE",
            "--duration": "AWS_OKTA_DURATION",
            "--key": "AWS_OKTA_KEY",
            "--factor": "AWS_OKTA_FACTOR",
            "--silent": "AWS_OKTA_SILENT"
        }


class Base:
    def __init__(self, command_args):
        self.options = docopt(
            self.__doc__,
            argv=command_args,
            options_first=True
        )

    def execute(self):
        raise NotImplementedError(
            'You must implement the execute() method yourself!'
        )


def get_args(options=None, environment=False):
    args = {}

    for param, var in ARG_MAP.items():
        if param not in options:
            args[var] = None
            continue

        if options[param]:
            args[var] = options[param]

        if var not in args.keys():
            if var in os.environ and environment:
                args[var] = os.environ[var]
            else:
                args[var] = None

    return args
