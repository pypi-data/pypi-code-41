from auger_ml.preprocessors.base import BasePreprocessor

import pandas as pd
import numpy as np
import logging


class DateTimePreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(DateTimePreprocessor, self).__init__(
            params=params,
            params_keys=['datetime_cols', 'discover_fields']
        )
        self._initial_datetime_cols = params.get('datetime_cols', [])
        self._discover_fields = params.get('discover_fields', True)

    @staticmethod
    def _extract_features(df, col):
        df["cyclic__" + col.name + "__minute"] = col.dt.minute
        df["cyclic__" + col.name + "__hour"] = col.dt.hour
        df["cyclic__" + col.name + "__mday"] = col.dt.day
        df["cat__" + col.name + "__wday"] = col.dt.weekday
        df["cyclic__" + col.name + "__yday"] = col.dt.dayofyear 
        df["cat__" + col.name + "__month"] = col.dt.month
        df["cyclic__" + col.name + "__week"] = col.dt.week
        df["cat__" + col.name + "__year"] = col.dt.year
        # return pd.DataFrame({"cyclic__" + col.name + "__minute": col.dt.minute,
        #                      "cyclic__" + col.name + "__hour": col.dt.hour,
        #                      "cyclic__" + col.name + "__mday": col.dt.day,
        #                      "cat__" + col.name + "__wday": col.dt.weekday,
        #                      "cyclic__" + col.name + "__yday": col.dt.dayofyear,
        #                      "cat__" + col.name + "__month": col.dt.month,
        #                      "cat__" + col.name + "__year": col.dt.year})

    def fit(self, df):
        super(DateTimePreprocessor, self).fit(df)

        self._datetime_cols = self._initial_datetime_cols
        if self._discover_fields:
            self._datetime_cols.extend(df.select_dtypes(include=[np.datetime64]).columns.tolist())

        for col in self._datetime_cols:
            if col not in df.columns:
                self._datetime_cols.remove(col)

        self._datetime_cols = list(set(self._datetime_cols))
        
    def transform(self, df):
        super(DateTimePreprocessor, self).transform(df)

        for c in self._datetime_cols:
            #df = pd.concat([df, self._extract_features(df[c])], axis=1).drop(c, axis=1)
            if df[c].dtype != 'datetime64[ns]':
                if df[c].dtype == 'object':
                    value = pd.to_datetime(df[c])
                else: 
                    value = pd.to_datetime(df[c], unit='s') #TODO : support ns

                self._extract_features(df, value)
            else:    
                self._extract_features(df, df[c])

            df.drop(c, axis=1, inplace=True)

        return df
