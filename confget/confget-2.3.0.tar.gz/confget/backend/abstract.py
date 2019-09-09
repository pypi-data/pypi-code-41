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
An abstract metaclass for confget backends.
"""

import abc
import configparser

import six

from .. import defs

try:
    from typing import Dict, Text

    _TYPING_USED = (defs, Dict, Text)
except ImportError:
    pass


@six.add_metaclass(abc.ABCMeta)
class Backend(object):
    # pylint: disable=too-few-public-methods
    """ An abstract confget parser backend. """

    def __init__(self, cfg):
        # type: (Backend, defs.Config) -> None
        self._cfg = cfg

    @abc.abstractmethod
    def read_file(self):
        # type: (Backend) -> defs.ConfigData
        """ Read and parse the configuration file, invoke the callbacks. """
        raise NotImplementedError("Backend.read_file")

    @abc.abstractmethod
    def get_dict(self):
        # type: (Backend) -> defs.ConfigData
        """ Return the sections and values from the configuration file. """
        raise NotImplementedError("Backend.get_dict")

    def get_configparser(self):
        # type: (Backend) -> configparser.ConfigParser
        """ Return a ConfigParser object with the parsed values. """
        par = configparser.ConfigParser(interpolation=None)
        par.read_dict(self.get_dict())
        return par
