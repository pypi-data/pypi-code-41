#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 18:54:26 2019

@author: vbokharaie

This module includes methods of fmri_dataset class used for clustering.
"""
from mitfat import _Lib
__methods__ = []  # self is a DataStore
register_method = _Lib.register_method(__methods__)


# %%
@register_method
def cluster(self, X_train, num_clusters):
    """A wrapper for clustering mthoeds.
    calls cluster_scalar if input data is 1 dimentional,
    otherwise calls cluster_raw.

    Parameters
    ----------
    X_train: 'numpy.ndarray', (N=1, N_voxels)
    no_clusters: 'int'

    Returns
    -------
    cluster_labels_sorted: 'numpy.ndarray', (N_voxel, 1)
    cluster_centroids_sorted:'numpy.ndarray',

    See-also
    --------
    cluster_scalar, cluster_raw
    """

    if X_train.shape[0]==1 or len(X_train.shape)==1:
            cluster_labels, cluster_centroid = self.cluster_scalar(X_train, num_clusters)
    elif X_train.shape[0]>1 and X_train.shape[0]<=self.num_voxels:
        cluster_labels, cluster_centroid = self.cluster_raw(X_train, num_clusters)
    else:
        print("Something wrong with the dimension of data while clustering:", sys.exc_info()[0])
        raise
    return cluster_labels, cluster_centroid

# %%
@register_method
def cluster_scalar(self, X_train, no_clusters):
    """kmean clustering of scalara data.
    Sorts the cluster such that cluser 1 always corresponds with
        the one with highest absolute mean.

    Parameters
    ----------
    X_train: 'numpy.ndarray', (N=1, N_voxels)
    no_clusters: 'int'

    Returns
    -------
    cluster_labels_sorted: 'numpy.ndarray', (N_voxel, 1)
    cluster_centroids_sorted:'numpy.ndarray',
    """

    from sklearn.cluster import KMeans
#    assert len(X_train.shape) == 1, \
#            print('This fucntion is to cluster scalar values for each voxel')
#    assert np.nan not in X_train, \
#            print('Data contain nan')
    X_train = X_train.reshape(-1, 1)
    kmeans = KMeans(n_clusters=no_clusters, random_state=0).fit(X_train)
    kmeans_labels_ = kmeans.labels_
    kmeans_centroids = kmeans.cluster_centers_

    cluster_labels_sorted, cluster_centroids_sorted = \
        sort_cluster(kmeans_labels_, kmeans_centroids)

    return cluster_labels_sorted, cluster_centroids_sorted


# %%
@register_method
def cluster_raw(self, X_train, no_clusters):
    """kmean clustering of time-series data.
    Sorts the cluster such that cluser 1 always corresponds with
        the one with highest absolute mean.

    Parameters
    ----------
    X_train: 'numpy.ndarray', (N_time_steps, N_voxels)
    no_clusters: 'int'

    Returns
    -------
    cluster_labels_sorted: 'numpy.ndarray', (N_voxel, 1)
    cluster_centroids_sorted:'numpy.ndarray', (N_time_steps, N_voxels)
    """

    import numpy as np
    from sklearn.cluster import KMeans
    X_train = X_train.T
    if np.sum(np.isnan(X_train)):
        has_nan = True
    else:
        has_nan = False

    if has_nan:
        kmeans_labels_, kmeans_centroids, kmeans_x_hat =\
            kmeans_missing(X_train, no_clusters=no_clusters)
    else:
        kmeans = KMeans(n_clusters=no_clusters, random_state=0).fit(X_train)
        kmeans_labels_ = kmeans.labels_
        kmeans_centroids = kmeans.cluster_centers_

    cluster_labels_sorted, cluster_centroids_sorted = \
        sort_cluster(kmeans_labels_, kmeans_centroids)

    return cluster_labels_sorted, cluster_centroids_sorted

# %%
@register_method
def kmeans_missing(self, xx_, no_clusters, max_iter=30):
    """Perform K-Means clustering on data with missing values.
    Found it in stackoverflow
    Argumentss:
      xx_:            An [n_samples, n_features] array of data to cluster.
      n_clusters:   Number of clusters to form.
      max_iter:     Maximum number of EM iterations to perform.

    Returns:
      labels:       An [n_samples] vector of integer labels.
      centroids:    An [n_clusters, n_features] array of cluster centroids.
      x_hat:        Copy of xx_ with the missing values filled in.
    """

    # dependencies
    from sklearn.cluster import KMeans
    import numpy as np


    # Initialize missing values to their column means
    prev_centroids = []  #just added tp remove warning that says they are used before being define
    prev_labels = [] #just added tp remove warning that says they are used before being define

    missing = ~np.isfinite(xx_)
    mu_ = np.nanmean(xx_, 0, keepdims=1)
    x_hat = np.where(missing, mu_, xx_)

    for cc_ in np.arange(max_iter):
        if cc_ > 0:
            # initialize KMeans with the previous set of centroids. this is much
            # faster and makes it easier to check convergence (since labels
            # won't be permuted on every iteration), but might be more prone to
            # getting stuck in local minima.
            cls = KMeans(no_clusters, init=prev_centroids)
        else:
            # do multiple random initializations in parallel
            cls = KMeans(no_clusters, n_jobs=-1)

        # perform clustering on the filled-in data
        labels = cls.fit_predict(x_hat)
        centroids = cls.cluster_centers_

        # fill in the missing values based on their cluster centroids
        x_hat[missing] = centroids[labels][missing]

        # when the labels have stopped changing then we have converged
        if cc_ > 0 and np.all(labels == prev_labels):
            break

        prev_labels = labels
        prev_centroids = cls.cluster_centers_

    return labels, centroids, x_hat

# %%
@register_method
def sort_cluster(cluster_labels, cluster_centroids):
    """sorts the cluster numbers,
    such that cluster 1 always correspond with centroid with highest mean absolute value.

    Parameters
    ----------
    cluster_labels:
    cluster_centroids:

    Returns
    -------
    cluster_labels_out:
    clusters_centroids_out:
    """
    import numpy as np
    cent_mean = np.mean(cluster_centroids, axis=1)
    cent_mean_arg_sorted = np.argsort(cent_mean)
    cent_mean_arg_sorted = cent_mean_arg_sorted[::-1]
    cent_mean_arg_sorted_SORTED = np.argsort(cent_mean_arg_sorted)

    list_cluster_labels = list(cluster_labels)

    list_cluster_labels_out = \
        [cent_mean_arg_sorted_SORTED[x] for x in list_cluster_labels]
    cluster_labels_out = np.array(list_cluster_labels_out)
    clusters_centroids_out = cluster_centroids[cent_mean_arg_sorted, :]
    return cluster_labels_out, clusters_centroids_out

# %%
@register_method
def kmean_it(self, cluster_no):
    """a wrapper for sklearn.cluster.KMeans
    sorts the clusters, assigns cluster labels to bbox non-zero cells

    Parameters
    ----------
    cluster_no: 'int'

    Returns
    -------
    bbox_cat: 'numpy.ndarray', (e1, e2, e3)
    cluster_labels_sorted:  'numpy.ndarray'
    cluster_centroids_sorted:  'numpy.ndarray'
    """
    from sklearn.cluster import KMeans
    import numpy as np
    # clustering
    mask_bbox = self.mask
    X = self.data_normalised
    kmeans = KMeans(n_clusters=cluster_no, random_state=0).fit(X)
    cluster_labels_sorted, cluster_centroids_sorted = \
        self.sort_cluster(kmeans.labels_, kmeans.cluster_centers_)
    bbox_cat = np.int8(np.zeros(np.shape(mask_bbox)))-1
    bbox_cat[mask_bbox == 1] = cluster_labels_sorted
    return bbox_cat, cluster_labels_sorted, cluster_centroids_sorted

# %%
@register_method
def cluster_hierarchial(self, signal='raw', num_clusters=2, if_save_plot=False):
    """Hieararchical clustering
    First 2 cluster over all data,
    choose all voxels corresponding to bigger centroid
    Then 2 clusters over these voxels.

    Parameters
    ----------
    signal: {'raw', 'mean', 'slope', 'slope'Segments', 'mean_segments'}
    num_clusters: int
        default=2
    if_save_plot: 'bool'
        default=False

    Returns
    -------
        cluster_labels2: 'list' of 'int'
        cluster_centroid2: 'numpy.ndarray'

    Notes
    -----
    Incomplete for 'mean', 'slope', 'slope'Segments', 'mean_segments'
    """
    import numpy as np

    if signal == 'raw':
        x_train = self.data
        x_train_label = 'RAW_hierarchical'
        cluster_labels, cluster_centroid = \
            self.cluster_raw(x_train, num_clusters)
        ###
        mask_bbox = self.bbox_mask
        # hieararchical clustering
        target_cluster = 0  # biggest values in sorted clusters
        x_new = x_train[:, cluster_labels == target_cluster]
        self.data_hierarchical = x_new
        bbox_new_temp = np.int8(np.zeros(np.shape(mask_bbox)))-1
        bbox_new = np.int8(np.zeros(np.shape(mask_bbox)))

        bbox_new_temp[mask_bbox == 1] = cluster_labels
        bbox_new[bbox_new_temp == target_cluster] = 1
        self.bbox_mask_hierarchical = bbox_new
        cluster_labels2, cluster_centroid2 = \
            self.cluster_raw(x_new, num_clusters)

        if if_save_plot:
            self.save_clusters(x_new, x_train_label,
                                cluster_labels2, cluster_centroid2)
            self.plot_clusters(x_new, x_train_label,
                                cluster_labels2, cluster_centroid2,
                                if_hierarchical=True)

    return cluster_labels2, cluster_centroid2
