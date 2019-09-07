# Copyright 2017-2019 Louis Paternault
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

"""Tests"""

import os
import subprocess
import sys
import unittest

from wand.image import Image
import pkg_resources


if "COVERAGE_PROCESS_START" in os.environ:
    EXECUTABLE = ["coverage", "run"]
else:
    EXECUTABLE = [sys.executable]

TEST_DATA_DIR = pkg_resources.resource_filename(__name__, "test_commandline-data")

FIXTURES = [
    {
        "command": [
            "--algorithm",
            "panel",
            "--gap",
            ".5cm",
            "--margin",
            "1cm",
            os.path.join(TEST_DATA_DIR, "pcb.pdf"),
        ],
        "returncode": 0,
        "diff": ("pcb-nup.pdf", "pcb-control.pdf"),
    },
    {
        "command": [os.path.join(TEST_DATA_DIR, "trigo.pdf")],
        "returncode": 0,
        "diff": ("trigo-nup.pdf", "trigo-control.pdf"),
    },
    {
        "command": [os.path.join(TEST_DATA_DIR, "trigo.pdf")],
        "env": {"PDFBACKEND": "pypdf2"},
        "returncode": 0,
        "diff": ("trigo-nup.pdf", "trigo-control-pypdf2.pdf"),
    },
    {
        "command": [os.path.join(TEST_DATA_DIR, "three-pages.pdf")],
        "returncode": 0,
        "diff": ("three-pages-nup.pdf", "three-pages-control.pdf"),
    },
    {"command": [os.path.join(TEST_DATA_DIR, "malformed.pdf")], "returncode": 1},
    {
        "command": [os.path.join(TEST_DATA_DIR, "zero-pages.pdf")],
        "returncode": 1,
        "stderr": "Error: PDF files have no pages to process.\n",
    },
    {
        "command": [os.path.join(TEST_DATA_DIR, "dummy.pdf")],
        "returncode": 1,
        "stderr": "Error: A PDF page have a null dimension.\n",
    },
]


class TestCommandLine(unittest.TestCase):
    """Run binary, and check produced files."""

    def assertPdfEqual(self, filea, fileb):
        """Test whether PDF files given in argument (as file names) are equal.

        Equal means: they look the same.
        """
        # pylint: disable=invalid-name
        images = (Image(filename=filea), Image(filename=fileb))

        # Check that files have the same number of pages
        self.assertEqual(len(images[0].sequence), len(images[1].sequence))

        # Check if pages look the same
        for (pagea, pageb) in zip(images[0].sequence, images[1].sequence):
            self.assertEqual(pagea.compare(pageb, metric="absolute")[1], 0)

    @unittest.skipIf(
        # I would like to get rid of this, but ImageMagick seems to produce
        # different pixel-to-pixel conversions from pdf to png in python3.5 and
        # python3.7.
        sys.version_info < (3, 7),
        "Tests require python version 3.7 or higher.",
    )
    def test_commandline(self):
        """Test binary, from command line to produced files."""
        for data in FIXTURES:
            with self.subTest(**data):
                env = data.get("env", {})
                env.update(os.environ)
                completed = subprocess.run(
                    EXECUTABLE + ["-m", "pdfautonup"] + data["command"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    env=env,
                )

                for key in ["returncode", "stderr", "stdout"]:
                    if key in data:
                        self.assertEqual(getattr(completed, key), data.get(key))

                if "diff" in data:
                    self.assertPdfEqual(
                        *(
                            os.path.join(TEST_DATA_DIR, filename)
                            for filename in data["diff"]
                        )
                    )
