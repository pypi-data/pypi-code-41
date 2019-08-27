__all__ = ["StopParsing", "ControlAction", "Yaap"]

import sys
import json
import yaml
import argparse
from dataclasses import dataclass, field
from typing import Dict, Sequence, Any

import jsonschema

from .argument import *


class StopParsing(Exception):

    def __init__(self, args: Sequence[str]):
        super(StopParsing, self).__init__()
        self.args = args


class ControlAction(argparse.Action):

    def __init__(self, *args, arse=None, **kwargs):
        super(ControlAction, self).__init__(*args, **kwargs)
        self.arse: Yaap = arse

        assert self.arse is not None
        subparser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        group = subparser.add_mutually_exclusive_group()
        group.add_argument("--load", type=str, metavar="CONFIG")
        group.add_argument("--schema", action="store_true", default=False)
        self.subparser = subparser

    def show_schema(self):
        schema = self.arse.schema()
        sys.stdout.write(json.dumps(schema, ensure_ascii=False, indent=2))
        sys.exit()

    def __call__(self, parser, namespace, values, option_string=None):
        delattr(namespace, self.dest)
        if not values:
            return
        values = ["--" + v.lstrip(self.arse.control_char)
                  if v.startswith(self.arse.control_char) else v for v in
                  values]
        subargs = self.subparser.parse_args(values)
        if subargs.schema:
            self.show_schema()
        elif subargs.load is not None:
            with open(subargs.load, "r") as f:
                cfg = yaml.safe_load(f)
            self.arse.validate(cfg)
            args = []
            for k, v in cfg.items():
                if v is None:
                    continue
                arg: Argument = self.arse.arguments[k]
                if isinstance(v, bool):
                    assert isinstance(arg, Bool)
                    if v != arg.invert:
                        args.append(f"--{k}")
                elif isinstance(v, str):
                    args.extend([f"--{k}", v])
                elif isinstance(v, list):
                    args.append(f"--{k}")
                    args.extend(map(str, v))
                else:
                    args.extend((f"--{k}", str(v)))
            raise StopParsing(args)


