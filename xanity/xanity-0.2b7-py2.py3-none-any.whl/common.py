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

import fnmatch
import os
import os.path as path
import hashlib
import sys
import cloudpickle as pickle
import traceback
import inspect
from argparse import Namespace
import re

if sys.version_info.major == 2:
    from codecs import open
    PY_SYSVER = 2

elif sys.version_info.major == 3:
    import importlib
    PY_SYSVER = 3

from sys import version_info as PYTHONSYS


class XanityDeprecationError(NotImplementedError):
    pass


class XanityNotOrientedError(RuntimeError):
    pass


class XanityNoProjectRootError(RuntimeError):
    pass


class XanityUnknownActivityError(ValueError):
    pass


class Experiment(object):
    def __init__(self, name, module_path, module=None):
        self.name = name
        self.module_path = module_path
        self.module = module
        self.default_params = None
        self.param_dict = None
        self.paramsets = None
        self.exp_dirs = None
        self.success = False
        self.analyses = {}

    def update(self, dict_of_values):
        for key, val in dict_of_values.items():
            assert hasattr(self, key), '\'{}\' is not an Experiment parameter'.format(key)
            setattr(self, key, val)


class Analysis(object):
    def __init__(self, name, module_path, module=None):
        self.name = name
        self.module_path = module_path
        self.module = module
        self.experiments = {}
        self.success = False


class ContextStack(list):
    def __init__(self):
        super(ContextStack, self).__init__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop()

    def __call__(self, activity):
        self.append(activity)
        return self


class Status(object):
    def __init__(self):
        self.act_tags = ContextStack()
        self.focus = None
        self.sub_index = None
        self.data_dir = None
        self.parameters = None
        # self.tripping = None
        # self.ready = False


class ConstantSet(Namespace):
    def __init__(self, constants):
        super(ConstantSet, self).__init__(**constants)

    # def __init__(self, dict_of_vals):
    #     self._asdict = dict(dict_of_vals)
    #     for key, val in self._asdict.items():
    #         setattr(self, key, val)
    #
    # def __dict__(self):
    #     return dict(self._asdict)
    #
    # def __contains__(self, item):
    #     return item in self._asdict.values()
    #
    # def __getitem__(self, item):
    #     for key, val in self._asdict.items():
    #         if item == key:
    #             return key
    #         else:
    #             if item in val:
    #                 return key
    #     raise KeyError
    #
    # def keys(self):
    #     return self._asdict.keys()
    #
    # def values(self):
    #     return self._asdict.values()
    #
    # def items(self):
    #     return self._asdict.items()


class XanityCommand(object):
    def __init__(self, aliases, entry):
        if isinstance(aliases, str):
            aliases = (aliases,)
        aliases.sort()
        self.aliases = aliases
        self.name = aliases[0]
        self.entry = entry

    def __iter__(self):
        for a in self.aliases:
            yield a

    def __add__(self, other):
        assert isinstance(other, XanityCommand)
        return CommandSet({self.name: self, other.name: other})

    def __contains__(self, item):
        return True if any([fnmatch.fnmatch(item.lower(), a) for a in self.aliases]) else False

    def __eq__(self, other):
        if isinstance(other, str):
            return True if any([fnmatch.fnmatch(other, a) for a in self.aliases]) else False
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, str):
            return False if any([fnmatch.fnmatch(other, a) for a in self.aliases]) else True
        else:
            return True

    def __repr__(self):
        return str(self.name)


