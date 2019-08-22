import sys, os

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0,  os.path.dirname(os.path.abspath(__file__)))
    
import JL_ML_models_dict as models_dict
import JL_ML_model_dict as model_dict
import JL_ML_GridSearchCV as GridSearchCV