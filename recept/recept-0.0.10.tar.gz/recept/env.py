"""
Env allows you to use 12factor inspired env variables for configuration.

ToEnvMixin is a class that does the opposite - Creates an environment variable
dictionary from class attributes.
"""

__all__ = ["Env", "ToEnvMixin"]

import os
import json
import logging
from pathlib import Path
from copy import deepcopy
from typing import Callable, Any, Optional, Dict
from urllib.parse import urlparse, ParseResult as UrlParseResult

from recept.errors import ImproperlyConfigured
from recept.utils import camel_case_to_snake_case


logger = logging.getLogger(__name__)


BOOLEAN_TRUE_STRINGS = ("true", "on", "yes")


def parse_value(value: str, cast) -> Any:
    """Parse and cast provided value.

    Args:
        value: Stringed value.
        cast: Callable used for casting or type.

    Returns:
        Casted value.
    """
    if cast is None:
        return value
    elif cast is bool:
        return value.lower() in BOOLEAN_TRUE_STRINGS
    elif isinstance(cast, list):
        return list(map(cast[0], [x for x in value.split(",") if x]))
    elif isinstance(cast, tuple):
        val = value.strip("(").strip(")").split(",")
        return tuple(map(cast[0], [x for x in val if x]))
    elif isinstance(cast, dict):
        key_cast = cast.get("key", str)
        value_cast = cast.get("value", str)
        value_cast_by_key = cast.get("cast", dict())
        return dict(
            map(
                lambda kv: (
                    key_cast(kv[0]),
                    parse_value(
                        kv[1], value_cast_by_key.get(kv[0], value_cast)
                    ),
                ),
                [val.split("=") for val in value.split(";") if val],
            )
        )
    elif cast is dict:
        return dict(
            val.split("=", maxsplit=1) for val in value.split(",") if val
        )
    elif cast is list:
        return [x for x in value.split(",") if x]
    elif cast is tuple:
        val = value.strip("(").strip(")").split(",")
        return tuple([x for x in val if x])
    else:
        value = cast(value)
    return value


class NoValue(object):
    def __repr__(self):
        return "<{0}>".format(self.__class__.__name__)


