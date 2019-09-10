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


def power_iteration(A: Matrix, n_rep: int) -> Matrix:
    # Ideally choose a random vector
    # To decrease the chance that our vector
    # Is orthogonal to the eigenvector
    b_k = np.random.rand(A.shape[1])
    for _ in range(n_rep):
        # calculate the matrix-by-vector product Ab
        b_k1 = np.dot(A, b_k)
        # calculate the norm
        b_k1_norm = np.linalg.norm(b_k1)
        # re normalize the vector
        b_k = b_k1 / b_k1_norm
    return b_k


def uniform_folding_ratio_coeff(d: int) -> float:
    if d % 2 == 0:
        p = d // 2
        r = pow(4, p) / np.pi
        for i in range(p):
            r = r * (1 + i) / (p + i)
        return r
    p = (d - 1) // 2
    r = d / pow(4, p)
    for i in range(p):
        r = r * (p + 1 + i) / (1 + i)
    return r


def uniform_folding_ratio(d: int) -> float:
    return 1 - (1 + 2 / d) * (uniform_folding_ratio_coeff(d) / (d + 1))**2


def hftu_target(X: Matrix, u: Matrix, c: float) -> float:
    HX = np.dot(X, u.reshape(-1, 1)) + c
    return HX.mean()**2 - np.abs(HX).mean()**2


def hftu_level(n: int, d: int, alpha: float) -> float:
    std = 0.9 / (d * np.sqrt(n))
    mu = 1 - 1.8 * np.log(d) / (d * np.sqrt(n))
    g = ss.norm(loc=mu, scale=std)
    return g.ppf(alpha)


def hftu(X: Matrix):
    def __constraint__fun(z: Matrix) -> float:
        beta = z[:-1].flatten()
        return np.dot(beta, beta) - 1

    def __constraint__jac(z: Matrix) -> float:
        t = 2 * z
        t[-1] = 0.
        return t

    def __obj_fun(y: Matrix):
        return hftu_target(X, y[:-1], y[-1])

    const = {"type": "eq",
             "fun": __constraint__fun,
             "jac": __constraint__jac}

    cov = np.cov(X.T)
    dim = int(cov.shape[0])
    trace = np.trace(cov)
    # u_init = np.zeros(X.shape[1])
    # u_init[X.var(0).argmax()] = 1
    u = power_iteration(cov, 15)
    u0 = -np.dot(X.mean(0), u)
    x0 = np.hstack((u.flatten(), u0))

    opt_results = opt.minimize(lambda u: hftu_target(X, u[:-1], u[-1]),
                               x0=x0,
                               constraints=(const),
                               method='SLSQP',
                               options={'maxiter': 100})

    folding_ratio = 1 + opt_results.fun / trace
    folding_statistics = folding_ratio / uniform_folding_ratio(dim)

    normal_vector = opt_results.x[:-1] / np.linalg.norm(opt_results.x[:-1])
    intercept = opt_results.x[-1]
    return folding_statistics, normal_vector, intercept


def hftu_approx(X: Matrix):
    def __obj_fun(u: Matrix, c: float):
        return hftu_target(X, u, c)

    cov = np.cov(X.T)
    dim = int(cov.shape[0])
    trace = np.trace(cov)
    u_init = np.zeros(X.shape[1])
    u_init[X.var(0).argmax()] = 1
    # u = power_iteration(cov, 15)
    _, u = lobpcg(A=cov,
                  X=u_init.reshape(-1, 1),
                  largest=True,
                  maxiter=15)
    # u0 = -np.dot(X.mean(0), u)
    # x0 = np.hstack((u.flatten(), u0))

    # opt_results = opt.minimize(lambda u: hftu_target(X, u[:-1], u[-1]),
    #                            x0=x0,
    #                            constraints=(const),
    #                            method='SLSQP',
    #                            options={'maxiter': 100})
    x0 = -np.dot(X.mean(0), u)
    opt_results = opt.minimize(lambda u0: __obj_fun(u, u0),
                               x0=x0[0],
                               method='Nelder-Mead')
    # opt_results = opt.minimize_scalar(lambda u0: hftu_target(X, u, u0),
    #                                   method='brent',
    #                                   bracket=(u0)
    #                                   )

    folding_ratio = 1 + opt_results.fun / trace
    folding_statistics = folding_ratio / uniform_folding_ratio(dim)

    normal_vector = opt_results.x[:-1] / np.linalg.norm(opt_results.x[:-1])
    intercept = opt_results.x[-1]
    return folding_statistics, normal_vector, intercept


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
            # k_means = KMeans(n_clusters=n_clusters,
            #                  init=self.cluster_centers_,
            #                  n_init=1,
            #                  **self._extra_kmeans_args)
            # self.labels_ = k_means.fit_predict(self._data)
            # self.cluster_centers_ = k_means.cluster_centers_

            # # add number of iterations
            # self.n_iter_ += k_means.n_iter_
            self._global_kmeans(n_clusters)

            # Try to split accoridng to the desired method
            for cluster in range(n_clusters):
                self._score_and_split(cluster)

            new_cluster = (n_clusters < self.n_clusters_)

    # def _split_with_hftu(self, index):
    #     """
    #     Test to split or not a cluster according to the
    #     Hyperplane Folding Test of Unimodality (HFTU)
    #     """
    #     n, d = self._data[index].shape
    #     phi, u, c = hftu(self._data[index])
    #     multimodal = False
    #     if phi < hftu_level(n, d, self.alpha):
    #         multimodal = True
    #     return multimodal, u, c
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

    # def _score_and_split(self, cluster):
    #     """
    #     Score the cluster. The split is performed according to the score
    #     """
    #     index = (self.labels_ == cluster)
    #     if sum(index) >= self.min_pts:

    #         split, u, c = self._split_with_hftu(index)

    #         if split:
    #             # get the prediction (points above or below the hyperplane)
    #             # print("shape:", self._data[index].shape)
    #             prediction = self._data[index] @ u.reshape(-1, 1) + c
    #             # print("prediction:", prediction)
    #             # get the mean of each parts
    #             pred_index = prediction.flatten() >= 0

    #             # check if it actually splits well the data
    #             if pred_index.all() or (~pred_index).all():
    #                 return

    #             try:
    #                 init_center_p = self._data[index][pred_index].mean(0)
    #                 init_center_n = self._data[index][~pred_index].mean(0)
    #                 # run k-means starting from these two centers (not anymore)
    #                 # labels, centers = self._split_center(cluster, np.vstack(
    #                 # (init_center_p, init_center_n)), index=index)
    #                 # print("KMEANS:", centers)
    #                 # print(init_center_p, init_center_n)
    #                 # print(labels - (1 - pred_index))
    #                 # validate the split
    #                 # self._accept_split(cluster, index, labels, centers)
    #                 # MAYBE WE CAN AVOID TO REUSE K-MEANS
    #                 # IT WORKS!
    #                 self._accept_split(cluster,
    #                                    index,
    #                                    1 - pred_index,
    #                                    np.vstack((init_center_n, init_center_p)))
    #             except BaseException as err:
    #                 print(err)
    #                 labels, centers = self._split_pca(cluster, index)
    #                 self._accept_split(cluster, index, labels, centers)
