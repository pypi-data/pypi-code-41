#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pype.misc import get_modules, DefaultHelpParser, SubcommandHelpFormatter
import pype.modules
from pype import __version__, __config__

VERSION = __version__.VERSION
DATE = __version__.DATE
AUTHOR = __version__.AUTHOR
MAIL = __version__.MAIL


def main():
    '''
    Execute the function with args
    '''
    PYPE_PROFILES = __config__.PYPE_PROFILES
    try:
        default_p = PYPE_PROFILES.default
    except AttributeError:
        default_p = 'default'
    parser = DefaultHelpParser(
        prog='pype', formatter_class=lambda prog:
        SubcommandHelpFormatter(prog, max_help_position=20, width=75),
        description=('Slim and simple framework to ease the managements '
                     'of data, tools and pipelines in the computerome HPC'),
        add_help=False,
        epilog='This is version %s - Francesco Favero - %s' % (VERSION, DATE))
    parser.add_argument('-p', '--profile', dest='profile',
                        type=str, default=default_p,
                        help=('Select the profile. This will define things '
                              'like databases, reference genomes paths,'
                              'specific version of programs to loads and '
                              'other similar configurations. '
                              'Default: %s') % default_p)
    subparsers = parser.add_subparsers(dest='module')

    modules = get_modules(pype.modules, subparsers, {})
    args, extra = parser.parse_known_args()
    try:
        use_module = args.module
        use_profile = args.profile
        if use_module in modules.keys():
            modules[use_module](parser, subparsers,
                                use_module, extra, use_profile)
        else:
            if args.module is None:
                return parser.print_help()
            else:
                return parser.parse_args(args)
    except IndexError:
        return parser.print_help()

if __name__ == "__main__":
    main()
