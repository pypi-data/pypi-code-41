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

"""Base classes for specclassify."""

import numpy as np
from typing import Union, List  # noqa F401  # flake8 issue
from multiprocessing import Pool
from tqdm import tqdm
from matplotlib import pyplot as plt
from geoarray import GeoArray
from py_tools_ds.numeric.array import get_array_tilebounds


global_shared_endmembers = None  # type: Union[None, np.ndarray]
global_shared_im2classify = None  # type: Union[None, GeoArray]


def _mp_initializer(endmembers, im2classify):
    """Declare global variables needed for image classifiers.

    :param endmembers:
    :param im2classify:
    """
    global global_shared_endmembers, global_shared_im2classify
    global_shared_endmembers = endmembers
    global_shared_im2classify = im2classify


class _ImageClassifier(object):
    """Base class for GMS image classifiers."""

    def __init__(self, train_spectra, train_labels, CPUs=1):
        # type: (np.ndarray, Union[np.ndarray, List[int]], Union[int, None]) -> None
        self.CPUs = CPUs
        self.train_spectra = train_spectra
        self.train_labels = train_labels
        self.n_samples = train_spectra.shape[0]
        self.n_features = train_spectra.shape[1]
        self.clf = None  # to be implemented by the subclass
        self.cmap = None
        self.clf_name = ''
        self._distance_metrics = None
        self._cmap_nodataVal = None

    def _predict(self, imdata, endmembers):
        raise NotImplementedError('This method has to be implemented by the subclass.')

    def _predict_tilewise(self, tilepos):
        assert global_shared_endmembers is not None and global_shared_im2classify is not None
        (rS, rE), (cS, cE) = tilepos
        tileimdata = global_shared_im2classify.get_subset(xslice=slice(cS, cE + 1), yslice=slice(rS, rE + 1))
        endmembers = global_shared_endmembers

        cmap, dists = self._predict(tileimdata, endmembers)

        return tilepos, cmap, dists

    def classify(self, image_cube, in_nodataVal=None, cmap_nodataVal=None, tiledims=(100, 100)):
        """Classify the image.

        :param image_cube:
        :param in_nodataVal:
        :param cmap_nodataVal:  written into classif_map at nodata pixels
        :param tiledims:
        :return:
        """
        self._cmap_nodataVal = cmap_nodataVal

        dtype_cmap = np.int16
        if cmap_nodataVal is not None and not np.can_cast(cmap_nodataVal, dtype_cmap):
            dtype_cmap = np.find_common_type(np.array(self.train_labels), np.array([cmap_nodataVal]))

        image_cube_gA = GeoArray(image_cube, nodata=in_nodataVal)  # lazily read in tiles to save memory

        bounds_alltiles = get_array_tilebounds(image_cube_gA.shape, tiledims)

        print('Performing %s image classification...' % self.clf_name)
        if self.CPUs is None or self.CPUs > 1:
            with Pool(self.CPUs, initializer=_mp_initializer, initargs=(self.train_spectra, image_cube_gA)) as pool:
                tiles_results = list(pool.imap_unordered(self._predict_tilewise, bounds_alltiles))

        else:
            _mp_initializer(self.train_spectra, image_cube_gA)
            tiles_results = [self._predict_tilewise(bounds) for bounds in tqdm(bounds_alltiles)]

        # use a local variable to avoid pickling in multiprocessing
        cmap_dist_shape = (image_cube_gA.rows, image_cube_gA.cols) if tiles_results[0][1].ndim == 2 else \
            (image_cube_gA.rows, image_cube_gA.cols, tiles_results[0][1].shape[2])
        cmap = GeoArray(np.empty(cmap_dist_shape, dtype=dtype_cmap), nodata=cmap_nodataVal)
        cmap.unclassified_val = None
        dist = np.empty(cmap_dist_shape, dtype=np.float32)

        for tile_res in tiles_results:
            ((rS, rE), (cS, cE)), tile_cm = tile_res[:2]
            cmap[rS: rE + 1, cS: cE + 1] = tile_cm
            if len(tile_res) == 3:
                dist[rS: rE + 1, cS: cE + 1] = tile_res[2]

        self.cmap = cmap
        if len(tiles_results[0]) == 3:
            self._distance_metrics = dist

        return self.cmap

    def overwrite_cmap_at_nodata_positions(self, cmap, imdata):
        # type: (np.ndarray, GeoArray) -> np.ndarray
        """Overwrite the classification map at all positions with nodata in ANY band.

        NOTE: nodata in not all but in any band would cause a wrong output class

        :param cmap:
        :param imdata:
        :return:
        """
        if imdata.nodata is not None and self._cmap_nodataVal is not None:
            mask_anynodata = np.any(imdata[:] == imdata.nodata, axis=2)
            cmap[mask_anynodata] = self._cmap_nodataVal

        return cmap

    @staticmethod
    def _label_unclassified_pixels(cmap, label_unclassified, threshold, distances):
        # type: (GeoArray, int, Union[str, int, float], np.ndarray) -> GeoArray
        assert cmap is not None and distances is not None
        assert np.can_cast(label_unclassified, cmap.dtype)
        # noinspection PyProtectedMember
        cmap_nodataVal = cmap._nodata

        if isinstance(threshold, (int, float)):
            pass
        elif isinstance(threshold, str) and threshold.endswith('%'):
            percent = float(threshold.split('%')[0].strip())

            # only include distances where the classification map is not nodata
            #   at nodata positions, the distances may have the initialzation value 1e6 (MinDist)
            dists = distances[cmap[:] != cmap_nodataVal] if cmap_nodataVal is not None else distances

            # noinspection PyTypeChecker
            threshold = np.nanpercentile(dists, 100 - percent)
        else:
            raise ValueError(threshold)

        mask_unclassified = distances > threshold
        if cmap_nodataVal is not None:
            mask_unclassified = mask_unclassified & (cmap[:] != cmap_nodataVal)

        cmap[mask_unclassified] = label_unclassified
        cmap.unclassified_val = label_unclassified

        return cmap

    def show_cmap(self, **kwargs):
        if self.cmap is not None:
            self.cmap.show(cmap=kwargs.pop('cmap', 'Spectral'),
                           **kwargs)

    def _show_distance_metrics(self, **kwargs):
        if self._distance_metrics is not None:
            dists = GeoArray(self._distance_metrics)
            if self._cmap_nodataVal is not None:
                dists[self.cmap[:] == self._cmap_nodataVal] = -9999
                dists.nodata = -9999

            dists.show(cmap=kwargs.pop('cmap', 'Spectral_r'),
                       vmin=kwargs.pop('vmin', 0),
                       **kwargs)

    @staticmethod
    def _show_distances_histogram(distances, cmap, figsize=(10, 5), bins=100, normed=False):
        # noinspection PyProtectedMember
        mask_gooddata = cmap[:] != cmap._nodata
        if cmap.unclassified_val is not None:
            mask_gooddata = mask_gooddata & (cmap[:] != cmap.unclassified_val)
        distances = distances[mask_gooddata]

        plt.figure(figsize=figsize)
        plt.hist(list(distances), density=normed, bins=bins, color='gray')
        plt.xlabel('Pixel value')
        plt.ylabel('Probabilty' if normed else 'Count')
        plt.show()


