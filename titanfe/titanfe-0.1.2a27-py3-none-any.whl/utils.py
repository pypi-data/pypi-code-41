#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""a collection of useful helper functions"""

import importlib.util
import itertools
import socket
import sys
import time
import uuid
from datetime import datetime
from collections.abc import Iterable

import titanfe.log as logging
log = logging.getLogger(__name__)


def first(iterable, default=None, key=None):
    """Return first element of *iterable* that evaluates to ``True``, else
    return ``None`` or optional *default*. Similar to :func:`one`.

    >>> first([0, False, None, [], (), 42])
    42
    >>> first([0, False, None, [], ()]) is None
    True
    >>> first([0, False, None, [], ()], default='ohai')
    'ohai'
    >>> import re
    >>> m = first(re.match(regex, 'abc') for regex in ['b.*', 'a(.*)'])
    >>> m.group(1)
    'bc'

    The optional *key* argument specifies a one-argument predicate function
    like that used for *filter()*.  The *key* argument, if supplied, should be
    in keyword form. For example, finding the first even number in an iterable:

    >>> first([1, 1, 3, 4, 5], key=lambda x: x % 2 == 0)
    4

    By Hynek Schlawack, author of `the original standalone module`_.

    .. _the original standalone module: https://github.com/hynek/first
    """
    return next(iter(filter(key, iterable)), default)


def flatten(iterable):
    """``flatten`` yields all the elements from *iterable* while collapsing any nested iterables.

    >>> nested = [[1, 2], [[3], [4, 5]]]
    >>> list(flatten(nested))
    [1, 2, 3, 4, 5]
    """
    for item in iterable:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for subitem in flatten(item):
                yield subitem
        else:
            yield item


def pairwise(iterable):
    # pylint: disable=invalid-name
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def create_uid(prefix=""):
    return prefix + uuid.uuid4().hex[:8]


def iso_unc_time_string():
    return datetime.utcnow().isoformat()


def ns_to_ms(ns):
    return ns / 1_000_000


def time_delta_in_ms(time_ns):
    return ns_to_ms(time.time_ns() - time_ns)


def get_module(location):
    """ Get the Brick content module

    If the Brick content module cannot be found, None is returned.

    Returns:
        (module or None): The loaded Brick content module
    """
    log.debug("load module: %s", location)

    name = "titanfe.bricks." + location.stem

    module = sys.modules.get(name)
    if module:
        log.debug("module %s already loaded.", name)
        return module

    try:
        if location.is_file():
            spec = importlib.util.spec_from_file_location(name, str(location))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[name] = module
        else:
            # the given location is a module
            module = importlib.import_module(str(location))

    except Exception:  # pylint: disable=broad-except
        log.error("loading module failed: name: %r, location: %r", name, location, exc_info=True)

    return module


def get_ip_address() -> str:
    """try to get the public IPv4 address"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # pylint: disable=invalid-name
        try:
            # UDP, this will only prepare but not actually send anything
            s.connect(("255.255.255.255", 1))
            return s.getsockname()[0]
        except Exception:  # pylint: disable=broad-except
            return "127.0.0.1"


class Timer:
    """ a simple Timer using the performance counters from the "time"-module

    >>> with Timer() as t:
    >>>    # do_something()
    >>>    print(t.elapsed)
    >>>    # do_something_else()
    >>>    print(t.elapsed)
    >>>    print(t.elapsed_total)
    """

    def __init__(self):
        self.start_proc = time.process_time_ns()
        self.start_perf = time.perf_counter_ns()
        self.last_proc = self.start_proc
        self.last_perf = self.start_perf

    @property
    def perf_counter_total(self):
        return time_delta_in_ms(self.start_perf)

    @property
    def process_time_total(self):
        return time_delta_in_ms(self.start_proc)

    @property
    def perf_counter_since_last(self):
        return time_delta_in_ms(self.last_perf)

    @property
    def process_time_since_last(self):
        return time_delta_in_ms(self.last_proc)

    @property
    def __elapsed_since_last(self):
        return f"perf: {self.perf_counter_since_last} ms  (proc: {self.process_time_since_last} ms)"

    @property
    def elapsed_total(self):
        return f"perf: {self.perf_counter_total} ms  (proc: {self.process_time_total} ms)"

    def update_last_access(self):
        self.last_proc = time.process_time_ns()
        self.last_perf = time.perf_counter_ns()

    @property
    def elapsed(self):
        since_last = self.__elapsed_since_last
        self.update_last_access()
        return since_last
