#!/usr/bin/env python
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

import os
import subprocess
import pkg_resources
import inspect
import shutil
import argparse
import time
import sys

from shlex import split as shsplit
from fnmatch import fnmatch

from .common import CommandSet, find_xanity_root, digest_string, digest_file
from .constants import XANITY_FILES, DIRNAMES, RELATIVE_PATHS


helptext = """
setup an existing xanity directory tree

usage:  xanity setup [help]

xanity setup assumes you're in a xanity tree
"""


def condabashcmd(cmd):
    root = find_xanity_root()
    if root:
        rcfile = os.path.join(root, XANITY_FILES.rcfile)
        if os.path.isfile(rcfile):
            return shsplit('bash --rcfile {} -lc \'{}\''.format(rcfile, cmd))
        else:
            return shsplit('bash -lc \'{}\''.format(cmd))
    else:
        print('could not find xanity root to execute condabash inside')


def check_environment(root=None):
    root = find_xanity_root(root)
    conda_env = os.path.join(root, XANITY_FILES.conda_env)

    if conda_env in os.path.abspath(sys.executable):
        return True
    else:
        return False


def check_xanity_ver():

    try:
        sys_xanity = os.environ['XANITY_HOST_VER']
        return sys_xanity

    except:
        pass

    sys_xanity = subprocess.check_output(shsplit('bash -l xanity --version')).decode().split('Version:')[1].split()[0]
    myver = sys.modules['xanity'].__version__
    result = myver == sys_xanity
    print('\n'
          'system xanity version: {}\n'
          'conda env xanity vers: {}\n'
          '\n'.format(sys_xanity, myver)
          )

    return result


def check_conda_env(root=None):
    root = find_xanity_root(root)
    conda_env_hash_file = os.path.join(root, XANITY_FILES.env_hash)

    if not os.path.isfile(conda_env_hash_file):
        return False

    conda_env_hash = hash_conda_env()
    with open(conda_env_hash_file, mode='r') as f:
        saved_hash = f.read()

    return conda_env_hash == saved_hash


def hash_conda_env(root=None):
    root = find_xanity_root(root)

    # conda_env_name = open(os.path.join(self.paths.xanity_data, 'UUID'), 'r').read().split('\n')[0].strip()
    conda_env_path = os.path.join(root, XANITY_FILES.conda_env)

    try:
        # conda_env_contents = ''.join(sorted(str(subprocess.check_output([
        #     # 'bash', '-c', 'source xanity-enable-conda.sh 2>&1 /dev/null && conda list -n {}'.format(conda_env_name)
        #     'bash', '-lc', 'conda list -n {}'.format(conda_env_name)  # xanity(bash) makes sure conda is on path :)
        # ]).decode()).replace(' ', '').split()))
        conda_env_contents = ''.join(sorted(str(
            subprocess.check_output(condabashcmd(
                'conda list -p {}'.format(conda_env_path))
            ).decode()).replace(' ', '').split()))

    except subprocess.CalledProcessError:
        return None
    conda_env_contents = conda_env_contents.replace(' ', '')
    return digest_string(conda_env_contents)


def check_conda_file(root=None):
    root = find_xanity_root(root)
    conda_file_hash = os.path.join(root, XANITY_FILES.conda_hash)

    if not os.path.isfile(conda_file_hash):
        return False

    conda_hash = hash_conda_env_file()
    with open(conda_file_hash, mode='r') as f:
        saved_hash = f.read()
    return conda_hash == saved_hash


def check_conda(root=None):
    root = find_xanity_root(root)
    return check_conda_env(root) and check_conda_file(root)


def hash_conda_env_file(root=None):
    root = find_xanity_root(root)
    hash_file = os.path.join(root, XANITY_FILES.conda_env_file)
    return digest_file(hash_file)


def freeze_conda(root=None):
    root = find_xanity_root(root)
    conda_hash_file = os.path.join(root, XANITY_FILES.conda_hash)
    env_hash_file = os.path.join(root, XANITY_FILES.env_hash)

    open(conda_hash_file, mode='w').write(hash_conda_env_file())
    open(env_hash_file, mode='w').write(hash_conda_env())

    while not os.path.isfile(conda_hash_file):
        time.sleep(0.1)
    while not os.path.isfile(env_hash_file):
        time.sleep(0.1)

    assert check_conda_file()


