try:
    import tensorflow as tf
except ImportError:
    sys.exit("""You need tensorflow. run: '!pip install tensorflow' or '!pip install tensorflow-gpu'""")
    
import sys as __sys__ 
import os as __os__
if __os__.path.dirname(__os__.path.abspath(__file__)) not in __sys__.path:
    __sys__.path.insert(0,  __os__.path.dirname(__os__.path.abspath(__file__)))
    
import JL_ConvNet as ConvNet
import JL_NeuralNet_plot as plot
import JL_NeuralNet_Search as search
import JL_DenseNet as DenseNet
import JL_NN_utils as utils