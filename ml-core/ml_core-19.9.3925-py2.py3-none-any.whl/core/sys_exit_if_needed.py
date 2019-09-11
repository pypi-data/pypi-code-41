# -*- coding: utf-8 -*-
import contextlib
import sys


@contextlib.contextmanager
def sys_exit_if_needed(throw_exception=False, exit_code=1):
    yield throw_exception

    if not throw_exception:
        sys.exit(exit_code)
