# Copyright Louis Paternault 2019
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Automatically import and installed backend."""

import importlib
import os
import sys

from . import PDFBACKENDS


def _import_backend(backend):
    this = sys.modules[__name__]
    backend_module = importlib.import_module(
        ".{}".format(backend), "pdfautonup.pdfbackend"
    )
    this.PDFFileWriter = backend_module.PDFFileWriter
    this.PDFFileReader = backend_module.PDFFileReader


def _import_backend_auto():
    for backend in PDFBACKENDS:
        if backend == "auto":
            continue
        try:
            _import_backend(backend)
        except ImportError:
            continue
        break


PDFBACKEND = os.environ.get("PDFBACKEND", "auto").lower()
if PDFBACKEND not in PDFBACKENDS:
    PDFBACKEND = "auto"

if PDFBACKEND == "auto":
    _import_backend_auto()
else:
    _import_backend(PDFBACKEND)
