"""
Implements relational neural gas (RNG) as described in the paper

Hammer, B. & Hasenfuss, A. (2007). Relational Neural Gas.
Proceedings of the 30th Annual German Conference on AI (KI).
URL: https://www.researchgate.net/publication/221562215_Relational_Neural_Gas

Copyright (C) 2019
Benjamin Paaßen
AG Machine Learning
Bielefeld University

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.base import BaseEstimator, ClusterMixin

__author__ = 'Benjamin Paaßen'
__copyright__ = 'Copyright 2019, Benjamin Paaßen'
__license__ = 'GPLv3'
__version__ = '1.0.0'
__maintainer__ = 'Benjamin Paaßen'
__email__  = 'bpaassen@techfak.uni-bielefeld.de'

_CUTOFF = np.log(10) * 3
_LAMBDA_FINAL = 0.5 / _CUTOFF
_ERR_CUTOFF = 1E-5
_COEFF_CUTOFF = 1E-3

class RNG(BaseEstimator, ClusterMixin):
    """ A relational neural gas clustering model, which assigns data to
    clusters depending on their proximity to learned prototypes, which are
    given as convex combinations of data points. Due to its purely distance-
    based definition, relational neural gas can cope with any kind of distance
    matrix input, as long as the input distance matrix is symmetric and zero on
    the diagonal.

    Attributes:
    K:        The number of prototypes to be learned.
    T:        The number of epochs in training. Defaults to 50.
    lambda_0: The initial neighborhood range, i.e. the rank on which the
              prototype influence on a datapoint degrades to 1/e. Defaults
              to K / 2.
    _Alpha:   A K x m matrix sparse matrix storing the convex coefficients
              that describe the prototypes.
    _z:       A K x 1 vector storing the normalization constants
              -0.5*_Alpha[k, :] * D² * _Alpha[k, :].T for all k.
    _loss:    The relational neural gas loss during the last training run
    """
    def __init__(self, K, T = 50, lambda_0 = None):
        self.K = K
        self.T = T
        if(lambda_0 is None):
            self.lambda_0 = self.K / 2
        else:
            self.lambda_0 = lambda_0

    def fit(self, D, y = None, is_squared = False):
        """ Fits a relational neural gas model to the given distance matrix.

        In more detail, the training consists of three steps, which are
        alternated.

        1. We compute the squared data-to-prototype distances via the
           relational distance formula:
           d(w_k, x_i)² = _Alpha[k, :] * D[:, i]² - _z[k]
        2. We compute the ranks of each prototype for each data point, i.e.
           r_i(k) = |{l | d(w_l, x_i)² < d(w_k, x_i)² }|
        3. We update the coefficients _Alpha via the formula
           _Alpha[k, i] = exp(-r_i(k) / lambda) / sum_l exp(-r_i(l) / lambda)

        Note that lambda is decreased in each iteration until the assignment is
        strict as for k-means.

        Args:
        D: A m x m matrix of pairwise distances, which need to be symmetric
           and zero on the diagonal.
        y: This parameter is ignored and is only here for API consistency.
        is_squared: If set to true, this method assumes D is already a matrix
                    of squared distances. Otherwise, the distances get squared.
        """
        # check symmetry and zero diagonal
        if(len(D.shape) != 2):
            raise ValueError('Input is not a matrix!')
        if(D.shape[0] != D.shape[1]):
            raise ValueError('Input matrix is not square!')
        if(np.sum(np.square(D - D.T)) > 1E-3):
            raise ValueError('Input matrix is not symmetric!')
        if(np.sum(np.square(np.diag(D))) > 1E-3):
            raise ValueError('The diagonal of the input matrix is not zero!')
        if(not is_squared):
            D = np.square(D)
        m = D.shape[0]
        # initialize the convex coefficients randomly
        self._Alpha = np.random.rand(self.K, m)
        self._Alpha /= np.expand_dims(np.sum(self._Alpha, axis=1), 1)
        # initialize the vector of normalization constants
        self._z = np.zeros(self.K)
        # initialize the ranking matrix
        R = np.zeros((self.K, m), dtype=int)
        # initialize lambda
        lambd = self.lambda_0
        dampen = np.power(_LAMBDA_FINAL / self.lambda_0, 1. / (self.T-1))
        # then start the main loop
        self._loss = []
        for t in range(self.T):
            # re-compute the normalization constants for each prototype
            for k in range(self.K):
                self._z[k] = -0.5 * np.dot(self._Alpha[k, :], np.dot(D, self._Alpha[k, :].T))
            # re-compute the prototype-to-datapoint distances;
            # add the normalization via broadcasting
            Dp = np.dot(self._Alpha, D) + np.expand_dims(self._z, 1)
            # compute the training loss
            loss = np.sum(Dp * self._Alpha)
            if(self._loss and self._loss[-1] - loss < _ERR_CUTOFF):
                # if we do not reduce the loss meaningfully anymore,
                # break off training early
                break
            self._loss.append(loss)
            # re-compute the ranks by sorting the distances
            idxs  = np.argsort(Dp, axis=0)
            for i in range(m):
                # note that we need to 'invert' the argsort result to get the
                # prototype ranks
                R[idxs[:,i], i] = np.arange(self.K)
            # compute the influence for each rank, cutting off the computation
            # for too large ranks
            K_max = min(self.K, int(np.ceil(_CUTOFF * lambd)))
            h = np.zeros(self.K)
            h[:K_max] = np.exp(-np.arange(K_max) / lambd)
            # re-compute the convex coefficients
            self._Alpha = h[R]
            # re-normalize
            self._Alpha /= np.expand_dims(np.sum(self._Alpha, axis=1), 1)
            # adapt lambda
            lambd *= dampen
        # post-process alpha to remove very small values
        self._Alpha[self._Alpha < _COEFF_CUTOFF] = 0.
        # re-normalize
        self._Alpha /= np.expand_dims(np.sum(self._Alpha, axis=1), 1)
        # make alpha sparse
        self._Alpha = csr_matrix(self._Alpha)
        # re-compute the normalization constants for each prototype
        for k in range(self.K):
            self._z[k] = -0.5 * self._Alpha[k, :].dot((self._Alpha[k, :].dot(D)).T)
        return self

    def predict(self, D, is_squared = False):
        """ Predicts the cluster assignments for the data represented by the
        given test-to-training distance matrix. Each datapoint will be assigned
        to the closest prototype.

        Args:
        D: A n x m matrix of distances from the test to the training
           datapoints.
        is_squared: If set to true, this method assumes D is already a matrix
                    of squared distances. Otherwise, the distances get squared.

        Return:
        y: a n-dimensional vector containing the cluster indices for each
           datapoint.
        """
        # check the dimensionality
        n = D.shape[0]
        m = D.shape[1]
        if(m != self._Alpha.shape[1]):
            raise ValueError('Expected %d columns in the input distance matrix, but got %d!' % (self._Alpha.shape[1], m))
        if(not is_squared):
            D = np.square(D)
        # compute the datapoint-to-prototype distances;
        # add the normalization via broadcasting
        Dp = self._Alpha.dot(D.T) + np.expand_dims(self._z, 1)
        # get the closest prototype for each datapoint
        y = np.argmin(Dp, axis=0)
        return y
