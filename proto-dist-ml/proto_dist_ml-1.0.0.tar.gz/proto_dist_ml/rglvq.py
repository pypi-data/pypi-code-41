"""
Implements relational generalized learning vector quantization (RGLVQ) as
described in the paper

Hammer, B., Hofmann, D., Schleif, F., & Zhu, X. (2014). Learning vector
quantization for (dis-)similarities. Neurocomputing, 131, 43-51.
doi:10.1016/j.neucom.2013.05.054.
URL: http://www.techfak.uni-bielefeld.de/~fschleif/pdf/nc_diss_2014.pdf

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
from scipy.optimize import minimize
from scipy.sparse import csr_matrix
from sklearn.base import BaseEstimator, ClassifierMixin
import proto_dist_ml.rng as rng

__author__ = 'Benjamin Paaßen'
__copyright__ = 'Copyright 2019, Benjamin Paaßen'
__license__ = 'GPLv3'
__version__ = '1.0.0'
__maintainer__ = 'Benjamin Paaßen'
__email__  = 'bpaassen@techfak.uni-bielefeld.de'

_COEFF_CUTOFF = 1E-3
_ERR_CUTOFF = 1E-5

class RGLVQ(BaseEstimator, ClassifierMixin):
    """ A relational generalized learning vector quantization model,
    which classifies data by assigning the label of the closest prototype.
    Prototypes are learned points, which are represented as convex combinations
    of the input data. Due to its purely distance-based definition, relational
    generalized vector quantization can deal with pure distance matrix input,
    as long as the input distance matrix is Euclidean (i.e. if and only if
    the corresponding similarity matrix via double centering is positive
    semi-definite). If that is not the case, negative distances may occur
    which can hurt the model during training.

    Attributes:
    K:        The number of prototypes per class to be learned.
    T:        The maximum number of BFGS optimization steps during training.
              Defaults to 100.
    phi:      A squashing function to post-process each error term. Defaults
              to the identity.
    phi_grad: The gradient function corresponding to phi
    _Alpha:   A K * num_labels x m matrix sparse matrix storing the convex
              coefficients that describe the prototypes.
    _z:       A K * num_labels x 1 vector storing the normalization constants
              -0.5*_Alpha[k, :] * D² * _Alpha[k, :].T for all k.
    _y:       A K * num_labels dimensional vector storing the label for each
              prototype.
    _loss:    The GLVQ loss after L-BFGS optimization.
    """
    def __init__(self, K, T = 100, phi = None, phi_grad = None):
        self.K = K
        self.T = T
        if(phi is None):
            self.phi = lambda mus : mus
            self.phi_grad = lambda mus : np.ones_like(mus)
        else:
            self.phi = phi

    def fit(self, D, y, is_squared = False):
        """ Fits a relational generalized learning vector quantization model to
        the given distance matrix.

        In more detail, the training optimizes the GLVQ loss function, which
        is given as

        sum_i self.phi[(d_i^+ - d_i^-) / (d_i^+ + d_i^-)]

        where i is the data point index, d_i^+ is the distance of i to the
        closest prototype with the same label and d_i^- is the distance of the
        closest prototype with another label. Note that i is correctly
        classified if and only if d_i^+ < d_i^-, such that the loss is a
        'soft' version of the classification error.

        We optimize this loss via L-BFGS as implemented in scipy. Our learnble
        parameters are the convex coefficients _Alpha. We can optimize these
        because the distance between data point i and prototype k can be
        re-written as follows:

        d_ik^2 = _Alpha[k, :] * D[:, i]^2 - 0.5 * _Alpha[k, :] * D^2 * _Alpha[k, :].T,

        yielding the gradient

        grad(d_ik^2) = D[i, :]^2 - _Alpha[k, :] * D^2

        Note that each gradient computation is quadratic in the number of
        nonzero entries of _Alpha[k, :], which may be expensive.

        Args:
        D: A m x m matrix of pairwise distances. Note that we have no
           preconditions for this matrix. It may even be asymmetric.
        y: A m dimensional label vector for the data points.
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
        # set up the model arrays
        unique_labels = np.unique(y)
        L = len(unique_labels)
        self._Alpha = np.zeros((self.K * L, m))
        self._y = np.zeros(self.K * L)
        if(self.K == 1):
            # if we have only a single data point per class, initialize alpha
            # extremely sparse, namely as 1 for the data point which is closest
            # to the class mean
            for l in range(L):
                self._y[l] = unique_labels[l]
                inClass_l  = np.where(unique_labels[l] == y)[0]
                D_l = D[inClass_l, :][:, inClass_l]
                idx = inClass_l[np.argmin(np.sum(D_l, axis=0))]
                self._Alpha[l, idx] = 1.
        else:
            # otherwise, we initialize Alpha via class-wise relational neural
            # gas
            for l in range(L):
                self._y[l*self.K:(l+1)*self.K] = unique_labels[l]
                inClass_l  = np.where(unique_labels[l] == y)[0]
                D_l   = D[inClass_l, :][:, inClass_l]
                rng_l = rng.RNG(self.K)
                rng_l.fit(D_l, is_squared = True)
                self._Alpha[l*self.K:(l+1)*self.K, :][:, inClass_l] = rng_l._Alpha.toarray()
            del rng_l
        del inClass_l
        del D_l

        # set up objective function
        obj = lambda Alpha : self._loss_and_grad(Alpha, D, y, unique_labels)

        # set up optimizer options
        options = { 'ftol' : _ERR_CUTOFF, 'maxiter' : self.T }

        # perform optimization
        res = minimize(obj, self._Alpha.ravel(), method='L-BFGS-B', jac = True, options = options)

        # check optimization result
        if(res.x is None):
            raise ValueError('Optimization returned none and failed with message: %s!' % str(res.message))
        self._Alpha = res.x.reshape(self._Alpha.shape)
        self._loss  = res.fun

        # post-process alpha to ensure convexity
        for k in range(len(self._Alpha)):
            # ensure that at least one alpha entry for each prototype is
            # positive
            if(np.max(self._Alpha[k, :]) < _COEFF_CUTOFF):
                self._Alpha[k, :] -= np.max(self._Alpha[k, :]) - 2 * _COEFF_CUTOFF
            # set small values to zero
            self._Alpha[k, self._Alpha[k, :] < _COEFF_CUTOFF] = 0.
            # re-normalize to sum 1
            self._Alpha[k, :] /= np.sum(self._Alpha[k, :])
        # make alpha sparse
        self._Alpha = csr_matrix(self._Alpha)
        # compute normalization constants
        self._z = np.zeros(self._Alpha.shape[0])
        for k in range(self._Alpha.shape[0]):
            self._z[k] = -0.5 * self._Alpha[k, :].dot((self._Alpha[k, :].dot(D)).T)

        return self

    def _loss_and_grad(self, Alpha, D, y, unique_labels):
        """ Computes the GLVQ loss and gradient for the current convex
        coefficients Alpha.

        Args:
        Alpha: The convex coefficients representing the prototypes.
        D:     The matrix of squared pairwise distances between training data
               points.
        y:     The labels of all training data points.
        unique_labels: The unique labels in y.

        Returns:
        loss: The current GLVQ loss.
        Grad: The current gradient of the GLVQ loss with respect to Alpha.
        """
        # reshape Alpha back into a matrix if its flattened for optimization
        is_flat = False
        if(len(Alpha.shape) == 1):
            is_flat = True
            Alpha = Alpha.reshape(self._Alpha.shape)

        # pre-process Alpha to ensure convexity and compute intermediate
        # values that we need for further processing
        z = np.zeros(len(Alpha))
        A = np.zeros_like(Alpha)
        for k in range(len(Alpha)):
            # ensure that at least one alpha entry for each prototype is
            # positive
            if(np.max(Alpha[k, :]) < _COEFF_CUTOFF):
                Alpha[k, :] -= np.max(Alpha[k, :]) - _COEFF_CUTOFF
            # set small values to zero
            Alpha[k, Alpha[k, :] < _COEFF_CUTOFF / Alpha.shape[1]] = 0.
            # re-normalize to sum 1
            Alpha[k, :] /= np.sum(Alpha[k, :])
            # get nonzero coefficients
            nzs_k = np.where(Alpha[k, :])[0]
            A[k, :] = np.dot(Alpha[k, nzs_k], D[nzs_k, :])
            z[k] = -0.5 * np.dot(A[k, nzs_k], Alpha[k, nzs_k].T)

        # find the closest correct and the closest wrong prototype for all
        # data points
        closest_plus  = np.zeros(len(D), dtype=int)
        closest_minus = np.zeros(len(D), dtype=int)
        dp = np.zeros(len(D))
        dm = np.zeros(len(D))
        for l in range(len(unique_labels)):
            # get data points in class l and prototypes in and out of class l.
            inClass_l = np.where(y == unique_labels[l])[0]
            inClass_w_l = np.where(self._y == unique_labels[l])[0]
            outClass_w_l = np.where(self._y != unique_labels[l])[0]
            # compute the distances to all prototypes in the same class.
            Dp = A[inClass_w_l, :][:, inClass_l] + np.expand_dims(z[inClass_w_l], 1)
            # find the closest prototype in the same class
            idxs = np.argmin(Dp, axis=0)
            closest_plus[inClass_l] = inClass_w_l[idxs]
            dp[inClass_l] = Dp[idxs, np.arange(len(inClass_l))]
            # compute the distances to all prototypes in a different class.
            Dm = A[outClass_w_l, :][:, inClass_l] + np.expand_dims(z[outClass_w_l], 1)
            # find the closest prototype in different class
            idxs = np.argmin(Dm, axis=0)
            closest_minus[inClass_l] = outClass_w_l[idxs]
            dm[inClass_l] = Dm[idxs, np.arange(len(inClass_l))]
        # compute the raw loss terms 
        mus = (dp - dm) / (dp + dm + 1E-5)
        # compute the loss
        loss = np.sum(self.phi(mus))
        # compute the gradient for all loss terms
        mus_grad = self.phi_grad(mus) * 2 / np.square(dp + dm + 1E-5)
        # compute the gradient with respect to Alpha
        Grad = np.zeros_like(Alpha)
        for k in range(len(Alpha)):
            # get all data points in the receptive field of w_k
            receptive_field_plus_k = closest_plus == k
            receptive_field_minus_k = closest_minus == k
            # get the gradient of the error contributions in the receptive
            # field
            grads_plus  = mus_grad[receptive_field_plus_k] * dm[receptive_field_plus_k]
            grads_minus = mus_grad[receptive_field_minus_k] * dp[receptive_field_minus_k]
            # compute the gradient for Alpha[k, :]
            Grad[k, :] = np.dot(grads_plus, D[receptive_field_plus_k, :]) - \
                         np.dot(grads_minus, D[receptive_field_minus_k, :]) - \
                         (np.sum(grads_plus) - np.sum(grads_minus)) * A[k, :]
        # return the results
        if(is_flat):
            Grad = Grad.flatten()
        return loss, Grad

    def predict(self, D, is_squared = False):
        """ Predicts the labels for the data represented by the
        given test-to-training distance matrix. Each datapoint will be assigned
        to the closest prototype.

        Args:
        D: A n x m matrix of distances from the test to the training
           datapoints.
        is_squared: If set to true, this method assumes D is already a matrix
                    of squared distances. Otherwise, the distances get squared.

        Return:
        y: a n-dimensional vector containing the predicted labels for each
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
        Dp = self._Alpha.dot(D.T) - np.expand_dims(self._z, 1)
        # get the closest prototype for each datapoint
        closest = np.argmin(Dp, axis=0)
        # return the label of the respective prototype
        return self._y[closest]
