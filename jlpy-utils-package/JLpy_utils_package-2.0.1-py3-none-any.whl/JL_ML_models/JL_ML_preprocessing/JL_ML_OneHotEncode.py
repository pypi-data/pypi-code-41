import numpy as np
import pandas as pd
import sklearn, sklearn.preprocessing

def transform(df, headers_dict, OneHotEncoder, return_format):
    warnings.filterwarnings('ignore')
    
    df = df.copy()
    headers_dict = headers_dict.copy()
    
    c =0
    for header in headers_dict['categorical_features']:
        #ensure integer data type
        df[header] = df[header].astype(int)
        
        #if a value in the df does not exist in the encoder, update it with the most frequent value from the fit_value_counts
        for unique in df[header].unique():
            if unique not in OneHotEncoder.categories_[c]:
                value = int(OneHotEncoder.fit_value_counts[c]['value'][OneHotEncoder.fit_value_counts[c]['count'] == np.max(OneHotEncoder.fit_value_counts[c]['count'])])
                df[header][df[header]==unique] = value
        c+=1
    
    OneHotEncodings = OneHotEncoder.transform(df[headers_dict['categorical_features']])
    
    df = df.drop(columns = headers_dict['categorical_features']).reset_index(drop=True)
    
    if return_format == 'DataFrame':
        OneHotEncodings = pd.DataFrame(OneHotEncodings.toarray(),
                            columns = list(OneHotEncoder.get_feature_names()))
        df_or_npArray = pd.concat((df, OneHotEncodings),axis=1)
    if return_format == 'npArray':
        headers_dict['headers_after_OneHot'] = list(df.columns) + list(OneHotEncoder.get_feature_names())
        df_or_npArray = np.concatenate((np.array(df), OneHotEncodings.toarray()), axis = 1)
    
    warnings.filterwarnings('default')
    return df_or_npArray, headers_dict
    
def categorical_features(df, headers_dict, return_format = 'DataFrame'):
    """
    OneHot encode each categorical feature. This function assumes an impute transforma (fill na) has been performed prior to encoding such that the encoder does not need to be able to transform datasets containng NaN values

    Arugments:
        df: Pandas df
        headers_dict: dictionary containing the key "categorical_features" with a list of categorical feature columns/headers in the dataframe
        return_format: string, default = 'DataFrame'
            - if 'DataFrame': the first element of the return statement will be a pandas dataframe with the one hot encodings integrated. This can consume a huge amount of memory for large arrays with many encodings
            - if 'npArray': the first element of the return statement will be a numpy array. The headers_dict will be updated to included "headers_after_OneHot", which is a list of headers associated with the numpy array.

    """
    df = df.copy()
    headers_dict = headers_dict.copy()

    categories = []
    for header in headers_dict['categorical_features']:
        df[header] = df[header].astype(int)
        categories.append([idx for idx in range(df[header].unique().min(), df[header].unique().max()+1)])

    OneHotEncoder = sklearn.preprocessing.OneHotEncoder(categories = categories)
    OneHotEncoder.fit(df[headers_dict['categorical_features']])

    df_or_npArray, headers_dict = OneHotEncoder_transform(df, headers_dict, OneHotEncoder, return_format)

    #add fit value counts to use if transforming unseen dataset with values not found in original data
    OneHotEncoder.fit_value_counts = []
    for header in headers_dict['categorical_features']:
        counts = df[header].value_counts().reset_index()
        counts.columns = ['value', 'count']
        OneHotEncoder.fit_value_counts.append(counts)

    return df_or_npArray, headers_dict, OneHotEncoder