def save_conda_snapshot(root=None):
    root = find_xanity_root(root)
    archive_file = os.path.join(root, RELATIVE_PATHS.tmp, 'conda_env_state.txt')
    with open(archive_file, 'w') as f:
        f.write(
            subprocess.check_output(condabashcmd('conda list'), stderr=subprocess.PIPE).decode()
        )
    print('saved output of \'conda list\'')
    return archive_file


def dump_pip_requirements(root=None):
    # make requirements.txt
    root = find_xanity_root(root)
    archive_file = os.path.join(root, RELATIVE_PATHS.tmp, 'pip-requirements.txt')
    last_hash_file = os.path.join(root, XANITY_FILES.last_pip_hash)

    # if os.path.isfile(archive_file) and os.path.isfile(last_hash_file):
    #     current_hash = digest_path(self.paths.experiments)
    #     if current_hash == open(last_hash_file, 'r').read():
    #         self.log('reusing existing archive of pip status')
    #         return archive_file

    # make requirements.txt
    reqs = subprocess.check_output(['pip', 'freeze']).decode()
    with open(archive_file, mode='w+') as reqsfile:
        reqsfile.write("""
                ############################################################################
                ##                                                                          ##
                ##   This is the state of the python environment running this experiment    ##
                ##   as understood by 'pip' and produced with the command `pip freeze`.     ##
                ##                                                                          ##
                 ###########################################################################
                """)
        reqsfile.write('\n')
        reqsfile.write(reqs)

    reqs = subprocess.check_output(['pip', 'freeze']).decode()
    with open(archive_file, mode='a+') as reqsfile:
        reqsfile.write(reqs)

    # with open(last_hash_file, 'w+') as f:
    #     f.write(digest_path(self.paths.experiments))
    print('saved output of \'pip freeze\'')
    return archive_file


