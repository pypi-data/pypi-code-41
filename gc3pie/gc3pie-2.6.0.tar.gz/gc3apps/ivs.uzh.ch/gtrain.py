#! /usr/bin/env python
#
#   ggamess.py -- Front-end script for submitting multiple GAMESS jobs to SMSCG.
#
#   Copyright (C) 2010-2012  University of Zurich. All rights reserved.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Front-end script for submitting multiple GAMESS jobs to SMSCG.
It uses the generic `gc3libs.cmdline.SessionBasedScript` framework.

See the output of ``ggamess --help`` for program usage instructions.
"""
# summary of user-visible changes
__changelog__ = """
  2017-11-09:
    * Initial release.
"""
__author__ = 'Riccardo Murri <riccardo.murri@uzh.ch>'
__docformat__ = 'reStructuredText'


# stdlib imports
import os
import sys

# GC3Pie imports
import gc3libs
from gc3libs import Application
from gc3libs.cmdline import SessionBasedScript, existing_file
from gc3libs.quantity import days

# run script, but allow GC3Pie persistence module to access classes defined here;
# for details, see: https://github.com/uzh/gc3pie/issues/95
if __name__ == '__main__':
    import gtrain
    gtrain.GtrainScript().run()


class GtrainScript(SessionBasedScript):
    """
Given a list of directories, each containing a `train.conllu`, 
a `parse.conllu`, and a word embedding file `vectors.xz`, 
run a parser training job for each, possibly in parallel.

The `gtrain` command keeps a record of jobs (submitted, executed and
pending) in a session file (set name with the '-s' option); at each
invocation of the command, the status of all recorded jobs is updated,
output from finished jobs is collected, and a summary table of all
known jobs is printed.  New jobs are added to the session if new input
files are added to the command line.

Options can specify a maximum number of jobs that should be in
'SUBMITTED' or 'RUNNING' state; `gtrain` will delay submission
of newly-created jobs so that this limit is never exceeded.
    """

    def setup_args(self):
        self.add_param("input_dirs", nargs='+',
                       type=existing_file, default=None,
                       help="Directories with input files.")

    def setup_options(self):
        self.add_param('--config', '-c', default='gtrain.cfg',
                       type=existing_file, help="Configuration file.")
        
    def __init__(self):
        SessionBasedScript.__init__(
            self,
            version='1.0',
        )

    def new_tasks(self, extra):
        # create tasks
        for path in self.params.input_dirs:
	    if path.endswith('/'):
		path = path[:-1]
            if not os.path.isdir(path):
                self.log.warning("Path `%s` is no directory! Skipping.", path)
                continue
            train_file = parse_file = embeddings = None
            for entry in os.listdir(path):
                if entry.endswith('train.conllu'):
                    train_file = os.path.join(path, entry)
                elif entry.endswith('dev.conllu'):
                    parse_file = os.path.join(path, entry)
                elif entry.endswith('vectors.xz'):
                    embeddings = os.path.join(path, entry)
                else:
                    continue
            if train_file is None:
                self.log.warning("Path `%s` does not contain a training file! Ignoring.", path)
            if parse_file is None:
                self.log.warning("Path `%s` does not contain a parsing file! Ignoring.", path)
            if embeddings is None:
                self.log.warning("Path `%s` does not contain a word embedding file! Ignoring.", path)
            # create task(s)
            kw = extra.copy()
            kw['jobname'] = os.path.basename(path)
            kw['inputs'] = {
                train_file: 'train.conllu',
                parse_file: 'parse.conllu',
                embeddings: 'vectors.xz',
                self.params.config: 'train.cfg',
            }
            kw['outputs'] = gc3libs.ANY_OUTPUT
            kw['requested_cores'] = 8
            kw['requested_walltime'] = 7*days
            kw['stdout'] = kw['jobname'] + '.log'
            kw['stderr'] = kw['jobname'] + '.log'
            yield Application(
                ['sh', '-c',
                 '. /home/ubuntu/parser/bin/activate'
                 ' &&'
                 ' mkdir -v config && ln -v /home/ubuntu/parser/src/config/defaults.cfg ./config'
                 ' &&'
                 ' sed -re "s:^train_files = .+:train_files = $PWD/train.conllu:" -i train.cfg'
                 ' &&'
                 ' sed -re "s:^parse_files = .+:parse_files = $PWD/parse.conllu:" -i train.cfg'
                 ' &&'
                 ' sed -re "s:^filename = .+:filename = $PWD/vectors.xz:" -i train.cfg'
                 ' &&'
                 ' python /home/ubuntu/parser/src/main.py --save_dir ./output train --config_file train.cfg'],
                **kw
            )
