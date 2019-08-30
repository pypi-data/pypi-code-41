import pandas as pd
import logging
#from sklearn.decomposition.pca import PCA
from sklearn.decomposition import IncrementalPCA

from auger_ml.preprocessors.base import BasePreprocessor


class SparsePreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(SparsePreprocessor, self).__init__(
            params=params,
            params_keys=['thresh_sparse', 'n_comp_frac']
        )
        self._thresh_sparse = params.get('thresh_sparse', 0.95)
        self._n_comp_frac = params.get('n_comp_frac', 0.2)

    def fit(self, df):
        super(SparsePreprocessor, self).fit(df)

        self._cols = []
        self._pca = None
        #print(df.dtypes)
        for c in df.select_dtypes(include=['float64', 'float32', 'float', 'float16']).columns:
            #print(c)
            if df[c].value_counts().max() > len(df) * self._thresh_sparse:
                self._cols.append(c)

        # TODO: replace PCA with self-written method
        n_comp = int(len(self._cols) * self._n_comp_frac)
        logging.info("SparsePreprocessor n_comp: %s"%n_comp)
        if n_comp > 1:
            self._pca = IncrementalPCA(n_comp)
            self._pca.fit(df[self._cols])

    def transform(self, df):
        super(SparsePreprocessor, self).transform(df)

        if self._pca is not None:
            df_pca = pd.DataFrame(self._pca.transform(df[self._cols]),
                                  columns=["pca_" + str(i) for i in range(self._pca.n_components)],
                                  index = df.index)
            df = pd.concat([df, df_pca], axis=1, copy=False)
            df.drop(self._cols, axis=1, inplace=True)

        return df
