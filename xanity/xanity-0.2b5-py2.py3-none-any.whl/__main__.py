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

import argparse
import os

from . import data, initialize, Xanity, environment
from .common import XanityNoProjectRootError, CommandSet


def list_action(*args):

    class ListParser(argparse.ArgumentParser):
        def __init__(self, *args, **kwargs):
            super(ListParser, self).__init__(*args, **kwargs)
            self.add_argument('action_object', nargs='?', default='experiments',
                              help='either "exeperiments" or "analyses"')

    kn, unk = ListParser().parse_known_args(*args)

    xanity = Xanity.Xanity()
    xanity._orient(clargs=['list'])
    print('available experiments:\n    ' + '\n    '.join(
        [item.split('.py')[0] for item in os.listdir(xanity.paths.experiments)
         if item.endswith('.py')
         and not item.endswith('~')
         and not item.endswith('.md')
         and not item.startswith('__')
         ]))


def catchall_entry(args=None):

    try:
        xanity = Xanity.Xanity()
        xanity._orient(args)

    except XanityNoProjectRootError:
        pass

    if isinstance(xanity.action, str):
        print('didn\'t recognize that request\n\n'
              '{}'.format(generate_help_text()))

    if callable(xanity.action):
        print(xanity.action())
    else:
        print(xanity.action)

    raise SystemExit


class RootParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(RootParser, self).__init__(*args, prog='xanity', usage=generate_help_text(), add_help=False, **kwargs)
        self.add_argument('action', help=generate_help_text())

    def parse_and_call(self, *args, **kwargs):
        kn, unk = self.parse_known_args(*args, **kwargs)

        if kn.action in COMMANDS.run + COMMANDS.analyze:
            COMMANDS[kn.action].entry([kn.action] + unk)
        elif kn.action in COMMANDS:
            COMMANDS[kn.action].entry(unk)
        else:
            catchall_entry([kn.action] + unk)


def generate_help_text():
    text = "available commands include:\n"

    for item in vars(COMMANDS).values():

        text += "   {}".format('|'.join(item))
        text += '\n'

    return text


COMMANDS = CommandSet({
    'run': (['run'], Xanity.main),
    'analyze': (['anal', 'analyze', 'analyse', 'analysis', 'analyses'], Xanity.main),
    'initialize': (['init', 'initialize', 'initialise'], initialize.main),
    'id': (['ID', 'uuid'], Xanity.main),
    'env': (['env', 'environment'], environment.main),
    'list': (['list'], list_action),
    'data': (['data'], data.main),
})


def main():
    RootParser().parse_and_call()
    raise SystemExit(0)


if __name__ == '__main__':
    main()

#     legacy_helptext ="""
# xanity initialize|init [--with-examples] [new-dir]
#     Create a bare-bones xanity project directory tree.
#
# xanity setup [proj-dir]
#     Create or update the conda environment associated with the project.
#
# xanity status [proj-dir]
#     Print the status of the current xanity project.
#
# xanity run [experiment_names] [-a analyses[...]]
#     Run all (or the specified) experiments and optionally, analyses.
#
# xanity anal[yze|yse|ysis] [-a analyses] [run_data_path]
#     Run all (or the specified) analyses on the most recent (or specified) data.
#
# xanity ses[h|s|sion]
#     Drops you into a new bash shell inside your project's environment.
# """
