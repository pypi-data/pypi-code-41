#
#                __   _,--="=--,_   __
#               /  \."    .-.    "./  \
#              /  ,/  _   : :   _  \/` \
#              \  `| /o\  :_:  /o\ |\__/
#               `-'| :="~` _ `~"=: |
#                  \`     (_)     `/
#           .-"-.   \      |      /   .-"-.
#    .-----{     }--|  /,.-'-.,\  |--{     }-----.
#     )    (_)_)_)  \_/`~-===-~`\_/  (_(_(_)    (
#    (                                           )
#     )                Oriole-VOS               (
#    (                  Eric.Zhou                )
#    '-------------------------------------------'
#

import builtins
import copy
from collections import namedtuple
import platform
from gettext import translation
from os import getcwd, pardir
from os import path as opath
from os import walk
from os.path import basename, splitext
from subprocess import run as sr
from sys import path as spath
from datetime import date, datetime
from decimal import Decimal

from oriole.yml import get_yml


def exe(s, cwd=None):
    return sr(s, cwd=cwd, shell=True)


def mexe(f, s):
    return tuple(map(f, s))


def cwd():
    return getcwd()


def get_node():
    return platform.node()


def get_path(f, loc):
    for fpath, _, fs in walk(loc):
        if f in fs:
            return fpath


def get_loc(f='services.cfg', is_file=True, loc=''):
    if not loc:
        loc = cwd().replace('/tests/', '/services/')

    for _ in range(3):
        config = opath.join(loc, f)

        if is_file:
            if opath.isfile(config):
                return config
        else:
            if opath.isdir(config):
                return loc

        loc = opath.abspath(opath.join(loc, pardir))


def set_loc(f='dao'):
    loc = get_loc(f, False)

    if loc and loc not in spath:
        spath.insert(0, loc)


def service_name(name, unit='service'):
    if name:
        return '_'.join((splitext(basename(name))[0], unit))


def get_first(s):
    return s.strip().split()[0]


def get_config(f="services.cfg"):
    return get_yml(get_loc(f))


def patch(a, b):
    builtins.__dict__[a] = builtins.__dict__[b]


def switch_lang(lang, loc, domain='messages'):
    try:
        translation(domain, loc, languages=[lang]).install()
        patch('__', '_')
    except Exception:
        raise RuntimeError('Error: i18n')


def _(o, k, d=None):
    if isinstance(k, dict):
        o.ms_params = copy.deepcopy(k)
        return o.ms_params

    if not hasattr(o, 'ms_params'):
        raise RuntimeError("Error: Use self._(params) first.")

    if isinstance(k, (list, tuple)):
        D = namedtuple('D', k)
        return D(*(o.ms_params.get(v, d) for v in k))

    return o.ms_params.get(k, d)


def _o(o, obj):
    """ Translate object to json.

    Dict in python is not json, so don't be confused.
    When return object from rpc, should always use _o.
    """

    if obj is None:
        return obj
    elif isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, date):
        return obj.strftime("%Y-%m-%d")
    elif isinstance(obj, (list, set, tuple)):
        return o._ol(obj)
    elif isinstance(obj, dict):
        return o._od(obj)
    elif isinstance(obj, (int, str, bool, float)):
        return obj
    else:
        return o._oo(obj)


def _oo(o, obj):
    result = {}
    try:
        for key in dir(obj):
            if key != "metadata" and key[0] != "_":
                value = getattr(obj, key)

                if not callable(value):
                    result[key] = o._o(value)
    except Exception:
        raise RuntimeError("Error: %s, only support json" % (type(obj)))

    return result


def _ol(o, obj):
    return [o._o(item) for item in obj]


def _od(o, obj):
    return {item: o._o(obj[item]) for item in obj}


def obj2dict(o, obj):
    return o._oo(obj)
