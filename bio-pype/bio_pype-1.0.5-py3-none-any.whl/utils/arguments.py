from pype import __config__
from pype.misc import get_module_method

PYPE_SNIPPETS = __config__.PYPE_SNIPPETS


def batch_arguments(batch_info, keys_dict={}):
    if type(batch_info) is str:
        with open(batch_info, 'rt') as input_list:
            argument_keys = next(input_list).strip().split('\t')
            for key in keys_dict:
                if key in argument_keys:
                    pos_k = argument_keys.index(key)
                    argument_keys[pos_k] = keys_dict[key]
            for line in input_list:
                line = line.rstrip()
                if line:
                    tmp_argv = {}
                    line = line.strip().split('\t')
                    for index in range(len(argument_keys)):
                        tmp_argv[argument_keys[index]] = line[index]
                    yield tmp_argv
    elif type(batch_info) is list:
        for args in batch_info:
            yield args


def is_composite_argument(argument):
    try:
        snippet = argument['snippet_name']
        res_key = argument['result_key']
        res_arguments = argument['result_arguments']
        if type(snippet) is str and type(res_key) is str \
                and type(res_arguments) is dict:
            return True
        else:
            return False
    except KeyError:
        return False


def composite_argument(argument, argv):
    snippet = argument['snippet_name']
    res_key = argument['result_key']
    res_arguments = argument['result_arguments']
    try:
        keys_dict = argument['args_synonims']
    except KeyError:
        keys_dict = {}
    res_args_tmp = {}
    for res_arg_key in res_arguments:
        if res_arg_key != '--input_batch':
            res_args_tmp[res_arg_key] = res_arguments[
                res_arg_key] % argv
    if '--input_batch' in res_arguments.keys():
        values = []
        input_batch = res_arguments['--input_batch']
        if type(input_batch) is str:
            input_batch = input_batch % argv
        elif type(input_batch) is list:
            pass
        for tmp_argv in batch_arguments(input_batch, keys_dict):
            tmp_argv.update(res_args_tmp)
            values.append(get_module_method(
                PYPE_SNIPPETS, snippet,
                'results')(tmp_argv)[res_key])
        value = ' '.join(map(str, values))
    else:
        value = get_module_method(
            PYPE_SNIPPETS, snippet, 'results')(res_args_tmp)[res_key]
    return(value)
