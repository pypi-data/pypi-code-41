from docopt import docopt

from ..base import get_args


class Base:
    def __init__(self, command_options):
        self.options = docopt(
            self.__doc__,
            argv=command_options
        )

        self.args = get_args(
            options=self.options,
            environment=True
        )

    def execute(self):
        raise NotImplementedError(
            'You must implement the execute() method yourself!'
        )

    def get_key_dict(self):
        return {
            "Organization": self.args["AWS_OKTA_ORGANIZATION"],
            "User": self.args["AWS_OKTA_USER"],
            "Key": self.args["AWS_OKTA_KEY"]
        }
