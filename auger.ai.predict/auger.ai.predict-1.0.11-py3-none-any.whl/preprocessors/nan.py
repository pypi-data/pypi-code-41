import logging

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

from sklearn.impute import SimpleImputer

from pandas.api.types import is_numeric_dtype

from auger_ml.preprocessors.base import BasePreprocessor


class NanPreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(NanPreprocessor, self).__init__(
            params=params,
            params_keys=['thresh_col', 'thresh_row']
        )

        self._thresh_col = params.get('thresh_col', 0.95)
        self._thresh_row = params.get('thresh_row', 0.05)

    def fit(self, df):
        super(NanPreprocessor, self).fit(df)

        self._cols_to_drop = [c for c in df.columns if df[c].isna().mean() > self._thresh_col]
        self._numeric_cols = [c for c in df.columns if is_numeric_dtype(df[c]) and c not in self._cols_to_drop]

        self._imputer = IterativeImputer().fit(df[self._numeric_cols])

    def transform(self, df):
        super(NanPreprocessor, self).transform(df)

        df.drop(self._cols_to_drop, axis=1, inplace=True)

        df[self._numeric_cols] = self._imputer.transform(df[self._numeric_cols])

        return df
