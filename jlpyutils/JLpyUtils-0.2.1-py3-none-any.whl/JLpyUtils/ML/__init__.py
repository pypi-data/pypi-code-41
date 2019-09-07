"""
Custom machine learning module for python focusing on streamlining and wrapping sklearn & tensorflow/keras functions
====================================================================================================================
"""
    
from . import model_selection
from . import NeuralNet
from . import preprocessing
from . import inspection

try:
    import tensorflow as tf
except:
    print('tensorflow is not installed, run "pip install tensorflow==1.12.2" and "pip install tensorflow-gpu==1.12.2"')