#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 14:16:40 2018

@author: asr
"""

import numpy as np
from math import log
from sklearn.cluster import KMeans

from .wtvmeans import WTVMeans


def spherical_var(data, center) -> float:
    return np.square(data - center).sum() / (data.shape[0] - 1)


def bic(data, labels, centers) -> float:
    n_obs, dim = data.shape
    n_cl = centers.shape[0]

    log_likelihood = 0.
    for i in range(n_cl):
        u = (labels == i)
        n = sum(u)
        sigma_2 = spherical_var(data[u], centers[i])
        log_likelihood += - 0.5 * n * dim * \
            np.log(2 * np.pi * sigma_2) - 0.5 * (n - 1) + n * np.log(np.mean(u))

    return -2 * log_likelihood + 0.5 * log(n_obs) * dim * n_cl


def bic_single_cluster(data) -> float:
    return bic(data,
               np.zeros(data.shape[0]),
               data.mean(axis=0).reshape(1, -1))


class XMeans(WTVMeans):
    """
    X-Means algorithm
    """

    def __init__(self, **kwargs):
        """
        Constructor

        Parameters
        ----------

        min_pts: int or float
            The minimum number of points in a cluster (to avoid over clustering). It can etier be an integer (absolute value) or a float between 0
            and 1 (ratio of the size of the input observations)

        **kwargs:
            Extra parameters passed to sklearn.cluster.KMeans
            (see http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
        """
        super(XMeans, self).__init__(**kwargs)

    def _fit(self):
        """
        Start XMeans
        """

        new_cluster = True
        while new_cluster:
            # Get the current number of clusters
            n_clusters = self.n_clusters_
            # Perform k-means with this value of k and the new centers (from
            # splits)
            self._global_kmeans(n_clusters)

            # Try to split every cluster
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
            labels, centers = self._split(cluster)

            # we score the split
            keep_the_split = self._split_with_bic(index, labels, centers)

            # we keep the split as the new clusters
            if keep_the_split:
                self._accept_split(cluster, index, labels, centers)

    def _split_with_bic(self, index, labels, centers) -> bool:
        """
        Test to split or not a cluster according to the Bayesian Information Criterion (BIC)
        """
        bic_1 = bic_single_cluster(self._data[index])
        bic_2 = bic(self._data[index], labels, centers)
        return bic_2 < bic_1
