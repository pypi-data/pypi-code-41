__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'
__date__ = '2019_04_25'

import numpy
import sklearn
from sklearn.decomposition import PCA
from scipy import stats
from sklearn.preprocessing import MinMaxScaler


def get_pca_transform(
        X: numpy.ndarray,
        number_of_components: int = 2,
        normalization: str = None
) -> sklearn.decomposition.PCA:
    """
    The :func:`get_pca_transform` returns the PCA transform on this data, using the Sci-Kit learn PCA
    functionalities.
    Parameters
    ------------
    X: `numpy.ndarray`, required
        The data which is a two-dimensional matrix, in which each row is a feature-vector.
    number_of_components: `int`, optional (default=2)
        The number of components in the PCA.
    normalization: `str`, optional (default=None)
        The normalization type, which is either None which means no normalization, or `minmax` or `zscore`.
    Returns
    ------------
    pca: `sklearn.decomposition.PCA`
        The PCA for this data.
    """
    if normalization == 'minmax':
        scaler = MinMaxScaler(copy=True, feature_range=(0, 1))
        scaler.fit(X)
        scaler.transform(X)
    elif normalization == 'zcsore':
        X = stats.zscore(X, axis=1, ddof=0)
        if not numpy.sum(numpy.isnan(X)) == 0:
            raise Exception("Not a number observed. Please choose a different normalization or inspect the data.")
    elif normalization is None:
        pass
    else:
        raise ValueError

    pca = PCA(n_components=number_of_components)
    pca.fit(X)

    return pca


def apply_pca(X: numpy.ndarray, pca: sklearn.decomposition.PCA):
    """
    To apply PCA, this method can be used.
    Parameters
    ----------
    X: `numpy.ndarray`, required
        This is the matrix, however, note that it is user's (caller's) responsibility to assure
        that if there was any normalization involved in the computation of the PCA, the same
        normalization should have already been applied to this parameter before applying this function.
        Otherwise, the output will be unreliable.
    pca: `sklearn.decomposition.PCA`, required
        The PCA to be applied
    Returns
    ----------
    output: `numpy.ndarray`
        The output matrix after applying the pCA
    """
    output = pca.transform(X)
    return output