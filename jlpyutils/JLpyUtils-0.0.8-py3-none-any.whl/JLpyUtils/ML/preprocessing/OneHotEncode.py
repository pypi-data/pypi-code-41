
    
class categorical_features():
    
    """
    OneHot encode each categorical feature. This function assumes an impute transforma (fill na) has been performed prior to encoding such that the encoder does not need to be able to transform datasets containng NaN values

    Arugments:
    ----------
       categorical_headers: list of categorical feature columns/headers in the dataframe
        return_format: string, default = 'DataFrame'
            - if 'DataFrame': the transformed data will be returned as a pandas dataframe. This can consume a large amount of memory for large arrays with many encodings
            - if 'npArray': the transformed data will be returned as a numpy array.
    """
    
    def __init__(self, return_format = 'DataFrame', LabelEncoder = None):
        
        import numpy as np
        import pandas as pd
        import sklearn, sklearn.preprocessing
        import warnings

        self.return_format = return_format
        self.LabelEncoder = LabelEncoder
        
    def fit(self, X, categorical_headers):
        """
        Arugments:
        ----------
        X: pandas dataframe of interest
        categorical_headers: list of categorical feature columns/headers in the X dataframe
        """
        import numpy as np
        import pandas as pd
        import sklearn, sklearn.preprocessing
        import warnings
    
        X = X.copy()
        
        self.categorical_headers = categorical_headers
        
        # fetch categories
        categories = []
        for header in categorical_headers:
            X[header] = X[header].astype(int)
            categories.append([idx for idx in range(X[header].unique().min(), X[header].unique().max()+1)])
        
        #build encoder
        self.Encoder = sklearn.preprocessing.OneHotEncoder(categories = categories)
        
        #run fit
        self.Encoder.fit(X[categorical_headers])
        
        #add fit value counts to use if transforming unseen dataset with values not found in original data
        self.fit_value_counts = []
        for header in categorical_headers:
            counts = X[header].value_counts().reset_index()
            counts.columns = ['value', 'count']
            self.fit_value_counts.append(counts)
        
        
        #compile OneHot_headers
        self.OneHot_headers = []
        for i in range(len(self.categorical_headers)):
            header = self.categorical_headers[i]
            for val in self.Encoder.categories_[i]:

                #if a LabelEncoder is passed, inverse transform the encoded value for labeling the header
                if self.LabelEncoder!= None:
                    if header in self.LabelEncoder.LabelEncoder_dict.keys():
                        val = self.LabelEncoder.LabelEncoder_dict[header].inverse_transform([val])[0]

                self.OneHot_headers.append(header+'['+str(val)+']')
        
        
    def transform(self, X):
        import numpy as np
        import pandas as pd
        import sklearn, sklearn.preprocessing
        import warnings
        
        warnings.filterwarnings('ignore')

        X = X.copy()

        c =0
        for header in self.categorical_headers:
            #ensure integer data type
            X[header] = X[header].astype(int)

            #if a value in the X does not exist in the encoder, update it with most frequent value from the fit_value_counts
            for unique in X[header].unique():
                if unique not in self.Encoder.categories_[c]:
                    value = int(self.fit_value_counts[c]['value'][self.fit_value_counts[c]['count'] == np.max(self.fit_value_counts[c]['count'])])
                    X[header][X[header]==unique] = value
            c+=1

        OneHotEncodings = self.Encoder.transform(X[self.categorical_headers])

        X = X.drop(columns = self.categorical_headers).reset_index(drop=True)
        
        if self.return_format == 'DataFrame':
            OneHotEncodings = pd.DataFrame(OneHotEncodings.toarray(),
                                columns = self.OneHot_headers )
            X = pd.concat((X, OneHotEncodings),axis=1)
            
            self.headers_after_OneHot = list(X.columns)
            
        if self.return_format == 'npArray':
            
            self.headers_after_OneHot = list(X.columns) + self.OneHot_headers
            
            X = np.concatenate((np.array(X), OneHotEncodings.toarray()), axis = 1)

        warnings.filterwarnings('default')

        return X
