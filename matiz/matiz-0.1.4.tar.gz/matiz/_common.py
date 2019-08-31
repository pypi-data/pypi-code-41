import itertools
import logging

import yaml

_logger = logging.getLogger(__name__)


def load_y(yaml_string: str) -> object:
    """Shortcut to yaml.dump (since explicit Loader specification became required)."""
    return yaml.load(yaml_string, Loader=yaml.Loader)


def dump_y(py_object: object) -> str:
    """Shortcut to yaml.dump (since explicit Dumper specification became required)."""
    return yaml.dump(py_object, Dumper=yaml.Dumper)


def trace_call(cls, positional_args, keyword_args, msg="", logger=None):
    statement = form_call_statement(cls, positional_args, keyword_args)

    (logger or _logger).debug(f" {msg}: calling: {statement}")
    print(f" {msg}: calling: {statement}")


def form_call_statement(cls, positional_args, keyword_args):
    args_ = (str(repr(a)) for a in positional_args)
    kwargs_ = (f"{k}={v!r}" for k, v in keyword_args.items())
    return f"{cls.__name__}({', '.join(itertools.chain(args_, kwargs_))})"