class CommandSet(ConstantSet):
    def __init__(self, command_list):
        d = {}
        for name, item in command_list.items():
            if isinstance(item, XanityCommand):
                d.update({name: item})
            elif isinstance(item, (tuple, list)):
                aliases = item[0]
                entry_fn = item[1]
                if name not in aliases:
                    aliases = aliases+[name]
                d.update({name: XanityCommand(aliases, entry_fn)})

        super(CommandSet, self).__init__(d)

        # rootdict = {}
        # parser_dict = {}
        # for key, val in dict_of_vals.items():
        #     rootdict.update({key: val[0]})
        #     parser_dict.update({key: val[1]})
        # super(CommandSet, self).__init__(rootdict)
        # self.parsers = parser_dict

    def __add__(self, other):
        assert isinstance(other, (CommandSet, XanityCommand))
        d = {}
        d.update(vars(self))
        if isinstance(other, CommandSet):
            d.update(vars(other))
        elif isinstance(other, XanityCommand):
            d.update({other.name: other})
        return CommandSet(d)

    def __contains__(self, item):
        return any([item in cmd for cmd in vars(self).values()])

    def __iter__(self):
        for c in vars(self).values():
            yield c

    def __getitem__(self, item):
        cands = [cmd for cmd in vars(self).values() if item in cmd]
        if len(cands) > 1:
            return [cand for cand in cands if cand != '*'][0]
        elif len(cands) == 1:
            return cands[0]
        else:
            raise KeyError


class Alias(object):
    def __init__(self, aliases):
        aliases = [aliases] if isinstance(aliases, str) else aliases
        self.aliases = tuple(aliases)

    def __contains__(self, item):
        return True if item.lower() in self.aliases else False

    def __repr__(self):
        return self.aliases[0]

    def __add__(self, other):
        assert isinstance(other, (Alias, list, tuple))
        return self.aliases + list(other)

    def __iter__(self):
        return self.aliases.__iter__()

    def __eq__(self, other):
        return self.__contains__(other)


def _get_live_package_object(package_path):
    # module_dir = path.split(module_path)[0]
    # opwd = os.getcwd()
    # os.chdir(module_dir)
    spec = importlib.util.spec_from_file_location(
        path.split(package_path)[-1].rstrip('/'),
        location=package_path+os.sep + '__init__.py')
    package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(package)
    # os.chdir(opwd)
    return package


# def _get_mainfn_sig(modulepath):
#     raise DeprecationWarning
#     live_module = _get_live_module_object(modulepath)
#     sig = inspect.signature(live_module.main)
#     del live_module
#     return sig


# def _get_module_obj(modulepath, obj_name):
#     module = _get_live_module_object(modulepath)
#     if hasattr(module, obj_name):
#         return getattr(module, obj_name)
#     else:
#         return None


def digest_path(path_root):
    hashes = []
    for root, sdirs, files in os.walk(path_root):
        sdirs.sort()
        files.sort()

        for sd in sdirs:
            hashes += [digest_path(os.path.join(root, sd))]

        for ff in files:
            hashes += [digest_file(os.path.join(root, ff))]

    hasher = hashlib.sha1()
    for item in hashes:
        hasher.update(item.encode('utf-8'))

    return hasher.hexdigest()


def digest_file(filename):
    if PY_SYSVER == 3:
        return hashlib.sha1(open(filename, 'rb').read()).hexdigest()
    elif PY_SYSVER == 2:
        return hashlib.sha1(open(filename, 'r', encoding='utf-8').read()).hexdigest()


def digest_string(string):
    return hashlib.sha1(string.encode('utf-8')).hexdigest()


def pickle_dump(item, filepath):
    if pickle.__name__ == 'dill':
        return pickle.dump(item, open(filepath, mode='wb'), 2)
    elif pickle.__name__ == 'cloudpickle':
        return pickle.dump(item, open(filepath, mode='wb'), protocol=2)


def pickle_load(filepath):
    if pickle.__name__ == 'dill':
        return pickle.load(open(filepath, mode='rb'), 2)
    elif pickle.__name__ == 'cloudpickle':
        return pickle.load(open(filepath, mode='rb'))


def file2mod(filepath):
    # print('file2mod: {}'.format(filepath))
    return os.path.split(filepath)[-1].split('.py')[0]


def list_modules_at_path(pathspec, names=None):
    assert os.path.isdir(pathspec)
    mods = [file.split('.')[0] for file in fnmatch.filter(os.listdir(pathspec), '[!_]*.py')]
    mods.sort()
    mods = list(filter(lambda item: item in names, mods)) if names else mods
    paths = [path.join(pathspec, mod + '.py') for mod in mods]
    return zip(mods, paths)


