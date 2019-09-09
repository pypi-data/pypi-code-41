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
Class definitions for the confget test suite.
"""

import abc
import os

import six

from confget import backend as cbackend
from confget import format as cformat

from . import util


try:
    from typing import Any, Dict, Iterable, List, Optional, Type

    _TYPING_USED = (Any, Dict, Iterable, List, Optional, Type)
except ImportError:
    pass


CMDLINE_OPTIONS = {
    "check_only": ("-c", False),
    "filename": ("-f", True),
    "hide_var_name": ("-n", False),
    "list_all": ("-l", False),
    "match_var_names": ("-L", False),
    "match_var_values": ("-m", True),
    "section": ("-s", True),
    "section_override": ("-O", False),
    "section_specified": ("", False),
    "show_var_name": ("-N", False),
}


@six.add_metaclass(abc.ABCMeta)
class XFormType(object):
    """ Transform something to something else with great prejudice. """

    @abc.abstractproperty
    def command(self):
        # type: (XFormType) -> str
        """ Get the shell command to transform the confget output. """
        raise NotImplementedError(
            "{tname}.command".format(tname=type(self).__name__)
        )

    @abc.abstractmethod
    def do_xform(self, res):
        # type: (XFormType, Iterable[cformat.FormatOutput]) -> str
        """ Transform the Python representation of the result. """
        raise NotImplementedError(
            "{tname}.do_xform()".format(tname=type(self).__name__)
        )


class XFormNone(XFormType):
    """ No transformation, newlines preserved. """

    @property
    def command(self):
        # type: (XFormNone) -> str
        return ""

    def do_xform(self, res):
        # type: (XFormNone, Iterable[cformat.FormatOutput]) -> str
        xform = "\n".join([line.output_full for line in res])  # type: str
        return xform


class XFormNewlineToSpace(XFormType):
    """ Translate newlines to spaces. """

    @property
    def command(self):
        # type: (XFormNewlineToSpace) -> str
        return '| tr "\\n" " "'

    def do_xform(self, res):
        # type: (XFormNewlineToSpace, Iterable[cformat.FormatOutput]) -> str
        xform = "".join([line.output_full + " " for line in res])  # type: str
        return xform


class XFormCountLines(XFormType):
    """ Count the lines output by confget. """

    def __init__(self, sought=None, sought_in=True):
        # type: (XFormCountLines, Optional[str], bool) -> None
        super(XFormCountLines, self).__init__()
        self.sought = sought
        self.sought_in = sought_in

    @property
    def command(self):
        # type: (XFormCountLines) -> str
        if self.sought:
            prefix = "| fgrep -{inv}e {sought} ".format(
                inv="" if self.sought_in else "v",
                sought=util.shell_escape(self.sought),
            )
        else:
            prefix = ""
        return prefix + "| wc -l | tr -d ' '"

    def do_xform(self, res):
        # type: (XFormCountLines, Iterable[cformat.FormatOutput]) -> str
        if self.sought:
            return str(
                len(
                    [
                        line
                        for line in res
                        if self.sought_in == (self.sought in line.output_full)
                    ]
                )
            )
        return str(len([line for line in res]))


XFORM = {
    "": XFormNone(),
    "count-lines": XFormCountLines(),
    "count-lines-eq": XFormCountLines(sought="="),
    "count-lines-non-eq": XFormCountLines(sought="=", sought_in=False),
    "newline-to-space": XFormNewlineToSpace(),
}


@six.add_metaclass(abc.ABCMeta)
class TestOutputDef(object):
    """ A definition for a single test's output. """

    def __init(self):
        # type: (TestOutputDef) -> None
        """ No initialization at all for the base class. """

    @abc.abstractmethod
    def get_check(self):
        # type: (TestOutputDef) -> str
        """ Get the check string as a shell command. """
        raise NotImplementedError(
            "{name}.get_check()".format(name=type(self).__name__)
        )

    @abc.abstractproperty
    def var_name(self):
        # type: (TestOutputDef) -> str
        """ Get the variable name to display. """
        raise NotImplementedError(
            "{name}.var_name".format(name=type(self).__name__)
        )

    @abc.abstractmethod
    def check_result(self, _res):
        # type: (TestOutputDef, str) -> None
        """ Check whether the processed confget result is correct. """
        raise NotImplementedError(
            "{name}.check_result()".format(name=type(self).__name__)
        )


