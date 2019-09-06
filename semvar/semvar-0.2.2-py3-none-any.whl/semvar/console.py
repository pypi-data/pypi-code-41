import time
import subprocess
import glob
import os
import sys
import importlib
import argparse
import yaml
from enum import Enum
import re
import sys
import os
import shutil


def makefilter(args):
    def _filter(filename):
        if not os.path.isfile(filename):
            return False
        try:
            filedata = open(filename).read()
        except Exception as e:
            print(f"{filename} error")
            raise e
        if args['version'] not in filedata:
            return False
        if 'ignored'in args.keys():
            for ignore in args['ignored']:
                if re.match(ignore, filename):
                    return False

        return True
    return _filter


class Actions(Enum):
    major = 'major'
    minor = 'minor'
    patch = 'patch'
    build = 'build'

    def __str__(self):
        return self.value


def run(args):
    mod = ('.'.join(['semvar'] + args.entry.split('.')))
    if ':' in mod:
        mod, func = mod.split(':')
    else:
        func = 'main'
    if args.debug:
        print(mod)
        print(func)
    a = importlib.import_module(mod)
    getattr(a, func)()


def do_bump(args):

    with open(args.configfile) as f:
        config = yaml.full_load(f.read())
    data = ({**config, **vars(args)})
    data['version'] = str(data['version'])
    files = list(
        filter(
            makefilter(data),
            list(
                set(
                    glob.glob('./**/*', recursive=True) +
                    glob.glob('./**/.*', recursive=True) +
                    glob.glob('./**/*.*', recursive=True)
                )
            )
        )
    )
    try:
        shutil.rmtree('.semvar.diffs')
    except:
        pass
    os.makedirs('.semvar.diffs', exist_ok=True)
    changes = 0
    for file in files:
        try:
            newversion = get_next_version(data)
            filedata = open(file).read().splitlines()
            occurance_indexes = [i for i, a in enumerate(
                filedata) if data['version'] in a]
        except Exception as e:
            print(f"{file} error")
            raise e

        for oi in occurance_indexes:
            changes += 1
            filedata[oi] = filedata[oi].replace(
                data['version'], newversion
            )
            new_file_path = os.path.abspath(
                os.path.join(os.path.abspath(os.path.join('.semvar.diffs', os.path.dirname(file))), f"{os.path.basename(file)}__{oi:05}"))
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
            # os.path.dirname(new_file_path)
            # import pdb
            # pdb.set_trace()
            with open(new_file_path, 'w') as f:
                f.write('\n'.join(filedata))
            command = f'/usr/bin/diff -U0 {os.path.abspath(file)} {new_file_path}'
            filedata[oi] = filedata[oi].replace(
                newversion,
                data['version']
            )
            try:
                unified_diff = subprocess.check_output(
                    command.split(' '))
            except subprocess.CalledProcessError as e:
                unified_diff = (e.output)
            with open(f"{new_file_path}.diff", 'w') as f:
                f.write((unified_diff).decode())
            os.remove(f"{new_file_path}")

    input(f'changes found {changes}')
    # return
    for file in files:
        diffs = (
            sorted([os.path.abspath(a).replace(f"{os.getcwd()}/", '') for a in glob.glob(f'.semvar.diffs/**/{file}__*diff', recursive=True)]))
        # print(diffs)
        for diff in diffs:
            print(chr(27) + "[2J")
            print(file)
            diff_content = open(diff).read().replace(
                f"{os.getcwd()}/", '').replace('.semvar.diffs/', '')
            answer = input(f'''apply?
====== {diff.replace('.semvar.diffs/','')} >>>>> {file}
--------------------
{diff_content}          
--------------------  
(Y/n)?''')
            if answer is not 'n':
                subprocess.check_output(f'patch {file} {diff}'.split(' '))
            os.remove(diff)
    shutil.rmtree('.semvar.diffs')
    print(chr(27) + "[2J")


def get_next_version(data):
    version_headers = ['major', 'minor', 'patch', 'build']
    version = dict(zip(version_headers, [int(a)
                                         for a in data['version'].split('.')]))
    for key in set(version_headers)-set(version.keys()):
        version[key] = 0
    version[str(data['type'])] += 1
    newver = "{major}.{minor}.{patch}.{build}".format(**version)
    if data['type'] == Actions.major:
        version['minor'] = version['patch'] = version['build'] = 0
        if data['minimize']:
            newver = "{major}".format(**version)
    elif data['type'] == Actions.minor:
        version['patch'] = version['build'] = 0
        if data['minimize']:
            newver = "{major}.{minor}".format(**version)
    elif data['type'] == Actions.patch:
        version['build'] = 0
        if data['minimize']:
            newver = "{major}.{minor}.{patch}".format(**version)

    return newver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--configfile', default='.semvar.yaml')
    parser.add_argument('--dryrun', action='store_true')
    parser.add_argument('--debug', action='store_true')

    parser.add_argument(
        'type',
        default=Actions.major,
        type=Actions,
        choices=list(Actions)
    )
    parser.set_defaults(func=do_bump)

    args = parser.parse_args()
    if args.debug:
        print(vars(args))
        print(args.command)
    args.func(args)
