#!/usr/bin/env python3

# Copyright Louis Paternault 2014-2019
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

"""Main function for the command."""

try:
    from math import gcd
except ImportError:
    from fractions import gcd
from decimal import Decimal
import sys


from pdfautonup.pdfbackend.auto import (  # pylint: disable=no-name-in-module
    PDFFileReader,
)
from pdfautonup import LOGGER
from pdfautonup import errors, options, paper, geometry, pdfbackend


def lcm(a, b):
    """Return least common divisor of arguments"""
    # pylint: disable=invalid-name, deprecated-method
    return (a * b) // gcd(a, b)


def _none_function(*args, **kwargs):  # pylint: disable=unused-argument
    """Accept any number of arguments. and does nothing."""


def _progress_printer(string):
    """Returns a function that prints the progress message."""

    def print_progress(page, total):
        """Print progress message."""
        try:
            text = string.format(
                page=page, total=total, percent=int(page * 100 / total)
            )
        except:  # pylint: disable=bare-except
            text = string
        print(text, end="")
        sys.stdout.flush()

    return print_progress


class PageIterator:
    """Iterator over pages of several PDF files."""

    def __init__(self, filenames):
        self.files = []
        self._filenames = filenames

    def __enter__(self):
        for name in self._filenames:
            try:
                if name == "-":
                    self.files.append(PDFFileReader())
                else:
                    self.files.append(PDFFileReader(name))
            except (FileNotFoundError, PermissionError) as error:
                raise errors.PdfautonupError(
                    "Error while reading file '{}': {}.".format(name, error)
                )
            except RuntimeError as error:
                raise errors.PdfautonupError(
                    "Error: Malformed file '{}': {}.".format(name, error)
                )
        return self

    def __exit__(self, *exc):
        for file in self.files:
            file.close()

    def __iter__(self):
        for pdf in self.files:
            yield from pdf

    def __len__(self):
        return sum(len(pdf) for pdf in self.files)

    def repeat(self, num):
        """Iterator over pages, repeated `num` times."""
        for __ in range(num):
            yield from self

    def metadata(self):
        """Aggregate metadata from input files."""
        if len(self.files) == 1:
            return self.files[0].metadata

        input_info = [pdf.metadata for pdf in self.files]
        output_info = dict()
        for key in pdfbackend.METADATA_KEYS:
            values = (
                data[key]
                for data in input_info
                if (key in data and (data[key] is not None))
            )
            if values:
                output_info[key] = " / ".join(["“{}”".format(item) for item in values])
        return output_info


def nup(arguments, progress=_none_function):
    """Build destination file."""
    # pylint: disable=too-many-branches

    with PageIterator(arguments.files) as pages:

        if not pages:
            raise errors.PdfautonupError("Error: PDF files have no pages to process.")

        page_sizes = list(zip(*[page.mediabox_size for page in pages]))
        source_size = (Decimal(max(page_sizes[0])), Decimal(max(page_sizes[1])))
        target_size = paper.target_papersize(arguments.target_size)

        if [len(set(page_sizes[i])) for i in (0, 1)] != [1, 1]:
            LOGGER.warning(
                "Pages have different sizes. The result might be unexpected."
            )

        if arguments.algorithm is None:
            if arguments.gap[0] is None and arguments.margin[0] is None:
                fit = geometry.Fuzzy
            else:
                fit = geometry.Panelize
        else:
            fit = {"fuzzy": geometry.Fuzzy, "panel": geometry.Panelize}[
                arguments.algorithm
            ]

        dest = fit(source_size, target_size, arguments=arguments)

        if arguments.repeat == "auto":
            if len(pages) == 1:
                arguments.repeat = "fit"
            else:
                arguments.repeat = 1
        if isinstance(arguments.repeat, int):
            repeat = arguments.repeat
        elif arguments.repeat == "fit":
            repeat = lcm(dest.pages_per_page, len(pages)) // len(pages)

        pagecount = 0
        pagetotal = repeat * len(pages)
        progress(pagecount, pagetotal)
        for page in pages.repeat(repeat):
            dest.add_page(page)
            pagecount += 1
            progress(pagecount, pagetotal)

        dest.write(arguments.output, arguments.files[0], metadata=pages.metadata())


def main():
    """Main function"""
    try:
        arguments = options.commandline_parser().parse_args(sys.argv[1:])

        if "-" in arguments.files and arguments.interactive:
            LOGGER.error(
                """Cannot ask user input while reading files from standard input. """
                """Try removing the "--interactive" (or "-i") option."""
            )
            sys.exit(1)

        nup(arguments, progress=_progress_printer(arguments.progress))
        if not (arguments.progress.endswith("\n") or arguments.progress == ""):
            print()
    except KeyboardInterrupt:
        print()
        sys.exit(1)
    except errors.PdfautonupError as error:
        LOGGER.error(error)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
