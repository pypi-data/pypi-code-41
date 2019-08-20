# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.objects import Global
from suanpan.run import cli, env, run

__version__ = "0.9.70"

g = Global()


if __name__ == "__main__":
    print("Suanpan SDK (ver: {})".format(__version__))
