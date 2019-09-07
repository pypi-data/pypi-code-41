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

"""Abstract classes to read and write PDF files."""

PDFBACKENDS = ["auto", "pymupdf", "pypdf2"]

METADATA_KEYS = ["title", "author", "keywords", "creator", "producer"]


class AbstractPDFFileReader:
    """PDF file reader."""

    def __init__(self, name=None):
        """Open file. If name is `None`, read from standard input."""

    def close(self):
        """Close file."""
        raise NotImplementedError()

    def __iter__(self):
        """Iterate over pages of PDF."""
        raise NotImplementedError()

    def __len__(self):
        """Return the number of pages."""
        raise NotImplementedError()

    @property
    def metadata(self):
        """Return a dictionary of PDF metadata."""
        raise NotImplementedError()


class AbstractPDFFileWriter:
    """PDF file writer."""

    def new_page(self, width, height):
        """Create a new page, of size (width, height)."""
        raise NotImplementedError()

    @property
    def metadata(self):
        """Return file metadata (as a dictionary)."""
        raise NotImplementedError()

    @metadata.setter
    def metadata(self, value):
        raise NotImplementedError()

    def write(self, name=None):
        """Write file to file system. If `name` is `None`, write to standard output."""
        raise NotImplementedError()


class AbstractPDFPage:
    """Page of a PDF file."""

    def __init__(self, page):
        super().__init__()
        self._page = page

    @property
    def mediabox_size(self):
        """Return the media box size (as a tuple)."""
        raise NotImplementedError()

    def merge_translated_page(self, page, x, y):
        """Merge `page` into current page, at coordinates `(x, y)`."""
        raise NotImplementedError()
