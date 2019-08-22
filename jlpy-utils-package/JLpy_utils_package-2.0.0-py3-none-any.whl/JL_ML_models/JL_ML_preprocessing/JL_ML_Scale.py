import pandas as pd
import numpy as np

import sklearn.preprocessing

def continuous_features(df, headers_dict, Scaler = sklearn.preprocessing.StandardScaler()):
    """
    Scale the "continuous_features" specified in headers_dict and contained in the df.
    Arguments:
        df: pandas dataframe
        headers_dict: dictionary containing the key "continuous_features" with a list of continuous feature headers contained in df
        Scaler: sklearn.preprocessing....: defaults: sklearn.preprocessing.StandardScaler()
            - Object specifing the scaler operation the data will be fit and transformed to.
    Returns:
        df, Scaler
    """
    warnings.filterwarnings('ignore')

    df = df.copy()

    Scaler.fit(df[headers_dict['continuous_features']])

    df[headers_dict['continuous_features']] = Scaler.transform(df[headers_dict['continuous_features']])

    warnings.filterwarnings('default')

    return df, Scaler

def fetch_Scalers_dict():
    """
    fetch dictionary containing typical scalers used for transforming continuous data
    """
    Scalers_dict = {'StandardScaler':sklearn.preprocessing.StandardScaler(),
                    'MinMaxScaler':sklearn.preprocessing.MinMaxScaler(),
                    'RobustScaler':sklearn.preprocessing.RobustScaler()}
    return Scalers_dict