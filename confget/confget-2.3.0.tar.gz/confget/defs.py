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
Common definitions for the confget configuration parsing library.
"""

try:
    from typing import Dict, List, Optional

    _TYPING_USED = (List, Optional)

    ConfigData = Dict[str, Dict[str, str]]
except ImportError:
    pass


VERSION_STRING = "2.3.0"
FEATURES = [("BASE", VERSION_STRING)]


class Config(object):
    # pylint: disable=too-few-public-methods
    """ Base class for the internal confget configuration. """

    def __init__(
        self,  # type: Config
        varnames,  # type: List[str]
        filename=None,  # type: Optional[str]
        section="",  # type: str
        section_specified=False,  # type: bool
    ):  # type: (...) -> None
        """ Store the specified configuration values. """
        self.filename = filename
        self.section = section
        self.section_specified = section_specified
        self.varnames = varnames