class _kNN_ImageClassifier(_ImageClassifier):
    def __init__(self, train_spectra, train_labels, CPUs=1, n_neighbors=3):
        super().__init__(train_spectra, train_labels, CPUs=CPUs)

        self.n_neighbors = n_neighbors

    def _predict(self, imdata, endmembers):
        raise NotImplementedError('This method has to be implemented by the subclass.')

    def get_min_distances_and_corresponding_cmap(self, dists):
        k = self.n_neighbors if self.n_neighbors <= dists.shape[2] else dists.shape[2]

        if self.n_neighbors < dists.shape[2]:
            cmap = np.argpartition(dists, k, axis=2)[:, :, :k].astype(np.int16)
            dists_min_k = np.partition(dists, k, axis=2)[:, :, :k].astype(np.float32)
        else:
            cmap = np.tile(np.arange(dists.shape[2]).reshape(1, 1, -1), (*dists.shape[:2], 1))
            dists_min_k = dists

        # sort cmap by ascending spectral distances
        idx_2D = np.argsort(dists_min_k, axis=2).reshape(-1, cmap.shape[2])
        cmap = \
            cmap.reshape(-1, cmap.shape[2])[np.arange(cmap.shape[0] * cmap.shape[1])[:, np.newaxis], idx_2D] \
                .reshape(*cmap.shape)
        dists_min_k = np.sort(dists_min_k, axis=2)

        return dists_min_k, cmap
