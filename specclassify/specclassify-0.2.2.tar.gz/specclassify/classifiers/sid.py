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

"""Classifiers using spectral information divergence as measure for class distances."""

import numpy as np
from typing import Union  # noqa F401  # flake8 issue
from geoarray import GeoArray

from .._baseclasses import _ImageClassifier
from ..similarity_measures import calc_sid
from ..misc import normalize_endmembers_image


class SID_Classifier(_ImageClassifier):
    def __init__(self, train_spectra, CPUs=1):
        # type: (np.ndarray, Union[int, None]) -> None
        super(SID_Classifier, self).__init__(train_spectra, np.array(range(train_spectra.shape[0])), CPUs=CPUs)

        self.clf_name = 'spectral information divergence (SID)'

    @property
    def sid(self):
        return self._distance_metrics

    def _predict(self, imdata, endmembers):
        # type: (GeoArray, np.ndarray) -> (np.ndarray, Union[np.ndarray, None])
        if not imdata.shape[2] == self.train_spectra.shape[1]:
            raise RuntimeError('Matrix dimensions are not aligned. Input image has %d bands but input spectra '
                               'have %d.' % (imdata.shape[2], self.train_spectra.shape[1]))

        # normalize input data because SID asserts only data between -1 and 1
        train_spectra_norm, tileimdata_norm = normalize_endmembers_image(endmembers, imdata[:])

        sid = np.zeros((imdata.shape[0], imdata.shape[1], self.n_samples), np.float)
        # if np.std(tileimdata) == 0:  # skip tiles that only contain the same value

        # loop over all training spectra and compute spectral information divergence for each pixel
        for n_sample in range(self.n_samples):
            train_spectrum = train_spectra_norm[n_sample, :].reshape(1, 1, self.n_features)
            sid[:, :, n_sample] = calc_sid(tileimdata_norm, train_spectrum, axis=2)

        sid_min = np.min(sid, axis=2).astype(np.float32)
        cmap = np.argmin(sid, axis=2).astype(np.int16)
        cmap = self.overwrite_cmap_at_nodata_positions(cmap, imdata)

        return cmap.astype(np.int16), sid_min

    def label_unclassified_pixels(self, label_unclassified, threshold):
        # type: (int, Union[str, int, float]) -> GeoArray
        return self._label_unclassified_pixels(
            self.cmap, label_unclassified, threshold, self.sid
        )

    def show_sid_histogram(self, figsize=(10, 5), bins=100, normed=False):
        self._show_distances_histogram(self.sid, self.cmap, figsize=figsize, bins=bins, normed=normed)