@dataclass
class Yaap:
    name: str = None
    desc: str = None
    control_char: str = "@"
    parser: argparse.ArgumentParser = field(init=False, hash=False)
    arguments: Dict[str, Argument] = field(init=False, hash=False,
                                           default_factory=dict)

    def __post_init__(self):
        if len(self.control_char) > 1:
            raise ValueError(f"control character must not be a string: "
                             f"len({self.control_char}) > 1")
        self.parser = argparse.ArgumentParser(
            prog=None if self.name is None else self.name,
            description=None if self.desc is None else self.desc
        )
        self.parser.add_argument("CONTROL", nargs="*",
                                 action=lambda *args, **kwargs:
                                 ControlAction(*args, arse=self, **kwargs))

    def add(self, arg: Argument):
        if arg.name in self.arguments:
            raise IndexError(f"argument of the same name exists: "
                             f"{self.arguments[arg.name]}")
        self.arguments[arg.name] = arg
        args, kwargs = arg.generate_args()
        self.parser.add_argument(*args, **kwargs)

    def add_int(self,
                name: str,
                shortcut: str = None,
                help: str = None,
                required: bool = False,
                default: Any = None,
                min_bound: int = None,
                max_bound: int = None,
                multiples: int = None,
                choices: Sequence[int] = None,
                is_list: bool = False,
                num_elements: int = None):
        """Specifies an integer-type argument.

        Arguments:
            name (str): Name of the argument. Unlike `argparse`, preceding
                hyphens should be omitted. Allows specification by `--{name}`.
            shortcut (optional, str): Argument shortcut. Allows specification
                by `-{shortcut}`.
            help (optional, str): Help text.
            required (optional, str): Whether this argument is required.
            default (optional, *): Default value for the argument. Must be
                hashable (`__hash__`).
            min_bound (optional, int): Minimum bounds for the integer argument.
                Bound inclusive.
            max_bound (optional, int): Maximum bounds for the integer argument.
                Bound inclusive.
            multiples (optional, int): Enforces the argument to be a multiple
                of this number.
            choices (optional, Sequence[int]): Enforces the argument to be
                one of these candidate numbers.
            is_list (bool): Whether this argument is of list type. If true,
                this argument can be specified with multiple values, i.e.

                    --{name} {val1} {val2} ... {valN}

                (default: False)
            num_elements (optional, int): Number of required elements.
                Applicable only if `is_list` is true.
        """
        kwargs = dict(
            name=name,
            shortcut=shortcut,
            help=help,
            required=required,
            default=default,
            min_bound=min_bound,
            max_bound=max_bound,
            multiples=multiples,
            choices=choices
        )
        if is_list:
            kwargs.update(dict(num_elements=num_elements))
        cls = Int if not is_list else IntList
        return self.add(cls(**kwargs))

    def add_flt(self,
                name: str,
                shortcut: str = None,
                help: str = None,
                required: bool = False,
                default: Any = None,
                min_bound: float = None,
                max_bound: float = None,
                multiples: float = None,
                choices: Sequence[float] = None,
                is_list: bool = False,
                num_elements: int = None):
        """Specifies a float-type argument.

        Arguments:
            name (str): Name of the argument. Unlike `argparse`, preceding
                hyphens should be omitted. Allows specification by `--{name}`.
            shortcut (optional, str): Argument shortcut. Allows specification
                by `-{shortcut}`.
            help (optional, str): Help text.
            required (optional, str): Whether this argument is required.
            default (optional, *): Default value for the argument. Must be
                hashable (`__hash__`).
            min_bound (optional, float): Minimum bounds for the float argument.
                Bound inclusive.
            max_bound (optional, float): Maximum bounds for the float argument.
                Bound inclusive.
            multiples (optional, float): Enforces the argument to be a multiple
                of this number.
            choices (optional, Sequence[float]): Enforces the argument to be
                one of these candidate numbers.
            is_list (bool): Whether this argument is of list type. If true,
                this argument can be specified with multiple values, i.e.

                    --{name} {val1} {val2} ... {valN}

                (default: False)
            num_elements (optional, int): Number of required elements.
                Applicable only if `is_list` is true.
        """
        kwargs = dict(
            name=name,
            shortcut=shortcut,
            help=help,
            required=required,
            default=default,
            min_bound=min_bound,
            max_bound=max_bound,
            multiples=multiples,
            choices=choices
        )
        if is_list:
            kwargs.update(dict(num_elements=num_elements))
        cls = Float if not is_list else FloatList
        return self.add(cls(**kwargs))

    def add_float(self, *args, **kwargs):
        """See `self.add_flt`."""
        return self.add_flt(*args, **kwargs)

    def add_pth(self,
                name: str,
                shortcut: str = None,
                help: str = None,
                required: bool = False,
                default: Any = None,
                must_exist: bool = False,
                is_dir: bool = False,
                is_list: bool = False,
                num_elements: int = None):
        """Specifies a path-type argument.

        Arguments:
            name (str): Name of the argument. Unlike `argparse`, preceding
                hyphens should be omitted. Allows specification by `--{name}`.
            shortcut (optional, str): Argument shortcut. Allows specification
                by `-{shortcut}`.
            help (optional, str): Help text.
            required (optional, str): Whether this argument is required.
            default (optional, *): Default value for the argument. Must be
                hashable (`__hash__`).
            must_exist (bool): The specified path must be an existing one.
                The argument parser will check whether path(s) do exist.
                (default: False)
            is_dir (bool): Whether the path is of directory type.
                The argument parser will check whether path(s) are directories.
                (default: False)
            is_list (bool): Whether this argument is of list type. If true,
                this argument can be specified with multiple values, i.e.

                    --{name} {val1} {val2} ... {valN}

                (default: False)
            num_elements (optional, int): Number of required elements.
                Applicable only if `is_list` is true.
        """
        kwargs = dict(
            name=name,
            shortcut=shortcut,
            help=help,
            required=required,
            default=default,
            must_exist=must_exist,
            is_dir=is_dir
        )
        if is_list:
            kwargs.update(dict(num_elements=num_elements))
        cls = Path if not is_list else PathList
        return self.add(cls(**kwargs))

    def add_path(self, *args, **kwargs):
        """See `self.add_pth`."""
        return self.add_pth(*args, **kwargs)

    def add_str(self,
                name: str,
                shortcut: str = None,
                help: str = None,
                required: bool = False,
                default: Any = None,
                min_length: int = None,
                max_length: int = None,
                regex: str = None,
                format: str = None,
                choices: Sequence[float] = None,
                is_list: bool = False,
                num_elements: int = None):
        """Specifies a string-type argument.

        Arguments:
            name (str): Name of the argument. Unlike `argparse`, preceding
                hyphens should be omitted. Allows specification by `--{name}`.
            shortcut (optional, str): Argument shortcut. Allows specification
                by `-{shortcut}`.
            help (optional, str): Help text.
            required (optional, str): Whether this argument is required.
            default (optional, *): Default value for the argument. Must be
                hashable (`__hash__`).
            min_length (optional, int): Minimum bound for length (inclusive).
            max_length (optional, int): Maximum bound for length (inclusive).
            regex (optional, str): Regular expression for matching values.
                The argument parser will check whether the value(s) conform
                the regular expression.
            format (optional, str): String format, as supported by JSONSchema.
                Some common formats include `date-time`, `time`, `url`, `email`.
                More information at JSONSchema reference.
            choices (optional, Sequence[str]): Enforces the argument to be
                one of these candidate strings.
            is_list (bool): Whether this argument is of list type. If true,
                this argument can be specified with multiple values, i.e.

                    --{name} {val1} {val2} ... {valN}

                (default: False)
            num_elements (optional, int): Number of required elements.
                Applicable only if `is_list` is true.
        """
        kwargs = dict(
            name=name,
            shortcut=shortcut,
            help=help,
            required=required,
            default=default,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            format=format,
            choices=choices
        )
        if is_list:
            kwargs.update(dict(num_elements=num_elements))
        cls = Str if not is_list else StrList
        return self.add(cls(**kwargs))

    def add_bol(self,
                name: str,
                shortcut: str = None,
                help: str = None,
                required: bool = False,
                invert: bool = False):
        """Specifies a bool-type argument. This is value-less argument, which is
        specified with only the keyword argument, i.e. `--{name}`.

        Arguments:
            name (str): Name of the argument. Unlike `argparse`, preceding
                hyphens should be omitted. Allows specification by `--{name}`.
            shortcut (optional, str): Argument shortcut. Allows specification
                by `-{shortcut}`.
            help (optional, str): Help text.
            required (optional, str): Whether this argument is required.
            invert (bool): Whether to invert bool operation. The default
                behavior stores True when the argument is specified and False
                for otherwise.
                (default: False)
        """
        return self.add(Bool(
            name=name,
            shortcut=shortcut,
            help=help,
            required=required,
            invert=invert
        ))

    def add_bool(self, *args, **kwargs):
        """See `self.add_bol`"""
        return self.add_bol(*args, **kwargs)

    def add_intlist(self, *args, **kwargs):
        return self.add_int(*args, **kwargs, is_list=True)

    def add_floatlist(self, *args, **kwargs):
        return self.add_flt(*args, **kwargs, is_list=True)

    def add_pathlist(self, *args, **kwargs):
        return self.add_pth(*args, **kwargs, is_list=True)

    def add_strlist(self, *args, **kwargs):
        return self.add_str(*args, **kwargs, is_list=True)

    def schema(self) -> dict:
        """Returns this argument specification in terms of JSONSchema."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": str(hash((self.name, self.desc))),
            "type": "object",
            "properties": {arg.name: arg.json_schema()
                           for arg in self.arguments.values()},
            "required": [arg.name for arg in
                         self.arguments.values() if arg.required]
        }

    def validate(self, args: dict):
        """Validate a dictionary of arguments against this argument spec."""
        jsonschema.validate(args, self.schema())

    def parse(self, args: Sequence[str] = None) -> dict:
        try:
            args = self.parser.parse_args(args)
        except StopParsing as e:
            args = self.parser.parse_args(e.args)
        return vars(args)
