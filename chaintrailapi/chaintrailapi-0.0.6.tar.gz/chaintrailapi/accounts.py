from sklearn.preprocessing import MinMaxScaler

DATADIR = '/home/jovyan/agg_feat_datasets'
    
class Accounts:
    def __init__(self, data):
        self.data = data
        
    def __getitem__(self, item):
         return self.data[item]

    def get_data(self):
        return self.data
        
    def get_scaled(self):
        retVal = self.data
        scaler = MinMaxScaler(copy=False)
        scaler.fit(retVal)
        return scaler.transform(retVal)
