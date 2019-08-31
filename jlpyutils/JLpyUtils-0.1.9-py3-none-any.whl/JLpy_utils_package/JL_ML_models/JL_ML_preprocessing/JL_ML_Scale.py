
import sklearn.preprocessing

class continuous_features():
    """
    Scale the "continuous_features" specified in headers_dict and contained in the X.
    Arguments:
        X: pandas dataframe
        continuous_headers: list containing the header for the continuous features of interest
        Scaler: sklearn.preprocessing....: defaults: sklearn.preprocessing.StandardScaler()
            - Object specifing the scaler operation the data will be fit and transformed to.
    Returns:
        X, Scaler
    """
    
    def __init__(self, Scaler = sklearn.preprocessing.RobustScaler()):
        
        self.Scaler = Scaler

        
    def fit(self, X, continuous_headers):
        
        X = X.copy()

        self.Scaler.fit(X[continuous_headers])
        self.continuous_headers = continuous_headers
        
    def transform(self, X):
        
        import warnings

        warnings.filterwarnings('ignore')
    
        X[self.continuous_headers] = self.Scaler.transform(X[self.continuous_headers])

        warnings.filterwarnings('default')

        return X

def default_Scalers_dict():
    """
    fetch dictionary containing typical scalers used for transforming continuous data
    """
    import sklearn.preprocessing
    
    Scalers_dict = {'StandardScaler':sklearn.preprocessing.StandardScaler(),
                    'MinMaxScaler':sklearn.preprocessing.MinMaxScaler(),
                    'RobustScaler':sklearn.preprocessing.RobustScaler()}
    return Scalers_dict