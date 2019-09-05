from docopt import docopt

from ..base import get_args


class Base:
    def __init__(self, command_options):
        self.options = docopt(
            self.__doc__,
            argv=command_options
        )

        self.args = get_args(
            options=self.options
        )

    def execute(self):
        raise NotImplementedError(
            'You must implement the execute() method yourself!'
        )
