"""Simple boilerplate for cli scripts"""

from collections import ChainMap
import inspect
from fire import Fire
# from typing import NamedTuple as Schema  # Facilitates importing from one location
# from typing import NamedTuple  # Facilitates importing from one location
import os
from clima.schema import MetaSchema
from clima import doc, configfile

__version__ = '0.2.1'

decorators_state = {
    'schema': None,
    'generated': None,
}


def add_to_decorators(key, value):
    decorators_state[key] = value


class Decorators:
    """Decorator helpers for the client interface (Configurable)"""

    @staticmethod
    def schema(cls):
        # if 'post_init' in cls.__dict__:
        #     decorators_state['schema'] = cls.post_init(cls)
        # else:
        decorators_state['schema'] = cls()
        return cls

    @staticmethod
    def cli(cls):
        state = decorators_state

        def init(self, **cli_args):
            """Generated init"""
            c(cli_args, state['schema'])

        cls_attrs = dict(
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

    def __init__(self):
        pass

    def __filter_fields(self, d: dict, nt):
        """Excludes fields not found in the schema/namedtuple"""
        res = {}
        for k, v in d.items():
            if k in nt._fields:
                res.update({k: v})

        return res

    def _type_correct_with(self, cdict, cfg_tuple):
        """Use type hints to cast variables into their intended types"""
        # TODO: This would be cleaner, if the config would use Schema or derivative in the
        # first place and use its validation process
        res = {}
        for k, v in cdict.items():
            res.update({k: type(getattr(cfg_tuple, k))(v)})
        return res

    def __initialize(self, params: dict, configuration_tuple):
        """Chains all configuration options together"""
        config_file = configfile.get_config_path(configuration_tuple)
        if config_file is not None:
            config_dict = self.__filter_fields(configfile.read_config(config_file), configuration_tuple)
            config_dict = self._type_correct_with(config_dict, configuration_tuple)
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
        chaining of parameters with the configuration"""
        is_initializing = (a is not None and b is not None)
        if is_initializing:
            return self.__initialize(params=a, configuration_tuple=b)

        is_decorating = (a is not None and b is None)
        if is_decorating:
            # is_schema = any(_cls is tuple for _cls in inspect.getmro(a))
            is_schema = isinstance(a, MetaSchema)
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
            try:
                res = self.configured[item]
            except Exception:
                res = getattr(self.configured, item)

        return res

    def __getitem__(self, item):
        return self.configured[item]


c = Configurable()


class Schema(metaclass=MetaSchema):
    def _asdict(self):
        return schema.asdict(self)

    def _wrap(self):
        c(self)
        c.configured = self

    @staticmethod
    def post_init(self, *args):
        pass

    @property
    def _fields(self):
        fields = [
            k for k in self.__dir__()
            if not k.startswith('_')
               and not inspect.ismethod(getattr(self, k))
        ]
        return fields


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
    doc.wrap_method_docs(cls, nt)
    Fire(cls)

# S = partial(c, Schema)
