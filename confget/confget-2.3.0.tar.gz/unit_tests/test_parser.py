# Copyright (c) 2019  Peter Pentchev <roam@ringlet.net>
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
Test that the backends return ConfigParser objects.
"""

from __future__ import print_function

import os

from confget import backend as cbackend
from confget import defs as cdefs

# pylint: enable=wrong-import-position


try:
    from typing import Any

    _TYPING_USED = (Any,)
except ImportError:
    pass


def test_ini():
    # type: () -> None
    """ Test the ConfigParser object returned by the INI file backend. """
    cfg = cdefs.Config([], filename=os.environ["TESTDIR"] + "/t3.ini")
    ini = cbackend.BACKENDS["ini"](cfg)

    data = ini.read_file()
    assert set(data.keys()) == set(["", "a"])
    assert data["a"]["aonly"] == "a"
    assert data["a"]["both"] == "a"
    assert data[""]["defonly"] == "default"
    assert data[""]["both"] == "default"
    assert "aonly" not in data[""]
    assert "defonly" not in data["a"]

    par = ini.get_configparser()
    assert set(par.sections()) == set(["", "a"])
    assert par.get("a", "aonly") == "a"
    assert par.get("a", "both") == "a"
    assert par.get("", "defonly") == "default"
    assert par.get("", "both") == "default"
    assert "aonly" not in par[""]
    # And this is where ConfigParser gets weird...
    assert par.get("a", "defonly") == "default"
