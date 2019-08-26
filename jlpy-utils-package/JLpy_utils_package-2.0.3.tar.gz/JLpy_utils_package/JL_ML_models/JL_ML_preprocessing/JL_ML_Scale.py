
import sklearn.preprocessing

def continuous_features(df, continuous_headers, Scaler = sklearn.preprocessing.StandardScaler()):
    """
    Scale the "continuous_features" specified in headers_dict and contained in the df.
    Arguments:
        df: pandas dataframe
        continuous_headers: list containing the header for the continuous features of interest
        Scaler: sklearn.preprocessing....: defaults: sklearn.preprocessing.StandardScaler()
            - Object specifing the scaler operation the data will be fit and transformed to.
    Returns:
        df, Scaler
    """
    import warnings
    
    warnings.filterwarnings('ignore')

    df = df.copy()

    Scaler.fit(df[continuous_headers])

    df[continuous_headers] = Scaler.transform(df[continuous_headers])

    warnings.filterwarnings('default')

    return df, Scaler

def default_Scalers_dict():
    """
    fetch dictionary containing typical scalers used for transforming continuous data
    """
    import sklearn.preprocessing
    
    Scalers_dict = {'StandardScaler':sklearn.preprocessing.StandardScaler(),
                    'MinMaxScaler':sklearn.preprocessing.MinMaxScaler(),
                    'RobustScaler':sklearn.preprocessing.RobustScaler()}
    return Scalers_dict