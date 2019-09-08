# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Displays filesystem conflicts between mods
"""

import os
import shutil
import subprocess
from portmod.configfile import find_config, read_config
from portmod.config import get_config


def main():
    """
    Main executable for openmw-conflicts executable
    """
    filename = get_config()["OPENMW_CONFIG"]
    config = read_config(os.path.expanduser(filename))
    mod_dirs = [
        directory.lstrip("data=").strip('"')
        for (index, directory) in find_config(config, "data=*")
    ]

    args = ["omwcmd", "file-conflicts", "--ignore", "txt,md"]
    args.extend(mod_dirs)

    if shutil.which("omwcmd"):
        subprocess.Popen(args).wait()
    else:
        print('Error: Could not find "dcv"')
