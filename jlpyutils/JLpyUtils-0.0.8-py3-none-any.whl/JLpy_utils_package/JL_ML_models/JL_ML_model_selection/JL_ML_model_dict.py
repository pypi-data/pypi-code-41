"""
Functions related to single dictionaries (model_dict)
"""

def save(path_model_dir, model_dict):
    """
    save model_dict as dill file
    """
    import dill, os
    
    if os.path.isdir(path_model_dir)==False:
        os.makedirs(path_model_dir)
    
    path_file = os.path.join(path_model_dir,'model_dict.dill')
    f = open(path_file, 'wb') 
    dill.dump(model_dict, f)
    f.close()
    
def load(path_model_dir, NeuralNet = False):
    """
    load model_dict from dill file
    """
    import dill, os
    
    path_file = os.path.join(path_model_dir,'model_dict.dill')                
    f = open(path_file, 'rb') 
    model_dict = dill.load(f)
    f.close()
    return model_dict

def load_NeuralNet(path_model_dir, X_train, y_train, epochs):
    """
    load model_dict for Nueral Net case
    """
    import JL_NeuralNet as NeuralNet
    import dill, os
    
    #fetch best params
    path_file = os.path.join(path_model_dir,'best_params_.dill')                
    f = open(path_file, 'rb') 
    best_params_ = dill.load(f)
    f.close()

    #rebuild model_dict
    model_dict = NeuralNet.DenseNet.model_dict(**best_params_)
    model_dict['model'].fit(X_train, y_train, epochs, verbose = 0)
    model_dict['best_model'] = model_dict['model']
    model_dict['best_params'] = best_params_ 
    model_dict['best_cv_score'] = np.nan

    return model_dict