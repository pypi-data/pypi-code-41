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

# NEW
from hftu import HFTU


from .wtvmeans import WTVMeans, Matrix
from .extra import isiterable


class PhiMeans(WTVMeans):
    """
    PhiMeans algorithm (based on HFTU)
    """

    def __init__(self, alpha: float = 1e-10, **kwargs):
        """Constructor

        Parameters
        ----------
        alpha: float
            The threshold on the type I error output
            by the HFTU (the closer to zero, the more restrictive)
        min_pts: int or float
            The minimum number of points in a cluster (to avoid over clustering). It can either be an integer (absolute value) or a float between 0 and 1 (ratio of the size of the input observations)
        **kwargs:
            Extra parameters passed to sklearn.cluster.KMeans
            (see http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
        """
        # build WTVMeans object
        super(PhiMeans, self).__init__(**kwargs)

        # specific to HFTU
        self.alpha = alpha

    def _fit(self):
        """
        Start Phi-Means
        """

        new_cluster = True
        while new_cluster:
            # Get the current number of clusters
            n_clusters = self.n_clusters_
            # Perform k-means with this value of k and the new centers (from
            # splits)
            self._global_kmeans(n_clusters)

            # Try to split accoridng to the desired method
            for cluster in range(n_clusters):
                self._score_and_split(cluster)

            new_cluster = (n_clusters < self.n_clusters_)

    def _split_with_hftu(self, index: Matrix):
        """
        Test to split or not a cluster according to the
        Hyperplane Folding Test of Unimodality (HFTU)
        """
        H = HFTU()
        classes, results = H.fit_predict(
            self._data[index], method='heuristic', init='random', n_init=10)
        return H.is_unimodal(self.alpha), classes, results.above_center, results.below_center

    def _score_and_split(self, cluster: int):
        """
        Score the cluster. The split is performed according to the score
        """
        index = (self.labels_ == cluster)
        if sum(index) >= self.min_pts:
            unimodal, classes, A, B = self._split_with_hftu(index)
            if not unimodal:
                self._accept_split(cluster,
                                   index,
                                   1 - classes,
                                   np.vstack((A, B)))