def setup(xanity_root=None):
    # ported from bash

    # # if project doesn't have a UUID make one:
    # uuid_file = os.path.join(xanity_root, '.xanity', 'UUID')
    # if not os.path.isfile(uuid_file):
    #     uuid = os.path.split(xanity_root)[-1] + '_' + "".join(choice(string.ascii_letters) for x in range(4))
    #     open(uuid_file, mode='w').writelines(uuid + '\n')
    # else:
    #     uuid = str(open(uuid_file, mode='r').read()).strip()
    root = find_xanity_root(xanity_root)

    # get the full path to this file :
    replication_source_path = os.path.abspath(os.path.realpath(os.path.split(inspect.stack()[0][1])[0]))
    self_replication_subdir = DIRNAMES.SELF_REPLICATION
    env_spec_filepath = os.path.join(root, XANITY_FILES.conda_env_file)
    conda_env_path = os.path.join(root, XANITY_FILES.conda_env)

    while self_replication_subdir in replication_source_path:
        print("running 'xanity setup' from inside a xanity installation. Correcting paths...")
        parts = replication_source_path.split(os.sep)
        repind = parts.index(self_replication_subdir)
        replication_source_path = os.path.join(*parts[:repind])

    # print('setup_env replication source path: {}'.format(replication_source_path))
    assert(os.path.isdir(replication_source_path)), 'could not find xanity self-replication package'
    # check for 'conda_environment.yaml' file

    if not os.path.isfile(os.path.join(xanity_root, env_spec_filepath)):
        print('could not find {} which contains the desired conda environment.'
              '  Please make one.\n\n'.format(env_spec_filepath))
        print(
            "example {} file:\n\n"
            "    name: < my-env-name >         \n"
            "    channels:                     \n"
            "      - javascript                \n"
            "    dependencies:                 \n"
            "      - python=3.4                \n"
            "      - bokeh=0.9.2               \n"
            "      - numpy=1.9.*               \n"
            "      - nodejs=0.10.*             \n"
            "      - flask                     \n"
            "      - pip:                      \n"
            "        - Flask-Testing           \n"
            "        - \"--editable=git+ssh://git@gitlab.com/lars-gatech/pyspectre.git#egg=pyspectre\"\n"
            "        - \"git+ssh://git@gitlab.com/lars-gatech/libpsf.git#egg=libpsf\"\n"
            "\n".format(env_spec_filepath, env_spec_filepath)
        )
        raise SystemExit(1)

    else:
        print("found environment file: {}".format(env_spec_filepath))

    # conda_env_path = os.path.join(xanity_root, '.xanity', 'conda_env')

    # if conda env exists:
    if os.path.isfile(os.path.join(conda_env_path, 'bin', 'python')):

        # update conda env
        subprocess.check_call(
            condabashcmd('conda env update --file {} -p {}'.format(env_spec_filepath, conda_env_path))
            # ['bash', '-ic', 'conda env update --file {} -p {}'.format(env_spec_filepath, conda_env_path)]
        )
        print('updated conda env at {}'.format(conda_env_path))

    else:

        # create conda env
        if os.path.isdir(conda_env_path):
            shutil.rmtree(conda_env_path)
        subprocess.check_call(
            condabashcmd('conda env create --file {} -p {}'.format(env_spec_filepath, conda_env_path))
            # ['bash', '-ic', 'conda env create --file {} -p {}'.format(env_spec_filepath, conda_env_path)]
        )
        print('created conda env at {}'.format(conda_env_path))

    # get xanity version
    try:
        xanityver = pkg_resources.require("xanity")[0].version
        print('installing (-e) your base xanity into the new env'.format(xanityver))

    except:
        print('this python interpreter does not have xanity installed.')
        raise SystemExit

    # link source:
    try:
        shutil.rmtree(os.path.join(replication_source_path, self_replication_subdir))
        os.mkdir(os.path.join(replication_source_path, self_replication_subdir))
    except OSError:
        pass

    # subprocess.check_call(shsplit(
    #     'rm -rf {}/xanity_self_replication'.format(replication_source_path)
    # ))

    ignore = ['*.egg-info', '.eggs', self_replication_subdir, '__pycache__', '*~', 'setup.py', '*.pyc']

    for based, subds, files in os.walk(os.path.join(replication_source_path)):
        # don't go into ignored dirs
        if any([fnmatch(dir, item) for item in ignore for dir in based.split(os.sep)]):
            continue

        for subd in subds:
            if not any([fnmatch(subd, item) for item in ignore]):
                try:
                    relpath = os.path.join(based, subd).split(replication_source_path)[1].lstrip(os.sep)
                    os.makedirs(os.path.join(replication_source_path, self_replication_subdir, 'xanity', relpath))
                except OSError:
                    pass

        for afile in files:
            if not any([fnmatch(afile, item) for item in ignore]):
                relpath = os.path.join(based, afile).split(replication_source_path)[1].lstrip(os.sep)

                s = os.path.join(based, afile)
                d = os.path.join(replication_source_path, self_replication_subdir, 'xanity', relpath)

                os.symlink(s, d)
                # do not make hardlinks... will confuse editors!!!
                # subprocess.check_call(shsplit(
                #     'ln -sf {} {}'.format(os.path.join(based, afile), os.path.join(replication_source_path, self_replication_subdir, 'xanity', relpath))
                # ))

    subprocess.check_call(
        condabashcmd(
            'conda activate {} && pip install -U --no-cache -e {}'.format(conda_env_path, replication_source_path)
        ))

    # shsplit(
    #    'bash -ic \'conda activate {} && pip install -U -e {}\''.format(
    #        conda_env_path, replication_source_path)

    # open(os.path.join(xanity_root, '.xanity', 'setupcomplete'), mode='w').write('')


def remove(root=None):
    root = find_xanity_root(root)
    conda_env = os.path.join(root, XANITY_FILES.conda_env)

    print('removing conda env: {}...'.format(conda_env))
    subprocess.check_call(condabashcmd(
        'conda env remove -p {}'.format(conda_env)
    ))
    # ['bash', '-ic', 'conda env remove -n {}'.format(xanity.uuid)])
    print('removed.')


