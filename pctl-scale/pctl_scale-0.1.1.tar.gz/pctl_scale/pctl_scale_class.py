from sklearn.base import BaseEstimator, TransformerMixin
from .pctl_scale_func import (
    saturate_upper_to_one, saturate_lower_to_zero, check_ignore,
    inverse)
import numpy as np


class PercentileScaler(BaseEstimator, TransformerMixin):
    def __init__(self, upper=.95, lower=.05, naignore=[0], naimpute=0):
        self.upper = upper
        self.lower = lower
        self.naignore = naignore
        self.naimpute = naimpute

    def fit(self, X, y=None):
        """compute and store scaling parameters"""
        # ignore certains values
        if self.naignore:
            tmp = [e for e in X if not check_ignore(e, self.naignore)]
        else:
            tmp = X

        # compute upper and lower pctl values
        self.pctl_lower, self.pctl_upper = np.percentile(
            np.array(tmp), q=(self.lower * 100, self.upper * 100))

        return self

    def transform(self, X, copy=None):
        """Scale data"""
        # memorize all ineligible values
        x_ = np.array(X)
        idxmiss = np.array([check_ignore(e, self.naignore) for e in x_])
        idxexist = np.logical_not(idxmiss)

        # scale x=[vd,vu] to y=[d,u]
        to1 = (x_[idxexist] - self.pctl_lower)
        to1 /= (self.pctl_upper - self.pctl_lower)
        y = self.lower + self.upper * to1

        # saturate upper values to [u,1]
        idxu = y > self.upper
        y[idxu] = saturate_upper_to_one(y[idxu], self.upper)

        # fit lower values to [0,d]
        idxd = y < self.lower
        y[idxd] = saturate_lower_to_zero(y[idxd], self.lower)

        # impute missing
        z = np.empty(shape=x_.shape)
        z[idxexist] = y
        z[idxmiss] = self.naimpute

        # done
        return z

    def inverse_transform(self, X, y=None):
        return inverse(
            X, self.lower, self.upper, self.pctl_lower, self.pctl_upper)
