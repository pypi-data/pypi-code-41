# -*- coding: utf-8 -*-
"""
@author: Miguel Ángel López Robles
"""


import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import DistanceMetric
import matplotlib.pyplot as plt
from PyDBOD.base import Base


class PINN_LOF(Base):
    def __init__(self, k=20, t=2, s=1, h =20):
        self.k = k
        self.t = t
        self.s = s
        self.h =h

    
    def fit_predict(self, data):
        
        n = data.shape[0]
        m = data.shape[1]


        ##########
        ## RP
        p1 = 1/(2* self.s)
        p0 = 1 - 1/ self.s
        #first, we do the random project
        r = np.array([ np.random.choice( [1,0,-1],p = [p1, p0, p1]) for i in range(m*self.t)] )
        r = np.reshape(r,(m, self.t))

        #r = np.fromfunction( generator_n(s), (data.shape[0],t) )
        y = np.dot(data,r)
        #print(x)
        #print(y.shape)
        #print(y)
        #print(r)

        ################
        ## PINN
        c_nbrs = NearestNeighbors(n_neighbors=self.h, algorithm='ball_tree').fit(y)

        ### find the h-nearest-neighbours in the projection
        c_distances, c_indices = c_nbrs.kneighbors(y)


        ### map the points is easy because we use the indices
        distances= np.array([])
        distances = np.reshape(distances,(-1,self.k))

        indices= np.array([],dtype= np.int)
        indices = np.reshape(indices,(-1, self.k))

        for i in range(n):
            ##calculate the k-neighbor in the local neighbours
            nbrs = NearestNeighbors(n_neighbors=self.k, algorithm='ball_tree').fit(data[ c_indices[i]])
            l_distances, l_indices = nbrs.kneighbors( np.reshape(data[i],(-1,m)) )

            #we have indices of the local neighbors, need the indices of the data
            #print(l_indices)
            l_indices = c_indices[i,l_indices]
            l_indices = np.reshape(l_indices,(1,self.k))
            #print(l_indices)

            l_distances = np.reshape(l_distances,(1,self.k))
            #print(l_distances)
            distances = np.concatenate( (distances, l_distances), axis=0)
            indices = np.concatenate( (indices, l_indices), axis=0)

        #######
        ###LOF
        n_points = distances.shape[0]
        reach_d = [ [ max( (distances[i, j], distances[indices[i,j],self.k-1] ) ) for j in range(self.k) ] for i in range(n_points) ]
        reach_d = np.array(reach_d)

        ave_reach_d = np.mean(reach_d,axis=1)
        
        meany = 1 / np.array( [ [ ave_reach_d[i] for i in indices[j]] for j in range(n_points)] )
        meany = np.mean(meany,axis=1)
        #print("Mean y in Lx")
        #print(meany)

        lof = ave_reach_d * meany

        return lof
