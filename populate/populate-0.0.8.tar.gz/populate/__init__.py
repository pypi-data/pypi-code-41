
from .logger import logger

# logger.info('hello world')
import os
import operator
import random
from .support import merge, dotdict, indent_to
import funcy
import json
import datetime


INDICATOR_START = '${{'
INDICATOR_END = '}}'




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
            'json':json,
            'indent_to': indent_to,
        })
    except Exception as e:
        raise Exception(f'error `{e}` in xeval for expression "{expr}"') from None

def populate_string(yaml_string, data={}, do_repr=False, do_eval=True, evaluator=xeval, INDICATOR_START=INDICATOR_START, INDICATOR_END=INDICATOR_END):
    """
    max one {{  }} per line!
    """
    # def replace_in_line(line):
    #     if INDICATOR_START in line and INDICATOR_END in line and not ('#' in line and line.index('#') < line.index(INDICATOR_START)): 
    #         begin = line.index(INDICATOR_START)
    #         end = line.index(INDICATOR_END, begin)
    #         expression = line[begin:end].replace(INDICATOR_START,'').replace(INDICATOR_END,'')
    #         try:
    #             if do_eval:
    #                 if evaluator:
    #                     value = evaluator(expression, data)
    #                 else:
    #                     value = xeval(expression, data)
    #             else:
    #                 value = expression
    #             line = (
    #                 line[:begin] +
    #                 # value if isinstance(value, (int, float)) else repr(value) +
    #                 (repr(value) if do_repr else str(value)) +
    #                 line[end + len(INDICATOR_END):]
    #             )
    #         except Exception as e:
    #             raise Exception('yaml file needs all data to be evaluated: {{{{ {} }}}}\n {}'.format(expression, e))
    #     return line
    def replace_multiline(string):
        result = ''
        parts = string.split(INDICATOR_START)
        if len(parts) > 1:
            for part in parts:
                if not INDICATOR_END in part:
                    result += part
                else:
                    # if not r'\n' in part:
                    #     result += INDICATOR_START + part
                    #     continue
                    index = part.index(INDICATOR_END)
                    expr = part[0:index]
                    # print(repr(expr))
                    expr = '\n'.join([line for line in expr.splitlines()]).strip() # TODO this strip is not ok
                    # print(repr(expr))
                    # print(expr)
                    if do_eval:
                        value = evaluator(expr, data)
                    else:
                        value = expr
                    if do_repr:
                        value = repr(value)
                    result += value + part[index:].replace(INDICATOR_END, '')
            return result
        else:
            return string
    # result = '\n'.join(map(replace_in_line, yaml_string.splitlines()))
    result = replace_multiline(yaml_string)
    return result

