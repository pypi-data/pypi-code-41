#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 14:16:40 2018

@author: asr
"""

import numpy as np
from math import exp
from scipy.stats import anderson
from sklearn.cluster import KMeans

from .wtvmeans import WTVMeans, Matrix
from .extra import project_and_normalize


def anderson_modified_pvalue(A):
    """
    The test means the following: If we reject the normal distribution
    then the probability to be wrong is given by p (type I error)

    These forumlas are given in :
    Ralph B. D'Agostino (1986). "Goodness-of-Fit Techniques" (table 4.9)
    [https://books.google.fr/books?id=WLs6DwAAQBAJ&printsec=frontcover&hl=fr&source=gbs_ge_summary_r&cad=0#v=onepage&q&f=false]

    Parameters
    ----------
    A: double
        The Anderson-Darling statistic (modified)

    Returns
    -------
    p: double
        type I error
    q: double
        (1-p) -> the test confidence
    """
    if A < 0.2:
        q = exp(-13.436 + 101.14 * A - 223.73 * pow(A, 2))
        p = 1 - q
    elif A < 0.340:
        q = exp(-8.318 + 42.796 * A - 59.938 * pow(A, 2))
        p = 1 - q
    elif A < 0.6:
        p = exp(0.9177 - 4.279 * A - 1.38 * pow(A, 2))
        q = 1. - p
    else:
        p = exp(1.2937 - 5.709 * A + 0.0186 * pow(A, 2))
        q = 1. - p
    return p, q


def anderson_type_I_error(data_proj):
    try:
        type_I_error, _ = anderson_modified_pvalue(
            anderson(data_proj.flatten()).statistic)
    except BaseException:
        type_I_error = 0.
    return type_I_error


class GMeans(WTVMeans):
    """
    Particular case G-Means
    """

    def __init__(
            self,
            anderson_threshold: float = 0.001,
            **kwargs):
        """Constructor

        Parameters
        ----------

        anderson_threshold: float
            The threshold on the type I error output
            by the Anderson-Darling test (the closer to zero, the more restrictive)

        min_pts: int or float
            The minimum number of points in a cluster (to avoid over clustering). It can etier be an integer (absolute value) or a float between 0
            and 1 (ratio of the size of the input observations)

        **kwargs:
            Extra parameters passed to sklearn.cluster.KMeans
            (see http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
        """
        super(GMeans, self).__init__(**kwargs)

        # specific to GMeans
        self.anderson_threshold = anderson_threshold

    def _fit(self):
        """
        Start G-Means
        """

        new_cluster = True
        while new_cluster:
            # Get the current number of clusters
            n_clusters = self.n_clusters_
            # Perform k-means with this value of k and the new centers (from
            # splits)
            self._global_kmeans(n_clusters)
            # Try to split every cluster (it can increase the number of clusters)
            for cluster in range(n_clusters):
                self._split_and_score(cluster)

            new_cluster = (n_clusters < self.n_clusters_)

    def _split_and_score(self, cluster):
        """
        Split a cluster and check if the new configuration is better
        than the initial one (scoring)
        """
        index = (self.labels_ == cluster)
        if sum(index) >= self.min_pts:
            # we make a real split
            labels, centers = self._split_pca(cluster)

            keep_the_split = self._split_with_anderson(index, centers)

            # we keep the split as the new clusters
            if keep_the_split:
                self._accept_split(cluster, index, labels, centers)

    def _split_with_anderson(self, index, centers):
        """
        Test to split or not a cluster according to the Anderson-Darling test
        """
        data_proj = project_and_normalize(
            self._data[index], centers[0] - centers[1])
        return anderson_type_I_error(data_proj) < self.anderson_threshold
