#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 17:39:47 2018

@author: asr
"""

from sklearn.decomposition import PCA
import numpy as np


def isiterable(obj) -> bool:
    """
    Check if an object can be iterated
    """
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def maxstuff(X):
    index = 0
    maxi = X[0]
    for i in range(1, len(X)):
        if X[i] > maxi:
            maxi = X[i]
            index = i
    return maxi, index


def eigenstuff(data):
    """
    Get the first eigenvalue/eigenvector
    """
    pca = PCA(1)
    pca.fit(data)
    return pca.components_, pca.explained_variance_


def project_and_normalize(data, v):
    """
    Project the data on the vector v and normalize it

    Parameters
    ----------
    data: numpy.ndarray
        Data to project, shape=(n_samples, n_features)

    v: numpy.array
        Projection vector (len = n_features)
    """
    data_proj = np.dot(data, v.reshape(-1, 1)) / np.linalg.norm(v)
    return (data_proj - data_proj.mean()) / data_proj.std()


def sort_labels(y):
    """
    Tidy up in-place the labels associated to the observations (the first
    observation must belongs to the cluster 0, the first next
    observation not belonging to cluster 0 must belong to cluster 1...).
    For example if 6 points are labelled as follows: [1,0,2,0,2,1]
    This function rename the labels as:  [0,1,2,1,2,0]

    Parameters
    ----------

    y: numpy.ndarray
        labels associated to observations, shape=(n_samples,)
    """
    clusters = np.unique(y)
    n_clusters = len(clusters)
    unsorted_clusters = (clusters + n_clusters).tolist()
    y += n_clusters
    i = 0
    new_cluster_index = 0
    while len(unsorted_clusters) > 0:
        if y[i] in unsorted_clusters:
            unsorted_clusters.remove(y[i])
            index = (y == y[i])
            y[index] = new_cluster_index
            new_cluster_index += 1
        i = i + 1
