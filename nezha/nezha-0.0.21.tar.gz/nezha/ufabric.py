"""
example:
from fabric import task

@task
def upload(ctx):
    pass

fabric -v 2.5
Python 3.7
"""
from typing import Callable

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
