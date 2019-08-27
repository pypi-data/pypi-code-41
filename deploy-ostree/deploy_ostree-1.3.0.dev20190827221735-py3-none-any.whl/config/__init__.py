# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

import json
import toml
from pathlib import Path
from typing import Iterable, Optional, TextIO, Mapping, Union
from uuid import uuid4
from .error import InvalidConfigError
from .provisioners import ProvisionerConfig, get_provisioners
from .provisioners import BuiltinProvisionerConfig, ScriptProvisionerConfig  # noqa
from .rootfs import get_root_fs
from .. import clsutil


def random_string() -> str:
    return uuid4().hex[:12]


@clsutil.repr
@clsutil.equals
class Url:
    def __init__(self, url: str) -> None:
        self.url = url

    def __str__(self) -> str:
        return str(self.url)


Source = Union[Path, Url]


@clsutil.repr
@clsutil.equals
class Config:
    def __init__(
        self,
        source: Source,
        ref: str,
        *,
        sysroot: Optional[Path] = None,
        root_filesystem: Optional[str] = None,
        fstab: Path = None,
        remote: Optional[str] = None,
        stateroot: Optional[str] = None,
        kernel_args: Iterable[str] = (),
        provisioners: Iterable[ProvisionerConfig] = ()
    ) -> None:
        self.source = source
        self.ref = ref
        self.sysroot = sysroot or Path('/')
        self.root_filesystem = root_filesystem or get_root_fs()
        self.fstab = fstab or Path('/', 'etc', 'fstab')
        self.remote = remote or random_string()
        self.stateroot = stateroot or random_string()
        self.kernel_args = list(kernel_args)
        self.provisioners = list(provisioners)
        self.deployment_name = None  # type: Optional[str]

    @property
    def stateroot_dir(self) -> Path:
        return self.sysroot / 'ostree' / 'deploy' / self.stateroot

    @property
    def var_dir(self) -> Path:
        return self.stateroot_dir / 'var'

    @property
    def deployments_dir(self) -> Path:
        return self.stateroot_dir / 'deploy'

    @property
    def deployment_dir(self) -> Path:
        if self.deployment_name is None:
            raise RuntimeError('deployment name not set')
        return self.deployments_dir / self.deployment_name

    @property
    def ostree_repo(self) -> Path:
        return self.sysroot / 'ostree' / 'repo'

    def set_deployment_name(self, deployment: str) -> None:
        self.deployment_name = deployment

    @classmethod
    def parse_json(
        cls,
        fobj: TextIO, *,
        base_dir: Path = Path(''),
        sysroot: Optional[Path] = None,
        root_filesystem: Optional[str] = None,
        fstab: Path = None
    ) -> 'Config':
        try:
            data = json.load(fobj)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidConfigError(str(exc))
        if not isinstance(data, Mapping):
            raise InvalidConfigError('top-level value must be object')
        return cls._from_data(data, base_dir, sysroot, root_filesystem, fstab)

    @classmethod
    def parse_toml(
        cls,
        fobj: TextIO, *,
        base_dir: Path = Path(''),
        sysroot: Optional[Path] = None,
        root_filesystem: Optional[str] = None,
        fstab: Path = None
    ) -> 'Config':
        try:
            data = toml.load(fobj)
        except (toml.TomlDecodeError, UnicodeDecodeError) as exc:
            raise InvalidConfigError(str(exc))
        return cls._from_data(data, base_dir, sysroot, root_filesystem, fstab)

    @classmethod
    def _from_data(
        cls,
        data: Mapping,
        base_dir: Path = Path(''),
        sysroot: Optional[Path] = None,
        root_filesystem: Optional[str] = None,
        fstab: Path = None
    ) -> 'Config':
        if 'url' in data and 'path' in data:
            raise InvalidConfigError("both 'url' and 'path' are present")
        elif 'url' in data:
            source = Url(data['url'])  # type: Source
        elif 'path' in data:
            source = base_dir / Path(data['path'])
        else:
            raise InvalidConfigError("neither 'url' nor 'path' are present")

        try:
            return cls(
                source=source,
                ref=data['ref'],
                sysroot=sysroot,
                root_filesystem=root_filesystem,
                fstab=fstab,
                remote=data.get('remote'),
                stateroot=data.get('stateroot'),
                kernel_args=data.get('kernel-args', ()),
                provisioners=get_provisioners(data),
            )
        except KeyError as exc:
            raise InvalidConfigError("missing key '{}'".format(exc.args[0]))
