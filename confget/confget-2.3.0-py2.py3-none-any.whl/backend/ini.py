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
A confget backend for reading INI-style files.
"""

import io
import re
import sys

from .. import defs

from . import abstract

try:
    from typing import Callable, Dict, Match, NamedTuple, Pattern

    _TYPING_USED = (defs, Dict)

    MatcherType = NamedTuple(
        "MatcherType",
        [
            ("regex", Pattern[str]),
            (
                "handle",
                Callable[
                    [Match[str], Dict[str, str], defs.Config, defs.ConfigData],
                    None,
                ],
            ),
        ],
    )
except ImportError:
    import collections

    MatcherType = collections.namedtuple(  # type: ignore
        "MatcherType", ["regex", "handle"]
    )


class INIBackend(abstract.Backend):
    # pylint: disable=too-few-public-methods
    """ Parse INI-style configuration files. """

    def __init__(self, cfg, encoding="UTF-8"):
        # type: (INIBackend, defs.Config, str) -> None
        super(INIBackend, self).__init__(cfg)

        if self._cfg.filename is None:
            raise ValueError("No config filename specified")
        if self._cfg.filename == "-":
            infile = io.open(sys.stdin.fileno(), mode="r", encoding=encoding)
        else:
            infile = io.open(self._cfg.filename, mode="r", encoding=encoding)
        self.infile = infile
        self.parsed = {}  # type: defs.ConfigData

    def read_file(self):
        # type: (INIBackend) -> defs.ConfigData
        state = {
            "section": "",
            "name": "",
            "value": "",
            "cont": "",
            "found": "",
        }
        res = {"": {}}  # type: defs.ConfigData

        def handle_section(
            match,  # type: Match[str]
            state,  # type: Dict[str, str]
            cfg,  # type: defs.Config
            res,  # type: defs.ConfigData
        ):  # type: (...) -> None
            """ Handle a section heading: store the name. """
            state["section"] = match.group("name")
            if state["section"] not in res:
                res[state["section"]] = {}
            if not (cfg.section_specified or cfg.section or state["found"]):
                cfg.section = state["section"]
            state["found"] = state["section"]

        def handle_comment(
            _match,  # type: Match[str]
            _state,  # type: Dict[str, str]
            _cfg,  # type: defs.Config
            _res,  # type: defs.ConfigData
        ):  # type: (...) -> None
            """ Handle a comment line: ignore it. """
            pass  # pylint: disable=unnecessary-pass

        def handle_variable(
            match,  # type: Match[str]
            state,  # type: Dict[str, str]
            _cfg,  # type: defs.Config
            res,  # type: defs.ConfigData
        ):  # type: (...) -> None
            """ Handle an assignment: store, check for a continuation. """
            state["name"] = match.group("name")
            state["value"] = match.group("value")
            state["cont"] = match.group("cont")
            state["found"] = state["name"]
            if not state["cont"]:
                res[state["section"]][state["name"]] = state["value"]

        matches = [
            MatcherType(
                regex=re.compile(r"^ \s* (?: [#;] .* )? $", re.X),
                handle=handle_comment,
            ),
            MatcherType(
                regex=re.compile(
                    r"""
                    ^
                    \s* \[ \s*
                    (?P<name> [^\]]+? )
                    \s* \] \s*
                    $""",
                    re.X,
                ),
                handle=handle_section,
            ),
            MatcherType(
                regex=re.compile(
                    r"""
                    ^
                    \s*
                    (?P<name> \S+ )
                    \s* = \s*
                    (?P<value> .*? )
                    \s*
                    (?P<cont> [\\] )?
                    $""",
                    re.X,
                ),
                handle=handle_variable,
            ),
        ]

        for line in self.infile.readlines():
            line = line.rstrip("\r\n")
            if state["cont"]:
                if line.endswith("\\"):
                    line, state["cont"] = line[:-1], line[-1]
                else:
                    state["cont"] = ""
                state["value"] += line
                if not state["cont"]:
                    res[state["section"]][state["name"]] = state["value"]
                continue

            for data in matches:
                match = data.regex.match(line)
                if match is None:
                    continue
                data.handle(match, state, self._cfg, res)
                break
            else:
                raise ValueError(
                    "Unexpected line in {fname}: {line}".format(
                        fname=self._cfg.filename, line=line
                    )
                )

        self.parsed = res
        return self.get_dict()

    def get_dict(self):
        # type: (INIBackend) -> defs.ConfigData
        # no dict comprehension, this ought to work on Python 2.6, too
        return dict((item[0], dict(item[1])) for item in self.parsed.items())
