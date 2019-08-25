
from .logger import logger

# logger.info('hello world')
import os
import operator
import random
from .support import merge, dotdict
import funcy
import json
import datetime


INDICATOR_START = '${{'
INDICATOR_END = '}}'

def populate_string(yaml_string, data={}, do_repr=False):
    """
    max one {{  }} per line!
    """

    def xeval(expr, data):
        try:
            return eval(expr, {
                **{name: getattr(funcy, name) for name in funcy.__all__},
                'random': random,
                'env': dotdict(**os.environ),
                'operator': operator,
                **data,
                'data':data,
                'datetime':datetime.datetime,
                'timedelta':datetime.timedelta,
                'json':json
            })
        except Exception as e:
            print(f'error `{e}` in xeval for expression "{expr}"')
            raise e from None
            
    def replace_in_line(line):
        while INDICATOR_START in line and INDICATOR_END in line and not ('#' in line and line.index('#') < line.index(INDICATOR_START)): 
            begin = line.index(INDICATOR_START)
            end = line.index(INDICATOR_END, begin)
            variable_name = line[begin:end].strip().replace(INDICATOR_START,'').replace(INDICATOR_END,'').strip()
            try:
                value = xeval(variable_name, data)
                line = (
                    line[:begin] +
                    # value if isinstance(value, (int, float)) else repr(value) +
                    (repr(value) if do_repr else str(value)) +
                    line[end + len(INDICATOR_END):]
                )
            except Exception as e:
                raise Exception('yaml file needs all data to be evaluated: {{{{ {} }}}}\n {}'.format(variable_name, e))
        return line
    def replace_multiline(string):
        result = ''
        parts = string.split(INDICATOR_START)
        if len(parts) > 1:
            for part in parts:
                if not INDICATOR_END in part:
                    result += part
                else:
                    index = part.index(INDICATOR_END)
                    expr = part[0:index]
                    expr = '\n'.join([line.strip() for line in expr.splitlines()])
                    # print(repr(expr))
                    # print(expr)
                    value = xeval(expr, data)
                    if do_repr:
                        value = repr(value)
                    result += value + part[index:].replace(INDICATOR_END, '')
            return result
        else:
            return string
    result = '\n'.join(map(replace_in_line, yaml_string.splitlines()))
    result = replace_multiline(result)
    return result



