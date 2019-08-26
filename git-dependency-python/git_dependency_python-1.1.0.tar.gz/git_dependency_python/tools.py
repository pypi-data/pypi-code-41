import logging
import errno
import subprocess
import traceback
import sys, os

from contextlib import contextmanager

logr = logging.getLogger(__name__)


def create_dir(path):
    # type: (str) -> None
    """
    Creates a directory.

    :param path: path to the directory to be created.

    :return:
    """
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        # Guard against race condition.
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise


def log_subprocess_err(msg, ex):
    # type: (str, subprocess.CalledProcessError) -> None
    logr.error(
        '{}. '
        'Output: {}. '
        'Exception representation: {}. '
        'Exit code: {}. '
        'Trace: {}.'.format(msg, ex.output, repr(ex), ex.returncode, traceback.format_exc())
    )


@contextmanager
def suppress_stdout():
    # type: () -> None
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            try:
                sys.stdout = old_stdout
            except ValueError as ex:
                logr.error('Failed to reattach stdout. Reason: {}.'.format(repr(ex)))
