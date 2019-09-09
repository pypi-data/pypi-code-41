# Copyright (c) 2018, 2019  Peter Pentchev <roam@ringlet.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""
Run the confget tests using the Python methods.

Load the test data, then run the tests using the objects provided by
the Python library, not by executing the command-line tool.
"""

import itertools
import os
import sys
import unittest

import ddt  # type: ignore
import pytest  # type: ignore

from confget import format as cformat

pytest.register_assert_rewrite("unit_tests.data.defs")

# pylint: disable=wrong-import-position
from .data import defs as tdefs  # noqa: E402
from .data import load as tload  # noqa: E402

# pylint: enable=wrong-import-position


try:
    from typing import Dict

    _TYPING_USED = (Dict,)
except ImportError:
    pass


TESTS = tload.load_all_tests(os.environ["TESTDIR"])

FULL_TEST_DATA = [
    (fname, setenv, test)
    for fname, idx, setenv, test in sorted(
        itertools.chain(
            *[
                [
                    (tfile[0], idx, tfile[1].setenv, test)
                    for idx, test in enumerate(tfile[1].tests)
                ]
                for tfile in TESTS.items()
            ]
        )
    )
]

SKIP_ARGS = set(["check_only"])


@ddt.ddt
class TestStuff(unittest.TestCase):
    # pylint: disable=no-self-use
    """ Run the tests using the Python library. """

    @ddt.data(*FULL_TEST_DATA)
    @ddt.unpack
    def test_run(
        self,  # type: TestStuff
        fname,  # type: str
        setenv,  # type: Dict[str, str]
        test,  # type: tdefs.TestDef
    ):  # type: (...) -> None
        """ Instantiate a confget object, load the data, check it. """

        save_env = dict(os.environ)
        try:
            if set(test.args.keys()) & SKIP_ARGS:
                return

            backend = test.get_backend()
            config = test.get_config()
            if test.setenv:
                os.environ.update(setenv)

            if test.stdin:
                fname = os.environ["TESTDIR"] + "/" + test.stdin
                with open(fname, mode="r") as stdin:
                    save_stdin = sys.stdin
                    try:
                        sys.stdin = stdin
                        obj = backend(config)
                        data = obj.read_file()
                    finally:
                        sys.stdin = save_stdin
            else:
                obj = backend(config)
                data = obj.read_file()

            res = cformat.filter_vars(config, data)
            output = test.do_xform(res)
            test.output.check_result(output)
        finally:
            if test.setenv:
                os.environ.clear()
                os.environ.update(save_env)
