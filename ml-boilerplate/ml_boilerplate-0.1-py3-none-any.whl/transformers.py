import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class ColumnSelector(BaseEstimator, TransformerMixin):
    """Short summary."""

    def __init__(self, columns):
        """Short summary."""
        self.columns = columns

    def fit(self, X, y=None):
        """Short summary."""
        return self

    def transform(self, X):
        """Short summary."""
        assert isinstance(X, pd.DataFrame)

        try:
            return X[self.columns]
        except KeyError:
            cols_error = list(set(self.columns) - set(X.columns))
            raise KeyError(
                "The DataFrame does not include the columns: %s" % cols_error)


class TypeSelector(BaseEstimator, TransformerMixin):
    """Short summary."""

    def __init__(self, dtype):
        """Short summary."""
        self.dtype = dtype

    def fit(self, X, y=None):
        """Short summary."""
        return self

    def transform(self, X):
        """Short summary."""
        assert isinstance(X, pd.DataFrame)
        return X.select_dtypes(include=[self.dtype])
