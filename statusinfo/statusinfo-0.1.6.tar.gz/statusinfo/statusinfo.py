import logging
import sys

from .arguments import parse_arguments
from .exception import StatusInfoArgumentException
from .gatherer import METHOD_CHOICES
from .logging import setup_logger

logger = logging.getLogger('statusinfo')


def main():
    setup_logger(logger)

    try:
        args = parse_arguments()
    except StatusInfoArgumentException as e:
        msg = 'Failed to parse arguments: ' + str(e)
        logger.error(msg)
        exit(1)

    if args.debug:
        logger.setLevel(logging.DEBUG)
        msg = 'Application is running in debug mode.'
        logger.debug(msg)
    elif args.quiet:
        logger.setLevel(logging.WARNING)

    logger.info('Starting StatusInfo.')

    choices = METHOD_CHOICES

    if args.space:
        space = ' ' * 3
    else:
        space = ''

    widget = choices[args.widget]
    icon, data = widget(args.args)
    out = '{icon}  {data}{space}'.format(icon=icon, data=data, space=space)
    sys.stdout.write(out)
