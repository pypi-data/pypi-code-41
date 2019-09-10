from sklearn.base import BaseEstimator, TransformerMixin


class NumericalImputer(BaseEstimator, TransformerMixin):
    """Numerical data missing imputer"""

    def __init__(self, variables = None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables

    def fit(self, X, y=None):
        self.imputer_dict_ = {}

        for feature in self.variables:
            self.imputer_dict_[feature] = X[feature].mean()
        return self

    def transform(self, X):
        X = X.copy()

        for feature in self.variables:
            X[feature].fillna(self.imputer_dict_[feature], inplace=True)
        return X


class ZeroImputer(BaseEstimator, TransformerMixin):
    """Numerical data missing imputer"""

    def __init__(self, variables = None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables

    def fit(self, X, y=None):
        self.imputer = 0
        return self

    def transform(self, X):
        X = X.copy()

        for feature in self.variables:
            X[feature].fillna(self.imputer, inplace=True)
        return X