# Copyright (c) 2018-2019, Eduardo Rodrigues and Henry Schreiner.
#
# Distributed under the 3-clause BSD license, see accompanying file LICENSE
# or https://github.com/scikit-hep/particle for details.

from __future__ import absolute_import

import csv

from .. import data
from ..pdgid import PDGID
from ..exceptions import MatchingIDNotFound


with data.open_text(data, 'pdgid_to_pythiaid.csv') as _f:
    _bimap = {int(v['PYTHIAID']):int(v['PDGID']) for v in csv.DictReader(_f)}


class PythiaID(int):
    """

    Examples
    --------
    Typical usage:
    >>> pythiaid = PythiaID(211)
    >>> p = Particle.from_pdgid(pythiaid.to_pdgid())
    >>> p = Particle.find(pdgid=pythiaid.to_pdgid())
    >>> p.name
    'pi+'
    """
    __slots__ = ()  # Keep PythiaID a slots based class

    @classmethod
    def from_pdgid(cls, pdgid):
        """
        Constructor from a PDGID.
        """
        for k, v in _bimap.items():
            if v == pdgid:
                return cls(k)
        raise MatchingIDNotFound("Non-existent PythiaID for input PDGID {0} !".format(pdgid))

    def to_pdgid(self):
        return PDGID(_bimap[self])

    """
    def __eq__(self, other):
        return (
            type(self) is self.__class__
            and type(other) is self.__class__
            and super().__eq__(other)
        )

    def __ne__(self, other):
        return not self == other

    __hash__ = int.__hash__
    """

    def __repr__(self):
        return "<PythiaID: {:d}>".format(int(self))

    def __str__(self):
        return repr(self)

    def __neg__(self):
        return self.__class__(-int(self))

    __invert__ = __neg__



"""
In [56]: class decorator_without_arguments(object):
    ...:
    ...:     def __init__(self, f):
    ...:         ""
    ...:         If there are no decorator arguments, the function
    ...:         to be decorated is passed to the constructor.
    ...:         ""
    ...:         print("Inside __init__()")
    ...:         self.f = f
    ...:
    ...:     def __call__(self, args):
    ...:         ""
    ...:         The __call__ method is not called until the
    ...:         decorated function is called.
    ...:         ""
    ...:         print("Inside __call__()", PythiaID(args).to_pdgid())
    ...:         return self.f(PythiaID(args).to_pdgid())
    ...:

In [57]: @decorator_without_arguments
    ...: def is_meson(v):
    ...:     return getattr(v, 'is_meson')
    ...:
Inside __init__()

In [58]: is_meson(10211)
Inside __call__() <PDGID: 9000211>
Out[58]: True


filename = data.open_text(data, 'pdgid_to_pythiaid.csv')
with filename as _f:
    bimap = {PythiaID(v['PYTHIAID']):PDGID(v['PDGID']) for v in csv.DictReader(_f)}

{PDGID(v1):PythiaID(v2) for v1, v2 in df.head().to_numpy()}

# Decorate the PythiaID class with a to_pdgid() conversion method
# This can only be done *after* the bi-map is defined, to avoid recursion!
def __to_pdgid(self):
    return Pythia2PDGIDBiMap[self]

#_decorator = property(getattr(_functions, __to_pdgid), doc=getattr(_functions, __to_pdgid).__doc__)
setattr(PythiaID, 'to_pdgid', __to_pdgid)

from particle.pdgid import functions as _functions
_n = 'is_meson'
_decorator = property(getattr(_functions, _n), doc=getattr(_functions, _n).__doc__)
setattr(PythiaID, _n, _decorator)
"""
