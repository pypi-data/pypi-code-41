#coding: utf8
from __future__ import absolute_import
import sys


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = (str, bytes)
    unicode = str
else:
    string_types = basestring
    unicode = unicode


def to_bytes(s):
    if isinstance(s, unicode):
        s = s.encode('utf8')
    return s
