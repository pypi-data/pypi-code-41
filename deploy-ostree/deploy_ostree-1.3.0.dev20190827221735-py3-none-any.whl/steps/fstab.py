# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

import os
from pathlib import Path
import shutil
from . import DeployStep


class Fstab(DeployStep):
    @property
    def title(self) -> str:
        return 'copying %s into deployment' % self.config.fstab

    def run(self):
        fstab = Path(self.config.deployment_dir, 'etc', 'fstab')
        shutil.copyfile(str(self.config.fstab), str(fstab))
        os.chmod(str(fstab), 0o644)
