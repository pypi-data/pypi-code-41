import builtins
import argparse
from inspect import signature, _empty
from docstring_parser.parser import parse


def foo2parser(foo):
    """Create a new parser with description matching the short description of the function."""
    return argparse.ArgumentParser(description=parse(foo.__doc__).short_description)


def get_defaults(foo):
    sign = signature(foo)
    return {n: p.default for n,p in sign.parameters.items() if not p.default == _empty}


def parse_arguments(foo):
    defaults = get_defaults(foo)
    parsed_doc = parse(foo.__doc__)
    all_params = {p.arg_name for p in parsed_doc.params}
    assert set(defaults).issubset(all_params), "Some parameters with defaults are not in the description."
    for p in parsed_doc.params:
        if p.arg_name not in ('kwds', 'args'):
            kwds = {}
            kwds['help'] = p.description
            try:
                kwds['type'] = getattr(builtins, p.type_name)
            except AttributeError:
                pass
            arg_name = p.arg_name
            if arg_name in defaults:
                kwds['help'] += " [default = {}]".format(defaults[arg_name])
                kwds['default'] = defaults[arg_name]
                arg_name = "--" + arg_name
            yield arg_name, kwds


def register_docs(foo, parser=None):
    if parser is None:
        parser = foo2parser(foo)
    for name, kwds in parse_arguments(foo):
        parser.add_argument(name, **kwds)
    return parser


if __name__ == '__main__':
    from docstr2argparse.mocked_foo import apex3d as foo
    parser = register_docs(foo)
    args = parser.parse_args()
    print(args.__dict__)
