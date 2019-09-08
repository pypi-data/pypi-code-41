# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
import subprocess
import shlex
import re
from pkg_resources import parse_version
from functools import lru_cache


@lru_cache()
def check_dependency():
    omwcmd = shutil.which("omwcmd")
    if not omwcmd:
        raise Exception("Cannot find omwcmd executable")

    try:
        output = subprocess.check_output(shlex.split("{} --version".format(omwcmd)))
        version = parse_version(re.sub(r"^[^\d]*", "", output.decode("ascii")))

        if version < parse_version("0.2"):
            raise Exception(
                "this version of Portmod requires omwcmd version >= 0.2. "
                f"Currently installed: {version}"
            )
    except subprocess.CalledProcessError:
        raise Exception("this version of Portmod requires omwcmd version >= 0.2")


def get_masters(file):
    """
    Detects masters for the given file
    """
    check_dependency()

    _, ext = os.path.splitext(file)
    if re.match(r"\.(esp|esm|omwaddon|omwgame)", ext, re.IGNORECASE):
        omwcmd = shutil.which("omwcmd")
        process = subprocess.Popen(
            shlex.split('{} masters "{}"'.format(omwcmd, file)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (output, err) = process.communicate()
        if err:
            raise Exception(err)

        result = output.decode("utf-8", errors="ignore").rstrip("\n")
        if result:
            return set(result.split("\n"))
    return set()
