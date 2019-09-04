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
"""
This is the central file of 'xanity'.
"""
import tarfile
import gc
import os
import logging
import sys
import time
import traceback
import cProfile as profile
import datetime
import inspect
import subprocess
import argparse
import shutil

from pyparsing import nestedExpr
from bdb import BdbQuit
from shlex import split as shsplit

from .common import Status, Analysis, Experiment, ConstantSet, CommandSet
from .common import XanityDeprecationError, XanityNoProjectRootError, XanityNotOrientedError, XanityUnknownActivityError
from .common import digest_file, digest_string, digest_path
from .common import pickle_dump, pickle_load, file2mod, list_modules_at_path, get_arg_names
from .common import get_external_caller
from .constants import RELATIVE_PATHS, ACTIVITIES, DIRNAMES, XANITY_FILES, INVOCATION, SOURCE_IGNORE
from .constants import EXPERIMENT_LOG_HEADER
from .constants import RUN_DIR_REGEX, LOG_FORMAT

# xanity_exe_path = resource_filename('xanity', '/bin')
# if 'PATH' in os.environ:
#     os.environ['PATH'] = xanity_exe_path + ':' + os.environ['PATH']
# else:
#     os.environ['PATH'] = xanity_exe_path

if sys.version_info.major == 2:
    import imp
    from codecs import open

    PY_SYSVER = 2

elif sys.version_info.major == 3:
    import importlib

    PY_SYSVER = 3

invocation = None


class ContextDecorator:
    def __init__(self, context):
        self.context = context

    def __call__(self, f):
        def f_wrapped(xanity, *args, **kwargs):
            if ACTIVITIES is not None and hasattr(ACTIVITIES, 'EXTERNAL') and self.context == ACTIVITIES.EXTERNAL:
                xanity._register_external_access(get_external_caller(context_decorator=True))

            with xanity.status.act_tags(self.context):
                result = f(xanity, *args, **kwargs)

            return result

        return f_wrapped


# class CheckpointManager(object):
#     def __init__(self, xanity, names, tvars=None):
#         self.names = names
#         self.vars = tvars
#         self.xanity = xanity
#
#     def __enter__(self):
#         res = self.xanity.load_checkpoint(self.names)
#         if all([r is not None for r in res]):
#             return Exit
#         else:
#             yield
#
#     def __exit__(exc_type, exc_val, exc_tb):

class RunRootParser(argparse.ArgumentParser):
    def __init__(self):
        super(RunRootParser, self).__init__(prog='xanity-run', add_help=False, usage='adfasdf', )
        self.add_argument('action')

    def parse_known_args(self, args=None):

        # if xanity.invocation == INVOCATION.HOOK:
        #     parser.add_argument('action', nargs='?', help='available actions include: {}'.format(RUN_COMMANDS))
        # else:
        #     parser.add_argument('action', help='available actions include: {}'.format(RUN_COMMANDS))

        args, unknownargs = super(RunRootParser, self).parse_known_args(args)

        # if action_arg.action not in RUN_COMMANDS and xanity.invocation == INVOCATION.HOOK:
        #     # a hook call should have clargs !
        #     raise NotImplementedError
        #     # hook_action = xanity._resolve_action_from_hook()
        #     # action_arg.action = hook_action
        # else:
        #     hook_action = False

        if args.action in RUN_COMMANDS.run:
            # 'run' command parser
            vars(args).update(vars(RunParser().parse_args(unknownargs)))

        elif args.action in RUN_COMMANDS.analyze:
            vars(args).update(vars(AnalParser().parse_args(unknownargs)))

        elif args.action.lower() == 'help':
            self.print_help()
            self.exit()

        # else:
        #     print('didn\'t recognize that command. Use \'xanity help\' for help.')
        #     raise SystemExit(1)

        # args, unknownargs = parser.parse_known_args(list_to_parse) if list_to_parse else parser.parse_known_args()
        # args.action = hook_action if hook_action else args.action

        return args, unknownargs


class AnalParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(AnalParser, self).__init__(*args, **kwargs)
        self.add_argument('runid', nargs='*',
                          help='specify the data-path to analyze')
        self.add_argument('-a', '--analyses', nargs='*',
                          help="""list of explicit analyses to run""")
        self.add_argument('--debug', action='store_true',
                          help='run experiment in debugging mode; experiment code may print additional output'
                               ' or behave differently')
        self.add_argument('--logging', action='store_true',
                          help='request experiment perform additional logging')
        self.add_argument('--profile', action='store_true',
                          help='run cProfile attatched to your experiment')


class RunParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(RunParser, self).__init__(*args, **kwargs)
        self.add_argument('experiments', nargs='*',
                          help='specify the experiments to run')
        self.add_argument('-D', '--directory', action='store')
        self.add_argument('--initialize', action='store_true', help='run xanity init before experiments')
        self.add_argument('--setup', action='store_true', help='run xanity setup before experiments')
        self.add_argument('-p', '--parameter', action='append')
        self.add_argument('-a', '--and-analyze', nargs='*',
                          help="request that data be analyzed upon completion of experiment")
        self.add_argument('--debug', action='store_true',
                          help='run experiment in debugging mode; experiment code may print additional output'
                               ' or behave differently')
        self.add_argument('--logging', action='store_true',
                          help='request experiment perform additional logging')
        self.add_argument('--loadcp', action='store_true',
                          help='request experiment look for and load stored checkpoints from src/include/persistent'
                               ' rather than start from scratch')
        self.add_argument('--savecp', action='store_true',
                          help='request experiment try to save checkpoints to src/include/persistent'
                               ' (will NOT overwrite)')
        self.add_argument('--checkpoints', action='store_true')
        self.add_argument('--profile', action='store_true',
                          help='run cProfile attatched to your experiment')
        self.add_argument('--count', '-c', type=int, default=1, help="will run the experiment(s) multiple times")

    def parse_known_args(self, *args):

        args, unknownargs = super(RunParser, self).parse_known_args(*args)
        if args.experiments == ['help']:
            self.print_usage()
            raise SystemExit
        return args, unknownargs


