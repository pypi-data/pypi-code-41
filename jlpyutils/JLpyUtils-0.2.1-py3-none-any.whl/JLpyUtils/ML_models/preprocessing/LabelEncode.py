class categorical_features():
    """
    LabelEncode non-numeric categorical features. Unlike in sklearns default encoder, this class ensures missing values can be handled when transforming an arbitrary dataset.
    Arguments:
    ---------
        verbose: int. Default: 0. higher implies more prints
    """
    def __init__(self, verbose = 0):
        self.verbose = verbose
        
    def fit(self,
            X, categorical_headers ):
        """
        Fit the LabelEncoder to the categorical_features
        Arguments:
        ----------
            X: pandas X with the features of interest
            categorical_headers: list of headers within the dataframe which are categorical
        """
        import sklearn.preprocessing
        import pandas as pd

        X = X.copy()
        
        #fetch the non-numeric categorical headers which will be encoded
        LabelEncode_headers = [header for header in categorical_headers if pd.api.types.is_numeric_dtype(X[header])==False and header in categorical_headers]
        if self.verbose>=1: 
            print("LabelEncode_headers:\n", LabelEncode_headers)

        #build label encoder
        self.LabelEncoder_dict = {}
        for header in LabelEncode_headers:
            
            #fill missing values
            X[header] = X[header].fillna('missing_value')
            
            # fetch unique values
            # ensure 'missing_value' is encoded so that the LabelEncoders can encode test sets
            uniques = list(X[header].sort_values().unique())+['missing_value']
            
            #fit the encoder
            self.LabelEncoder_dict[header] = sklearn.preprocessing.LabelEncoder()
            self.LabelEncoder_dict[header].fit(uniques)
    
    def transform(self, X):
        """
        Transform the X dataset passed. If the dataset contains a value which the encoder has not previously seen, it will assume that value is a NaN/missing_value.
        """
        import numpy as np
        import warnings
        
        X = X.copy()
        for header in self.LabelEncoder_dict.keys():
            warnings.filterwarnings('ignore')
            
            #fill na as "missing_value"
            X[header] = X[header].fillna('missing_value')
            
            #check if all unique values are contained in the encodings
            #if not assume they are 'missing_value'
            for unique in X[header].unique():
                if unique not in list(self.LabelEncoder_dict[header].classes_):
                    X[header][X[header]==unique] = 'missing_value'

            X[header] = self.LabelEncoder_dict[header].transform(X[header])
            
            #fill back in nan values
            nan_encoding = self.LabelEncoder_dict[header].transform(['missing_value'])[0]
            X[header][X[header]==nan_encoding] = np.nan

            warnings.filterwarnings('default')

        return X