# -*- coding: utf-8 -*-
"""
    flest._utils
    ~~~~~~~~~~~~

    internal routines.
"""


def _join_paths(*args, delim='/'):
    path = delim.join([x.strip(delim) for x in args if x.strip(delim)])
    if args[-1] == delim:
        path += delim
    if args[0].startswith(delim) and not path.startswith(delim):
        path = delim + path

    return path


def _up_in_path(path, delim='.'):
    return delim.join(path.split(delim)[:-1])


def _unwind(d: dict, p: str = ''):
    u = {}
    for k, v in d.items():
        tk = _join_paths(p, k, delim='_').upper()
        if isinstance(v, dict):
            u.update(_unwind(v, tk))
        else:
            u[tk] = v

    return u
