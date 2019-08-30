import os
import numpy as np
import pandas as pd
import requests
from sklearn.decomposition import PCA
from sklearn.covariance import EllipticEnvelope

from .dataset import Dataset
from .accounts import Accounts

class ChainTrail:
    def __init__(self, server, dataset):
        self.server = server
        self.dataset = dataset
           
    def get_accounts(self, columns=None):
        response = requests.get(
            'http://'+self.server+'/v1/accountactivity',
            params={
                'start_selected_month': '2019-{:02d}-01'.format(self.dataset.value),
                'end_selected_month': '2019-{:02d}-01'.format(self.dataset.value + 1),
            },
        )

        accounts = pd.DataFrame(response.json())
        accounts['tx_count'] = accounts.tx_in + accounts.tx_out
        accounts = accounts.rename(columns={  
            'avg_tx_in_month':'avg_tx_in',
            'avg_tx_out_month':'avg_tx_out',
            'std_tx_in_month':'std_tx_in',
            'std_tx_out_month':'std_tx_out'
        })
        accounts = accounts.fillna({
            'avg_tx_in':0,
            'avg_tx_out':0,
            'std_tx_in':0,
            'std_tx_out':0
        })
        if columns is not None:
            accounts = accounts[columns]
        return Accounts(accounts)
    
    @staticmethod
    def predict_outliers(data, c=0.00001, fraction=1.0):
        xx, yy = np.meshgrid(
            np.arange(data[:,0].min()-0.3, data[:,0].max(), 0.001),
            np.arange(data[:,1].min()-0.2, data[:,1].max(), 0.001)
        )
        
        clf = EllipticEnvelope(contamination=c, support_fraction=fraction)
        y_pred = clf.fit_predict(data)
        z_train = clf.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        
        return y_pred==1, y_pred==-1, xx, yy, z_train
        
    @staticmethod
    def calculate_pca(data, components):
        pca = PCA(n_components=components)
        return pca.fit_transform(data)