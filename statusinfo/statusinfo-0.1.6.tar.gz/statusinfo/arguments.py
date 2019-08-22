import logging

from argparse import ArgumentParser

from .exception import StatusInfoArgumentException
from .gatherer import METHOD_CHOICES

logger = logging.getLogger('statusinfo')


def parse_arguments():
    method_choices = METHOD_CHOICES.keys()

    parser = ArgumentParser(
        prog='StatusInfo',
        description='A tool for gathering status information.'
    )
    parser.add_argument('widget', type=str, choices=method_choices,
                        help='Widget to display.')
    parser.add_argument('-v', '--debug', action='store_true',
                        help='Print debug information.')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Print errors and warnings only.')
    parser.add_argument('-s', '--space', action='store_true',
                        help='Whether to add space to the right.')
    parser.add_argument('args', nargs='*',
                        help='Additional arguments for the widget.')

    args = parser.parse_args()

    if args.debug and args.quiet:
        msg = 'Cannot be quiet in debug mode.'
        raise StatusInfoArgumentException(msg)

    return args
