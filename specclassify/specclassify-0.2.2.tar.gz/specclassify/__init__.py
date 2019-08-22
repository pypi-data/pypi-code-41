# -*- coding: utf-8 -*-

# specclassify, A Python package for multi- or hyperspectral image classification.
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

"""Top-level package for specclassify."""

from .version import __version__, __versionalias__   # noqa (E402 + F401)
from .classifiers.euclidian import MinimumDistance_Classifier
from .classifiers.euclidian import kNN_MinimumDistance_Classifier
from .classifiers.euclidian import kNN_Classifier
from .classifiers.sam import SAM_Classifier
from .classifiers.sam import kNN_SAM_Classifier
from .classifiers.sid import SID_Classifier
from .classifiers.hybrid import FEDSA_Classifier
from .classifiers.hybrid import kNN_FEDSA_Classifier
from .classifiers.random_forest import RF_Classifier
from .classify import classify_image

__author__ = """Daniel Scheffler"""
__email__ = 'daniel.scheffler@gfz-potsdam.de'
__all__ = [
    'MinimumDistance_Classifier',
    'kNN_MinimumDistance_Classifier',
    'kNN_Classifier',
    'SAM_Classifier',
    'kNN_SAM_Classifier',
    'SID_Classifier',
    'FEDSA_Classifier',
    'kNN_FEDSA_Classifier',
    'RF_Classifier',
    'classify_image',
    '__author__',
    '__email__',
    '__version__',
    '__versionalias__'
]
