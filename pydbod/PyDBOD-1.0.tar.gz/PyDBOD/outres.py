# -*- coding: utf-8 -*-
"""
@author: Miguel Ángel López Robles
"""


import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import DistanceMetric
import matplotlib.pyplot as plt
from PyDBOD.base import Base
from scipy import stats
import math


class OUTRES(Base):
    def __init__(self, epsilon=15, alpha=0.01):

        self.epsilon = epsilon## por defecto
        self.alpha = alpha
        

    def outres(self, o, s, d):
        index = np.setdiff1d(d, s)
        #print("Holas")
        #print(index)
        #print("llamada")
        for i in index:
            s_ = np.union1d(s,i)
            #self.d[o] = np.setdiff1d(self.d[o], i )
            #print("añadiendo")
            #print(i)
            #print(s_)
            ## posible change, take the k-nearest-neighbour? and not use radius

            ##calculate the distance in this subspace
            dist = DistanceMetric.get_metric('euclidean')
            distances = dist.pairwise( self.data[:,s_ ] )

            ## take the index of the neighbor of o
            neighbor = np.linspace(0, self.n-1, self.n, dtype= np.int)
            neighbor = neighbor[distances[o,:] < self.epsilon]

            # test if there is a uniform atributte
            # if one is uniform, the subspace is not relevant
            uniform = False
            j = 0
            #bucle while, to stop de search with condition
            while (j < len(s_) ) and ~uniform:

                test = stats.kstest(self.data[neighbor,s_[j] ], 'uniform')

                
                if (test[1]) > self.alpha:
                    
                    uniform = True
                j = j+1
            
            # if de subspace is relevant
            if ~uniform:
                #print("sirve para algo")
                # first we have to calculate the adaptive neigborhood

                # calculate de value of e(|S|)
                if len(s_) > 2:
                    adaptative_e = self.epsilon * ( self.h_optimal(len(s_) / self.h_optimal(2) ) )

                else:
                    adaptative_e = self.epsilon
                
                #now we take the neighboor adaptative
                a_neighbor = np.linspace(0, self.n-1, self.n, dtype= np.int)
                a_neighbor = a_neighbor[distances[o,:] < adaptative_e]


                # calculate the density
                density = (1/self.n) * np.sum( 1- np.power(distances[o,a_neighbor] / adaptative_e, 2)  )
                

                # we need the density of the rest of the neihborhood to calculate de average
                densities = np.array([])
                # calculate a array with the density of the local neihgboor
                for neig in a_neighbor:
                    a_neighbor_local = np.linspace(0, self.n-1, self.n, dtype= np.int)
                    a_neighbor_local = a_neighbor_local[distances[neig,:] < adaptative_e]
                    
                    densities  = np.append(densities, (1/self.n) * np.sum( 1- np.power(distances[neig, a_neighbor_local] / adaptative_e, 2)  ) )

                # calculate the mean and the standard desviation
                mean = np.mean(densities)
                std = np.std(densities)
                #calculate de desviation
                desviation = (mean - density) / (2 * std)

                #if we have a hig deviation
                if desviation >= 1:
                    # aggregation of scoring
                    self.r[o] = self.r[o] * (density /desviation)

                #####
                # recursively next subspace
                #print("debe haber recursividad")
                self.outres(o,s_,d)
            #else uniform
            #### else break point for higher dimensional subspaces

            ## delete to avoid repeating this dimension
            # we can not change the dimension, use the last element
            # and use that the diference erase the repeated
            #print(type(i))
            #print(self.d[0].shape)
            #print(self.d[o])
            #element = np.reshape(np.array(i), (-1,1) )
            #print(element)
            #if len(s_) == 1:
                
            #print("me cargo")
            #print(d)
            #self.d[o,i] = self.d[o,len(self.d[o])-1]
            d = np.setdiff1d(d, np.array(i))
            #print(d)
            #print(i)
            #print("cargado")
            
                

    def h_optimal(self,d):
        value = d/2
        gamma = value* math.gamma( value)
        return  ( ( (8 * (gamma) )/  math.pow(math.pi,d/2)  ) * (d+4) *  math.pow(2*math.sqrt(math.pi),d)     )  * math.pow(self.n, -1/(d+4) ) 
    
    def fit_predict(self, data):
        self.n = data.shape[0]
        d = np.linspace(0,data.shape[1]-1,data.shape[1], dtype= np.int)
        #self.d = np.reshape( np.tile(self.d, self.n), (self.n, data.shape[1] ))
        self.r = np.ones(self.n)
        self.data = data
        #we use the function OUTRES for all objects
        #print("Hi")
        [self.outres(o, np.array([],dtype= np.int), d) for o in range(self.n)]
        #print(self.r)
        return self.r





