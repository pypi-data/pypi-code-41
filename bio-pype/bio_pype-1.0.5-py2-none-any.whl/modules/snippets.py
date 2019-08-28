import os
from pype import __config__
from pype.misc import get_modules
from pype.modules.profiles import get_profiles
from pype.logger import PypeLogger

PYPE_SNIPPETS = __config__.PYPE_SNIPPETS


def add_parser(subparsers, module_name):
    return subparsers.add_parser(module_name,
                                 help=('Single tasks implementations'),
                                 add_help=False)


def snippets_args(parser, subparsers, argv, profile):
    lastparsers = parser.add_subparsers(dest='snippet')
    parser.add_argument('--log', dest='log', type=str, default=os.getcwd(),
                        help=('Path used for the snippet logs. '
                              'Default  working directory.'))
    snippets = get_modules(PYPE_SNIPPETS, lastparsers, {})
    args, extra = parser.parse_known_args(argv)
    try:
        used_snippet = args.snippet
        if used_snippet in snippets.keys():
            profile = get_profiles({})[profile]
            log = PypeLogger(used_snippet, args.log, profile)
            log.log.info('Prepare snippet %s' % used_snippet)
            log.log.info('Attempt to execute snippet %s' % used_snippet)
            snippets[used_snippet](parser, lastparsers,
                                   used_snippet, extra, profile, log)
            log.log.info('Snippet %s executed' % used_snippet)

        else:
            if args.snippet is None:
                return parser.print_help()
            else:
                return parser.parse_args(args)
    except IndexError:
        return parser.print_help()


def snippets(parser, subparsers, module_name, argv, profile):
    args = snippets_args(add_parser(subparsers, module_name),
                         subparsers, argv, profile)
    return args
