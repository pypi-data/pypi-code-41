"""Docstring."""
import random

import numpy as np
from scipy.stats import randint, uniform
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, cohen_kappa_score,
                             confusion_matrix, f1_score, log_loss,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import (RandomizedSearchCV, cross_val_predict,
                                     cross_val_score, train_test_split)
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

# from sklearn.linear_model import LinearRegression
from .transformers import ColumnSelector, TypeSelector


class TrainLinearReg:
    """
    A short description.

    A bit longer description.

    Args:
        variable (type): description

    Returns:
        type: description

    Raises:
        Exception: description

    """

    def __init__(self, X, y, x_cols, binary_cols, text_cols, category_cols, numerical_cols):
        """docstring."""
        self.X, self.y, self.x_cols = X, y, x_cols
        self.binary_cols = binary_cols
        self.text_cols = text_cols
        self.category_cols = category_cols
        self.numerical_cols = numerical_cols

        self.pipeline = Pipeline([
            ('preprocess_pipeline', self.get_preprocess_pipeline(self.x_cols)),
            ('classifier', XGBClassifier(max_delta_step=1,
                                         objective='binary:logistic',
                                         booster='gbtree',
                                         njobs=1))
        ])

    def get_preprocess_pipeline(self, x_cols, numeric=True, text=True, categorical=True, boolean=True):
        """Docstring."""
        transformer_list = []

        if numeric:
            numeric_features = ("numeric_features", Pipeline([
                ('selector', TypeSelector(np.number)),
                ('imputer', SimpleImputer(strategy="median")),
                ('scaler', StandardScaler())]))
            transformer_list.append(numeric_features)

        if text:
            text_features = ("text_features", Pipeline([
                ('selector', ColumnSelector(columns=self.text_cols)),
                ('vectoriser', TfidfVectorizer(stop_words='english')),
                ('select_features', SelectKBest())]))
            transformer_list.append(text_features)

        if categorical:
            categorical_features = ("categorical_features", Pipeline([
                ('selector', TypeSelector("category")),
                ('one_hot', OneHotEncoder(categories="auto", handle_unknown='ignore')),
                ('imputer', SimpleImputer(strategy="most_frequent")),
                ('select_features', SelectKBest())]))
            transformer_list.append(categorical_features)

        if boolean:
            boolean_features = ("boolean_features", Pipeline([
                ('selector', TypeSelector("bool"))]))
            transformer_list.append(boolean_features)

        return Pipeline([
            ('select_columns', ColumnSelector(columns=x_cols)),
            ('features_union', FeatureUnion(transformer_list=transformer_list))])

    def get_results(y_test, y_pred):
        """Docstring summary."""
        print(f'f1 score of {np.round(f1_score(y_test, y_pred),3)}')
        print(f'recall score of {np.round(recall_score(y_test, y_pred),3)}')
        print(
            f'kappa score of {np.round(cohen_kappa_score(y_test, y_pred),3)}')
        print(
            f'precision score of {np.round(precision_score(y_test, y_pred),3)}')
        print(
            f'accuracy score of {np.round(accuracy_score(y_test, y_pred),3)}')
        print(f'roc_auc score of {np.round(roc_auc_score(y_test, y_pred),3)}')
        print(f'logloss score of {np.round(log_loss(y_test, y_pred),3)}')
        confus_mat = confusion_matrix(y_test, y_pred)
        print(confus_mat)

    def train_model(self):
        """Docstring summary."""
        # Partition data set into training/test split (2 to 1 ratio)
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=1 / 3., random_state=42)
        clf = RandomizedSearchCV(
            self.pipeline, self.linreg_param_grid(), cv=5)
        clf.fit(X_train, y_train)
        params = clf.best_params_
        y_pred = cross_val_predict(clf.set_params(**params).fit(X_train, y_train),
                                   X_test, y_test, cv=5)
        self.get_results(y_test, y_pred)
        scores = cross_val_score(clf.set_params(
            **params), X_test, y_test, cv=3, scoring='f1')
        print(scores)
        print(scores.mean())

    def linreg_param_grid():
        """Docstring summary."""
        return {
            "classifier__max_depth": [i for i in range(1, 15)],
            "classifier__gamma": [0.1 * x for x in range(1, 6)],
            "classifier__n_estimators": randint(1, 1000),
            "classifier__learning_rate": uniform(),
            "classifier__subsample": uniform(),
            "classifier__colsample_bytree": uniform(),
            "preprocess_pipeline__features_union__categorical_features__select_features__k":
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 'all'],
        }


def set_x_random_missing_vals(X):
    """Docstring summary."""
    # Randomly set 500 items as missing values
    random.seed(42)
    num_missing = 500
    indices = [(row, col) for row in range(X.shape[0])
               for col in range(X.shape[1])]
    for row, col in random.sample(indices, num_missing):
        X.iat[row, col] = np.nan
    return X


def get_X_and_y(df, target_column, cols_to_drop, binary_cols,
                categorical_cols, text_cols, numeric_cols):
    """Remove the target column and the phone number."""
    cols_to_drop.append(target_column)
    x_cols = [c for c in df if c not in cols_to_drop]

    X = df[x_cols]

    X[binary_cols] = X[binary_cols].astype("bool")
    X[categorical_cols] = X[categorical_cols].astype("category")
    X[text_cols] = X[text_cols].astype("object")
    X[numeric_cols] = X[numeric_cols].astype("float64")

    y = df[target_column]
    return X, y, x_cols
