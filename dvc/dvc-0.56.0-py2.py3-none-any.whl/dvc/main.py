"""Main entry point for dvc CLI."""

from __future__ import unicode_literals

import logging

from dvc.cli import parse_args
from dvc.config import ConfigError
from dvc.analytics import Analytics
from dvc.exceptions import NotDvcRepoError, DvcParserError
from dvc.remote.pool import close_pools


logger = logging.getLogger("dvc")


def main(argv=None):
    """Run dvc CLI command.

    Args:
        argv: optional list of arguments to parse. sys.argv is used by default.

    Returns:
        int: command's return code.
    """
    args = None
    cmd = None

    outerLogLevel = logger.level
    try:
        args = parse_args(argv)

        if args.quiet:
            logger.setLevel(logging.CRITICAL)

        elif args.verbose:
            logger.setLevel(logging.DEBUG)

        cmd = args.func(args)
        ret = cmd.run_cmd()
    except ConfigError:
        logger.exception("configuration error")
        ret = 251
    except KeyboardInterrupt:
        logger.exception("interrupted by the user")
        ret = 252
    except NotDvcRepoError:
        logger.exception("")
        ret = 253
    except DvcParserError:
        ret = 254
    except Exception:  # pylint: disable=broad-except
        logger.exception("unexpected error")
        ret = 255
    finally:
        logger.setLevel(outerLogLevel)
        # Python 2 fails to close these clean occasionally and users see
        # weird error messages, so we do it manually
        close_pools()

    Analytics().send_cmd(cmd, args, ret)

    return ret
