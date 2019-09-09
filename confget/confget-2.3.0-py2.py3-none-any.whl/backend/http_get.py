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

import os
import re
import urllib

from .. import defs

from . import abstract

try:
    from typing import Dict, List

    _TYPING_USED = (defs, Dict, List)
except ImportError:
    pass


try:
    import urllib.parse  # pylint: disable=ungrouped-imports

    urllib_unquote = urllib.parse.unquote  # pylint: disable=invalid-name
except ImportError:
    urllib_unquote = urllib.unquote  # pylint: disable=invalid-name,no-member


RE_ENTITY = re.compile(r"^ (?P<full> [a-zA-Z0-9_]+ ; )", re.X)


class HTTPGetBackend(abstract.Backend):
    # pylint: disable=too-few-public-methods
    """ Parse INI-style configuration files. """

    def __init__(self, cfg):
        # type: (HTTPGetBackend, defs.Config) -> None
        super(HTTPGetBackend, self).__init__(cfg)

        if self._cfg.filename is not None:
            raise ValueError("No config filename expected")

        qname = (
            "QUERY_STRING" if self._cfg.section == "" else self._cfg.section
        )
        qval = os.environ.get(qname, None)
        if qval is None:
            raise ValueError(
                'No "{qname}" variable in the environment'.format(qname=qname)
            )
        self.query_string = qval
        self.parsed = {}  # type: defs.ConfigData

    def read_file(self):
        # type: (HTTPGetBackend) -> defs.ConfigData
        def split_by_amp(line):
            # type: (str) -> List[str]
            """ Split a line by "&" or "&amp;" tokens. """
            if not line:
                return []

            start = end = 0
            while True:
                pos = line[start:].find("&")
                if pos == -1:
                    return [line]
                if line[pos + 1 :].startswith("amp;"):
                    end = pos + 4
                    break
                entity = RE_ENTITY.match(line[pos + 1 :])
                if entity is None:
                    end = pos
                    break
                start = pos + len(entity.group("full"))

            return [line[:pos]] + split_by_amp(line[end + 1 :])

        data = {}  # type: Dict[str, str]
        fragments = split_by_amp(self.query_string)
        for varval in fragments:
            fields = varval.split("=")
            if len(fields) == 1:
                fields.append("")
            elif len(fields) != 2:
                raise ValueError(
                    'Invalid query string component: "{varval}"'.format(
                        varval=varval
                    )
                )
            data[urllib_unquote(fields[0])] = urllib_unquote(fields[1])

        self.parsed = {self._cfg.section: data}
        return self.get_dict()

    def get_dict(self):
        # type: (HTTPGetBackend) -> defs.ConfigData
        # no dict comprehension, this ought to work on Python 2.6, too
        return dict((item[0], dict(item[1])) for item in self.parsed.items())
