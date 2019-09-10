#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 14:16:40 2018

@author: asr
"""

import numpy as np
from sklearn.cluster import KMeans
import scipy.optimize as opt
import scipy.stats as ss
from scipy.sparse.linalg import lobpcg

from .wtvmeans import WTVMeans, Matrix
from .extra import isiterable


class Elbow(WTVMeans):
    """
    K-Means with elbow method to find k. 'Elbow method' means optimizing
    argmax_k (SSE_k−1 − SSE_k) / (SSE_k − SSE_k+1), where
    SSE_i is the sum of squared errors (also known as inertia)
    assuming i clusters within k−means
    """

    def __init__(self, kmin: int = 1, kmax: int = 12, **kwargs):
        """Constructor

        Parameters
        ----------
        min_pts: int or float
            The minimum number of points in a cluster (to avoid over clustering). It can etier be an integer (absolute value) or a float between 0
            and 1 (ratio of the size of the input observations)

        **kwargs:
            Extra parameters passed to sklearn.cluster.KMeans
            (see http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
        """
        # build WTVMeans object
        super(Elbow, self).__init__(**kwargs)

        # specific to Elbow
        if kmin >= 1 and kmax >= kmin:
            self.kmin = kmin
            self.kmax = kmax + 1
        self.inertia_ = {}.fromkeys(range(kmin, kmax))
        self.elbow_ = {}.fromkeys(range(kmin + 1, kmax))

    def _compute_elbow(self, k: int):
        try:
            return (self.inertia_[k - 1] - self.inertia_[k]) / \
                (self.inertia_[k] - self.inertia_[k + 1])
        except TypeError:
            return None

    def _fit(self):
        """
        Start k-means with elbow method
        """

        # First: starts with the lowest k
        # k = self.kmin
        # k_means = KMeans(n_clusters=k,
        #                  **self._extra_kmeans_args)
        # self.labels_ = k_means.fit_predict(self._data)
        # self.cluster_centers_ = k_means.cluster_centers_

        # self.inertia_[k] = k_means.inertia_
        max_elbow = None
        for k in range(self.kmin, self.kmax + 1):
            k_means = KMeans(n_clusters=k,
                             **self._extra_kmeans_args)
            k_means.fit(self._data)
            self.n_iter_ += k_means.n_iter_
            self.inertia_[k] = k_means.inertia_
            if k > self.kmin + 1:
                self.elbow_[k - 1] = self._compute_elbow(k - 1)
                if (max_elbow is None) or (self.elbow_[k - 1] > max_elbow):
                    max_elbow = self.elbow_[k - 1]

        self.n_clusters_ = max(self.elbow_.keys(),
                               key=lambda k: self.elbow_[k])
        k_means = KMeans(n_clusters=self.n_clusters_,
                         **self._extra_kmeans_args)
        self.labels_ = k_means.fit_predict(self._data)
        self.cluster_centers_ = k_means.cluster_centers_
