
import json
from funcy import lfilter, post_processing, pluck, count

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def merge(a, b):
    result = dict(**a)

    [result.update({x: dict(**a[x], **b[x])}) for x in set(a.keys()) & set(b.keys())
        if isinstance(a[x], dict) and isinstance(b[x], dict)]

    [result.update({x: [*a[x], *b[x]]}) for x in set(a.keys()) & set(b.keys())
        if isinstance(a[x], list) and isinstance(b[x], list)]

    [result.update({x: a[x] if x in a else b[x]}) for x in set(a.keys()) ^ set(b.keys() )]

    return result

if __name__ == '__main__':
    x = merge(
        dict(
            a=dict(b=[3,4]),
            b=[5,4,6]
        ),
        dict(
            a=dict(c=[9]),
            b=[1]
        )
    )
    print(x)



def zip_pluck(d, keys, enumerate=False):
    args = [pluck(k, d) for k in keys]
    if enumerate:
        args = [count(), *args]
    return zip(*args)

join_yields = lambda separator='': post_processing(lambda parts: separator.join(list(parts)))

def remove_indentation(string: str):
    lines = string.split('\n')
    lines = lfilter(bool, lines)
    indents = [len(line) - len(line.lstrip()) for line in lines]
    base_indent = min(indents) if indents else 0
    lines = [x[base_indent:] for x in lines]
    # lines = lfilter(lambda s: len(s.replace(' ', '')), lines)
    # print(lines)
    return '\n'.join(lines)

def indent_to(indentation, string):
    string = remove_indentation(string)
    return '\n'.join([indentation + line for line in string.split('\n')]).lstrip()






# def replace_expressions(obj):
#     for k, v in obj.items():
#         if isinstance(v, str):
#             obj[k] = EXPR_INDICATOR + str(v) + EXPR_INDICATOR
#         if isinstance(v, dict):
#             replace_expressions(v)
#     return obj

# def _repr_eval_dict(obj, indentation=''):
#     obj = replace_expressions(obj)
#     dumped = json.dumps(obj, indent=4)
#     dumped = dumped.replace('"' + EXPR_INDICATOR, '').replace(EXPR_INDICATOR + '"', '')
#     dumped = bytes(dumped, 'utf-8').decode('unicode_escape')
#     dumped = indent_to(indentation, dumped)
#     return dumped.lstrip()
    
EXPR_START = '${{'
EXPR_END = '}}'

def repr_eval_dict(obj, indentation=''):
    dumped = json.dumps(obj, indent=4)
    # dumped = populate_string(dumped, do_eval=False)
    dumped = dumped.replace('"' + EXPR_START, '').replace(EXPR_END + '"', '')
    dumped = bytes(dumped, 'utf-8').decode('unicode_escape')
    dumped = indent_to(indentation, dumped)
    return dumped.lstrip()



if __name__ == '__main__':
    join_yields()
    print('hello')
    x = remove_indentation("""
    ciao x
        come va
    """)
    print(x)
    x = '''
    xxx
        yy
    '''
    print(indent_to('....', x))