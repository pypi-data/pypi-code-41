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

# def interpolation(Z, X, F):
#     """
#     """
#     try:
#         indices = X.searchsorted(Z)
#     except BaseException:
#         print(X)
#         print(Z)
#     return -(F[indices] * (X[indices - 1] - Z) - F[indices - 1] *
#              (X[indices] - Z)) / (X[indices] - X[indices - 1])


# def gcm(X, left, right):
#     F = np.arange(0, 1, 1 / len(X))
#     GCM = np.array(left)
#     while left < right:
#         slopes_left = (F[(left + 1):(right + 1)] - F[left]) / \
#             (X[(left + 1):(right + 1)] - X[left])
#         left += 1 + slopes_left.argmin()
#         GCM = np.append(GCM, left)
#     return GCM


# def lcm(X, left, right):
#     F = np.arange(0, 1, 1 / len(X))
#     LCM = np.array(right)
#     while left < right:
#         slopes_right = (F[left:right] - F[right]) / (X[left:right] - X[right])
#         right = left + slopes_right.argmin()
#         LCM = np.append(right, LCM)
#     return LCM


def dip_threshold(n, p_value):
    k = 21.642
    theta = 1.84157e-2 / sqrt(n)
    return gamma.ppf(1. - p_value, a=k, scale=theta)


# def dip(X):
#     X = np.sort(X)
#     F = np.arange(0, 1, 1 / X.shape[0]) + 1 / X.shape[0]
#     left = 0
#     right = len(X) - 1
#     D = 0
#     d = 1
#     while True:
#         GCM = gcm(X, left, right)
#         LCM = lcm(X, left, right)

#         Lg = interpolation(X[GCM], X[LCM], F[LCM])
#         Gl = interpolation(X[LCM], X[GCM], F[GCM])

#         gap_g, gap_g_index = maxstuff(np.abs(F[GCM] - Lg))
#         gap_l, gap_l_index = maxstuff(np.abs(F[LCM] - Gl))

#         if gap_g > gap_l:
#             d = gap_g
#             left_ = GCM[gap_g_index]
#             right_ = LCM[LCM.searchsorted(GCM[gap_g_index])]
#         else:
#             d = gap_l
#             left_ = GCM[GCM.searchsorted(LCM[gap_l_index]) - 1]
#             right_ = LCM[gap_l_index]
#         if d <= D:
#             return D / 2
#         else:
#             sup_l = np.abs(interpolation(
#                 X[left:(left_ + 1)], X[GCM], F[GCM]) - F[left:(left_ + 1)]).max()
#             sup_r = np.abs(interpolation(
#                 X[right_:(right + 1)], X[LCM], F[LCM]) - F[right_:(right + 1)]).max()
#             D = max([D, sup_l, sup_r])
#             left = left_
#             right = right_


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
            # k_means = KMeans(n_clusters=n_clusters,
            #                  init=self.cluster_centers_,
            #                  n_init=1,
            #                  **self._extra_kmeans_args)
            # self.labels_ = k_means.fit_predict(self._data)
            # self.cluster_centers_ = k_means.cluster_centers_
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
