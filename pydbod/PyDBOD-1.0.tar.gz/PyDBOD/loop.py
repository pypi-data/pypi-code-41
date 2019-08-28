# -*- coding: utf-8 -*-
"""
@author: Miguel Ángel López Robles
"""


import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.special import erf
from PyDBOD.base import Base

class LOOP(Base):

    def __init__(self,  k=20, lamda=3):
        self.k = k
        self.lamda = lamda
    
    def fit_predict(self, data):
        
        nbrs = NearestNeighbors(n_neighbors= self.k, algorithm='ball_tree').fit(data)
        distances, indices = nbrs.kneighbors(data)
 
        n_points = distances.shape[0]

        #calculate the standar distances 
        standar_distances = np.sqrt( np.sum( np.power(distances,2), axis=1 ) / n_points )

        #calculate the probabilistic distances
        p_distances = self.lamda * standar_distances
        #print("distancias probabilisticas")
        #print(p_distances)

        #calculate the probabilistic Local Outlier Factor
        plof = p_distances /  [ np.sum([p_distances[j] for j in indices[i] ]) for i in indices]
        #we eliminate the -1 because we assume that the data is distributed from 0

        #calculate de normalized probabilistic local outlier factor
        nplof = self.lamda * np.sqrt( np.mean( np.power( plof, 2) ) )

        #apply the Gaussian Error Function to obtain the Local Outlier Probability
        
        loop = np.maximum(0, erf( plof / ( nplof * np.sqrt(2) ) ) )
        

        return loop
