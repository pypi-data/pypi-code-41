"""
Custom machine learning module for python focusing on streamlining and wrapping sklearn & tensorflow/keras functions
====================================================================================================================

See https://github.com/jlnerd/JLpy_utils_package.git for more details
"""

__version__='1.0.0'

import sys, os

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0,  os.path.dirname(os.path.abspath(__file__)))
    
import JL_ML_model_selection as model_selection
import JL_NeuralNet as NeuralNet
import JL_ML_preprocessing as preprocessing
import JL_ML_inspection as inspection
