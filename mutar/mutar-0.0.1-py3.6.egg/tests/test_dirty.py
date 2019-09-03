import pytest
import numpy as np

from sklearn.datasets import load_iris
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_allclose

from mutar import Dirty


@pytest.fixture
def data():
    return load_iris(return_X_y=True)


def test_dirty(data):
    est = Dirty(alpha=0.1, beta=0.1)

    X, y = data
    X = [X, X]
    y = [y, y]
    est.fit(X, y)
    est.fit(*data)
    assert hasattr(est, 'is_fitted_')

    # assert_array_equal(y_pred, np.ones(X.shape[0], dtype=np.int64))
