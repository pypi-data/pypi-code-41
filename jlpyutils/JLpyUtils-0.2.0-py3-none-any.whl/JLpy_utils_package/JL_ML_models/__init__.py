"""
Custom machine learning module for python focusing on streamlining and wrapping sklearn & tensorflow/keras functions
====================================================================================================================
"""

import sys as __sys__ 
import os as __os__

if __os__.path.dirname(__os__.path.abspath(__file__)) not in __sys__.path:
    __sys__.path.insert(0,  __os__.path.dirname(__os__.path.abspath(__file__)))
    
import JL_ML_model_selection as model_selection
import JL_NeuralNet as NeuralNet
import JL_ML_preprocessing as preprocessing
import JL_ML_inspection as inspection
