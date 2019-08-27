# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from pathlib import Path
from typing import Mapping, Any
import uuid


def machine_id(deployment: Path, args: Mapping[str, Any]):
    path = Path(args.get('path', '/etc/machine-id'))
    if path.is_absolute():
        path = path.relative_to('/')

    machine_id_file = deployment / path
    if machine_id_file.exists():
        return

    write_machine_id_file(machine_id_file)


def new_id() -> str:
    return str(uuid.uuid4()).replace('-', '')


def write_machine_id_file(machine_id_file: Path):
    machine_id_file.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    with machine_id_file.open('w') as f:
        f.write(new_id())
    machine_id_file.chmod(0o644)
