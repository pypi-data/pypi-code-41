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

"""Algorithms for multispectral image classification."""

import numpy as np
from typing import Union, List, Tuple  # noqa F401  # flake8 issue
from geoarray import GeoArray

from specclassify import \
    MinimumDistance_Classifier, kNN_MinimumDistance_Classifier, kNN_Classifier, SAM_Classifier, kNN_SAM_Classifier, \
    FEDSA_Classifier, kNN_FEDSA_Classifier, SID_Classifier, RF_Classifier

global_shared_endmembers = None  # type: Union[None, np.ndarray]
global_shared_im2classify = None  # type: Union[None, GeoArray]


def classify_image(image, train_spectra, train_labels, classif_alg, in_nodataVal=None, cmap_nodataVal=None,
                   tiledims=(1000, 1000), CPUs=None, return_distance=False, unclassified_threshold=None,
                   unclassified_pixVal=-1, **kwargs):
    # type: (Union[np.ndarray, GeoArray], np.ndarray, Union[np.ndarray, List[int]], str, int, int, tuple, int, bool, Union[int, float, str], int, dict) -> Union[GeoArray, Tuple[GeoArray, np.ndarray]]  # noqa E501
    """Classify image to find the class each spectrum belongs to.

    :param image:           image to be classified
    :param train_spectra:
    :param train_labels:
    :param classif_alg:     algorithm to be used for image classification
                            (to define which cluster each pixel belongs to)
                            'MinDist':      Minimum Distance (Nearest Centroid)
                            'kNN_MinDist':  Minimum Distance (Nearest Centroid)
                            'kNN':          k-nearest-neighbour
                            'SAM':          spectral angle mapping
                            'kNN_SAM':      k-nearest neighbour spectral angle mapping
                            'FEDSA':        fused euclidian distance / spectral angle
                            'SID':          spectral information divergence
                            'RF':           random forest
    :param in_nodataVal:
    :param cmap_nodataVal:
    :param tiledims:
    :param CPUs:            number of CPUs to be used for classification
    :param return_distance: whether to return the distance metrics leading to the returned classification map
    :param unclassified_threshold:  if given, all pixels where the computed distance metric exceeds the given threshold
                                    are labelled as unclassified (only usable for 'MinDist', 'SAM' and 'SID'
                                    - may be given as float, integer or string to label a certain distance percentile
                                    - if given as string, it must match the format, e.g., '10%' for labelling the worst
                                      10 % of the distances as unclassified
    :param unclassified_pixVal:     pixel value to be used in the classification map for unclassified pixels
                                    (default: -1)
    :param kwargs:          keyword arguments to be passed to classifiers if possible
    """
    if classif_alg == 'kNN':
        clf = kNN_Classifier(
            train_spectra,
            train_labels,
            CPUs=CPUs,
            **kwargs)

    elif classif_alg == 'MinDist':
        clf = MinimumDistance_Classifier(
            train_spectra,
            train_labels,
            CPUs=CPUs,
            **kwargs)

    elif classif_alg == 'kNN_MinDist':
        clf = kNN_MinimumDistance_Classifier(
            train_spectra,
            train_labels,
            CPUs=CPUs,
            **kwargs)  # 'n_neighbors' should be in there

    elif classif_alg == 'SAM':
        clf = SAM_Classifier(
            train_spectra,
            CPUs=CPUs)

    elif classif_alg == 'kNN_SAM':
        kw = dict(n_neighbors=kwargs['n_neighbors']) if 'n_neighbors' in kwargs else dict()
        clf = kNN_SAM_Classifier(
            train_spectra,
            CPUs=CPUs,
            **kw)

    elif classif_alg == 'FEDSA':
        clf = FEDSA_Classifier(
            train_spectra,
            CPUs=CPUs)

    elif classif_alg == 'kNN_FEDSA':
        kw = dict(n_neighbors=kwargs['n_neighbors']) if 'n_neighbors' in kwargs else dict()
        clf = kNN_FEDSA_Classifier(
            train_spectra,
            CPUs=CPUs,
            **kw)

    elif classif_alg == 'SID':
        clf = SID_Classifier(
            train_spectra,
            CPUs=CPUs)

    elif classif_alg == 'RF':
        clf = RF_Classifier(
            train_spectra,
            train_labels,
            CPUs=CPUs, **kwargs)

    else:
        raise NotImplementedError("Currently only the methods 'kNN', 'MinDist', 'kNN_MinDist', 'SAM', 'kNN_SAM', "
                                  "'FEDSA', 'kNN_FEDSA', 'SID' and 'RF' are implemented.")

    cmap = clf.classify(image, in_nodataVal=in_nodataVal, cmap_nodataVal=cmap_nodataVal, tiledims=tiledims)

    # label unclassified pixels
    if unclassified_threshold is not None:
        if classif_alg not in ['MinDist', 'kNN_MinDist', 'SAM', 'kNN_SAM', 'FEDSA', 'kNN_FEDSA', 'SID']:
            raise RuntimeError("Only the methods 'MinDist', 'kNN_MinDist', 'SAM', 'kNN_SAM', 'FEDSA', 'kNN_FEDSA' and "
                               "'SID' can label unclassifed pixels.")

        clf.label_unclassified_pixels(label_unclassified=unclassified_pixVal, threshold=unclassified_threshold)

    # return
    if not return_distance:
        return cmap
    else:
        if classif_alg in ['MinDist', 'kNN_MinDist']:
            dist = clf.euclidian_distance
        elif classif_alg in ['SAM', 'kNN_SAM']:
            dist = clf.angles_deg
        elif classif_alg in ['FEDSA', 'kNN_FEDSA']:
            dist = clf.fedsa
        elif classif_alg == 'SID':
            dist = clf.sid
        else:
            dist = None

        return cmap, dist