class TestExactOutputDef(TestOutputDef):
    """ Check that the program output this exact string. """

    def __init__(self, exact):
        # type: (TestExactOutputDef, str) -> None
        """ Initialize an exact test output object. """
        self.exact = exact

    def get_check(self):
        # type: (TestExactOutputDef) -> str
        return '[ "$v" = ' + util.shell_escape(self.exact) + " ]"

    @property
    def var_name(self):
        # type: (TestExactOutputDef) -> str
        return "v"

    def check_result(self, res):
        # type: (TestExactOutputDef, str) -> None
        assert res == self.exact


class TestExitOKOutputDef(TestOutputDef):
    """ Check that the program succeeded or failed as expected. """

    def __init__(self, success):
        # type: (TestExitOKOutputDef, bool) -> None
        """ Initialize an "finished successfully" test output object. """
        self.success = success

    def get_check(self):
        # type: (TestExitOKOutputDef) -> str
        return '[ "$res" {compare} 0 ]'.format(
            compare="=" if self.success else "!="
        )

    @property
    def var_name(self):
        # type: (TestExitOKOutputDef) -> str
        return "res"

    def check_result(self, res):
        # type: (TestExitOKOutputDef, str) -> None
        # pylint: disable=useless-super-delegation
        super(TestExitOKOutputDef, self).check_result(res)


class TestDef:
    # pylint: disable=too-few-public-methods
    """ A definition for a single test. """

    def __init__(
        self,  # type: TestDef
        args,  # type: Dict[str, str]
        keys,  # type: List[str]
        output,  # type: TestOutputDef
        xform="",  # type: str
        backend="ini",  # type: str
        setenv=False,  # type: bool
        stdin=None,  # type: Optional[str]
    ):  # type: (...) -> None
        # pylint: disable=too-many-arguments
        """ Initialize a test object. """

        self.args = args
        self.keys = keys
        self.xform = xform
        self.output = output
        self.backend = backend
        self.setenv = setenv
        self.stdin = stdin

    def get_backend(self):
        # type: (TestDef) -> Type[cbackend.abstract.Backend]
        """ Get the appropriate confget backend type. """
        return cbackend.BACKENDS[self.backend]

    def get_config(self):
        # type: (TestDef) -> cformat.FormatConfig
        """ Convert the test's data to a config object. """
        data = {}  # type: Dict[str, Any]
        for name, value in self.args.items():
            if name == "hide_var_name":
                continue

            opt = CMDLINE_OPTIONS[name]
            if opt[1]:
                data[name] = value
            else:
                data[name] = True

        if "filename" in data:
            data["filename"] = os.environ["TESTDIR"] + "/" + data["filename"]
        elif self.stdin:
            data["filename"] = "-"

        data["show_var_name"] = "show_var_name" in self.args or (
            (
                "match_var_names" in self.args
                or "list_all" in self.args
                or len(self.keys) > 1
            )
            and "hide_var_name" not in self.args
        )

        return cformat.FormatConfig(self.keys, **data)

    def do_xform(self, res):
        # type: (TestDef, Iterable[cformat.FormatOutput]) -> str
        """ Return the output delimiter depending on the xform property. """
        return XFORM[self.xform].do_xform(res)


class TestFileDef:
    # pylint: disable=too-few-public-methods
    """ A definition for a file defining related tests. """

    def __init__(
        self,  # type: TestFileDef
        tests,  # type: List[TestDef]
        setenv=None,  # type: Optional[Dict[str, str]]
    ):  # type: (...) -> None
        """ Initialize a test file object. """
        self.tests = tests
        self.setenv = {} if setenv is None else setenv
