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
from typing import Union, List  # noqa F401  # flake8 issue
from sklearn.neighbors import KNeighborsClassifier as _KNeighborsClassifier
from sklearn.neighbors import NearestCentroid as _NearestCentroid
from geoarray import GeoArray

from .._baseclasses import _ImageClassifier, _kNN_ImageClassifier
from ..misc import im2spectra


class MinimumDistance_Classifier(_ImageClassifier):
    """Classifier computing the n-dimensional euclidian distance of each pixel vector to each cluster mean vector.

    NOTE:   - distance equation:   D² = sqrt(sum((Xvi - Xvj)²)
    NOTE:   - NearestCentroid parallelizes automatically but as long as the tile size is below 100 x 100,
              Python multiprocessing is faster
    """

    def __init__(self, train_spectra, train_labels, CPUs=1, **kwargs):
        # type: (np.ndarray, Union[np.ndarray, List[int]], Union[int, None], dict) -> None
        super(MinimumDistance_Classifier, self).__init__(train_spectra, train_labels, CPUs=CPUs)

        self.clf_name = 'minimum distance (nearest centroid)'

        self.clf = _NearestCentroid(**kwargs)  # this is the fastest implementation
        self.clf.fit(train_spectra, train_labels)
        self.class_centroids = self.clf.centroids_

    @property
    def euclidian_distance(self):
        return self._distance_metrics

    def compute_euclidian_distance(self, imdata, cmap, nodataVal_cmap):
        spectra = im2spectra(imdata)
        distances = np.full(np.dot(*imdata.shape[:2]), 1e6, np.float32)
        labels = cmap.flatten()

        for lbl in np.unique(cmap):
            if nodataVal_cmap is not None and lbl == nodataVal_cmap:
                continue
            mask = labels == lbl
            centroid = self.class_centroids[list(self.train_labels).index(lbl), :].reshape(1, -1).astype(np.float)
            diff = spectra[mask, :] - centroid
            distances[mask] = np.sqrt((diff ** 2).sum(axis=1))

        return distances.reshape(*imdata.shape[:2])

    def _predict(self, imdata, endmembers):
        # type: (GeoArray, np.ndarray) -> (np.ndarray, Union[np.ndarray, None])
        cmap = self.clf.predict(im2spectra(imdata)).reshape(*imdata.shape[:2])
        cmap = self.overwrite_cmap_at_nodata_positions(cmap, imdata)
        dist = self.compute_euclidian_distance(imdata.astype(np.float32), cmap, self._cmap_nodataVal)

        return cmap.astype(np.int16), dist

    def label_unclassified_pixels(self, label_unclassified, threshold):
        # type: (int, Union[str, int, float]) -> GeoArray
        return self._label_unclassified_pixels(
            self.cmap, label_unclassified, threshold, self.euclidian_distance
        )

    def show_distances_histogram(self, figsize=(10, 5), bins=100, normed=False):
        self._show_distances_histogram(self.euclidian_distance, self.cmap, figsize=figsize, bins=bins, normed=normed)

    def show_distances(self, **kwargs):
        self._show_distance_metrics(**kwargs)


class kNN_MinimumDistance_Classifier(MinimumDistance_Classifier, _kNN_ImageClassifier):
    def __init__(self, train_spectra, train_labels, n_neighbors=3, CPUs=1, **kwargs):
        # type: (np.ndarray, Union[np.ndarray, List[int]], int, Union[int, None], dict) -> None
        super(kNN_MinimumDistance_Classifier, self).__init__(train_spectra, train_labels, CPUs=CPUs, **kwargs)

        self.clf_name = 'k-nearest neighbour minimum distance (nearest centroid) (kNN_MinDist; k=%d)' % n_neighbors
        self.n_neighbors = n_neighbors

    @staticmethod
    def compute_euclidian_distance_3D(image, endmembers):
        n_samples, n_features = endmembers.shape

        if not image.shape[2] == endmembers.shape[1]:
            raise RuntimeError('Matrix dimensions are not aligned. Input image has %d bands but input spectra '
                               'have %d.' % (image.shape[2], endmembers.shape[1]))

        dists = np.zeros((image.shape[0], image.shape[1], n_samples), np.float32)
        # if np.std(tileimdata) == 0:  # skip tiles that only contain the same value

        # loop over all training spectra and compute spectral angle for each pixel
        for n_sample in range(n_samples):
            train_spectrum = endmembers[n_sample, :].reshape(1, 1, n_features).astype(np.float)
            diff = image - train_spectrum
            dists[:, :, n_sample] = np.sqrt((diff ** 2).sum(axis=2))

        return dists

    def _predict(self, imdata, endmembers):
        # type: (GeoArray, np.ndarray) -> (np.ndarray, Union[np.ndarray, None])
        dists = self.compute_euclidian_distance_3D(imdata, endmembers)
        dists_min_k, cmap = self.get_min_distances_and_corresponding_cmap(dists)
        cmap = self.overwrite_cmap_at_nodata_positions(cmap, imdata)

        return cmap.astype(np.int16), dists_min_k


class kNN_Classifier(_ImageClassifier):
    def __init__(self, train_spectra, train_labels, CPUs=1, **kwargs):
        # type: (np.ndarray, Union[np.ndarray, List[int]], Union[int, None], dict) -> None
        super(kNN_Classifier, self).__init__(train_spectra, train_labels, CPUs=CPUs)

        self.clf_name = 'k-nearest neighbour (kNN)'

        self.clf = _KNeighborsClassifier(n_jobs=1, **kwargs)
        self.clf.fit(train_spectra, train_labels)

    def _predict(self, imdata, endmembers):
        # type: (GeoArray, np.ndarray) -> (np.ndarray, Union[np.ndarray, None])
        cmap = self.clf.predict(im2spectra(imdata)).reshape(*imdata.shape[:2])

        return cmap.astype(np.int16), None
