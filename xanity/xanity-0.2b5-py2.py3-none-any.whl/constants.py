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

from .common import ConstantSet, CommandSet

SOURCE_IGNORE = [
    '/data/runs',
    '/data/saved',
    '/data/persistent/persist_lib',
    '/.xanity',
    '/.git',
    '/.idea',
]

RELATIVE_PATHS = ConstantSet({
    'src': 'src/',
    'include': 'include/',
    'experiments': 'experiments/',
    'analyses': 'analyses/',
    'run_data': 'data/runs/',
    # 'run_data_by_time': 'data/runs/by_time',
    # 'run_data_by_experiment': 'data/runs/by_experiment',
    'persistent_data': 'data/persistent/',
    'saved_data': 'data/saved/',
    'project_root': '/',
    'xanity_data': '.xanity/',
    'checkpoints': 'data/checkpoints/',
    'tmp': '.xanity/tmp/',
})

XANITY_FILES = ConstantSet({
    'conda_env': '.xanity/conda_env',
    'conda_env_file': 'conda_environment.yaml',
    'conda_hash': '.xanity/conda.md5',
    'env_hash': '.xanity/env_state.md5',
    'rcfile': '.xanity/bashrc',
    'shell_prelude': '.xanity/shell_prelude',
    'shell_conclude': '.xanity/shell_conclude',
    'last_source_hash': '.xanity/last_source_hash',
    'last_pip_hash': '.xanity/last_pip_hash',
})


ACTIVITIES = ConstantSet({
    'CONSTRUCT':  'const',  # only during constructor call
    'ORIENT': 'orient',     # only while orienting  !! this should be the only opportunity for recursive calls
    'RUN':    'run',        # only during _absolute_trip()
    'ABORT':  'abort',      # signals a fatal error
    'DEL':    'del',        # during call to __del__()
    'EXTERNAL': 'ext',      # handling an external invocation
    'INTERNAL': 'int',      # unspecified moments... inside xanity
    'MOD_LOAD': 'lm',       # loading a live module obj...  !! also an opportunity for recursive calls
    'EXP': 'exp',           # during experimentation
    'ANAL': 'anal',         # during analysis
    'GLOBAL': 'global'      # universal
})

DIRNAMES = ConstantSet({
    'SAVED_VARS': "xanity_variables",
    'RUN_PARAMETERS': 'xanity_parameters.dill',
    'LOG_SUFFIX': '.xanity.log',
    'SELF_REPLICATION': 'xanity_self_replication',
    'XANITY_INFO': 'xanity_info',
})


INVOCATION = ConstantSet({
    'COMMAND': 'module_command',
    'HOOK': 'hook',
    'IMPORT': 'import',
})

EXPERIMENT_LOG_HEADER =\
    "\n\n"\
    "################################################################################\n"\
    "## \n"\
    "##   starting experiment #{} ({}/{}) \'{}\'\n"\
    "##   {}\n"\
    "## \n"\
    "################################################################################\n"\
    "\n"\

RUN_DIR_REGEX = r'^(\d{4}-\d{2}-\d{2}-\d{6}(?:-debug)?)_(\S*)_(\d+)$'
LOG_FORMAT = 'self.run_id + \':%(created)s:[xanity]: %(message)s\''
