# coding=utf-8
from os import access, chmod, linesep, W_OK
from os.path import exists
from shutil import rmtree
from stat import S_IWUSR
from typing import Any, Callable, TypeVar

from ._core import log


ResultType = TypeVar('ResultType')


def _error_handler(_function, path, _):
    # type: (Callable[[str], ResultType], str, Any) -> ResultType
    log.debug('Unable to invoke shutil.rmtree on ' + path)

    if access(path, W_OK):
        # If the user has access, then not sure why rmtree failed. Re-raise the exception
        log.debug("User has access to {}. Re-raising exception.".format(path))

        # This is called inside of an exception handler, so there is indeed an exception to re-raise
        raise

    log.debug("Attempting to change access to {}...".format(path))
    chmod(path, S_IWUSR)
    log.debug('...access changed successfully. Re-invoking rmtree...')

    return _function(path)


def remove_directory(directory, raise_exceptions=True):
    # type: (str, bool) -> bool
    if not exists(directory):
        return True

    # noinspection PyBroadException
    try:
        log.debug('Attempting to remove directory: ' + directory)
        rmtree(directory, onerror=_error_handler)
        log.info('Directory removed: ' + directory)

        return True
    except BaseException as exception:
        log.error("Unable to remove directory: {}{}\t{}".format(
            directory, linesep, repr(exception)))
        if raise_exceptions:
            raise

        return False
