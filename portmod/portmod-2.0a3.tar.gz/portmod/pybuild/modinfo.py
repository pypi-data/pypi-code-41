# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Importing values from this module fills them with information about the file
from which they were imported
This module should be removed from sys.modules prior to importing to ensure that
the cached version is not used instead.
"""
import inspect
import os
from pathlib import Path
from portmod.repo.atom import Atom


def _get_modinfo():
    """Puts module information in the global scope so that it can be imported"""
    global M, MF, MN, MV, MR, MVR, CATEGORY
    filename = None
    for i in inspect.stack(0):
        if i.filename.endswith(".pybuild"):
            filename = i.filename
    if filename is not None:
        CATEGORY = Path(filename).resolve().parent.parent.name
        atom = Atom(
            "{}/{}".format(CATEGORY, os.path.basename(filename)[: -len(".pybuild")])
        )

        M = atom.M
        MF = atom.MF
        MN = atom.MN
        MV = atom.MV
        MR = atom.MR
        MVR = atom.MV
        if atom.MR is not None:
            MVR += "-" + atom.MR


_get_modinfo()
