"""
Date : 2019-09-05
Author: Sagar Paudel
Description : This is a utility module which elimiates features using backward
              elimination technique.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant


def singularity(X):
    dropped_features = []
    # Singularity causes Runtime error so eliminating it first
    df_unique = X.nunique().reset_index()
    for col, unq in zip(df_unique.iloc[:, 0], df_unique.iloc[:, 1]):
        if unq == 1:
            dropped_features.append(col)

    return dropped_features


class BackwardElmination(object):
    def __init__(self, sl=0.05):
        self.sl = sl

    def fit(self, X=None, y=None):
        try:
            if X is None or y is None:
                raise Exception("Please specify X and y!!")

            # Removing Singularity first
            self.dropped_features = singularity(X)

            if len(self.dropped_features) > 0:
                X.drop(columns=self.dropped_features, axis=1, inplace=True)

            while True:
                model = sm.OLS(y, X).fit()
                p_values = dict(model.pvalues)
                p_values = {k: v for k, v in p_values.items() if v > self.sl}
                if p_values != {}:
                    max_key = max(p_values, key=p_values.get)
                    self.dropped_features.append(max_key)
                    X.drop(max_key, axis=1, inplace=True)
                else:
                    break

            self.selected_features = [col for col in X.columns
                                      if col not in self.dropped_features]

        except Exception as e:
            raise Exception(e)


class VIF(object):
    """
    The Variance Inflation Factor (VIF) is a measure of colinearity
    among predictor variables within a multiple regression.
    It is calculated by taking the the ratio of the variance of all a given
    model's betas divide by the variane of a single beta if it were fit alone.
    """

    def fit(self, df):
        '''
        Parameters
        ----------
        df : dataframe, (nobs, k_vars)
            design matrix with all explanatory variables, as for example used in
            regression.

        Returns
        -------
        vif : Series
            variance inflation factors
        '''

        try:
            # Getting only numeric columns
            df = df._get_numeric_data()

            # Removing Singularity first
            self.dropped_features = singularity(df)

            if len(self.dropped_features) > 0:
                df.drop(columns=self.dropped_features, axis=1, inplace=True)

            df = add_constant(df)
            self.vifs = pd.Series(
                [1 / (1. - OLS(df[col].values,
                               df.loc[:, df.columns != col].values
                               ).fit().rsquared) for col in df],
                index=df.columns,
                name='VIF')

        except Exception as e:
            raise Exception(e)


class FeaturesImportance(object):
    def __init__(self, threshold=0.05):
        self.threshold = threshold

    def fit(self, X=None, y=None):
        try:
            if X is None or y is None:
                raise Exception("Please specify X and y!!")

            clf = RandomForestClassifier(n_estimators=100)
            clf.fit(X.values, y.values)

            df = pd.DataFrame({
                'FEATURE': X.columns,
                'IMPORTANCE': np.round(clf.feature_importances_, 3)})
            df.sort_values('IMPORTANCE', ascending=False, inplace=True)

            self.selected_features = df[df["IMPORTANCE"] > self.threshold]["FEATURE"].tolist()
            self.dropped_features = df[df["IMPORTANCE"] <= self.threshold]["FEATURE"].tolist()
            self.feature_importances = df

        except Exception as e:
            raise Exception(e)
