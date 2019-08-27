r"""
Polymake Python library

The polymake python library provides Python bindings to polymake.
"""
from __future__ import absolute_import

from .integer import Integer
from .rational import Rational
from .quadratic_extension import QuadraticExtension

from .vector import VectorInteger, VectorRational

from .functions import *
from .big_object import Polytope

from .coercion import as_pm_object as polymake
