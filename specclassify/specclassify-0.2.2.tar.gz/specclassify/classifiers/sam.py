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

"""Classifiers using spectral angle as measure for class distances."""

import numpy as np
from typing import Union  # noqa F401  # flake8 issue
from geoarray import GeoArray

from .._baseclasses import _ImageClassifier, _kNN_ImageClassifier
from ..misc import normalize_endmembers_image
from ..similarity_measures import calc_sam


class SAM_Classifier(_ImageClassifier):
    def __init__(self, train_spectra, CPUs=1):
        # type: (np.ndarray, Union[int, None]) -> None
        super(SAM_Classifier, self).__init__(train_spectra, np.array(range(train_spectra.shape[0])), CPUs=CPUs)

        self.clf_name = 'spectral angle mapper (SAM)'

    @property
    def angles_rad(self):
        return self._distance_metrics

    @property
    def angles_deg(self):
        return np.rad2deg(self._distance_metrics) if self._distance_metrics is not None else None

    @staticmethod
    def calc_sam(image, endmembers):
        n_samples, n_features = endmembers.shape

        if not image.shape[2] == endmembers.shape[1]:
            raise RuntimeError('Matrix dimensions are not aligned. Input image has %d bands but input spectra '
                               'have %d.' % (image.shape[2], endmembers.shape[1]))

        # normalize input data because SAM asserts only data between -1 and 1
        train_spectra_norm, tileimdata_norm = normalize_endmembers_image(endmembers, image)

        angles = np.zeros((image.shape[0], image.shape[1], n_samples), np.float)
        # if np.std(tileimdata) == 0:  # skip tiles that only contain the same value

        # loop over all training spectra and compute spectral angle for each pixel
        for n_sample in range(n_samples):
            train_spectrum = train_spectra_norm[n_sample, :].reshape(1, 1, n_features)
            angles[:, :, n_sample] = calc_sam(tileimdata_norm, train_spectrum, axis=2)

        return angles

    def _predict(self, imdata, endmembers):
        # type: (GeoArray, np.ndarray) -> (np.ndarray, Union[np.ndarray, None])
        angles = self.calc_sam(imdata, endmembers)
        angles_min = np.min(angles, axis=2).astype(np.float32)
        cmap = np.argmin(angles, axis=2).astype(np.int16)
        cmap = self.overwrite_cmap_at_nodata_positions(cmap, imdata)

        return cmap.astype(np.int16), angles_min

    def label_unclassified_pixels(self, label_unclassified, threshold):
        # type: (int, Union[str, int, float]) -> GeoArray
        return self._label_unclassified_pixels(
            self.cmap, label_unclassified, threshold, self.angles_deg
        )

    def show_angles_histogram(self, figsize=(10, 5), bins=100, normed=False):
        self._show_distances_histogram(self.angles_deg, self.cmap, figsize=figsize, bins=bins, normed=normed)

    def show_angles(self, **kwargs):
        self._show_distance_metrics(**kwargs)


class kNN_SAM_Classifier(SAM_Classifier, _kNN_ImageClassifier):
    def __init__(self, train_spectra, n_neighbors=3, CPUs=1):
        # type: (np.ndarray, int, Union[int, None]) -> None
        super(kNN_SAM_Classifier, self).__init__(train_spectra, CPUs=CPUs)

        self.clf_name = 'k-nearest neighbour spectral angle mapper (kNN_SAM; k=%d)' % n_neighbors
        self.n_neighbors = n_neighbors

    def _predict(self, imdata, endmembers):
        # type: (GeoArray, np.ndarray) -> (np.ndarray, Union[np.ndarray, None])
        angles = self.calc_sam(imdata, endmembers)
        angles_min_k, cmap = self.get_min_distances_and_corresponding_cmap(angles)
        cmap = self.overwrite_cmap_at_nodata_positions(cmap, imdata)

        return cmap.astype(np.int16), angles_min_k

    def label_unclassified_pixels(self, label_unclassified, threshold):
        # type: (int, Union[str, int, float]) -> GeoArray
        cmap_labelled0 = self._label_unclassified_pixels(
            GeoArray(self.cmap[:, :, 0], nodata=self.cmap.nodata),
            label_unclassified, threshold, self.angles_deg[:, :, 0]
        )
        cmap = self.cmap
        if label_unclassified in cmap_labelled0[:]:
            cmap[cmap_labelled0[:] == label_unclassified] = label_unclassified

        return cmap
