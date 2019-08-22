# -*- coding: utf-8 -*-

# pyrsr, A package providing relative spectral response functions for remote sensing instruments.
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Top-level package for pyrsr."""

from .version import __version__
from .rsr import RelativeSpectralResponse, RSR

__author__ = """Daniel Scheffler"""
__email__ = 'daniel.scheffler@gfz-potsdam.de'


__all__ = [
    '__author__',
    '__email__',
    '__version__',
    'RelativeSpectralResponse',
    'RSR'
]
