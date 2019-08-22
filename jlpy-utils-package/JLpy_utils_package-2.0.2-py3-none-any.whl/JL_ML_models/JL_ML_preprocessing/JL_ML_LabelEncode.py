import numpy as np
import pandas as pd
import sklearn.preprocessing

def transform(df, LabelEncoders):
        
    df = df.copy()
    for header in LabelEncoders.keys():
        warnings.filterwarnings('ignore')

        df[header] = df[header].fillna('missing_value')

        #check if all unique values are contained in the encodings, if not assume they are 'missing_value'
        for unique in df[header].unique():
            if unique not in list(LabelEncoders[header].classes_):
                df[header][df[header]==unique] = 'missing_value'

        df[header] = LabelEncoders[header].transform(df[header])

        nan_encoding = LabelEncoders[header].transform(['missing_value'])[0]
        df[header][df[header]==nan_encoding] = np.nan

        warnings.filterwarnings('default')

    return df

def categorical_features(df, headers_dict, verbose = 0):
    """
    Arguments:
        df: pandas dataframe
        headers_dict: dictionary containing "categorical_features" key with a list of the headers for each categorical feature in the df. numeric categorical features will not be encoded
        verbose: verbosity index.
    """
    df = df.copy()
    headers_dict = headers_dict.copy()

    #fetch the non-numeric categorical headers which will be encoded
    headers_dict['LabelEncodings'] = [header for header in headers_dict['categorical_features'] if pd.api.types.is_numeric_dtype(df[header])==False]
    if verbose>=1: 
        print("headers_dict['LabelEncodings']:\n", headers_dict['LabelEncodings'])

    #build label encoder
    LabelEncoders = {}
    for header in headers_dict['LabelEncodings']:
        LabelEncoders[header] = sklearn.preprocessing.LabelEncoder()

        df[header] = df[header].fillna('missing_value')

        if verbose:
            print(df[header].unique())

        #fetch unique values and ensure 'missing_value' is encoded so that the LabelEncoders can encode test sets
        uniques = list(df[header].sort_values().unique())+['missing_value']
        LabelEncoders[header].fit(uniques)

    #transform the data
    df = LabelEncoder_transform(df, LabelEncoders)

    return df, headers_dict, LabelEncoders