def report_status(root=None):
    root = find_xanity_root(root)

    conda_env = os.path.join(root, XANITY_FILES.conda_env)
    conda_env_file = XANITY_FILES.conda_env_file

    # uuid = open(os.path.join(self.paths.xanity_data, 'UUID')).read() if os.path.isfile(
    #     os.path.join(self.paths.xanity_data, 'UUID')) else None
    setup_complete = True if check_conda else False
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode()
    installed_packages = [r.split('==')[0] for r in reqs.split()]

    req_packages = open(conda_env_file, 'r').read()
    req_packages = [line.lstrip(' -').split('#')[0].rstrip() if not line.lstrip().startswith('#') else '' for
                    line in req_packages.split('\n')]
    req_packages = list(filter(lambda item: bool(item), req_packages))

    req_start = [True if 'dependencies' in item else False for item in req_packages]
    req_start = req_start.index(1) + 1
    req_packages = req_packages[req_start:]

    missing_packages = [
        item if not any([item in item2 for item2 in installed_packages]) and not 'python' in item else None for
        item in req_packages]

    missing_packages = list(filter(lambda item: bool(item), missing_packages))
    print(
        '\n'
        '        conda env path: {}\n'
        '        setup complete: {}\n'
        '    installed packages: {}\n'
        '      missing packages: {}\n'
        ''.format(
            conda_env,
            setup_complete,
            len(installed_packages),
            '\n                        {}\n'.join(missing_packages) if missing_packages else None
        )
    )


class EnvRootParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(EnvRootParser, self).__init__(*args, **kwargs)
        self.add_argument('action', help='manipulate the internal conda env')

    def parse_and_enter(self, args):
        kn, unk = self.parse_known_args(args)
        if kn.action in ENV_COMMANDS:
            ENV_COMMANDS[kn.action].entry(unk)
        else:
            catchall_fn(kn, unk)


class SetupParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(SetupParser, self).__init__(*args, **kwargs)
        self.add_argument('directory', nargs='?', help='path to location of an existing xanity project')


class RemoveParser(argparse.ArgumentParser):
    pass


class StatusParser(argparse.ArgumentParser):
    pass


def catchall_fn():
    print('unknown xanity-env command')


def setup_entry(args=None):
    kn, unk = SetupParser().parse_known_args(args)

    dirspec = kn.directory

    if dirspec == 'help':
        print(helptext)
        raise SystemExit(1)

    if not dirspec:
        root = find_xanity_root()
        dirspec = root if root else os.getcwd()

    dirspec = os.path.expandvars(os.path.expanduser(dirspec))

    if os.path.isdir(dirspec):
        if os.path.isdir(os.path.join(dirspec, '.xanity')):
            project_root = os.path.realpath(dirspec)

        else:
            print('Specified directory doesn\'t seem to be a xanity project. Try running \'xanity init\'')
    else:
        print('Specified directory does not exist')
        # project_root = os.path.abspath(os.path.join(os.getcwd(), dirspec))

    if not os.path.isfile(os.path.join(project_root, XANITY_FILES.conda_env, 'bin', 'python')):
        # result = subprocess.call(['bash', setup_script, xanity_root])
        try:
            setup(project_root)
            freeze_conda()

        except Exception as e:
            print('failed to setup a conda environment')
            print(e)
            raise SystemExit(1)

    else:
        print('environment exists. checking status...')
        if not check_conda():
            print('updating environment...')

            try:
                setup(project_root)
                freeze_conda()

            except Exception as e:
                print('failed to update the conda environment')
                print(e)
                raise SystemExit(1)
        else:
            print('looks like current setup is valid')


def remove_entry(args=None):
    _ = RemoveParser().parse_args(args)
    remove()


def status_entry(args=None):
    _ = StatusParser().parse_args(args)
    report_status()


ENV_COMMANDS = CommandSet({
    'remove': (['rm'], remove_entry),
    'status': (['status'], status_entry),
    'setup':  (['setup'], setup_entry),
})


def main(args=None):
    EnvRootParser().parse_and_enter(args)
    SystemExit


if __name__ == "__main__":
    main()
