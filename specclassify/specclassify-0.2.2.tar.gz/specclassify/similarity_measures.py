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

"""Classifiers using euclidian distance as measure for class distances."""

import numpy as np


def calc_sam(s1_norm, s2_norm, axis=0):
    """Compute spectral angle between two vectors or images (in radians)."""
    upper = np.sum(s1_norm * s2_norm, axis=axis)
    lower = np.sqrt(np.sum(s1_norm * s1_norm, axis=axis)) * np.sqrt(np.sum(s2_norm * s2_norm, axis=axis))

    if isinstance(lower, np.ndarray):
        lower[lower == 0] = 1e-10
    else:
        lower = lower or 1e-10

    quotient = upper / lower
    quotient[np.isclose(quotient, 1)] = 1  # in case of pixels that are equal to the endmember

    return np.arccos(quotient)


def calc_sid(s1_norm, s2_norm, axis=0):
    """Compute the spectral information divergence between two vectors or images."""
    def get_sum(x, axis=0):
        s = np.sum(x, axis=axis)
        s[s == 0] = 1e-10
        return s

    if s1_norm.ndim == 3 and s2_norm.ndim == 3:
        p = (s1_norm / get_sum(s1_norm, axis=axis)[:, :, np.newaxis]) + np.spacing(1)
        q = (s2_norm / get_sum(s1_norm, axis=axis)[:, :, np.newaxis]) + np.spacing(1)
    else:
        p = (s1_norm / get_sum(s1_norm, axis=axis)) + np.spacing(1)
        q = (s2_norm / get_sum(s1_norm, axis=axis)) + np.spacing(1)

    return np.sum(p * np.log(p / q) + q * np.log(q / p), axis=axis)
