"""Simple boilerplate for cli scripts"""

from collections import ChainMap, OrderedDict
import inspect
import configparser
from pathlib import Path
from fire import Fire
from typing import NamedTuple as Schema  # Facilitates importing from one location
import os

__version__ = '0.1.1'


class ConfigFile:
    """Configuration file (sth.cfg) handling"""

    @staticmethod
    def is_in_module(f):
        return len(list(Path(f).parent.glob('__init__.py')))

    @staticmethod
    def cfgs_gen(f):
        yield from Path(f).parent.glob('*.cfg')

    @staticmethod
    def find_cfg(f):
        f = Path(f)
        cfgs = list(ConfigFile.cfgs_gen(f))
        if len(cfgs) == 0:
            if ConfigFile.is_in_module(f):
                return ConfigFile.find_cfg(f.parent)
            else:
                return None
        else:
            return cfgs[0]

    @staticmethod
    def read_config(_filepath='test.cfg') -> dict:
        filepath = Path(_filepath)
        if not filepath.exists():
            return {}

        file_config = configparser.ConfigParser()
        file_config.read(filepath)
        if 'Default' in file_config:
            return dict(file_config['Default'])
        else:
            print(f'warning: config file found at {str(filepath)}, but it was missing section named [Default]')
            return {}

    @staticmethod
    def get_config_path(configuration_tuple):
        client_file = Path(inspect.getfile(configuration_tuple.__class__))
        if hasattr(configuration_tuple, 'cwd'):
            p = Path(configuration_tuple._asdict()['cwd'])
            if not p.absolute():
                p = client_file / p
        else:
            p = client_file
        config_file = ConfigFile.find_cfg(p)

        return config_file


decorators_state = {
    'schema': None,
    'generated': None,
}


class Decorators:
    """Decorator helpers for the client interface (Configurable)"""

    @staticmethod
    def schema(cls):
        decorators_state['schema'] = cls()
        return cls

    @staticmethod
    def cli(cls):
        state = decorators_state

        def init(self, **cli_args):
            """Generated init"""
            c(cli_args, state['schema'])

        cls_attrs = dict(
            # __slots__=cls.__slots__,
            __init__=init,
            __repr__=cls.__repr__,
            **{k: v for k, v in cls.__dict__.items() if not k.startswith('_')}
        )

        _Cli = type('Cli', (cls,), cls_attrs)
        state['generated'] = _Cli

        return _Cli


class Configurable:
    """Configuration management"""
    # TODO: idiomatic handling for use cases that apply to NamedTuple
    configured = None

    def __filter_fields(self, d: dict, nt):
        """Excludes fields not found in the schema/namedtuple"""
        res = {}
        for k, v in d.items():
            if k in nt._fields:
                res.update({k: v})

        return res

    def __initialize(self, params: dict, configuration_tuple):
        """Chains all configuration options together"""
        config_file = ConfigFile.get_config_path(configuration_tuple)
        if config_file is not None:
            config_dict = self.__filter_fields(ConfigFile.read_config(config_file), configuration_tuple)
        else:
            config_dict = {}

        self.configured = dict(ChainMap(
            params,
            config_dict,
            self.__filter_fields(os.environ, configuration_tuple),
            configuration_tuple._asdict()
        ))

        return self.configured

    def __call__(self, a=None, b=None, *, noprepare=False):
        """Handles delegating method overloading acting as a decorator and initiator for the
        chain configuration"""
        is_initializing = (a is not None and b is not None)
        if is_initializing:
            return self.__initialize(params=a, configuration_tuple=b)

        is_decorating = (a is not None and b is None)
        if is_decorating:
            is_schema = any(_cls is tuple for _cls in inspect.getmro(a))
            if is_schema:
                return Decorators.schema(a)
            else:
                cli = Decorators.cli(a)
                if not noprepare:
                    prepare(decorators_state['generated'], decorators_state['schema'])

                return cli

    def __repr__(self):
        return repr(self.configured)

    def __getattr__(self, item):
        res = None
        if self.configured is not None:
            res = self.configured[item]

        return res

    def __getitem__(self, item):
        print(item)
        return self.configured[item]


c = Configurable()


class Doc:
    """Doc string handling"""

    @staticmethod
    def wrap_method_docs(cls: object, nt):
        methods = [m.object for m in inspect.classify_class_attrs(cls)
                   if m.kind == 'method' and not m.name.startswith('_')]
        for m in methods:
            Doc.prepare_doc(nt, m)

    @staticmethod
    def params_with_defs(N):
        """parse the source of the schema for its details"""
        params_with_definitions = tuple(
            tuple(
                str(arg_and_def).strip()
                for arg_and_def in src_line.split(':', 1)
            )
            for src_line in inspect.getsourcelines(N.__class__)[0][1:]
            if src_line.startswith(' ')
        )
        return OrderedDict(params_with_definitions)

    @staticmethod
    def attr_map(N):
        """Mapping for the schema's details"""
        _attr_map = {}
        for param, _def in Doc.params_with_defs(N).items():
            _type, def_desc = _def.split('=', 1)
            _type = _type.strip()

            # TODO: this won't handle # in strings ...
            if '#' in def_desc:
                default, description = def_desc.split('#', 1)
                default = default.strip()
                description = description.strip()
            else:
                default = def_desc.strip()
                description = ''

            _attr_map.update(
                {
                    param: {
                        'type': _type,
                        'default': default,
                        'description': description,
                    }
                }
            )
        return _attr_map

    @staticmethod
    def prepare_doc(N, f):
        """Replace docstrings to include the parameters (schema)"""
        # TODO: fix for fire 0.2.1
        ps_doc = []
        for attr_name, cls in N.__annotations__.items():
            attr = Doc.attr_map(N).get(attr_name)
            if attr is None:
                continue

            ps_doc.append(f'    --{attr_name} ({attr["type"]}): {attr["description"]} (Default is {attr["default"]})')

        ps_doc = '\n'.join(ps_doc)
        doc = f.__doc__
        doc = (doc if doc is not None else '') + '\nArgs:\n' + ps_doc
        f.__doc__ = doc


def prepare_signatures(cls, nt):
    """Uses the implicit Configuration NamedTuple's fields as the
    classes methods' signatures i.e. helps fire to show up the
    named tuple's arguments instead of a generic "**params" for the
    subcommands on command line.

    Works in-place, returns None
    """
    # methods = {k: cls.__dict__[k] for k in inspect.getmembers(cls, inspect.ismethod)}
    methods = {
        k: v for k, v in cls.__dict__.items()
        if not k.startswith('_') and inspect.isfunction(v)
    }
    for m_name, method in methods.items():
        params = [
            inspect.Parameter(name=field, kind=inspect._VAR_KEYWORD)
            for field in nt._fields
        ]
        sig = inspect.signature(method)
        method.__signature__ = sig.replace(parameters=[
            inspect.Parameter(name='self', kind=inspect._VAR_KEYWORD),
            *params
        ])


def prepare(cls, nt):
    """Beef: prepares signatures, docstrings and initiates fire for the cli-magic"""
    prepare_signatures(cls, nt)
    Doc.wrap_method_docs(cls, nt)
    Fire(cls)
