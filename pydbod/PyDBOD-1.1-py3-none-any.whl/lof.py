# -*- coding: utf-8 -*-
"""
@author: Miguel Ángel López Robles
"""


import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import DistanceMetric
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from PyDBOD.base import Base



class LOF(Base):
    def __init__(self, k=20):
        self.k = k
    
    def fit_predict(self, data):
        
        nbrs = NearestNeighbors(n_neighbors= self.k, algorithm='ball_tree').fit(data)
        distances, indices = nbrs.kneighbors(data)

        n_points = distances.shape[0]
        reach_d = [ [ max( (distances[i, j], distances[indices[i,j], self.k-1] ) ) for j in range(self.k) ] for i in range(n_points) ]
        reach_d = np.array(reach_d)

        ave_reach_d = np.mean(reach_d,axis=1)
        
        meany = 1 / np.array( [ [ ave_reach_d[i] for i in indices[j]] for j in range(n_points)] )
        meany = np.mean(meany,axis=1)
        #print("Mean y in Lx")
        #print(meany)

        lof = ave_reach_d * meany
        #print("lof")
        #print(lof)

        return lof
