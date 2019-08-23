"""
example:
from fabric import task

@task
def upload(ctx):
    pass

fabric -v 2.5
Python 3.7
"""
from functools import reduce
from itertools import chain
from typing import Callable, Optional, Mapping

from fabric import Connection as _cn
from invoke import run as _local


def print_command(func: Callable, is_method: bool = False):
    println = lambda x: print(f'execute => {x[0]}')
    if is_method:
        def wrap(self, *args, **kwargs):
            println(args)
            return func(self, *args, **kwargs)

        return wrap
    else:
        def wrap(*args, **kwargs):
            println(args)
            return func(*args, **kwargs)

        return wrap


local = print_command(_local)
_cn.sudo = print_command(_cn.sudo, is_method=True)
_cn.run = print_command(_cn.run, is_method=True)
Connection = _cn


def _run(command, env) -> None:
    env and Connection(env).run(command) or local(command)


def _join_command_option(command: str, option_name: str, option_val: str) -> str:
    optional_str = f'{option_name}={option_val}' if option_name.startswith('--') else f'{option_name} {option_val}'
    return ' '.join((command, optional_str))


def _join_multi_options(command: str, options: Optional[Mapping] = None):
    if options:
        reduced = reduce(lambda x, y: _join_command_option('', option_name=x, option_val=y), chain(*options.items()))
        command = ' '.join((command, reduced))
    return command


def rm(tar: str, env: str = '') -> None:
    command = f'rm -f {tar}'
    _run(command, env)


def tar(tar: str, package: str, env: str = '', options: Optional[Mapping] = None) -> None:
    command = f'tar -cvf {tar} {package}'
    command = _join_multi_options(command, options)
    _run(command, env)


def untar(tar_file: str, untar_path: str, env: str = '') -> None:
    command = f'tar -xvf {tar_file} -C {untar_path}'
    _run(command, env)


def scp(env: str, local_file: str, destination_path: str) -> None:
    command = f'scp {local_file} {env}:{destination_path}'
    local(command)


if __name__ == '__main__':
    print(_join_multi_options('tar -cvf a', options={'--exclude': '', '-h': ''}))
