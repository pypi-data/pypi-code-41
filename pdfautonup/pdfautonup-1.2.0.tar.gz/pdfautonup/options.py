# Copyright Louis Paternault 2014-2019
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Manage options"""

import argparse
import os
import sys
import textwrap

import papersize

from pdfautonup import VERSION
from pdfautonup import pdfbackend


def length_type(text):
    """Check type of length (number plus optional unit).

    Wrapper to :func:`papersize.parse_length`.
    """
    try:
        return papersize.parse_length(text)
    except papersize.CouldNotParse as error:
        raise argparse.ArgumentTypeError(str(error))


def size_type(text):
    """Check type of paper size (couple of numbers plus optional units).

    Wrapper to :func:`papersize.parse_papersize`.
    """
    try:
        return papersize.parse_papersize(text)
    except papersize.CouldNotParse as error:
        raise argparse.ArgumentTypeError(str(error))


def repeat_type(text):
    """Check type of '--repeat' option.

    Must be either a positive integer, or 'fit' or 'auto'.
    """
    if text in ["auto", "fit"]:
        return text
    try:
        if int(text) > 0:
            return int(text)
        raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(
            textwrap.dedent(
                """
        Argument must be either 'fit' or 'auto', or a positive integer.
        """
            )
        )


def progress_type(text):
    """Return plain progress text, turning aliases into their value."""
    return {
        "dot": ".",
        "percent": "{percent}%\n",
        "pages": "{page}/{total}\n",
        "none": "",
    }.get(text, text)


def inputfile_type(filename):
    """Return the argument, with the `.pdf` extension if missing (and if argument is not "-").

    If `filename` does not exist, but `filename.pdf` does exist, return the
    latter. Otherwise (even if it does not exist), return the former.
    """
    if filename == "-":
        return filename
    if not os.path.exists(filename):
        extended = "{}.pdf".format(filename)
        if os.path.exists(extended):
            return extended
    return filename


class HelpPaper(argparse.Action):
    """Argparse action to display help about paper sizes."""

    #: pylint: disable=too-few-public-methods, line-too-long

    def __init__(self, *args, **kwargs):
        if "nargs" in kwargs:
            raise ValueError("nargs not allowed")
        kwargs["nargs"] = 0
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        # pylint: disable=arguments-differ
        print(
            textwrap.dedent(
                """
            # Source

            Paper size is read from the following sources (in that order):

            - Argument of "--size" option;
            - LC_PAPER environment variable (read as mm);
            - PAPERSIZE environment variable;
            - content of file specified by the PAPERCONF environment variable;
            - content of file /etc/papersize;
            - output of the paperconf command;
            - if everything else have failed, A4.

            # Recognized sizes

            Using the "--size" option, paper size can be either specified by the explicit dimensions, or by the name of the size.

            - Explicit dimensions are of the form WIDTHxHEIGHT, where WIDTH and HEIGHT are floating point numbers in one of the following units (default being pt): {units};
            - Recognized paper size names are: {papersizenames}.

            For instance, A4 paper can be set using "--size=A4" or "--size=21cmx29.7cm".
            """
            )
            .format(
                units=str(
                    ", ".join([size for size in sorted(papersize.UNITS.keys()) if size])
                ),
                papersizenames=str(", ".join(sorted(papersize.SIZES.keys()))),
            )
            .strip()
        )
        sys.exit(0)


def commandline_parser():
    """Return a command line parser."""
    # pylint: disable=line-too-long

    parser = argparse.ArgumentParser(
        prog="pdfautonup",
        description=textwrap.dedent(
            """\
            Convert PDF files to 'n-up' file, with multiple input pages per destination pages. The output size is configurable, and the program compute the page layout, to fit as much source pages in per destination pages as possible. If necessary, the source pages are repeated to fill all destination pages.
            """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent(
            """\
                The backend Python library used to read and write PDF files can be forced using the environment variable BACKEND. If this variable is not defined (or defined with an invalid value), a library is automatically (and silently) chosen. Available libraries are: {}.
                """.format(
                ", ".join(
                    "'{}'".format(item)
                    for item in pdfbackend.PDFBACKENDS
                    if item != "auto"
                )
            )
        ),
    )

    parser.add_argument(
        "--version",
        help="Show version",
        action="version",
        version="%(prog)s " + VERSION,
    )

    parser.add_argument(
        "--help-paper",
        help="Show an help message about paper sizes, and exit.",
        action=HelpPaper,
    )

    parser.add_argument(
        "files",
        metavar="FILES",
        help=(
            "PDF files to merge. If their page sizes are different, they are "
            "considered to have the same page size, which is the maximum width "
            """and height of all pages. To read from standard input, use "-"."""
        ),
        nargs="*",
        type=inputfile_type,
        default=["-"],
    )

    parser.add_argument(
        "--output",
        "-o",
        help=(
            'Destination file (or "-" to write to standard output). Default is "-nup" appended to first source file (excepted if first source file is standard input, where default output is standard output).'
        ),
        type=str,
        nargs="?",
    )

    parser.add_argument(
        "--interactive",
        "-i",
        help="Ask before overwriting destination file if it exists.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--algorithm",
        "-a",
        help=textwrap.dedent(
            """\
            Algorithm used to arrange source documents into destination documents. This program tries to put as many copies of the source document into the destination document, given that:
            - `fuzzy`: documents can overlap, or leave blank spaces between them, but not too much;
            - `panel`: the gap length between documents is fixed, and a minimum destination margin is respected.
            """
        ),
        default=None,
        choices=["fuzzy", "panel"],
    )

    parser.add_argument(
        "--orientation",
        "-O",
        help=textwrap.dedent(
            """\
            Destination paper orientation. Default is 'auto', which choose the paper orientation to fit the maximum number of source pages on the destination page.
            """
        ),
        default="auto",
        choices=["auto", "portrait", "landscape"],
    )

    parser.add_argument(
        "--size",
        "-s",
        dest="target_size",
        help="Target paper size (see below for accepted sizes).",
        default=None,
        nargs=1,
        action="store",
        type=size_type,
    )

    parser.add_argument(
        "--margin",
        "-m",
        dest="margin",
        help=textwrap.dedent(
            """\
            Margin size.
            """
        ),
        default=[None],
        nargs=1,
        type=length_type,
        action="store",
    )

    parser.add_argument(
        "--gap",
        "-g",
        help=textwrap.dedent(
            """\
            Gap size.
            """
        ),
        default=[None],
        type=length_type,
        nargs=1,
        action="store",
    )

    parser.add_argument(
        "--repeat",
        "-r",
        help=textwrap.dedent(
            """
        Number of times the input files have to be repeated. Possible values are:
        - an integer;
        - 'fit': the input files are repeated enough time to leave no blank
          space in the output file.
        - 'auto': if there is only one input page, equivalent to 'fit'; else,
          equivalent to 1.
        """
        ),
        type=repeat_type,
        default="auto",
        action="store",
    )

    parser.add_argument(
        "--progress",
        "-p",
        help=textwrap.dedent(
            r"""
        Text to print after processing each page. Strings "{page}", "{pagetotal}", "{percent}" are replaced by their respective values. The following alias are defined:
        - 'none': no progress;
        - 'dot': '.';
        - 'pages': '{page}/{total}\n';
        - 'percent': '{percent}%%\n'.
        """
        ),
        type=progress_type,
        default="",
        action="store",
    )

    return parser
