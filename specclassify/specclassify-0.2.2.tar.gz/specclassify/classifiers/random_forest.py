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

"""Classifiers using random forest algorithms for class separation."""

import numpy as np
from typing import Union, List  # noqa F401  # flake8 issue
from sklearn.ensemble import RandomForestClassifier as _RandomForestClassifier
from geoarray import GeoArray

from .._baseclasses import _ImageClassifier
from ..misc import im2spectra


class RF_Classifier(_ImageClassifier):
    """Random forest classifier."""
    def __init__(self, train_spectra, train_labels, CPUs=1, **kwargs):
        # type: (np.ndarray, Union[np.ndarray, List[int]], Union[int, None], dict) -> None

        # if CPUs is None or CPUs > 1:
        #     CPUs = 1  # The NearestCentroid seems to parallelize automatically. So using multiprocessing is slower.

        super(RF_Classifier, self).__init__(train_spectra, train_labels, CPUs=CPUs)

        self.clf_name = 'random forest'
        self.clf = _RandomForestClassifier(n_jobs=1, **kwargs)
        self.clf.fit(train_spectra, train_labels)

    def _predict(self, imdata, endmembers):
        # type: (GeoArray, np.ndarray) -> (np.ndarray, Union[np.ndarray, None])
        cmap = self.clf.predict(im2spectra(imdata)).reshape(*imdata.shape[:2])
        cmap = self.overwrite_cmap_at_nodata_positions(cmap, imdata)

        return cmap.astype(np.int16), None
