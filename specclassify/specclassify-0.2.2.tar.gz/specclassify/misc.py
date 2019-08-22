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

"""Functions commonly used by specclassify modules."""

import numpy as np
from typing import Union, Tuple  # noqa F401  # flake8 issue
from sklearn.preprocessing import MaxAbsScaler
from geoarray import GeoArray


def normalize_endmembers_image(endmembers, image):
    # type: (np.ndarray, np.ndarray) -> Tuple[np.ndarray, np.ndarray]
    em = endmembers.astype(np.float)
    im = image.astype(np.float)

    allVals = np.hstack([em.flat, im.flat]).reshape(-1, 1)

    if allVals.min() < -1 or allVals.max() > 1:
        max_abs_scaler = MaxAbsScaler()
        max_abs_scaler.fit_transform(allVals)
        endmembers_norm = max_abs_scaler.transform(em)
        image_norm = spectra2im(max_abs_scaler.transform(im2spectra(im)), tgt_rows=im.shape[0], tgt_cols=im.shape[1])

        return endmembers_norm, image_norm

    else:
        return em, im


def im2spectra(geoArr):
    # type: (Union[GeoArray, np.ndarray]) -> np.ndarray
    """Convert 3D images to array of spectra samples (rows: samples;  cols: spectral information)."""
    return geoArr.reshape((geoArr.shape[0] * geoArr.shape[1], geoArr.shape[2]))


def spectra2im(spectra, tgt_rows, tgt_cols):
    # type: (Union[GeoArray, np.ndarray], int, int) -> np.ndarray
    """Convert array of spectra samples (rows: samples;  cols: spectral information) to a 3D image.

    :param spectra:     2D array with rows: spectral samples / columns: spectral information (bands)
    :param tgt_rows:    number of target image rows
    :param tgt_cols:    number of target image rows
    :return:            3D array (rows x columns x spectral bands)
    """
    return spectra.reshape(tgt_rows, tgt_cols, spectra.shape[1])
