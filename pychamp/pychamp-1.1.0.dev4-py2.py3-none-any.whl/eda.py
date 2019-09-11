"""
Date : 2019-09-05
Author: Sagar Paudel
Description : This is a utility module which handles data types and missing values.
"""

import numpy as np
import pandas as pd


class DtypeHandler(object):
    def __init__(self, mapping=None, include=None, exclude=None):
        if mapping is None:
            raise Exception("You must specify mappling dictionary!!")

        if type(mapping) != dict:
            raise Exception("mapping must be dictionary type!!")

        if include is not None and type(include) != list:
            raise Exception("include must be list type!!")

        if exclude is not None and type(exclude) != list:
            raise Exception("exclude must be list type!!")

        self.data_types = ["int", "float", "object",
                           "category", "date", "datetime"]

        self.mapping = mapping
        self.include = include
        self.exclude = exclude

    def fit_transform(self, df):
        if self.include is not None:
            not_matched_cols = set(self.include) - set(df.columns)
            if len(not_matched_cols) > 0:
                temp = ",".join(not_matched_cols)
                raise Exception("{} columns in include not matched with source!!".format(temp))

            self.operational_cols = self.include
        elif self.exclude is not None:
            not_matched_cols = set(self.exclude) - set(df.columns)
            if len(not_matched_cols) > 0:
                temp = ",".join(not_matched_cols)
                raise Exception("{} columns in exclude not matched with source!!".format(temp))

            self.operational_cols = [col for col in df.columns
                                     if col not in self.exclude]

        not_matched_cols = set(self.mapping.keys()) - set(self.operational_cols)
        not_matched_dtypes = [dty for dty in self.mapping.values()
                              if dty not in self.data_types]

        if len(not_matched_cols) > 0:
            not_matched_cols = ",".join(not_matched_cols)
            raise Exception("{} columns don't match with source!!".format(not_matched_cols))

        if len(not_matched_dtypes) > 0:
            not_matched_dtypes = ",".join(not_matched_dtypes)
            raise Exception("{} dtypes not supported!!".format(not_matched_dtypes))

        self.affeced_cols = []
        self.unaffected_cols = []
        for col, data_type in self.mapping.items():
            if data_type == "int":
                if df[col].dtype != np.int:
                    try:
                        df[col] = df[col].astype("int")
                        self.affeced_cols.append(col)
                    except Exception:
                        self.unaffected_cols.append(col)
                        raise Exception("Failed to convert {} into {} data type!!".format(col, data_type))
                else:
                    self.unaffected_cols.append(col)

            elif data_type == "float":
                if df[col].dtype != np.float:
                    try:
                        df[col] = df[col].astype("float")
                        self.affeced_cols.append(col)
                    except Exception:
                        self.unaffected_cols.append(col)
                        raise Exception("Failed to convert {} into {} data type!!".format(col, data_type))
                else:
                    self.unaffected_cols.append(col)
            elif data_type == "category":
                if not pd.api.types.is_categorical_dtype(df[col]):
                    try:
                        df[col] = df[col].astype("category")
                        self.affeced_cols.append(col)
                    except Exception as e:
                        self.unaffected_cols.append(col)
                        raise Exception(e)
                else:
                    self.unaffected_cols.append(col)

            elif data_type == "date" or data_type == "datetime":
                if df[col].dtype != np.datetime64:
                    try:
                        df[col] = pd.to_datetime(df[col])
                        self.affeced_cols.append(col)
                    except Exception as e:
                        self.unaffected_cols.append(col)
                        raise Exception("Failed to convert {} into {} data type!!".format(col, data_type))
                else:
                    self.unaffected_cols.append(col)

        return df


class MissingHandler(object):
    def __init__(self, include=None, exclude=None, threshold=0.05):
        self.include = include
        self.exclude = exclude
        self.threshold = threshold
        self.impute_technique = ["mean", "mode", "median"]

    def fit(self, df):
        self.df = df
        size = self.df.shape[0]
        self.missing = self.df.isnull().sum().reset_index()
        self.missing.columns = ["labels", "missing"]
        self.missing["missing"] = self.missing["missing"].apply(
            lambda x: round(x/size, 3))
        self.missing = self.missing[self.missing["missing"] > 0.0]
        self.missing["droppable"] = self.missing["missing"].apply(
            lambda x: 1 if x > self.threshold else 0)

    def transform(self, impute_mapping=None, drop_cols=None):
        self.impute_mapping = impute_mapping
        self.drop_cols = drop_cols
        RETURN = False

        if self.impute_mapping is not None and type(self.impute_mapping) != dict:
            raise Exception("impute_technique must be dictionary type!!")

        if self.drop_cols is not None and type(self.drop_cols) != list:
            raise Exception("drop_cols must be list type!!")

        if type(self.impute_mapping) == dict:
            impute_tech = self.impute_mapping.values()
            impute_cols = self.impute_mapping.keys()

        not_matched_impute = set(impute_tech) - set(self.impute_technique)
        not_matched_cols = set(impute_cols) - set(self.df.columns)

        if len(not_matched_cols) > 0:
            not_matched_cols = ",".join(not_matched_cols)
            raise Exception("{} columns not found!!".format(not_matched_cols))

        if len(not_matched_impute) > 0:
            not_matched_impute = ",".join(not_matched_impute)
            raise Exception(("{} impute technique not found.\n"
                             "Only mean, median and mode are supported")
                            .format(not_matched_impute))

        if type(self.drop_cols) == list:
            not_matched_cols = [col for col in self.drop_cols
                                if col not in self.df.columns]

        if len(not_matched_cols) > 0:
            not_matched_cols = ",".join(not_matched_cols)
            raise Exception("{} columns not found!!".format(not_matched_cols))

        if self.drop_cols is not None and type(self.drop_cols) == list:
            print("I am here")
            temp = self.df.drop(columns=self.drop_cols, axis=1)
            RETURN = True

        if self.impute_mapping is not None and type(self.impute_mapping) == dict:
            if RETURN:
                self.__imputer(temp, self.impute_mapping)
            else:
                temp = self.__imputer(self.df.copy(), self.impute_mapping)
            RETURN = True

        if RETURN:
            return temp

    def __imputer(self, df, mapping):
        for col, impute in mapping.items():
            if impute == "mean":
                df[col].fillna(df[col].mean(), inplace=True)
            elif impute == "mode":
                df[col].fillna(df[col].mode(), inplace=True)
            elif impute == "median":
                df[col].fillna(df[col].median(), inplace=True)
        return df


if __name__ == "__main__":
    # Data Type Handler
    df = pd.DataFrame({"A": [1, 3, 4], "B": ["a", "b", "d"], "C": [0.1, 0.2, 0.4]})
    obj = DtypeHandler(mapping={"A": "int", "B": "category"}, include=["A", "B"])
    temp = obj.fit_transform(df)
    obj.affeced_cols
    obj.unaffected_cols

    # Missing Values Handler
    df = pd.DataFrame({"A": [1, 3, 4], "B": ["a", "b", "d"], "C": [0.1, np.NaN, 0.4]})
    obj = MissingHandler()
    obj.fit(df)
    temp = obj.transform(impute_mapping={"C": "mean"}, )
    temp.head()
