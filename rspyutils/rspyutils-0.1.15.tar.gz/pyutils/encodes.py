# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zhanglanhui
homepage recommender:ffm
"""
import json
import time, datetime
import numpy as np
import pandas as pd
from pyutils import dates
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler


class FeaturesEncode(object):
    def __init__(self):
        pass

    def get_df_cols(self, df: pd.DataFrame):
        return set(df.columns.tolist())

    def get_nan_transform(self, df: pd.DataFrame, cols: list, method="default", type="category"):
        """
        缺省值处理，当前只支持默认值，后面需要加上其他处理方式
        :param cols:
        :param method:
        :param type:
        :return:
        """
        if method == "default":
            if type == "category":
                print("df.info()",df.info())
                print(cols)
                df_tmp = df.astype({x: "object" for x in cols})
                df_tmp.fillna({x: "0" for x in cols}, inplace=True)
                return df_tmp
            elif type == "numerical":
                df_tmp = df.astype({x: "float32" for x in cols})
                df_tmp.fillna({x: 0 for x in cols}, inplace=True)
                return df_tmp
        else:
            pass

    def get_scaler_transform(self, df: pd.DataFrame, cols: list, method="normalize"):
        if not cols:
            return df
        if method == "normalize":
            for v in cols:
                norm = MinMaxScaler().fit_transform(df[v].values.astype(np.float).reshape(-1, 1))
                df[v] = norm.astype(np.float).reshape(-1)
        elif method == "standard":
            for v in cols:
                norm = StandardScaler().fit_transform(df[v].values.astype(np.float).reshape(-1, 1))
                df[v] = norm.astype(np.float).reshape(-1)
        else:
            raise Exception("get_scaler_transform method input error!!!")
        return df

    def get_discrete_transform(self, df: pd.DataFrame, cols: dict):
        for v in cols:
            df[v] = np.floor(df[v].values.astype(np.float) * cols[v]).astype(np.int8).reshape(-1)
        df_type = df.astype({x: "object" for x in cols})
        return df_type

    def get_singular_truncation_transform(self, df: pd.DataFrame, cols: list, thr=None, method="min"):
        if not thr or not cols:
            return df
        if method == "min":
            for v in cols:
                df[v] = df[v].apply(lambda x: min(x, thr))
        else:
            for v in cols:
                df[v] = df[v].apply(lambda x: max(x, thr))
        return df

    def get_category_type_transform(self, df: pd.DataFrame, cols: list):
        if not cols:
            return df
        for v in cols:
            if df[v].dtype == 'float64' or df[v].dtype == 'float32':
                df[v] = df[v].apply(lambda x: int(x))
        df.astype({x: "object" for x in cols})
        return df

    # 时间特征处理
    def get_time2category_transform(self, df: pd.DataFrame, cols: list, method="timestamp", dim="day"):
        if not cols:
            return df
        if method == "timestamp":
            if dim == "sec":
                for k in cols:
                    df[k] = df[k].apply(lambda x: dates.str_to_timestamp(x))
            elif dim == "day":
                for k in cols:
                    df[k] = df[k].apply(lambda x: dates.get_date_from_str(x).day)
            elif dim == "month":
                for k in cols:
                    df[k] = df[k].apply(lambda x: dates.get_date_from_str(x).month)
            else:
                raise Exception("get_time2category_transform dim input error!!!")
        elif method == "timediff":
            if dim == "sec":
                for k in cols:
                    df[k] = df[k].apply(lambda x: dates.get_date_diff(start_date=x,
                                                                      end_date=datetime.datetime.now().strftime(
                                                                          '%Y-%m-%d %H:%M:%S')).seconds)
            elif dim == "day":
                for k in cols:
                    df[k] = df[k]. \
                        apply(lambda x: dates.get_date_diff(start_date=x,
                                                            end_date=datetime.datetime.now().strftime(
                                                                '%Y-%m-%d %H:%M:%S')).days)
            elif dim == "month":
                for k in cols:
                    df[k] = df[k].apply(lambda x: int(dates.get_date_diff(start_date=x,
                                                                          end_date=datetime.datetime.now().strftime(
                                                                              '%Y-%m-%d %H:%M:%S')).days) / 30)
            else:
                raise Exception("get_time2category_transform dim input error!!!")
        else:
            raise Exception("get_time2category_transform method input error!!!")
        return df

    # json特征处理
    def get_json2category_transform(self, df: pd.DataFrame, cols: list):
        def func(d):
            try:
                return "|".join(json.loads(d).keys())
            except:
                return ""

        if not cols:
            return df
        for k in cols:
            df[k] = df.apply(lambda x: func(x[k]), axis=1)
        return df

    # 多维特征处理
    def get_vector2category_transform(self, df: pd.DataFrame, cols: list):
        drop_features = []
        category_features_gen = []
        if not cols:
            return []
        df_vector = df
        for v in cols:
            if v in self.get_df_cols(df):
                dfTmp = df_vector[v].str.get_dummies(sep='|')
                dfTmp.rename(columns=lambda x: v + ":" + x, inplace=True)
                df_vector = df_vector.join(dfTmp)
                drop_features.append(v)
                category_features_gen.append(dfTmp.columns.tolist())
        df_vector.drop(drop_features, axis=1, inplace=True)
        return df_vector, category_features_gen

    def get_vector2value_transform(self, df: pd.DataFrame, cols: list):
        drop_features = []
        value_features_gen = []
        if not cols:
            return df, []
        df_vector = df
        for v in cols:
            if v in self.get_df_cols(df):
                val = np.array([str.split(x, "|") for x in df[v].values])
                index = [v + ":" + str(i) for i in range(1, len(val) + 1)]
                dfTmp = pd.DataFrame(val, index=index)
                df_vector = df_vector.join(dfTmp)
                drop_features.append(v)
                value_features_gen.append(dfTmp.columns.tolist())
        df_vector.drop(drop_features, axis=1, inplace=True)
        return df_vector, value_features_gen

    # 构造交叉特征
    def get_cross_transform(self, df: pd.DataFrame, cols: list, vector_col: list):
        def func(df: pd.DataFrame, col1: str, col2: str, vector_col: set):
            v = []
            if col1 in vector_col and col2 in vector_col:
                for x in str.split(df[col1], "|"):
                    for y in str.split(df[col2]):
                        v.append('{}*{}'.format(x, y))
            elif col1 in vector_col:
                for x in str.split(df[col1], "|"):
                    v.append('{}*{}'.format(x, df[col2]))
            elif col2 in vector_col:
                for x in str.split(df[col2], "|"):
                    v.append('{}*{}'.format(df[col1], x))
            else:
                v.append('{}*{}'.format(df[col1], df[col2]))
            return '|'.join(v)

        cross_col = []
        for c in cols:
            df['{}*{}'.format(c[0], c[1])] = df.apply(lambda x: func(x, c[0], c[1], set(vector_col)), axis=1)
            cross_col.append('{}*{}'.format(c[0], c[1]))
        return cross_col

    def gen_features_id_map(self, df: pd.DataFrame, feature_id_dict: dict):
        cols = self.get_df_cols(df)
        cols.remove("lable")
        max_len = max(feature_id_dict.values())
        for c in cols:
            if not feature_id_dict.get(c, None):
                feature_id_dict[c] = max_len
                max_len += 1