class Xanity(object):

    def __init__(self):
        self.status = Status()

        with self.status.act_tags(ACTIVITIES.CONSTRUCT):
            self.start_time = time.localtime()
            self.run_id = time.strftime('%Y-%m-%d-%H%M%S', self.start_time)
            self.project_root = None
            self._env_path = None
            self.name = ''
            self.paths = None
            self.conf_files = None
            # self.uuid = ''
            self.action = None
            self.invoker = None
            self.callers = set()
            self.importers = set()
            self._registered_associations = {}
            self._exps_requesting_analysis = set()
            self._exp_paramset_requests = {}
            self._trial_requests = {}
            self.invocation = None

            self.avail_experiments = {}
            self.avail_analyses = {}
            self.experiments = {}
            self.analyses = {}
            # self.anal_data_dirs = []

            self._init_logger()
            self._oriented = False
            self._requests_resolved = False
            self._has_run = False
            self.timed_fn_results = None

    @ContextDecorator(ACTIVITIES.DEL)
    def __del__(self):
        # print('(xanity instance deleted)')
        pass

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _parse_args(self, clargs=None):
        """ parse MODULE arguments """

        if self.invocation == INVOCATION.HOOK:
            if clargs is None:
                clargs = []

                if self.invoker is not None:
                    caller = self.invoker
                elif len(self.callers) == 1:
                    caller = list(self.callers)[0]
                else:
                    import ipdb
                    ipdb.set_trace()

                if caller in [exp.module_path for exp in self.avail_experiments.values()]:
                    clargs.extend([RUN_COMMANDS.run.name, file2mod(caller)])

                elif caller in [anal.module_path for anal in self.avail_analyses.values()]:
                    clargs.extend([RUN_COMMANDS.analyze.name, '-a', file2mod(caller)])

            clargs.extend(sys.argv[1:])  # pickup any commandline args

        self.args, self.unknownargs = RunRootParser().parse_known_args(args=clargs)
        # if len(unknownargs) > 0:
        #     print('did not recognize "{}"'.format(*unknownargs))
        #     raise SystemExit

        if self.args.action in RUN_COMMANDS.run and self.args.checkpoints:
            self.args.savecp = True
            self.args.loadcp = True

        if self.args.action not in RUN_COMMANDS and self.args.action in dir(self):
            self.action = getattr(self, self.args.action)
        else:
            self.action = self.args.action

        # else:
        #     raise XanityUnknownActivityError

        # else:
        #     print('\nunknown or missing xanity action')
        #     raise SystemExit(1)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _purge_registered_associations(self):
        """ parse requested action_objects and options"""
        if not self.project_root:
            raise XanityNoProjectRootError
        # upstream activities may have added items that analyses are incapable of handling: remove them

        for ra in self.analyses.values():
            del_keys = []
            if any([ra.name in nali for nali in self._registered_associations.keys()]):
                for e in ra.experiments.values():
                    if e.name not in self._registered_associations[ra.name]:
                        del_keys.append(e.name)

            for key in del_keys:
                del ra.experiments[key]

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _resolve_associations(self):
        """ parse requested action_objects and options"""
        if not self.project_root:
            raise XanityNoProjectRootError

        # first, resolve declared associations
        for anal, exps in self._registered_associations.items():
            # self._trip_hooks(anal, 'associated_experiments')
            self.avail_analyses[anal].experiments.update({exp: self.avail_experiments[exp] for exp in exps})
            [self.avail_experiments[exp].analyses.update({anal: self.avail_analyses[anal]}) for exp in exps]

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _purge_dangling_experiments(self):
        # remove experiments from analyses
        if self.action in RUN_COMMANDS.run:
            for anal in self.analyses.values():
                chop = []
                for exp in anal.experiments.values():
                    if exp.name not in self.experiments.keys():
                        chop.append(exp.name)
                for name in chop:
                    del anal.experiments[name]

        elif self.action in RUN_COMMANDS.analyze:
            pass

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _resolve_requests(self):
        """ parse requested action_objects and options"""
        from .data import resolve_data_spec, split_rundir
        if not self.project_root:
            raise XanityNoProjectRootError

        self.experiments = {}
        self.analyses = {}

        # if running, define experiments to run
        if self.action == RUN_COMMANDS.run:
            if hasattr(self.args, 'experiments') and self.args.experiments:
                expreqd = [os.path.split(item)[-1].split('.py')[0] for item in self.args.experiments]
                print('looking for requested experiments: {}'.format(expreqd))

                if not all([item in self.avail_experiments for item in expreqd]):
                    print('couldnt find a requested experiment.')
                    raise SystemExit(1)

                self.experiments = {item: self.avail_experiments[item] for item in expreqd}

            else:
                if self.invocation == INVOCATION.HOOK:
                    cli_mods = [file2mod(fp) for fp in self.callers]
                    if any([climod in self.avail_experiments for climod in cli_mods]):
                        self.experiments = {item: self.avail_experiments[item] for item in cli_mods if
                                            item in self.avail_experiments}
                    else:
                        callmods = [file2mod(fp) for fp in self.callers]
                        if any([clmod in self.avail_experiments for clmod in callmods]):
                            self.experiments = {item: self.avail_experiments[item] for item in callmods if
                                                item in self.avail_experiments}
                else:
                    self.experiments = self.avail_experiments

            if self.args.and_analyze is not None:
                if self.args.and_analyze:
                    analreqd = self.args.and_analyze
                    assert all([item in self.avail_analyses for item in analreqd]), 'couldnt find a requested analysis'
                    self.analyses = {item: self.avail_analyses[item] for item in analreqd}
                else:
                    self.analyses = self.avail_analyses
            else:
                self.analyses = {}

        # if analyzing define anals to run
        elif self.action == RUN_COMMANDS.analyze:

            if self.args.analyses:
                analreqd = self.args.analyses
                if not all([item in self.avail_analyses for item in analreqd]):
                    print('couldn\'t find a requested analysis')
                    raise SystemExit(1)
                self.analyses = {item: self.avail_analyses[item] for item in analreqd}
            else:
                self.analyses = self.avail_analyses

            # self.anal_data_dirs = []

            if self.args.runid:
                for id in self.args.runid:
                    if id in self.avail_experiments:
                        # an experiment was requested
                        # add all experiments (will be removed when resolving associations)
                        [a.experiments.update({id: self.avail_experiments[id]}) for a in self.analyses.values()]
                        # self.anal_data_dirs = xanity_data.get_rundirs(experiment=id)
                        break

                    else:
                        cands = resolve_data_spec(id)
                        for c in cands:
                            run, exp, subexpind = split_rundir(c)
                            if not all([exp in a for a in self.analyses.values()]):
                                [a.experiments.update({exp: self.avail_experiments[exp]}) for a in
                                 self.analyses.values()]
                        # self.anal_data_dirs.extend(cands)
            else:
                # add all experiments (will be removed when resolving associations)
                [a.experiments.update({id: self.avail_experiments[id]}) for a in self.analyses.values() for id in
                 self.avail_experiments.keys()]

        else:
            self.experiments = {}
            self.analyses = {}

        if self.action == RUN_COMMANDS.run:
            # for those experiments requesting analysis, add analyses, if necessary

            # for exp in self.experiments.values():
            #     self._trip_hooks(exp, 'analyze_this')

            for exp in self._exps_requesting_analysis:
                if exp in self.experiments:
                    for anal, anal_it in self.avail_analyses.items():
                        if exp in anal_it.experiments:
                            self.experiments[exp].analyses.update({anal: anal_it})

            if 'parameter' in self.args and self.args.parameter is not None and len(self.args.parameter) > 0:
                pdict = {}

                def seq_dive(item):
                    # item should be either list or str

                    if isinstance(item, str):

                        # could be number
                        if item.isdigit():
                            if '.' not in item:
                                return int(item)
                            else:
                                return float(item)

                        # or sequence
                        elif ',' in item:
                            items = item.split(',')
                            return tuple(seq_dive(iitem) for iitem in items)

                        else:
                            return item

                    elif isinstance(item, list):
                        return [seq_dive(iitem) for iitem in item]

                for string in self.args.parameter:

                    if '=' not in string:
                        print('parameters should be specified in the format: -p name=value')
                        raise SystemExit

                    name, valstring = string.split('=')

                    if '[' in valstring and ']' in valstring:
                        listParser = nestedExpr("[", "]")
                        valstring = listParser.parseString(valstring).asList()[0]

                    valstring = seq_dive(valstring)
                    pdict.update({name: valstring})

                for exp in self.experiments:
                    self._exp_paramset_requests.update({exp: pdict})

        self._requests_resolved = True

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _process_parameters(self):
        """see if any experiments have asked for param-sets """

        if not self._oriented:
            raise XanityNotOrientedError

        # first, get all parameter hooks
        # for exp in self.experiments.values():
        #     self._trip_hooks(exp, 'experiment_parameters')

        self._parse_exp_params()

        for experiment in self.experiments.values():

            # def create_single_subexp_dir():
            #     # create single subexperiment directory
            #     experiment.update({
            #         #'exp_dir': os.path.join(self.paths.run_Data, experiment.name),
            #         'exp_dirs': [os.path.join(self.paths.run_data, experiment.name,
            #                                   '{}_{}_{}'.format(experiment.name, i))],
            #         'success': [False],
            #         'paramsets': [experiment.default_params],
            #     })

            experiment.param_dict = experiment.default_params
            if experiment.name in self._exp_paramset_requests:
                experiment.param_dict.update(self._exp_paramset_requests[experiment.name])

            for key, value in experiment.param_dict.items():
                if not isinstance(value, list):
                    experiment.param_dict[key] = [value, ]

            # get number of subexperiments
            frozen_names = tuple(experiment.param_dict.keys())
            kwlens = [len(experiment.param_dict[name]) for name in frozen_names]
            indmax = [item - 1 for item in kwlens]

            # compose all parameter sets
            indvec = [[0] * len(kwlens)]
            while True:
                tvec = list(indvec[-1])
                if tvec == indmax:
                    break
                tvec[-1] += 1
                for place in reversed(range(len(kwlens))):
                    if tvec[place] > indmax[place]:
                        if place == 0:
                            break
                        else:
                            tvec[place - 1] += 1
                            tvec[place] = 0

                indvec.append(tvec)
                if indvec[-1] == indmax:
                    break

            psets = [{frozen_names[i]: experiment.param_dict[frozen_names[i]][choice] for i, choice in
                      enumerate(vect)} for vect in indvec]

            # create all the subexperiment info
            if experiment.name in self._trial_requests:
                multiplier = self._trial_requests[experiment.name]
            else:
                multiplier = 1

            count = multiplier * len(psets)
            experiment.update({
                # 'exp_dir': os.path.join(self.exp_data_dir, experiment.name),
                'exp_dirs': [os.path.join(self.paths.run_data, experiment.name,
                                          '{}_{}_{}'.format(self.run_id, experiment.name, i))
                             for i in range(count)],
                'success': [False] * count,
                'paramsets': psets * multiplier,
            })

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _parse_anal_data(self):
        """ unsure... """
        from .data import get_rundirs
        # if self.anal_data_dirs is None:
        #     return

        if self.experiments and self.action == RUN_COMMANDS.run:
            for anal in self.analyses.values():
                rm = []
                for exp in anal.experiments.values():
                    if all([not item for item in exp.success]):
                        rm.append(exp.name)
                for name in rm:
                    del anal.experiments[name]

        elif self.analyses and self.action == RUN_COMMANDS.analyze:
            for anal in self.analyses.values():
                rm = []
                for exp in anal.experiments.values():
                    if not any(get_rundirs(experiments=exp.name, include_saved=True)):
                        rm.append(exp.name)
                for name in rm:
                    del anal.experiments[name]

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _init_logger(self):
        """ setup a logger ... """
        # create logger
        self.logger = logging.getLogger('xanity_logger')
        self.logger.handlers = []
        self.logger.setLevel(logging.DEBUG)

        lsh = logging.StreamHandler(sys.stdout)
        lsh.setFormatter(logging.Formatter(eval(LOG_FORMAT)))
        lsh.setLevel(logging.DEBUG)
        self.logger.addHandler(lsh)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _attach_root_logger_fh(self):
        root_handle = logging.FileHandler(filename=os.path.join(self.paths.tmp, self.run_id + DIRNAMES.LOG_SUFFIX))
        root_handle.setFormatter(logging.Formatter(eval(LOG_FORMAT)))
        root_handle.setLevel(logging.DEBUG)
        self.logger.addHandler(root_handle)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _parse_exp_params(self):
        """ get default parameters """
        malformed = []
        for experiment in self.experiments.values():
            # sig = _get_mainfn_sig(os.path.join(self.paths.experiments, experiment + '.py'))
            if not hasattr(experiment.module, 'main'):
                malformed.append(experiment.name)
            else:
                if PY_SYSVER == 3:
                    sig = inspect.signature(experiment.module.main)
                    experiment.default_params = {parameter.name: parameter.default for parameter in
                                                 sig.parameters.values()}
                elif PY_SYSVER == 2:
                    sig = inspect.getargspec(experiment.module.main)
                    experiment.default_params = {parameter: sig.defaults[i]
                                                 for i, parameter in enumerate(sig.args)}
        for exp in malformed:
            if exp in self.avail_experiments:
                del self.avail_experiments[exp]
            if exp in self.experiments:
                del self.experiments[exp]

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _load_required_modules(self):
        """
        docstring
        :return:
        """

        sys.path.append(self.paths.experiments)
        for name, fullpath in [(exp.name, exp.module_path) for exp in self.experiments.values()]:
            self.experiments[name].module = self._get_live_module(fullpath)
        sys.path.remove(self.paths.experiments)

        sys.path.append(self.paths.analyses)
        for name, fullpath in [(anal.name, anal.module_path) for anal in self.analyses.values()]:
            self.analyses[name].module = self._get_live_module(fullpath)
        sys.path.remove(self.paths.analyses)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _parse_avail_modules(self):
        """
        docstring
        :return:
        """
        # self.exp_package = _get_live_package_object(self.paths.experiments)
        # self.anal_package = _get_live_package_object(self.paths.analyses)
        # sys.modules['experiments'] = self.exp_package
        # sys.modules['analyses'] = self.anal_package

        exp_list = self._list_avail_experiments()
        anal_list = self._list_avail_analyses()

        sys.path.append(self.paths.experiments)
        for name, fullpath in exp_list:
            # self.avail_experiments.update({name: Experiment(name, fullpath, importlib.import_module('experiments.'+name))})
            self.avail_experiments.update({name: Experiment(name, fullpath, None)})
        sys.path.remove(self.paths.experiments)

        sys.path.append(self.paths.analyses)
        for name, fullpath in anal_list:
            # self.avail_analyses.update({name: Analysis(name, fullpath, importlib.import_module('analyses.'+name))})
            self.avail_analyses.update({name: Analysis(name, fullpath, None)})
        sys.path.remove(self.paths.analyses)

    @ContextDecorator(ACTIVITIES.ORIENT)
    def _orient(self, clargs=None):
        """
        just-in-time orientation
        :param clargs:
        :return:
        """

        # sensitive ordering
        if not self.project_root:
            self._resolve_xanity_root()

        if clargs is not None:
            # raise XanityUnknownActivityError
            self._parse_args(clargs)

        else:
            if self.action is None:
                self._parse_args(clargs)

        self.run_id += '-debug' if 'debug' in self.args and self.args.debug else ''
        # rundir_sig = '{}-debug' if self.args.debug else '{}'
        # self.exp_data_dir = os.path.join(self.paths.run_data_by_time, rundir_sig.format(self.run_id))
        # self.anal_data_dirs = self.exp_data_dir

        self._oriented = True

    @ContextDecorator(ACTIVITIES.MOD_LOAD)
    def _get_live_module(self, module_path):
        # module_dir = os.path.split(module_path)[0]
        # opwd = os.getcwd()
        # os.chdir(module_dir)
        if self.paths.experiments in module_path:
            sys.path.append(self.paths.experiments)
        elif self.paths.analyses in module_path:
            sys.path.append(self.paths.analyses)

        module_name = file2mod(module_path)
        if PY_SYSVER == 2:
            module = imp.load_source(module_name, module_path)
        else:
            spec = importlib.util.spec_from_file_location(module_name, location=module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _archive_source_tree(self):

        if self.args.debug:
            return None

        archive_file = os.path.join(self.paths.xanity_data, 'source_archive.tar.gz')
        last_hash_file = self.conf_files.last_source_hash

        if os.path.isfile(archive_file) and os.path.isfile(last_hash_file):
            current_hash = digest_path(self.paths.experiments)
            if current_hash == open(last_hash_file, 'r').read():
                self.log('reusing existing source archive')
                return archive_file

        self.log('creating archive of source code')
        filterfn = lambda tarinfo: None if any([pattern in tarinfo.name for pattern in SOURCE_IGNORE]) \
            else tarinfo

        with tarfile.open(archive_file, mode='w:gz') as tarball:
            tarball.add(self.project_root, arcname=self.project_name, filter=filterfn)

        with open(last_hash_file, 'w+') as f:
            f.write(digest_path(self.paths.experiments))

        return archive_file

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def find_file(self, filename=None, experiment=None, include_debug=False):
        from .data import get_rundirs
        if not experiment:
            if isinstance(self.status.focus, Experiment):
                experiment = self.status.focus.name
            elif isinstance(self.status.focus, Analysis):
                if self.status.focus.experiments:
                    experiment = list(self.status.focus.experiments.values())[0].name

        if not filename:
            return os.path.join(self._find_recent_run_path(experiment), experiment)

        if os.path.isfile(os.path.join(os.getcwd(), filename)):
            return os.path.join(os.getcwd(), filename)

        run_dirs = get_rundirs(experiments=experiment, include_saved=True, include_debug=include_debug)

        cands = []

        for ddir in run_dirs:
            if filename in os.listdir(ddir):
                cands.append(ddir)

        cands.sort()
        return [os.path.join(item, filename) for item in cands] if cands else None

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def find_recent_data(self):
        return self._find_recent_run_path()

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _find_recent_run_path(self, experiment_names=None):

        if experiment_names is None:
            expnames = set()
            for anal in self.analyses.values():
                expnames.update([exp.name for exp in anal.experiments.values()])

        else:
            expnames = experiment_names if not isinstance(experiment_names, str) else [experiment_names]

        cands = []

        rcands = []
        for dirs, subdirs, files in os.walk(self.paths.run_data_by_time, followlinks=False):
            if any([subdir in expnames for subdir in subdirs]):
                rcands.append(dirs)

        cands.extend(sorted(set(rcands), key=str.lower))

        rcands = []
        for dirs, subdirs, files in os.walk(self.paths.saved_data, followlinks=False):
            if any([subdir in expnames for subdir in subdirs]):
                rcands.append(dirs)

        cands.extend(sorted(set(rcands), key=str.lower))

        if len(cands) > 0:
            print(cands)
            return cands[-1]
        else:
            print('could not find any recent data to analyze')
            return None

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _in_xanity_tree(self, file_or_path=None):
        """returns the root of a xanity tree

        test a file/dir to see if it's in a xanity tree.

        :param file_or_path: hint for searching

        :returns: root of hinted xanity project tree
        """
        result = None

        if not file_or_path:
            file_or_path = os.getcwd()

        else:
            if os.path.isfile(file_or_path):
                file_or_path = os.path.split(file_or_path)[0]
            elif os.path.isdir(file_or_path):
                pass
            else:
                file_or_path = os.getcwd()

        path_parts = file_or_path.split('/')

        for i in range(len(path_parts))[::-1]:
            test_path = '/' + os.path.join(*path_parts[:i + 1])
            if os.path.isdir(os.path.join(test_path, '.xanity')):
                result = test_path
                break

        return result

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _resolve_xanity_root(self):
        """attempts to ground the current xanity within a tree

                look at given disposition and determine a xanity root

                """

        def _populate_root_info(root_path):
            if os.path.isdir(os.path.join(root_path, '.xanity')):
                self.project_root = root_path
                self.project_name = self.project_root.split('/')[-1]
                self.paths = ConstantSet({
                    key: os.path.join(self.project_root, value)
                    for key, value in vars(RELATIVE_PATHS).items()})
                self.conf_files = ConstantSet({
                    key: os.path.join(self.project_root, value)
                    for key, value in vars(XANITY_FILES).items()})
                self._env_path = self.conf_files.conda_env
                # self.uuid = open(self.conf_files.uuid, mode='r').read().strip()
                self._parse_avail_modules()

        result = self._in_xanity_tree()

        if not result:
            print('not presently within a xanity tree')

            # look into 'callers' first, then 'importers' for hints
            cands = set(filter(lambda item: bool(item), [self._in_xanity_tree(hint) for hint in self.callers]))
            if len(cands) > 1:
                print('multiple xanity project roots found... usure what to do')
                raise NotImplementedError
            if len(cands) == 1:
                result = cands.pop()

            if not result:
                # now try importers
                cands = set(filter(lambda item: bool(item), [self._in_xanity_tree(hint) for hint in self.importers]))
                if len(cands) > 1:
                    print('multiple xanity project roots found... usure what to do')
                    raise NotImplementedError
                if len(cands) == 1:
                    result = cands.pop()

                if not result:
                    print('coudn\'t find a relevant xanity project root.  exiting.')
                    raise XanityNoProjectRootError

        _populate_root_info(result)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _register_import(self, caller):
        if caller not in self.callers:
            # self._check_invocation()
            self.importers.add(caller)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _register_external_access(self, caller):
        if caller not in self.callers:
            # self._check_invocation()
            self.callers.add(caller)

    # @ContextDecorator(ACTIVITIES.INTERNAL)
    # def _resolve_action_from_hook(self):
    #     if not self.invocation == INVOCATION.HOOK:
    #         return
    #
    #     votes = []
    #
    #     def sortit(filepath, votes):
    #         caller_name = file2mod(filepath)
    #         if caller_name in self.avail_experiments:
    #             votes.append(RUN_COMMANDS.run)
    #         elif caller_name in self.avail_analyses:
    #             votes.append(RUN_COMMANDS.analyze)
    #
    #     for caller in self.callers:
    #         sortit(caller, votes)
    #
    #     if RUN_COMMANDS.run in votes:
    #         return RUN_COMMANDS.run
    #
    #     elif RUN_COMMANDS.analyze in votes:
    #         return RUN_COMMANDS.analyze
    #     else:
    #         return None

    # @ContextDecorator(ACTIVITIES.INTERNAL)
    # def _check_invocation(self):
    #
    #     invocation = ' '.join(sys.argv)
    #
    #     if invocation.startswith('-m '):
    #         # looks like an import... no useful arguments in sys.argv
    #         self.invocation = INVOCATION.IMPORT
    #         print('import only...')
    #
    #     elif '/xanity/__main__.py ' in invocation or invocation.startswith('xanity'):
    #         # invoked directly -- arg parser will catch everything
    #         self.invocation = INVOCATION.COMMAND
    #         print('called directly')
    #
    #     else:
    #         # started from an import or a hook
    #         # root = self.resolve_xanity_root()
    #
    #         matcher = re.compile(r'((?:[\\/]?\w+)+.py)')
    #         self.invocation_files = matcher.findall(invocation)
    #         self.invocation = INVOCATION.HOOK
    #         print('called from hook')
    #         # if not root:
    #         #     for tfile in self.invocation_files:
    #         #         root = self.resolve_xanity_root(tfile)
    #         #         if root:
    #         #             break
    #         #
    #         # else:
    #         #     self.project_root = root
    #         #     self.called_from_hook = True   # deprecated
    #         #     print('run hook from file')
    #
    #     self._parse_args()

    @ContextDecorator(ACTIVITIES.RUN)
    def _runprep(self):
        pass

    @ContextDecorator(ACTIVITIES.RUN)
    def _absolute_trigger(self):
        """
        docstring
        :return:
        """
        from .environment import check_environment, condabashcmd
        if not self._oriented:
            raise XanityNotOrientedError

        self._resolve_requests()
        self._load_required_modules()
        self._purge_registered_associations()
        self._purge_dangling_experiments()
        self._process_parameters()

        self.n_total_exps = sum([len(item.success) for item in self.experiments.values()])
        self.n_total_anals = sum([len(item.experiments) for item in self.analyses.values()])

        if not check_environment():
            if os.path.isdir(self.conf_files.conda_env):
                try:
                    print('you\'re not in the right env... starting over from the right one...')
                    subprocess.call(condabashcmd('conda activate && {}'.format(' '.join(sys.argv))))

                except Exception:
                    print('\n\n'
                          'looks like you\'re not inside the correct conda environment. \n'
                          'If you\'re using an IDE or calling a script directly, \n'
                          'please be sure you\'re using the python inside the \n'
                          'conda environment at path:\n{}\n\n'.format(self.conf_files.conda_env))
                    raise SystemExit(1)

            else:
                print('you\'re not in the right env and it doesn\'t look like one has been setup.'
                      'Try runing \'xanity setup\'.')

        self._run_basic_prelude()
        if self.experiments:
            self._run_all_exps()
        if self.analyses:
            self._run_all_anals()
        self._has_run = True

    @ContextDecorator(ACTIVITIES.RUN)
    def _interactive_session(self, clargs=None):
        """
        docstring
        :return:
        """
        from .environment import check_environment, check_xanity_ver
        self.invocation = INVOCATION.HOOK
        self.invoker = get_external_caller()
        self._orient(clargs)

        if not self._oriented:
            raise XanityNotOrientedError

        self._resolve_requests()
        self._purge_dangling_experiments()
        # self._load_required_modules()
        # self._resolve_associations()
        self._process_parameters()

        self.n_total_exps = sum([len(item.success) for item in self.experiments.values()])
        self.n_total_anals = sum([len(item.experiments) for item in self.analyses.values()])

        if not check_environment():
            print('\n\n'
                  'looks like you\'re not inside the correct conda environment. \n'
                  'If you\'re using an IDE or calling a script directly, \n'
                  'please be sure you\'re using the python inside the \n'
                  'conda environment at path:\n{}\n\n'.format(self.conf_files.conda_env))
            raise SystemExit(1)
        # if not self.check_conda():
        #     print('\n\n'
        #           'looks like you\'ve made some changes '
        #           'to your conda environment file....\n'
        #           'please issue \'xanity setup\' to resolve the new one')
        #     raise SystemExit(1)

        check_xanity_ver()

        self._run_basic_prelude()
        # if self.experiments:
        #     self._run_all_exps()
        # if self.analyses:
        #     self._run_all_anals()
        # self._has_run = True

    @ContextDecorator(ACTIVITIES.EXP)
    def _make_exp_dirs(self, experiment, index):
        # make directories:
        # if not os.path.isdir(self.paths.run_data_by_time):
        #     os.makedirs(self.paths.run_data_by_time)

        exp_root = os.path.join(experiment.exp_dirs[index])
        xanity_vars = os.path.join(exp_root, DIRNAMES.SAVED_VARS)
        info = os.path.join(exp_root, DIRNAMES.XANITY_INFO)

        try:
            os.makedirs(os.path.join(self.paths.run_data, experiment.name))
        except OSError:
            pass

        try:
            os.makedirs(xanity_vars)
            os.makedirs(info)

        except OSError:
            print('run data directory was already created... something\'s wrong')
            raise SystemExit(1)

        for root, subd, files in os.walk(self.paths.tmp):
            relpath = root.split(self.paths.tmp)[1]

            for sd in subd:
                os.mkdir(os.path.join(experiment.exp_dirs[index], info, relpath, sd))

            for ff in files:
                os.link(os.path.join(root, ff), os.path.join(experiment.exp_dirs[index], info, relpath, ff))

        # # create hardlinks sorted by experiment
        # if not os.path.isdir(os.path.join(
        #         self.paths.run_data_by_experiment,
        #         experiment.name,
        #         experiment.exp_dir.split(os.sep)[-2])):
        #     os.symlink(
        #         experiment.exp_dir,
        #         os.path.join(self.paths.run_data_by_experiment,
        #                      experiment.name,
        #                      experiment.exp_dir.split(os.sep)[-2]),
        #         target_is_directory=True,
        #     )

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_basic_prelude(self):

        # clear .xanity/tmp:
        if os.path.isdir(os.path.join(self.paths.tmp)):
            shutil.rmtree(os.path.join(self.paths.tmp))
        os.mkdir(os.path.join(self.paths.tmp))

        # start writing logs to /.xanity/tmp
        self._attach_root_logger_fh()

        # set global root dirs and do some basic path operations
        os.chdir(self.project_root)

        # create root logger   ### already created during xanity __init__
        # self._init_logger()
        # lsh = logging.StreamHandler(sys.stdout)
        # if self.experiments:
        #     lsh.setFormatter(
        #         logging.Formatter(
        #             self.run_id.split('/')[-1]
        #             + LOG_FORMAT))
        # else:
        #     lsh.setFormatter(logging.Formatter(' %(asctime)s :%(levelname)s: %(message)s'))
        # lsh.setLevel(logging.DEBUG)
        # self.logger.addHandler(lsh)

        # print some info
        self.log(
            '\n'
            '################################################################################\n'
            '## \n'
            '## \'run\' called at {} \n'
            '## {}\n'
            '## xanity_root: {} \n'
            '################################################################################\n'
            '\n'.format(
                datetime.datetime.fromtimestamp(time.mktime(self.start_time)).strftime('%Y-%m-%d %H:%M:%S'),
                vars(self.args),
                self.project_root)
        )

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_exp_prelude(self):
        """
            bunch of meta-level setup for subsequent experiments
        """
        from .environment import dump_pip_requirements, save_conda_snapshot
        if not self.args.debug:
            # dump bookkeeping
            self._archive_source_tree()
            dump_pip_requirements()
            save_conda_snapshot()

        # print number of subexperiments found:
        self.log(
            "\n"
            "################################################################################\n"
            "################################################################################\n"
            "###"
            "###                 going to run {} experiments in total... \n"
            "###\n"
            "################################################################################\n"
            "################################################################################\n".format(
                len(self.experiments))

        )
        for exp in self.experiments.values():
            if len(exp.paramsets) > 1:
                self.log(
                    '\n'
                    '################################################################################\n'
                    '##  experiment: {} has {} subexperiments:\n'.format(exp.name, len(exp.paramsets))
                    + '\n'.join(['##     exp #{}: {}'.format(i, param) for i, param in
                                 enumerate(exp.paramsets)]) + '\n'
                    + '################################################################################'
                )

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_anal_prelude(self):
        pass

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_all_exps(self):
        # do all experiments of interest

        # make data dir --- should be brand spanking new -- but just in case....
        # os.makedirs(self.exp_data_dir, exist_ok=True) if PY_SYSVER == 3 else os.makedirs(self.exp_data_dir)

        self._run_exp_prelude()

        # sys.path.append(self.paths.experiments)
        for experiment in self.experiments.values():
            for index, _ in enumerate(experiment.success):
                try:
                    self._run_one_exp(experiment, index)
                except (KeyboardInterrupt, BdbQuit):
                    break
        # sys.path.remove(self.paths.experiments)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _run_all_anals(self):
        # do all analyses
        self._parse_anal_data()
        # os.makedirs(self.exp_data_dir, exist_ok=True) if PY_SYSVER == 3 else os.makedirs(self.exp_data_dir)
        self._run_anal_prelude()

        # if self.anal_data_dirs:
        #     # for d in self.anal_data_dirs:
        #     # self.anal_data_dirs = d
        #     # sys.path.append(self.paths.analyses)
        #     for anal_ind, analysis in enumerate(self.analyses.values()):
        #         analysis.success = []
        #         for exp_ind, exp in enumerate(analysis.experiments.values()):
        #             self._run_one_anal(analysis, exp, anal_ind, exp_ind)
        #     # sys.path.remove(self.paths.analyses)
        # else:
        for anal_ind, analysis in enumerate(self.analyses.values()):
            analysis.success = []
            for exp_ind, exp in enumerate(analysis.experiments.values()):
                self._run_one_anal(analysis, exp, anal_ind, exp_ind)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _wrap_failed_exp(self):
        experiment = self.status.focus
        experiment.success[self.status.sub_ind] = False
        self.log('experiment {} was NOT successful'.format(experiment.name))
        with open(os.path.join(self.status.data_dir, DIRNAMES.XANITY_INFO, 'unsuccessful'), 'w+') as f:
            pass
        self.save_xanity_obj_panic()

    @ContextDecorator(ACTIVITIES.EXP)
    def _run_one_exp(self, experiment, index):
        self._make_exp_dirs(experiment, index)
        self.status.focus = experiment
        self.status.sub_ind = index
        self.status.parameters = experiment.paramsets[index]
        self.status.data_dir = experiment.exp_dirs[index]
        self.status.xanity_data = os.path.join(self.status.data_dir, DIRNAMES.SAVED_VARS)
        self.timed_fn_results = {}
        # save some stuff..
        self.save_xantiy_status(path=self.status.xanity_data)
        pickle_dump(self.status.parameters, os.path.join(self.status.xanity_data, DIRNAMES.RUN_PARAMETERS))

        # set some environment variablves for the benefit of any downstream shells
        os.environ['XANITY_DEBUG'] = str(self.args.debug)
        os.environ['XANITY_LOGGING'] = str(self.args.logging)
        os.environ['XANITY_DATA_DIR'] = str(experiment.exp_dirs[index])

        # if not self.args.debug:
        tfh = logging.FileHandler(
            filename=os.path.join(
                self.status.data_dir, DIRNAMES.XANITY_INFO,
                self.run_id + '_' + experiment.name + '_' + str(index) + DIRNAMES.LOG_SUFFIX))
        tfh.setFormatter(logging.Formatter(eval(LOG_FORMAT)))
        tfh.setLevel(logging.DEBUG)
        self.logger.addHandler(tfh)

        self.log(EXPERIMENT_LOG_HEADER.format(
            index, index + 1, len(experiment.success), experiment.name, self.status.parameters))

        try:
            opwd = os.getcwd()
            os.chdir(self.status.data_dir)
            sys.path.append(self.paths.experiments)

            if self.args.profile:
                profile.runctx(
                    'module.main(**paramdict)',
                    {},
                    {'module': experiment.module, 'paramdict': self.status.parameters},
                    os.path.join(experiment.subexp_dirs[index], experiment.name + '.profile'))
            else:
                experiment.module.main(**self.status.parameters)

            experiment.success[index] = True
            self.log('experiment {} was successful'.format(experiment.name))
            with open(os.path.join(self.status.data_dir, DIRNAMES.XANITY_INFO, 'successful'), 'w+') as f:
                pass

        except (KeyboardInterrupt, BdbQuit) as the_interrupt:
            self.log('experiment terminated by user.')
            self._wrap_failed_exp()
            raise the_interrupt

        except Exception as e:
            msg = traceback.format_exc()
            if msg is not None:
                self.logger.error(msg)
            self._wrap_failed_exp()

        finally:
            if 'tfh' in locals() and hasattr(self, 'logger'):
                self.logger.removeHandler(tfh)
            os.chdir(opwd)
            sys.path.remove(self.paths.experiments)
            gc.collect()

    @ContextDecorator(ACTIVITIES.ANAL)
    def _run_one_anal(self, analysis, experiment, analysis_ind=None, exp_ind=None):
        self.status.focus = analysis
        self.status.sub_ind = experiment
        # self.status.data_dir = self.anal_data_dirs

        # set some environment variablves for the benefit of any children's shells
        os.environ['XANITY_DEBUG'] = str(self.args.debug)
        os.environ['XANITY_LOGGING'] = str(self.args.logging)
        os.environ['XANITY_DATA_DIR'] = str(self.status.data_dir)

        #        if not self.args.debug:
        #            tfh = logging.FileHandler(
        #               filename=os.path.join(self.analyses[analysis].subexp_dirs[index],
        #               analysis + '.log'))
        #            tfh.setFormatter(logging.Formatter('%(asctime)s :%(levelname)s: %(message)s'))
        #            tfh.setLevel(logging.DEBUG)
        #            self.logger.addHandler(tfh)

        self.log(
            "\n"
            "################################################################################\n"
            "##                                     \n"
            "##  starting analysis:  {} (#{} of {}) \n"
            "##      -  experiment:  {} (#{} of {}) \n"
            "##      - total anals:  {}             \n"
            "################################################################################\n"
            "\n".format(
                analysis.name, analysis_ind + 1, len(self.analyses),
                experiment.name, exp_ind + 1, len(analysis.experiments),
                self.n_total_anals,
            )
        )

        try:
            opwd = os.getcwd()
            os.chdir(self.paths.tmp)
            sys.path.append(self.paths.analyses)

            if self.args.profile:
                profile.runctx(
                    'module.main()',
                    {},
                    {'module': analysis.module},
                    os.path.join(self.status.data_dir, analysis.name + '.profile'))
            else:
                analysis.module.main()

            analysis.success.append(True)
            self.logger.info('analysis {} was successful'.format(analysis.name))


        except KeyboardInterrupt as e:
            self.save_xanity_obj_panic()
            raise e

        except Exception:
            msg = traceback.print_exc()
            if msg is not None:
                self.logger.error(msg)

            analysis.success.append(False)
            self.logger.info('analysis {} was NOT successful'.format(analysis.name))

        finally:
            # if 'tfh' in locals():
            #     self.logger.removeHandler(tfh)
            os.chdir(opwd)
            sys.path.remove(self.paths.analyses)
            gc.collect()

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _list_avail_experiments(self, names=None):
        if not self.project_root:
            raise XanityNoProjectRootError

        return list_modules_at_path(self.paths.experiments, names=names)

    @ContextDecorator(ACTIVITIES.INTERNAL)
    def _list_avail_analyses(self, names=None):
        if not self.project_root:
            raise XanityNoProjectRootError

        return list_modules_at_path(self.paths.analyses, names=names)

    """
    the following private methods are deprecated:
    """

    # def _trip_hooks(self, item, hookname):
    #     """ this will trip all hooks.
    #     they each will check self.status.activity to see whether it's appropriate
    #     to fire"""
    #     raise XanityDeprecationError
    #     # assert hookname in dir(self), 'thats not a hook'
    #     # self.status.tripping = hookname
    #     # self.status.focus = item
    #     # # item.module = importlib.reload(item.module)
    #     # self._get_live_module(item.module_path)
    #     # self.status.focus = None
    #     # self.status.tripping = None
    #
    # def _catch_trip(self):
    #     raise XanityDeprecationError
    #     # if self.status.tripping == stack()[1][3]:
    #     #     return True
    #     # else:
    #     #     return False

    """
    the following are all public methods -- DO NOT USE INTERNALLY --
    """

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def subprocess(self, command):
        cmd = self._condabashcmd('conda activate {} && {}'.format(self._env_path, command))
        return subprocess.Popen(cmd, shell=True)

    @property
    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def shell_prelude(self):
        return open(self.conf_files.shell_prelude, mode='r').read()

    @property
    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def shell_conclude(self):
        return open(self.conf_files.shell_conclude, mode='r').read()

    @shell_prelude.setter
    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def shell_prelude(self, value):
        if isinstance(value, str):
            value = [value]
        else:
            value = list(value)

        result = open(self.conf_files.shell_prelude, mode='w').write('\n'.join(value))

        if result is None:
            print('wrote new shell prelude script. please restart xanity.')
            raise SystemExit

        else:
            raise NotImplementedError

    @shell_prelude.setter
    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def shell_conclude(self, value):
        if isinstance(value, str):
            value = [value]
        else:
            value = list(value)

        result = open(self.conf_files.shell_prelude, mode='w').write('\n'.join(value))
        if result is None:
            print('wrote new shell conclude script. please restart xanity.')
            raise SystemExit

        else:
            raise NotImplementedError

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def run(self, clargs=None):
        self.invocation = INVOCATION.HOOK
        self.invoker = get_external_caller(invocation=True)
        self._orient(clargs)
        self._absolute_trigger()

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def metarun(self, experiment=None, parameters=None, host=None, remote_command=''):
        global invocation
        self.invocation = INVOCATION.HOOK
        invocation = INVOCATION.HOOK
        self.invoker = get_external_caller()
        self._orient(['run', experiment])

        caller = os.path.split(get_external_caller())[-1].split('.py')[0]
        if caller in self.experiments:
            del self.experiments[caller]

        if host is not None:

            if not os.path.isdir(self.exp_data_dir):
                os.makedirs(self.exp_data_dir)

            self._run_basic_prelude()

            self.log('sending source to {}...'.format(host))
            subprocess.check_call(
                self._condabashcmd('rsync -avzhuP --info=progress2 {} {}:~/XANITY_REMOTE/ {}'.format(
                    self.project_root,
                    host,
                    ' '.join(['--exclude={}'.format(item.lstrip('/')) for item in SOURCE_IGNORE])
                ))
            )

            self.log('checking xanity on {}...'.format(host))
            try:
                subprocess.check_call(
                    shsplit(
                        'ssh {} \'bash -lc "which xanity"\''.format(
                            host,
                        )
                    ))

            except subprocess.CalledProcessError:
                print('xanity doesn\'t appear to be installed on host')
                raise SystemExit

            if parameters is not None:

                # self._exp_paramset_requests[experiment] = parameters
                # self._resolve_requests()
                # self._purge_dangling_experiments()
                # self._load_required_modules()
                # self._resolve_associations()
                self._process_parameters()

                for pset in self.experiments[experiment].paramsets:
                    cmd = remote_command + ' ' if remote_command else ''
                    cmd += 'xanity run {} -D XANITY_REMOTE/{} --initialize --setup'.format(
                        experiment,
                        os.path.split(self.project_root)[-1],
                    )

                    for name, val in pset.items():
                        if isinstance(val, tuple):
                            val = str(val).rstrip(')').lstrip('(')
                        cmd += ' -p {}={}'.format(name, val)

                    self.log('executing \'{}\' on {}...'.format(cmd, host))
                    subprocess.check_call(
                        shsplit(
                            'ssh {} \'bash -lc "{}"\''.format(
                                host,
                                cmd,
                            )
                        )
                    )

        else:

            if parameters is not None:
                self._exp_paramset_requests[experiment] = parameters
            self._absolute_trigger()

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def save_xanity_obj_panic(self):
        if ACTIVITIES.EXP in self.status.act_tags:
            del self.logger
            for exp in self.avail_experiments.values():
                del exp.module
            for anal in self.avail_analyses.values():
                del anal.module
            pickle_dump(self, os.path.join(self.status.xanity_data, 'xanity_panic.dill'))

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def save_xantiy_status(self, path=None):
        #  Experiment class (self.focus)
        #         self.name = name
        #         self.module_path = module_path
        #         self.module = module
        #         self.default_params = None
        #         self.param_dict = None
        #         self.paramsets = None
        #         self.exp_dir = None
        #         self.subexp_dirs = None
        #         self.success = False
        #         self.analyses = {}

        focus = self.status.focus
        data = {'name': focus.name,
                'default_params': focus.default_params,
                'success': focus.success,
                'data_path': self.status.data_dir,
                'parameters': self.status.parameters
                }

        if ACTIVITIES.EXP in self.status.act_tags:
            if not path:
                pickle_dump(data, 'xanity_status.dill')
            else:
                pickle_dump(data, os.path.join(path, 'xanity_status.dill'))

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def load_checkpoint(self, checkpoint_name, variables=None, overwrite=False, noload=False):
        if isinstance(variables, str):
            variables = [variables]
            solo = True
        elif variables is not None:
            solo = False

        if not self.args.loadcp or noload:
            print('checkpoint loading not enabled. use \'--loadcp\' or \'--chekcpoints\'')
            return None

        assert isinstance(checkpoint_name, str), 'can only save one checkpoint at a time!'

        cp_dir = os.path.join(self.paths.checkpoints, self.status.focus.name, checkpoint_name)
        # cp_files = [os.path.join(self.paths.checkpoints, self.status.focus.name, var + '.pkl') for var in checkpoints]

        if os.path.isdir(cp_dir):

            for root, dirs, files in os.walk(cp_dir):
                if os.path.join(cp_dir, 'xanity_variables') in root:
                    continue

                # s = os.path.join(cp_dir, item)
                # d = os.path.join(self.status.data_dir, item)

                # if os.path.isfile(s):
                #     os.link(s, d)
                # elif os.path.isdir(s):
                #     shutil.copytree(s, d, copy_function=os.link)

                for dir in dirs:
                    if dir != 'xanity_variables':
                        try:
                            os.mkdir(os.path.join(self.status.data_dir, root.split(cp_dir)[1], dir))
                        except OSError:
                            pass

                for f in files:
                    s = os.path.join(root, f)
                    d = os.path.join(self.status.data_dir, root.split(cp_dir)[1], f)
                    if os.path.isfile(d):
                        if overwrite:
                            os.remove(d)
                            os.link(s, d)
                        else:
                            pass
                    else:
                        os.link(s, d)

            vardir = os.path.join(cp_dir, 'xanity_variables')

            rvars = []
            if os.path.isdir(vardir) and variables is not None:

                available = [v.split('.pkl')[0] for v in os.listdir(vardir)]

                for var in variables:
                    if var not in available:
                        rvars.append(None)

                    else:
                        rvars.append(pickle_load(os.path.join(vardir, var + '.pkl')))

            if rvars:
                if solo:
                    return rvars[0]
                else:
                    return rvars
            else:
                return True

        else:
            return [False] * len(variables) if variables is not None and not solo else False

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def save_checkpoint(self, checkpoint_name, variables=None, cwd=True, overwrite=False):
        if not self.args.savecp:
            # return False
            pass

        assert isinstance(checkpoint_name, str), 'can only save one checkpoint at a time!'

        cp_dir = os.path.join(self.paths.checkpoints,
                              self.status.focus.name,
                              checkpoint_name)

        if variables is not None:
            variables = [variables] if not isinstance(variables, (list, tuple)) else variables
            args = get_arg_names()
            varnames = None

            for item in args[1:]:
                if 'variables' in item.split('=')[0]:
                    varnames = [iitem.strip('\' []()') for iitem in item.split('=')[1].split(',')]

            if not varnames:
                varnames = [iitem.strip('\' [()]') for iitem in args[1].split(',')]

            assert len(variables) == len(varnames)

            cp_files = [os.path.join(cp_dir,
                                     DIRNAMES.SAVED_VARS,
                                     var + '.pkl')
                        for var in varnames]

            for item, file in zip(variables, cp_files):
                if not os.path.isfile(file) or overwrite:
                    if not os.path.isdir(os.path.split(file)[0]):
                        os.makedirs(os.path.split(file)[0])
                    pickle_dump(item, file)

        if cwd:
            # saving runpath in file-system
            if not os.path.isdir(cp_dir):
                os.makedirs(cp_dir)

            for root, dirs, files in os.walk(self.status.data_dir):
                # s = os.path.join(self.status.data_dir, item)
                # d = os.path.join(cp_dir, item)
                if any([os.path.split(root)[-1] in item for item in vars(DIRNAMES).values()]):
                    continue

                for dir in dirs:
                    if any([dir in item for item in vars(DIRNAMES).values()]):
                        continue
                    try:
                        os.makedirs(os.path.join(cp_dir, root.split(self.status.data_dir)[1], dir))
                    except OSError:
                        pass

                for f in files:
                    s = os.path.join(root, f)
                    d = os.path.join(cp_dir, root.split(self.status.data_dir)[1], f)

                    if not os.path.isfile(d):
                        os.link(s, d)
                    elif overwrite:
                        os.remove(d)
                        os.link(s, d)

                # elif os.path.isdir(s):
                #     try:
                #         shutil.copytree(s, d, copy_function=os.link)
                #     except OSError:
                #         shutil.copytree(s, d)

            return True

        else:

            return True

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def save_variable(self, value, name=None):
        # inspect.stack( #lines of context )[stack_idx][code context][codes lines]
        name = get_arg_names()[0] if not name else name
        datapath = os.path.join(self.status.data_dir, DIRNAMES.SAVED_VARS)
        os.makedirs(datapath, exist_ok=True) if PY_SYSVER == 3 else os.makedirs(datapath)
        pickle_dump(value, os.path.join(datapath, name + '.dill'))

    ###
    ###    all data loading has been moved to xanity.data module
    ###  NOT SO FAST

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def load_variable(self, name, experiment=None, run=None):
        """
        load variable returns only the most recent candidate

        :param name:
        :param experiment:
        :param run:
        :return:
        """
        from .data import fetch_variable
        if isinstance(experiment, str):
            experiment = [experiment]

        if experiment is None:
            # if isinstance(self.status.focus, Experiment):
            #     experiment = self.status.focus.name
            # elif isinstance(self.status.focus, Experiment):
            #     experiment = [self.status.focus.name]
            if isinstance(self.status.focus, Analysis):
                experiment = list(self.status.focus.experiments.values())[0].name

        if isinstance(self.status.focus, Experiment) and self.status.data_dir and os.path.isdir(self.status.data_dir):
            test = fetch_variable(variable=name, runids=self.run_id)
            if test is not None:
                return test
        # if isinstance(self.status.focus, Analysis) and self.status.data_dir and os.path.isdir(self.status.data_dir):
        #     runids = [os.path.split(self.status.data_dir)[-1]]
        # else:
        #     runids = None
        frame = fetch_variable(experiment=experiment, variable=name, most_recent=True, runids=run)
        return frame[name].values[0]

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def persistent(self, name, value=None):
        if ACTIVITIES.EXP in self.status.act_tags or ACTIVITIES.ANAL in self.status.act_tags:

            filename = os.path.join(self.paths.persistent_data, '{}.dill'.format(name))

            if value is not None and not os.path.isfile(filename):
                # set if it's not already there:
                pickle_dump(value, filename)
                return value

            # load the saved value and return it:
            if os.path.isfile(filename):
                return pickle_load(filename)
            else:
                return None

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def persistent_file(self, filename):
        if ACTIVITIES.EXP in self.status.act_tags or ACTIVITIES.ANAL in self.status.act_tags:
            return os.path.join(self.paths.persistent_data, filename)

    @ContextDecorator(ACTIVITIES.GLOBAL)
    def log(self, message):
        self.logger.info(message)

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def experiment_parameters(self, parameters_dict):
        # if self._catch_trip():
        #     self.status.focus.param_dict = parameters_dict
        caller_name = file2mod(get_external_caller())
        self._exp_paramset_requests[caller_name] = parameters_dict

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def associated_experiments(self, experiment_list):
        # if self._catch_trip():
        #     if not all([name in self.avail_experiments for name in experiment_list]):
        #         print('analysis list of associated experiments contains an unknown xanity experiment')
        #     self.status.focus.experiments.update(
        #         {exp: self.avail_experiments[exp] for exp in experiment_list if exp in self.avail_experiments})
        #     [self.avail_experiments[name].analyses.update({self.status.focus.name: self.status.focus}) for name in
        #      experiment_list if name in self.avail_experiments]
        if not isinstance(experiment_list, list):
            if isinstance(experiment_list, str):
                experiment_list = [experiment_list]
            else:
                print('provide associations as either single string or list of strings')
                raise SystemExit

        caller_name = file2mod(get_external_caller())
        if caller_name not in self._registered_associations:
            self._registered_associations[caller_name] = set(experiment_list)
        else:
            self._registered_associations[caller_name].update(experiment_list)

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def analyze_this(self):
        # if self._catch_trip():
        #     cand_anals = list(
        #         filter(lambda item: self.status.focus.name in item.experiments, self.avail_analyses.values()))
        #     for anal in cand_anals:
        #         if anal.name not in self.analyses:
        #             self.analyses.update({anal.name: anal})

        caller_name = file2mod(get_external_caller())
        self._exps_requesting_analysis.add(caller_name)

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def trials(self, number_of_trials):
        caller_name = file2mod(get_external_caller())
        self._trial_requests.update({caller_name: number_of_trials})

    @ContextDecorator(ACTIVITIES.EXTERNAL)
    def subdir(self, name):
        path = os.path.join(self.status.data_dir, name)
        try:
            os.makedirs(path)
        except OSError:
            pass
        return path


def run_entry():
    xanity = Xanity()
    xanity.run()
    raise SystemExit


def analyze_entry():
    xanity = Xanity()
    xanity.run()
    raise SystemExit


RUN_COMMANDS = CommandSet({
    'run': (['run'], run_entry),
    'analyze': (['anal', 'analyze', 'analyse', 'analysis', 'analyses'], analyze_entry),
})


def main(args=None):
    kn, unk = RunRootParser().parse_known_args(args)

    if 'directory' in kn and kn.directory is not None:
        targdir = os.path.realpath(os.path.expandvars(os.path.expanduser(kn.directory)))
        if not os.path.isdir(targdir):
            print('directory specified with the "-D" option doesn\'t seem to exist')
            raise SystemExit
        os.chdir(os.path.realpath(os.path.expandvars(os.path.expanduser(kn.directory))))

    if 'initialize' in kn and kn.initialize:
        subprocess.check_call(shsplit('xanity init'))

    if 'setup' in kn and kn.setup:
        subprocess.check_call(shsplit('xanity setup'))

    if not hasattr(kn, 'count'):
        n_runs = 1
    else:
        n_runs = kn.count

    from . import new_xanity_session
    for run_idx in range(n_runs):
        new_xanity_session()
        from . import xanity
        xanity._orient(args)
        xanity._absolute_trigger()


if __name__ == '__main__':
    main()
