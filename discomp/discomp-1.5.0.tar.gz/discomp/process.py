# /**
#  * Copyright (c) Samsung, Inc. and its affiliates.
#  *
#  * This source code is licensed under the RESTRICTED license found in the
#  * LICENSE file in the root directory of this source tree.
#  */
import types
import sys
import os
from . import utils
from . import job_handler


class Process:

    def __init__(self, name, target, args=()):
        if not isinstance(name, str):
            raise ValueError("name must be a string")

        if not isinstance(target, types.FunctionType) and not isinstance(target, types.BuiltinFunctionType):
            raise ValueError("target must be a function")

        if not isinstance(args, tuple):
            raise ValueError("args must be a tuple")

        if sys.version_info >= (3, 0):
            os.system('pip3 freeze > requirements.txt')
        else:
            os.system('pip2 freeze > requirements.txt')

        self._job_name = utils.get_unique_job_name(name)
        self._func = target
        self._args = tuple(args)
        self._job_id = ''
        self._job_status = 'JobStatus.init'

        # add the job
        self._job_id = job_handler.add_job(self._job_name, self._func, self._args, utils.get_process_args_type())
        if (self._job_id):
            self._job_status = 'JobStatus.created'

    def start(self):
        # start the job
        if self._job_status == 'JobStatus.created':
            retcode = job_handler.start_job(self._job_id)
            if retcode:
                self._job_status = 'JobStatus.started'

    def join(self, timeout=None):
        # wait for job done
        assert timeout is None, 'Currently join with timeout is not supported'

        if self._job_status == 'JobStatus.started':
            retcode = job_handler.wait_for_job_done(self._job_id)
            self._job_status = 'JobStatus.done'

    def terminate(self):
        raise NotImplementedError

    def kill(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def is_alive(self):
        if self._job_status != 'JobStatus.init':
            return True
        return False

    @property
    def job_name(self):
        return self._job_name

    @property
    def job_id(self):
        return self._job_id

    @property
    def job_status(self):
        return self._job_status