class Env(object):
    """Provide scheme-based lookups of environment variables.

    This elevates the caller of doing conversion or passing default value.

    Usage::

        env = Env(RECEPT_DEBUG=bool, MONGO_USERNAME=(str, 'DEFAULT'))
        if env('RECEPT_DEBUG'):
            ...

    Args:
        prefix: Prefix used for variables. For example if prefix is set to
            `mongo` and you search for variable `username` then the env object
            will search for the key `MONGO_USERNAME` in the `os.environment`.
            If `prefix` is `None`, search key will only be `USERNAME`.s

        **scheme: Types definition for variables.
    """

    ENVIRON = os.environ
    NOTSET = NoValue()
    URL_CLASS = UrlParseResult

    def __init__(self, prefix: str = None, **scheme):
        self.prefix = prefix
        self.scheme = scheme

    def __str__(self):
        if self.prefix:
            return f"Env(prefix={self.prefix})"
        return "Env()"

    __repr__ = __str__

    def bake(self, prefix: str = None, **scheme):
        """Return a new instance of Env with merged parameters."""
        s = deepcopy(self.scheme)
        s.update(scheme)
        return Env(prefix=prefix, **s)

    def __call__(self, var, cast=None, default=NOTSET, parse_default=False):
        return self.get_value(
            var, cast=cast, default=default, parse_default=parse_default
        )

    def __contains__(self, var):
        if self.prefix is not None:
            var = f"{self.prefix}_{var}"
        return var.upper() in self.ENVIRON

    # Shortcuts

    def str(self, var, default=NOTSET, multiline=False) -> str:
        value = self.get_value(var, default=default)
        if multiline:
            return value.replace("\\n", "\n")
        return value

    def bytes(self, var, default=NOTSET, encoding="utf8") -> bytes:
        return self.get_value(var, default=default, cast=str).encode(encoding)

    def bool(self, var, default=NOTSET) -> bool:
        return self.get_value(var, cast=bool, default=default)

    def int(self, var, default=NOTSET) -> int:
        return self.get_value(var, cast=int, default=default)

    def float(self, var, default=NOTSET) -> float:
        return self.get_value(var, cast=float, default=default)

    def json(self, var, default=NOTSET) -> dict:
        return self.get_value(var, cast=json.loads, default=default)

    def list(self, var, cast=None, default=NOTSET) -> list:
        return self.get_value(
            var, cast=list if cast is None else [cast], default=default
        )

    def tuple(self, var, cast=None, default=NOTSET) -> tuple:
        return self.get_value(
            var, cast=tuple if cast is None else (cast,), default=default
        )

    def dict(self, var, cast=dict, default=NOTSET) -> dict:
        return self.get_value(var, cast=cast, default=default)

    def url(self, var, default=NOTSET) -> UrlParseResult:
        return self.get_value(
            var, cast=urlparse, default=default, parse_default=True
        )

    def path(self, var, default=NOTSET, **kwargs) -> Path:
        return Path(self.get_value(var, default=default), **kwargs)

    def get_value(
        self,
        var: str,
        cast: Optional[Callable[[str], Any]] = None,
        default: Any = NOTSET,
        parse_default: bool = False,
    ) -> Any:
        """Return value for given environment variable.

        Args:
            var: Name of variable.
            cast: Callable used to cast return value.
            default: If var not present in environ, return this instead.
            parse_default: Parse the default value too.

        Returns:
            Value from environment or default if value is not set.
        """

        logger.debug(
            "get '%s' casted as '%s' with default '%s'", var, cast, default
        )

        if var in self.scheme:
            var_info = self.scheme[var]

            try:
                has_default = len(var_info) == 2
            except TypeError:
                has_default = False

            if has_default:
                if not cast:
                    cast = var_info[0]

                if default is self.NOTSET:
                    try:
                        default = var_info[1]
                    except IndexError:
                        pass
            else:
                if not cast:
                    cast = var_info

        search_var = (
            var.upper()
            if self.prefix is None
            else f"{self.prefix}_{var}".upper()
        )
        try:
            value = self.ENVIRON[search_var]
        except KeyError:
            if default is self.NOTSET:
                raise ImproperlyConfigured(
                    f"Set the {search_var} environment variable"
                )

            value = default

        if (
            cast is None
            and default is not None
            and not isinstance(default, NoValue)
        ):
            cast = type(default)

        if value != default or (parse_default and value):
            value = parse_value(value, cast)

        return value


class ToEnvMixin:
    """ToEnvMixin provides a class to env variables dictionary function.

    It will only convert simple types to environment variables:

        str, bytes, bool, int, float

    Usage::

        >>> @dataclass
        ... class Mongo(ToEnvMixin):
        ...     host: str = "127.0.0.1"
        ...     port: int = 27017
        ...
        >>> mongo = Mongo()
        >>> mongo.to_env()
        {
            "MONGO_HOST": "127.0.0.1",
            "MONGO_PORT": "27017"
        }
    """

    # If env_prefix is None a snake case version of a class name will be used.
    env_prefix = None

    # Environment variable attributes.
    # If it's set to None, all keys from __dict__ will be considered as env
    # attributes.
    env_attrs = None

    @classmethod
    def __types(cls):
        return str, bytes, bool, int, float, Path, ToEnvMixin

    def __get_env(self, prefix: str, attr: str) -> Dict[str, str]:
        obj = getattr(self, attr)

        if isinstance(obj, ToEnvMixin):
            return obj.to_env()

        key = (
            attr.upper()
            if prefix.strip() == ""
            else f"{prefix}_{attr}".upper()
        )
        if isinstance(obj, str):
            return {key: obj}
        elif isinstance(obj, bool):
            return {key: "true" if obj else "false"}
        elif isinstance(obj, bytes):
            return {key: str(obj, encoding="utf-8")}
        else:
            return {key: str(obj)}

    def to_env(self) -> dict:
        """Returns this class variables in env format dictionary."""
        prefix = camel_case_to_snake_case(
            self.__class__.__name__
            if self.__class__.env_prefix is None
            else self.__class__.env_prefix
        )

        if self.__class__.env_attrs is None:
            env_attrs = [
                key
                for key, value in self.__dict__.items()
                if isinstance(value, self.__types())
            ]
        else:
            env_attrs = self.__class__.env_attrs

        env = {}
        for attr in env_attrs:
            env.update(self.__get_env(prefix=prefix, attr=attr))
        return env
