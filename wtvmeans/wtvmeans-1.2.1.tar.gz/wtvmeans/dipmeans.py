#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 14:16:40 2018

@author: asr
"""


import numpy as np
from math import sqrt
from scipy.stats import gamma
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import pairwise_distances
from .extra import maxstuff
from .wtvmeans import WTVMeans

# NEW
from unidip.dip import dip_fn


def dip(X):
    return dip_fn(X)[0]


def dip_threshold(n, p_value):
    k = 21.642
    theta = 1.84157e-2 / sqrt(n)
    return gamma.ppf(1. - p_value, a=k, scale=theta)


class DipMeans(WTVMeans):
    """
    DipMeans Algorithm
    """

    def __init__(self,
                 p_value: float = 0.05,
                 split_viewers: float = 0.5,
                 monte_carlo_samples: int = 1000,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        p_value: float
            The threshold on the p-value output by the
            dip test of unimodality (the closer to zero, the more restrictive)

        split_viewers: float
            The minimum required percentage of points within
            a cluster voting for a split to make it effective

        monte_carlo_samples: int
            The number of uniform samples to draw in order to
            compute the p-value of the dip test (it must be high enough according to the p_value parameter)

        min_pts: int or float
            The minimum number of points in a cluster (to avoid over clustering). It can either be an integer (absolute value) or a float between 0
            and 1 (ratio of the size of the input observations)

        **kwargs:
            Extra parameters passed to sklearn.cluster.KMeans
            (see http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
        """
        # build WTVMeans object
        super(DipMeans, self).__init__(**kwargs)

        # add specific attributes
        self.pairwise_distances_ = None
        self.split_viewers = split_viewers
        self.p_value = p_value
        self.monte_carlo_samples = monte_carlo_samples
        self._cluster_to_split = None

    def _fit(self):
        """
        Start DipMeans
        """
        # The dip test needs the pairwise distances
        self.pairwise_distances_ = pairwise_distances(self._data)

        new_cluster = True
        while new_cluster:
            # Get the current number of clusters
            n_clusters = self.n_clusters_
            # Perform k-means with this value of k and the new centers (from
            # splits)
            self._global_kmeans(n_clusters)

            self._score_all_and_split()
            new_cluster = (n_clusters < self.n_clusters_)

    def _dip_score(self, cluster):
        """
        Test to split or not a cluster according to the dip test
        """
        index = (self.labels_ == cluster)
        cluster_size = sum(index)
        if cluster_size >= self.min_pts:
            dist = self.pairwise_distances_[index].T[index]
            # step 1
            dip_uniform = np.zeros(self.monte_carlo_samples)
            for i in range(self.monte_carlo_samples):
                dip_uniform[i] = dip(np.random.uniform(0, 1, cluster_size))

            # step 2
            dip_pointwise = np.zeros(cluster_size)
            for i in range(cluster_size):
                dip_pointwise[i] = dip(dist[:, i])

            # step 3
            threshold = dip_threshold(cluster_size, self.p_value)
            candidates = (dip_pointwise > threshold)
            if sum(candidates) >= cluster_size * self.split_viewers:
                return np.mean(dip_pointwise)
        return 0

    def _get_dip_split_candidate(self):
        """
        Return the cluster to split (dip-test only) or None if all clusters are OK
        """
        scores = []
        for cluster in range(self.n_clusters_):
            scores.append(self._dip_score(cluster))
        max_score, cluster = maxstuff(scores)
        if max_score > 0:
            return cluster
        return None

    def _score_all_and_split(self):
        """
        Score all the clusters and split the more 'splitable'
        (if there are several splitable clusters)
        """
        cluster = self._get_dip_split_candidate()
        if cluster is not None:
            index = (self.labels_ == cluster)
            labels, centers = self._split(cluster, index)
            self._accept_split(cluster, index, labels, centers)
