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

import io
import sys

import PyPDF2

from pdfautonup import LOGGER

from . import METADATA_KEYS
from . import AbstractPDFFileReader, AbstractPDFFileWriter, AbstractPDFPage


def _rectangle_size(rectangle):
    """Return the dimension of rectangle (width, height)."""
    return (
        rectangle.upperRight[0] - rectangle.lowerLeft[0],
        rectangle.upperRight[1] - rectangle.lowerLeft[1],
    )


def _metadata2dict(pdf):
    raw = pdf.getDocumentInfo()
    return {
        key: raw["/{}".format(key.capitalize())]
        for key in METADATA_KEYS
        if "/{}".format(key.capitalize()) in raw
    }


class PDFFileReader(AbstractPDFFileReader):
    """Read a PDF file."""

    def __init__(self, name=None):
        super().__init__()
        if name is None:
            # Read from standard input
            self._file = PyPDF2.PdfFileReader(io.BytesIO(sys.stdin.buffer.read()))
        else:
            self._file = PyPDF2.PdfFileReader(name)

    def close(self):
        pass

    def __len__(self):
        return self._file.numPages

    def __iter__(self):
        for num in range(self._file.numPages):
            yield PDFPage(self._file.getPage(num))

    @property
    def metadata(self):
        return _metadata2dict(self._file)


class PDFFileWriter(AbstractPDFFileWriter):
    """PDF file writer."""

    def __init__(self):
        super().__init__()
        self._file = PyPDF2.PdfFileWriter()

    def new_page(self, width, height):
        return PDFPage(self._file.addBlankPage(width=width, height=height))

    def write(self, name=None):
        if name is None:
            output = io.BytesIO()
            self._file.write(output)
            sys.stdout.buffer.write(output.getvalue())
        else:
            self._file.write(open(name, "w+b"))

    @property
    def metadata(self):
        return _metadata2dict(self._file)

    @metadata.setter
    def metadata(self, value):
        # Source:
        #    http://two.pairlist.net/pipermail/reportlab-users/2009-November/009033.html
        try:
            # pylint: disable=protected-access, no-member
            # Since we are accessing to a protected membre, which can no longer exist
            # in a future version of PyPDF2, we prevent errors.
            infodict = self._file._info.getObject()
            infodict.update(
                {
                    PyPDF2.generic.NameObject(
                        "/{}".format(key.capitalize())
                    ): PyPDF2.generic.createStringObject(value)
                    for key, value in value.items()
                }
            )
        except AttributeError:
            LOGGER.warning("Could not copy metadata from source document.")


class PDFPage(AbstractPDFPage):
    """Page of a PDF file (using PyPDF2)."""

    @property
    def pypdf2_page(self):
        """Return the underlying PyPDF2 Page object."""
        return self._page

    @property
    def mediabox_size(self):
        return _rectangle_size(self._page.mediaBox)

    def merge_translated_page(self, page, x, y):
        return self._page.mergeTranslatedPage(page.pypdf2_page, x, y)
