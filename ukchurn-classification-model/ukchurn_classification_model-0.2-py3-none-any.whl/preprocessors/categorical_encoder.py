import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CategoricalEncoder(BaseEstimator, TransformerMixin):
    """Convert strings to numbers categorical encoder"""

    def __init__(self, variables = None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables

    def fit(self, X, y=None):
        temp = pd.concat([X, y], axis=1)
        temp.columns = list(X.columns) + ['target']

        self.encoder_dict_ = {}

        for feature in self.variables:
            t = temp.groupby([feature])['target'].mean().sort_values(
                ascending=True).index
            self.encoder_dict_[feature] = {k:i for i, k in enumerate(t, 0)}

        return self

    def transform(self, X):
        # encode labels
        X = X.copy()
        for feature in self.variables:
            X[feature] = X[feature].map(self.encoder_dict_[feature])

        # check if the transformer introduces NaN values
        if X[self.variables].isnull().any().any():
            null_counts = X[self.variables].isnull().any()
            vars_ = {key: value for (key, value) in null_counts.items()
                     if value is True}
            raise ValueError(
                f'Categorical encoder has introduced NaN when '
                f'transforming categorical variables: {vars_.keys()}')

        return X