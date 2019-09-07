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

"""Read and write PDF files using the PyMuPDF library."""

import decimal
import io
import sys

import fitz

from . import AbstractPDFFileReader, AbstractPDFFileWriter, AbstractPDFPage


class PDFFileReader(AbstractPDFFileReader):
    """Read a PDF file."""

    def __init__(self, name=None):
        super().__init__()
        if name is None:
            # Read from standard input
            self._file = fitz.open(
                stream=io.BytesIO(sys.stdin.buffer.read()), filetype="application/pdf"
            )
        else:
            self._file = fitz.open(name)

    def close(self):
        self._file.close()

    def __len__(self):
        return self._file.pageCount

    def __iter__(self):
        for page in self._file:
            yield PDFPage(page)

    @property
    def metadata(self):
        return self._file.metadata


class PDFFileWriter(AbstractPDFFileWriter):
    """PDF file writer."""

    def __init__(self):
        super().__init__()
        self._file = fitz.Document()

    def new_page(self, width, height):
        return PDFPage(self._file.newPage(width=width, height=height))

    def write(self, name=None):
        if name is None:
            sys.stdout.buffer.write(self._file.write())
        else:
            self._file.save(name)

    @property
    def metadata(self):
        return self._file.metadata

    @metadata.setter
    def metadata(self, value):
        self._file.setMetadata(value)


class PDFPage(AbstractPDFPage):
    """Page of a PDF file (using PyMuPDF)."""

    @property
    def parent(self):
        """PDF Object this page belongs to."""
        return self._page.parent

    @property
    def number(self):
        """Number of this page in the PDF."""
        return self._page.number

    @property
    def mediabox_size(self):
        return self._page.MediaBoxSize

    def merge_translated_page(self, page, x, y):
        return self._page.showPDFpage(
            fitz.Rect(
                x,
                y,
                x + decimal.Decimal(page.mediabox_size.x),
                y + decimal.Decimal(page.mediabox_size.y),
            ),
            page.parent,
            page.number,
        )
