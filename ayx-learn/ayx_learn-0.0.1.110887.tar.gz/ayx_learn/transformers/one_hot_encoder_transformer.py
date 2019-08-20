# Copyright (C) 2019 Alteryx, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""One-hot encoder that fits both Hamilton and Code Free ML paradigm."""

from typing import List

from ayx_learn.utils import DataScienceException
from ayx_learn.utils.validate import validate_list_of_str

import pandas as pd

import sklearn.base


class UnexpectedLevelsError(DataScienceException):
    """Exception for unexpected level in One Hot Encoding."""

    def __init__(self, message, errors):
        self.levels, self.column_name = errors
        super().__init__(message)


class OneHotEncoderTransformer(sklearn.base.TransformerMixin):
    """Used to perform one-hot-encoding on a dataframe."""

    def __init__(
        self: object,
        factor_feature_col_names: List[str] = list(),
        categorical_labels: dict = {},
        inplace: bool = False,
        sep: str = "_",
        handle_unknown="ignore",
        **kwargs,
    ):
        """Constructor.

        Parameters
        ----------
        factor_feature_col_names : list (of `str`s), default []
            List of features that should be encoded.

        categorical_labels : dict (column name -> list (of categories)), default {}
            Dictionary mapping column names to an iterable of categories expected in that column.
            Each key in categorical labels must be an element of `factor_feature_col_names`.
            Any omitted key (element of `factor_feature_col_names` not present as a key)
            will have its categories determined automatically.
            That is, the categories will be taken from the appropriate column passed into the `fit` method.

        inplace : bool, default False
            Where possible, operate on data (transform) in place.

        sep : str, default "_"
            When encoding, separator between column name and category to use.

        handle_unknown: str or dict
            Valid options are "ignore" and "error".
            If a string, the value is taken for all columns.
            If a dict, the keys should be column names and values should "ignore" or "error".
                The default for missing column names is "ignore".

            Dictates how to handle an level present in .transform but not in .fit.
            "ignore" encodes it to 0 for all columns.
            "error" raises an error.

        **kwargs
            additional arguments to mop up

        """
        self.factor_feature_col_names = factor_feature_col_names
        # TODO categorical_labels isn't used by Hamilton at the moment
        # Should add getters and setters for it in future, but no tests
        # exist currently.
        self.categorical_labels = categorical_labels
        self._factor_map = {}
        self.inplace = inplace
        self.sep = sep
        self.handle_unknown = handle_unknown

    @property
    def handle_unknown(self):
        """Getter for handling unknown category."""
        return self.__handle_unknown

    @handle_unknown.setter
    def handle_unknown(self, value):
        if isinstance(value, str):
            if value in ["ignore", "error"]:
                self.__handle_unknown = value
            else:
                raise ValueError("handle_unknown must be 'ignore' or 'error'")
        elif isinstance(value, dict):
            for _, val in value.items():
                if val not in ["ignore", "error"]:
                    raise ValueError(
                        "values in handle_unknown must be 'ignore' or 'error'"
                    )
            self.__handle_unknown = value
        else:
            raise TypeError("handle_unknown must be a string or dict")

    @property
    def sep(self):
        """Getter for column prefix-category separator."""
        return self.__sep

    @sep.setter
    def sep(self, value):
        """Setter for column prefix-category separator."""
        if isinstance(value, str):
            self.__sep = value
        else:
            raise TypeError("sep must be string")

    @property
    def factor_feature_col_names(self):
        """Getter for factor feature column names."""
        return self.__factor_feature_col_names

    @factor_feature_col_names.setter
    def factor_feature_col_names(self, value):
        """Setter for factor feature column names."""
        if isinstance(value, list):
            validate_list_of_str(value)
            self.__factor_feature_col_names = value
        else:
            raise TypeError("factor_feature_col_names must be list of strings")

    @property
    def categorical_labels(self):
        """Getter for categorical labels."""
        return self.__categorical_labels

    @categorical_labels.setter
    def categorical_labels(self, value):
        """Setter for categorical labels."""
        if isinstance(value, dict):
            self.__categorical_labels = value
        else:
            raise TypeError("categorical_labels should be a dictionary")

    @property
    def inplace(self):
        """Getter for inplace."""
        return self.__inplace

    @inplace.setter
    def inplace(self, value):
        """Setter for inplace."""
        if isinstance(value, bool):
            self.__inplace = value
        else:
            raise TypeError("inplace must be boolean")

    def fit(self, x, y=None, **kwargs):
        """Fit the transform."""
        for colname in self.factor_feature_col_names:
            if self.categorical_labels.get(colname):
                self._factor_map[colname] = list(self.categorical_labels[colname])
            else:
                column = x[colname].astype("category")
                self._factor_map[colname] = list(column.cat.categories)
        return self

    def transform(self, x, y=None, inplace=None, **kwargs):
        """One-hot encode the columns from factor_feature_col_names.

        NOTE: this will re-order columns.  The ordering priority is:
        1. Encoded dummies of columns in "factor_feature_names", alphabetically
        2. Alphabetically, all other columns.
        """
        if inplace is None:
            inplace = self.inplace
        df = x if inplace else x.copy()
        df = df[self._order_columns(df.columns)]
        for colname, categories in self._factor_map.items():
            self._handle_unexpected_categories(df=df, colname=colname)
            df[colname] = df[colname].astype("category")
            df[colname].cat.set_categories(categories, inplace=True)
        df = pd.get_dummies(df, prefix_sep=self.sep)
        df.columns = OneHotEncoderTransformer._get_unique_col_names(df.columns)
        return df

    def _handle_unexpected_categories(self, df, colname):
        categories = self._factor_map[colname]
        if isinstance(self.handle_unknown, str):
            unknown_handling = self.handle_unknown
        else:
            if self.handle_unknown.get(colname):
                unknown_handling = self.handle_unknown.get(colname)
            else:
                unknown_handling = "ignore"
        if unknown_handling == "error":
            expected_cats = set(categories)
            actual_cats = set(df[colname])
            if not actual_cats.issubset(expected_cats):
                unexpected_cats = actual_cats.difference(expected_cats)
                raise UnexpectedLevelsError("", (unexpected_cats, colname))

    @staticmethod
    def _get_unique_col_names(column_names, sep="_"):
        """Modify the new column names so that they are unique."""
        new_column_names = []
        for column_name in column_names:
            if column_name in new_column_names:
                base_name = column_name
                col_idx = 2
                while base_name + sep + str(col_idx) in new_column_names:
                    col_idx += 1
                new_column_names.append(base_name + sep + str(col_idx))
            else:
                new_column_names.append(column_name)
        return new_column_names

    def get_link(self, column_names: List[str]):
        """Get the link between original column names and encoded ones."""
        # use list of tuples instead of dicts, which wouldn't allow name collisions
        ordered_column_names = self._order_columns(column_names)
        link = []
        for name in ordered_column_names:
            if self._factor_map.get(name):
                for category in self._factor_map[name]:
                    link.append((name + self.sep + str(category), name))
            else:
                link.append((name, name))
        encoded_names, original_names = zip(*link)
        encoded_names = OneHotEncoderTransformer._get_unique_col_names(encoded_names)
        return dict(zip(encoded_names, original_names))

    def _order_columns(self, column_names):
        """Order the columns.

        Crucial for consistency of link.
        """
        factor_colnames = sorted(
            [name for name in column_names if name in self._factor_map.keys()]
        )
        nonfactor_colnames = sorted(
            [name for name in column_names if name not in factor_colnames]
        )
        return factor_colnames + nonfactor_colnames
