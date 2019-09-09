"""
Custom machine learning module for python focusing on streamlining and wrapping sklearn & tensorflow/keras functions
====================================================================================================================
"""
    
from . import model_selection
from . import NeuralNet
from . import preprocessing
from . import inspection

try:
    import tensorflow as __tf__
except:
    print('tensorflow is not installed, run "pip install tensorflow==1.12.2" and "pip install tensorflow-gpu==1.12.2"')
    
    
class metrics():
    def lift_score(y_true, y_pred):
        """
        Computes the lift score for a given model
        """
        import sklearn.metrics
        conf_mat = sklearn.metrics.confusion_matrix(y_true,y_pred)
        TP = conf_mat[0,0]
        FN = conf_mat[1,0]
        FP = conf_mat[0,1]
        TN = conf_mat[1,1]
        lift = (TP/(TP+FP)) / ((TP+FN)/(TP+TN+FP+FN))
        return lift
        