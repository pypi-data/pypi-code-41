# /**
#  * Copyright (c) Samsung, Inc. and its affiliates.
#  *
#  * This source code is licensed under the RESTRICTED license found in the
#  * LICENSE file in the root directory of this source tree.
#  */
import types
import os
import sys
from . import job_handler
from . import utils


class Pool:

    def __init__(self, processes=None):

        if sys.version_info >= (3, 0):
            os.system('pip3 freeze > requirements.txt')
        else:
            os.system('pip2 freeze > requirements.txt')

    def map(self, func, iterable, chunksize=None):

        try:
            iter(iterable)
        except TypeError:
            raise ValueError("iterable must be of iterable type")

        return self._map(func, iterable, utils.get_map_args_type(), chunksize)

    def _map(self, func, iterable, args_types=False, chunksize=None):

        if not isinstance(func, types.FunctionType) and not isinstance(func, types.BuiltinFunctionType):
            raise ValueError("target must be a function")

        self._job_name = utils.get_unique_job_name(func.__name__)
        func = func
        job_id = ''
        job_status = 'JobStatus.init'
        results = ['' for arg in (iterable)]

        # 'add' the job
        is_success_result = job_handler.add_job(self._job_name, func, iterable, args_types, True)

        # Get the Results
        if is_success_result:
            get_results = job_handler.get_results(self._job_name)
            results = get_results if (get_results != []) else results
        return results

    def starmap(self, func, iterable, chunksize=None):
        try:
            iter(iterable)
        except TypeError:
            raise ValueError("iterable must be of iterable type")

        try:
            for elem in iterable:
                iter(elem)

        except TypeError:
            raise ValueError("elements of the `iterable` are expected to be iterables as well")

        return self._map(func, iterable, utils.get_starmap_args_type(), chunksize)

    def close(self):
        return

    def terminate(self):
        return

    def join(self):
        raise NotImplementedError

    def apply(self, func, args=(), kwds={}):
        raise NotImplementedError

    def apply_async(self, func, args=(), kwds={}, callback=None,
                    error_callback=None):
        raise NotImplementedError

    def map_async(self, func, iterable, chunksize=None, callback=None,
                  error_callback=None):
        raise NotImplementedError

    def starmap_async(self, func, iterable, chunksize=None, callback=None,
                      error_callback=None):
        raise NotImplementedError

    def imap(self, func, iterable, chunksize=1):
        raise NotImplementedError

    def imap_unordered(self, func, iterable, chunksize=1):
        raise NotImplementedError

    @property
    def job_name(self):
        return self._job_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()
