# -*- coding: utf-8 -*-
"""
@author: Miguel Ángel López Robles
"""



import numpy as np
from sklearn.neighbors import NearestNeighbors


from PyDBOD.base import Base


class ODIN(Base):
    def __init__(self, k=20, t=10):
        self.k = k
        self.t = t

    def fit_predict(self, data):
        
        nbrs = NearestNeighbors(n_neighbors= self.k, algorithm='ball_tree').fit(data)
        distances, indices = nbrs.kneighbors(data)
        
        graph_conexion = np.array([ [ vector in indices[i] for i in indices[vector,:] ] for vector in range(indices.shape[0]) ])

        indegree = np.sum(graph_conexion, axis=1)

        odin = np.array(indegree <= self.t, dtype=np.int)

        return odin