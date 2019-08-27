# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from typing import Any, Iterable, Mapping, Union, Optional
import warnings
from .error import InvalidConfigError
from .. import clsutil


@clsutil.repr
@clsutil.equals
class BuiltinProvisionerConfig:
    KEY = 'builtin'

    def __init__(self, name: str, args: Mapping[str, Any]) -> None:
        self.name = name
        self.args = args

    @classmethod
    def from_default_provisioner_dict(cls, data: Mapping[str, Any]):
        name = data['provisioner']
        args = {key: value for key, value in data.items() if key != 'provisioner'}
        return cls(name, args)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]):
        args = {key: value for key, value in data.items() if key != cls.KEY}
        return cls(data[cls.KEY], args)


@clsutil.repr
@clsutil.equals
class ScriptProvisionerConfig:
    KEY = 'script'
    DEFAULT_INTERPRETER = '/bin/sh'

    def __init__(
        self,
        script: str,
        interpreter: str = DEFAULT_INTERPRETER,
        description: Optional[str] = None
    ) -> None:
        self.script = script
        self.interpreter = interpreter
        self.description = description

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]):
        interpreter = data.get('interpreter', cls.DEFAULT_INTERPRETER)
        return cls(data[cls.KEY], interpreter, data.get('description'))


ProvisionerConfig = Union[BuiltinProvisionerConfig, ScriptProvisionerConfig]


def get_provisioner(data: Mapping[str, Any]) -> ProvisionerConfig:
    if BuiltinProvisionerConfig.KEY in data and ScriptProvisionerConfig.KEY in data:
        raise InvalidConfigError('invalid provisioner block (conflicting keys)')
    elif BuiltinProvisionerConfig.KEY in data:
        return BuiltinProvisionerConfig.from_dict(data)
    elif ScriptProvisionerConfig.KEY in data:
        return ScriptProvisionerConfig.from_dict(data)
    else:
        raise InvalidConfigError('invalid provisioner block (missing type)')


def get_provisioners(data: Mapping[str, Any]) -> Iterable[ProvisionerConfig]:
    if 'default-provisioners' in data and 'provisioners' in data:
        raise InvalidConfigError("both 'provisioners' and 'default-provisioners' are present")
    if 'default-provisioners' in data:
        warnings.warn("The 'default-provisioners' config setting has been replaced by the 'provisioners' setting.\n"
                      "The 'default-provisioners' setting will be removed in a future release.", FutureWarning)
        return (BuiltinProvisionerConfig.from_default_provisioner_dict(x) for x in data['default-provisioners'])

    return (get_provisioner(prov) for prov in data.get('provisioners', ()))
