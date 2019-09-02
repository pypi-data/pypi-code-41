import os
from pype import __config__
from pype.misc import get_modules_names, get_module_method, generate_uid
from pype.modules.profiles import get_profiles
from pype.utils.pipeline import get_pipelines
from pype.logger import PypeLogger

PYPE_QUEUES = __config__.PYPE_QUEUES


def add_parser(subparsers, module_name):
    return subparsers.add_parser(module_name,
                                 help=('Workflows built by chaining '
                                       'pipelines and snippets'),
                                 add_help=False)


def pipelines_args(parser, subparsers, argv, profile):
    queues = get_modules_names(PYPE_QUEUES)
    try:
        default_q = PYPE_QUEUES.default
    except AttributeError:
        default_q = queues[0]
    lastparsers = parser.add_subparsers(dest='pipeline')
    if len(queues) > 0:
        parser.add_argument('--queue', dest='queue', action='store',
                            choices=queues, default=default_q,
                            help=('Select the queuing system '
                                  'to run the pipeline. '
                                  'Default %s' % default_q))
    else:
        raise Exception(('There are no queues in %s '
                         'to run a pipeline!!') % PYPE_QUEUES.__path__[0])
    parser.add_argument('--log', dest='log', type=str, default=os.getcwd(),
                        help=('Path used to write the pipeline logs. '
                              'Default  working directory.'))
    pipelines = get_pipelines(lastparsers, {})
    args, extra = parser.parse_known_args(argv)
    try:
        used_pipeline = args.pipeline
        if used_pipeline in pipelines.keys():
            profile_dict = get_profiles({})
            try:
                profile = profile_dict[profile]
            except KeyError:
                profile = profile_dict[profile_dict.keys()[0]]
            log = PypeLogger('%s_%s' %
                             (generate_uid(), used_pipeline),
                             args.log, profile)
            pipelines[used_pipeline].submit(
                lastparsers, extra, args.queue, profile.__name__, log)
            log.log.info('Pipeline %s terminated' % log.__name__)
            log.log.info(
                'Execute post run processes of queue %s, if any' % args.queue)
            post_run = get_module_method(PYPE_QUEUES, args.queue, 'post_run')
            if post_run is not None:
                post_run(log)
        else:
            try:
                if args.snippet is None:
                    return parser.print_help()
                else:
                    return parser.parse_args(args)
            except AttributeError:
                return parser.print_help()
    except IndexError:
        return parser.print_help()


def pipelines(parser, subparsers, module_name, argv, profile):
    args = pipelines_args(add_parser(
        subparsers, module_name), subparsers, argv, profile)
    return args
