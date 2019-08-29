#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 19 12:21:06 2019

@author: mishugeb
"""

from sigproextractor import subroutines as sub
import numpy as np
import pandas as pd
import os
import importlib
importlib.reload(sub)

processAvg = np.array(pd.read_csv("/Users/mishugeb/Desktop/decomposition/De_Novo_Solution_Signatures.txt", sep = "\t", index_col=0) )
exposureAvg = pd.read_csv("/Users/mishugeb/Desktop/decomposition/De_Novo_Solution_Activities.txt", sep = "\t", index_col = 0)
genomes = pd.read_csv("/Users/mishugeb/Desktop/decomposition/Samples.txt", sep = "\t", index_col = 0)
m="96"
layer_directory2 = "/Users/mishugeb/Desktop/decomposition/Decomposed_Solution"
if not os.path.exists(layer_directory2):
    os.makedirs(layer_directory2)



final_signatures = sub.signature_decomposition(processAvg, m, layer_directory2)
# extract the global signatures and new signatures from the final_signatures dictionary
globalsigs = final_signatures["globalsigs"]
globalsigs = np.array(globalsigs)
newsigs = final_signatures["newsigs"]
processAvg = np.hstack([globalsigs, newsigs])  
allsigids = final_signatures["globalsigids"]+final_signatures["newsigids"]
attribution = final_signatures["dictionary"]
background_sigs= final_signatures["background_sigs"]
index = genomes.index
colnames = genomes.columns

"""
print(type(processAvg))
print(type(genomes))
print(allsigids)
print(m)
print(index)
print(colnames)
print(background_sigs)
"""
result = sub.make_final_solution(processAvg, genomes, allsigids, layer_directory2, m, index, colnames, \
                        remove_sigs=True, attribution = attribution, denovo_exposureAvg  = exposureAvg , penalty=0.05, background_sigs=background_sigs, verbose=True)












