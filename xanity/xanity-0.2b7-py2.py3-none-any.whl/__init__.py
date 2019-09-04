# -*- coding: utf-8 -*-
#
# Copyright 2018 Barry Muldrey
#
# This file is part of xanity.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

__version__ = "0.2b7"            # this is the definitive version for distribution
__author__ = "Barry Muldrey"
__copyright__ = "Copyright 2018"
__license__ = "GNU Affero GPL"
__maintainer__ = "Barry Muldrey"
__email__ = "barry@muldrey.net"
__status__ = "Beta"
__credits__ = []


import traceback
import time

from .Xanity import Xanity as _XanityClass

xanity = None
run_id = None


def new_xanity_session():
    global xanity, run_id
    # have to set placeholders because modules which import
    # xanity might have to be imported during the creation of the Xanity object

    xanity = _XanityClass()
    run_id = str(xanity.run_id)
    # # the following will replace the 'xanity' module with the _xanity object:

    # del sys.modules['xanity']
    # sys.modules['xanity'] = _xanity


if 'xanity' not in globals():
    new_xanity_session()


from .constants import ACTIVITIES
from .common import get_external_caller, pickle_load
from .constants import EXPERIMENT_LOG_HEADER
from .data import fetch_variable, fetch_timer_data, load_data, scan_logs

# check frame, register import, check_invocation
tb = traceback.extract_stack(limit=15)
for frame in tb:
    if 'import xanity' in frame[3]:
        xanity._register_import(frame[0])
        break

# thismodule = sys.modules[__name__]


def experiment_parameters(*args, **kwargs):
    return xanity.experiment_parameters(*args, **kwargs)


def associated_experiments(*args, **kwargs):
    return xanity.associated_experiments(*args, **kwargs)


def log(*args, **kwargs):
    return xanity.log(*args, **kwargs)


def save_variable(*args, **kwargs):
    return xanity.save_variable(*args, **kwargs)


def load_variable(*args, **kwargs):
    return xanity.load_variable(*args, **kwargs)


def analyze_this(*args, **kwargs):
    return xanity.analyze_this(*args, **kwargs)


def checkpoint(*args, **kwargs):
    return xanity.checkpoint(*args, **kwargs)


def load_checkpoint(checkpoint_name, variables=None, overwrite=False, noload=False):
    return xanity.load_checkpoint(checkpoint_name, variables, overwrite=overwrite, noload=noload)


def save_checkpoint(checkpoint_name, variables=None, cwd=True, overwrite=False):
    return xanity.save_checkpoint(checkpoint_name, variables, cwd, overwrite)


def persistent(*args, **kwargs):
    return xanity.persistent(*args, **kwargs)


def persistent_file(*args, **kwargs):
    return xanity.persistent_file(*args, **kwargs)


def report_status(*args, **kwargs):
    return xanity.report_status(*args, **kwargs)


def run(*args, **kwargs):
    return xanity.run(*args, **kwargs)


def metarun(*args, **kwargs):
    return xanity.metarun(*args, **kwargs)


def find_recent_data(*args, **kwargs):
    return xanity.find_recent_data(*args, **kwargs)


def status():
    return xanity.status


def project_root():
    return xanity.project_root


def trials(*args, **kwargs):
    return xanity.trials(*args, **kwargs)


# def _rcfile():
#     return xanity._rcfile


# def _env_path(*args, **kwargs):
#     return xanity._env_path


def find_file(*args, **kwargs):
    return xanity.find_file(*args, **kwargs)


def subdir(*args, **kwargs):
    return xanity.subdir(*args, **kwargs)


def shell_prelude(value=None):
    if value is None:
        return xanity.shell_prelude
    else:
        xanity.shell_prelude = value


def subprocess(call):
    return xanity.subprocess(call)


def interactive_session():
    return xanity._interactive_session()


def timed_fn(fn):

    def wrapped(*args, **kwargs):

        xanity.log('[timed_fn][{}][start]'.format(fn.__name__))
        starttime = time.time()

        results = fn(*args, **kwargs)

        elapsed = time.time() - starttime
        xanity.log('[timed_fn][{}][done] {} s'.format(fn.__name__, elapsed))

        td = xanity.timed_fn_results
        if fn.__name__ in td:
            val = td[fn.__name__] + [elapsed]
        else:
            val = [elapsed]

        td.update({fn.__name__: val})
        xanity.save_variable(td, name='xanity_timed_fn_dict')

        return results

    return wrapped



