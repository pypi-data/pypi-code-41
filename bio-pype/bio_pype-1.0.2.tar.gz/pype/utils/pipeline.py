import os
import re
import yaml
import argparse
from pydoc import locate
from pype import __config__, __version__
from pype.misc import package_files, get_module_method, generate_uid
from pype.utils.arguments import batch_arguments, composite_argument, \
    is_composite_argument

PYPE_SNIPPETS = __config__.PYPE_SNIPPETS
PYPE_PIPELINES = __config__.PYPE_PIPELINES
PYPE_QUEUES = __config__.PYPE_QUEUES
PIPELINES_API = __version__.PIPELINES_API

def get_pipelines(subparsers, pipes):
    pipelines = package_files(PYPE_PIPELINES, '.yaml')
    for pipeline in sorted(pipelines):
        try:
            with open(pipeline, 'rb') as pipe:
                pipe_dict = yaml.safe_load(pipe)
                pipe_name = os.path.basename(os.path.splitext(pipeline)[0])
                if subparsers:
                    subparsers.add_parser(pipe_name, help=pipe_dict['info'][
                                          'description'], add_help=False)
                pipes[pipe_name] = Pipeline(pipeline, pipe_name)
        except AttributeError:
            pass
    return pipes


def compare_version(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

class PipelineItem:

    def __init__(self, item):
        self.name = item['name']
        self.arguments = item['arguments']
        self.type = item['type']
        self.jobs = []
        self.requirements = {}
        try:
            self.requirements = item['requirements']
        except KeyError:
            if self.type == 'snippet' or self.type == 'batch_snippet':
                requirements = get_module_method(
                    PYPE_SNIPPETS, self.name, 'requirements')
                if requirements is not {}:
                    self.requirements = requirements()
        try:
            self.deps = [PipelineItem(x)
                         for x in item['dependencies']['items']]
        except KeyError:
            pass
        try:
            self.mute = item['mute']
            if self.mute is True:
                pass
            else:
                self.mute = False
        except KeyError:
            self.mute = False

    def all_args(self):
        arguments = list(self.arguments.values())
        try:
            for dep in self.deps:
                arguments = arguments + dep.all_args()
        except AttributeError:
            pass
        args = list()
        for arg in arguments:
            if arg not in args:
                args.append(arg)
        return args

    def run(self, argv, queue, profile, log, jobs):
        self.jobs = []
        try:
            for deps in self.deps:
                res = deps.run(argv, queue, profile, log, jobs)
                if res:
                    self.jobs += res
        except AttributeError:
            pass
        self.jobs += jobs
        possible_types = ('snippet', 'pipeline',
                          'batch_snippet', 'batch_pipeline')
        if self.type in possible_types:
            if self.type == 'snippet':
                item_run = exec_snippet(self, argv, queue, profile, log)
            elif self.type == 'pipeline':
                item_run = exec_pipeline(self, argv, queue, profile, log)
            elif self.type == 'batch_snippet':
                item_run = batch_exec_unit(self, argv, queue, profile,
                                           log, exec_snippet_unit)
            elif self.type == 'batch_pipeline':
                item_run = batch_exec_unit(self, argv, queue, profile,
                                           log, exec_pipeline_unit)
            if self.mute is True:
                return self.jobs
            else:
                return item_run
        else:
            raise Exception('Type %s is not in the possible types %s' %
                            (self.type, possible_types))


class Pipeline:

    def __init__(self, path, name):
        self.__path__ = path
        self.__name__ = name
        self.__results__ = []
        with open(self.__path__, 'rb') as file:
            pipeline = yaml.safe_load(file)
            for key in pipeline:
                setattr(self, key, pipeline[key])
        self.pipelineitems = [PipelineItem(x) for x in self.items]
        try:
            api_version = self.info['api']
        except KeyError:
            raise Exception (('Can\'t find the pipeline API '
                             'version for pipeline %s' % self.__name__))
        version_diff = compare_version(api_version, PIPELINES_API)
        if version_diff != 0:
            raise Exception (('%s pipeline API version - %s - differs from '
                              'the supported API version - %s -') %
                              (self.__name__, api_version, PIPELINES_API))

    def submit(self, parser, argv, queue, profile, log, jobs=[]):
        types_dict = {'s': 'str', 'i': 'int', 'f': 'float'}
        arg_tag_regex = re.compile('\%\(.+\)[s,i,f]$')
        log.log.info('Prepare argument parser for pipeline')
        parse_snippets = parser.add_parser(self.__name__, help=self.info[
            "description"], add_help=False)
        log.log.info(
            'Retrieve all arguments required in the pipeline snippets')
        arguments = list()
        composite_args = list()
        for item in self.pipelineitems:
            arguments_item = item.all_args()
            for arg in arguments_item:
                if type(arg) is str:
                    if arg not in arguments:
                        arguments.append(arg)
                elif type(arg) is dict:
                    if is_composite_argument(arg):
                        if arg not in composite_args:
                            composite_args.append(arg)
                    else:
                        log.log.error(('Composite argument in '
                                       'a wrong formta'))
                        raise Exception(('Composite argument in '
                                         'a wrong formta'))
                elif type(arg) is list:
                    for a in arg:
                        if type(a) is dict:
                            pass
                        else:
                            log.log.error(('Batch list does not contains '
                                           'arguments in a dictionary'))
                            raise Exception(('Batch list does not contains '
                                             'arguments in a dictionary'))
                else:
                    raise Exception(
                        'Unexpected type %s for argument %s'
                        % (type(arg), arg))

        for arg in composite_args:
            '''
            Arguments tags for composite arguments are located in a dictionary
            in the result_arguments key.
            composite args is a dictionary with structure:
            {'snippet_name': snippet_name,
             'result_key': key_of_snippet_results,
             'result_arguments':{ '--arg1': tag1, '--arg2': tag2}}
            '''
            for sub_key in arg['result_arguments']:
                if sub_key != '--input_batch':
                    sub_arg = arg['result_arguments'][sub_key]
                    if re.match(arg_tag_regex, sub_arg):
                        if sub_arg not in arguments:
                            raise AttributeError(
                                ('Composite attribute %s '
                                 'contains undefined tag: %s') % (
                                    arg, sub_arg))
        log.log.info(
            ('Use unique tags %s with specified '
             'type to the pipeline argument parser')
            % ', '.join(arguments))
        parser_req = parse_snippets.add_argument_group(
            title='Required', description='Required pipeline arguments')
        try:
            default_args = len(self.info['defaults'].keys())
            if default_args >= 1:
                parser_opt = parse_snippets.add_argument_group(
                    title='Optional', description=('Optional pipeline '
                                                   'arguments'))
        except KeyError:
            pass
        for arg in arguments:
            if re.match(arg_tag_regex, arg):
                arg_type = types_dict[arg[arg.find(")") + 1]]
                arg = arg[arg.find("%(") + 2:arg.find(")")]
                try:
                    description = '%s, type: %s' % (
                        self.info['arguments'][arg], arg_type)
                except KeyError:
                    description = '%s, type: %s' % (arg, arg_type)
                try:
                    default_val = self.info['defaults'][arg]
                    description = '%s. Default: %s' % (
                        description, default_val)
                except KeyError:
                    default_val = False
                if default_val is False:
                    parser_req.add_argument('--%s' % arg, dest=arg,
                                            help=description, type=locate(
                                                arg_type),
                                            required=True)
                else:
                    parser_opt.add_argument('--%s' % arg, dest=arg,
                                            help=description, type=locate(
                                                arg_type),
                                            default=default_val)
        log.log.info('Parse arguments %s' % ', '.join(argv))
        args = parse_snippets.parse_args(argv)
        args = vars(args)
        log.log.info('Run all snippets with arguments %s' % args)
        for item in self.pipelineitems:
            self.__results__ += item.run(args, queue, profile, log, jobs)


def exec_snippet_unit(item, arg_dict, queue, profile, log):
    arg_str = []
    for key in arg_dict:
        if arg_dict[key] != 'None':
            arg_str.append(key)
            if arg_dict[key] != 'True':
                arg_str.append(arg_dict[key])
    log.log.info('Snippet %s relevant item.arguments: %s' %
                 (item.name, arg_dict))
    try:
        results = get_module_method(
            PYPE_SNIPPETS, item.name, 'results')(arg_dict)
        results = results.values()
        completed = sum([os.path.isfile(x) for x in results]) == len(results)
        log.log.info('Results file(s) for snippet %s: %s' %
                     (item.name, ', '.join(results)))
    except AttributeError:
        completed = False
    if completed:
        log.log.info(('Found results file(s) %s: '
                      'skipping execution of snippet %s')
                     % (', '.join(results), item.name))
        return([])
    else:
        log.log.info('Submit Snippet %s with queue : %s' %
                     (item.name, queue))
        queue_name = '%s_%s_%s' % (generate_uid(), item.name, queue)
        log.add_log(queue_name)
        queuelog = log.programs_logs[queue_name]
        log.log.info(('Add log information for snippets %s '
                      '(for results %s) to folder %s')
                     % (item.name, ', '.join(results), queuelog.__path__))
        queuelog.log.info(
            'Execute snippet %s with queue %s' % (item.name, queue))
        queue = get_module_method(PYPE_QUEUES, queue, 'submit')
        if len(item.jobs) > 0:
            log.log.info('Snippets %s on queue %s depends on jobs: %s' %
                         (item.name, queuelog.__name__,
                          ', '.join(map(str, item.jobs))))
        res_queue = queue(
            ' '.join(map(str, [item.name] + arg_str)), item.requirements,
            item.jobs, queuelog, profile)
        log.log.info('Snippets %s returned %s' % (item.name, res_queue))
        return [res_queue]


def exec_pipeline_unit(item, arg_dict, queue, profile, log):
    parser = argparse.ArgumentParser(prog='pype', description='exec_pipeline')
    subparsers = parser.add_subparsers(dest='modules')
    this_pipeline = get_pipelines(subparsers, {})[item.name]
    arg_str = []
    for key in arg_dict:
        arg_str.append(key)
        arg_str.append(arg_dict[key])
    log.log.info('Pipeline %s relevant item.arguments: %s' %
                 (item.name, arg_dict))
    this_pipeline.submit(subparsers, arg_str, queue, profile, log, item.jobs)
    return this_pipeline.__results__


def exec_snippet(item, argv, queue, profile, log):
    arg_dict = {}
    for key in item.arguments:
        try:
            value = item.arguments[key] % argv
        except TypeError:
            '''
            Composite arguments, WARNING this format might change
            '''
            value = composite_argument(item.arguments[key], argv)
        arg_dict[key] = value
    results = exec_snippet_unit(item, arg_dict, queue, profile, log)
    return(results)


def exec_pipeline(item, argv, queue, profile, log):
    arg_dict = {}
    for key in item.arguments:
        try:
            value = item.arguments[key] % argv
        except TypeError:
            '''
            Composite arguments, WARNING this format might change
            '''
            value = composite_argument(item.arguments[key], argv)
        arg_dict[key] = value
    results = exec_pipeline_unit(item, arg_dict, queue,
                                 profile, log)
    return results


def batch_exec_unit(item, argv, queue, profile, log, exec_unit):
    arg_dict = {}
    results = []
    arg_batch = item.arguments['--input_batch']
    if type(arg_batch) is str:
        arg_batch = arg_batch[arg_batch.find("%(") + 2:arg_batch.find(")")]
        arg_batch = argv[arg_batch]
    elif type(arg_batch) is list:
        pass
    for key in item.arguments:
        if key != '--input_batch':
            try:
                value = item.arguments[key] % argv
            except TypeError:
                '''
                Composite arguments, WARNING this format might change
                '''
                if is_composite_argument(item.arguments[key]):
                    value = composite_argument(item.arguments[key], argv)
                else:
                    value = item.arguments[key]
            arg_dict[key] = value
    for tmp_argv in batch_arguments(arg_batch):
        tmp_argv.update(arg_dict)
        results += exec_unit(item, tmp_argv, queue, profile, log)
    return(results)