def get_external_caller(context_decorator=False, invocation=False):
    tb_stack = traceback.extract_stack()

    #filtered = [item[0] for item in tb_stack]
    #filtered = list(filter(lambda item: item.endswith('.py'), filtered))
    #filtered = list(filter(lambda item: 'xanity' not in item.lower(), filtered))
    #filtered = list(filter(lambda item: 'pydev' not in item.lower(), filtered))
    # if not filtered:
    #     return None
    # else:
    this_ind = [i for i in range(len(tb_stack)) if tb_stack[i].name == 'get_external_caller'][-1]

    if not context_decorator and not invocation:
        ext_ind = this_ind-2
    if context_decorator and not invocation:
        ext_ind = this_ind-3
    if not context_decorator and invocation:
        ext_ind = this_ind-2
        while 'xanity/' in tb_stack[ext_ind].filename:
            ext_ind -= 1

    return tb_stack[ext_ind].filename


def get_arg_names():

    frames = inspect.stack(1)

    for idx, frame in enumerate(frames[1:]):
        code = frame.code_context[0]
        if re.findall( 'get_arg_names\(', code):
            callers_name = frame.function
            caller_idx = idx+1
            break
        return None

    for idx, frame in enumerate(frames[caller_idx+1:]):
        code = frame.code_context[0]
        matches = re.findall(callers_name+'\(', code)
        if matches and not (frame.filename.endswith('xanity/__init__.py') and frame.function == 'save_variable')\
                and not (frame.filename.endswith('xanity/__init__.py') and frame.function == 'save_checkpoint'):
            inv_ind = caller_idx + idx + 1
            break

    line = frames[inv_ind].code_context[0]
    line = line.split(callers_name)[1].split('\n')[0].lstrip('(')
    n_opens = len([c for c in line if c == '('])
    cl_paren_inds = [i for i, c in enumerate(line) if c == ')']
    line = line[:cl_paren_inds[n_opens]]

    arg = []
    args = []
    ct = 0
    for i, c in enumerate(line):

        if c in '[({':
            ct += 1
        elif c in '])}':
            ct -= 1

        if c == ',' and ct == 0:
            args.append('='.join([half.strip() for half in ''.join(arg).split('=')]))
            arg = []

        elif i == len(line) - 1 and ct == 0:
            arg.append(c)
            args.append('='.join([half.strip() for half in ''.join(arg).split('=')]))
        else:
            arg.append(c)

    return args


def find_xanity_root(hint=None):

    if hint and not hint.startswith('/'):
        hint = os.path.normpath(os.path.join(os.getcwd(), hint))

    bot = os.getcwd() if not hint else os.path.expanduser(os.path.expandvars(hint))
    maxdepth = 7
    parts = bot.split(os.sep)
    cur_dep = len(parts)

    root = None
    for d in range(cur_dep, cur_dep - maxdepth-1, -1):
        if d > cur_dep or d == 0:
            break
        targ = os.sep + os.path.join(*parts[:d])
        dirs = os.listdir(targ)
        if '.xanity' in dirs:
            root = targ

    return root


def confirm(prompt=None, default_response=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', default_response=True)
    Create Directory? [y]|n:
    True
    >>> confirm(prompt='Create Directory?', default_response=False)
    Create Directory? [n]|y:
    False
    >>> confirm(prompt='Create Directory?', default_response=False)
    Create Directory? [n]|y: y
    True

    """

    if prompt is None:
        prompt = 'Confirm?'

    if default_response:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

    while True:
        if PYTHONSYS[0] > 2:
            ans = input(prompt)
        else:
            ans = raw_input(prompt)

        if not ans:
            return default_response

        if ans not in ['y', 'Y', 'n', 'N']:
            print
            'please enter y or n.'
            continue

        if ans == 'y' or ans == 'Y':
            return True

        if ans == 'n' or ans == 'N':
            return False

        time.sleep(1e-3)

    print('')
