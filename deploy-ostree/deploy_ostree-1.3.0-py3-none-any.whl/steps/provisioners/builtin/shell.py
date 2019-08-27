# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

from pathlib import Path
import deploy_ostree
from ....run import run


PROVISIONER_DIR = Path(deploy_ostree.__file__).parent / 'builtin-provisioners'


def shell_provisioner(name):
    exe = PROVISIONER_DIR / name

    def provision(deployment_dir: Path, args):
        env = {'DEPLOY_OSTREE_%s' % key: value for key, value in args.items()}
        run([str(exe), str(deployment_dir)], check=True, env=env)

    return provision
