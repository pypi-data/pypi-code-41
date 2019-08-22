"""
GridSearchCV methods to run on a single model or mult_model cases
methods:
    single_model
    multi_model
"""

def single_model(model_dict, 
                 X_train, y_train, X_test, y_test, 
                 cv, scoring, 
                 path_model_dir, 
                 n_jobs=-1, 
                 verbose = 1,
                 **kwargs):
    """
    Run Grid Search CV on a single model specified by the "key" argument
    """
    
    #import libs
    import sys, os
    sys.path.insert(0,  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    import JL_NeuralNet as NeuralNet
    import sklearn, sklearn.model_selection
    import JL_ML_model_dict
    
    if 'compiler' not in model_dict.keys(): #i.e. if you're not running a neural network
        model_dict['GridSearchCV'] = sklearn.model_selection.GridSearchCV(model_dict['model'],
                                                                          model_dict['param_grid'],
                                                                          n_jobs=n_jobs,
                                                                          cv = cv,
                                                                          scoring=scoring,
                                                                          verbose = verbose)
        model_dict['GridSearchCV'].fit(X_train,y_train)

    else: #run gridsearch using neural net function
        if scoring == None:
            scoring={'metric': 'loss', 'maximize': False}

        #check kwargs for epochs
        epochs = 100
        for item in kwargs.items():
            if 'epochs' in item[0]: epochs = item[1]

        model_dict['GridSearchCV'] = NeuralNet.search.GridSearchCV(model_dict['compiler'],
                                                                   model_dict['param_grid'],
                                                                   cv = cv,
                                                                   scoring=scoring,
                                                                   epochs =  epochs,
                                                                   path_report_folder = path_model_dir)

        model_dict['GridSearchCV'].fit(X_train,y_train, X_test, y_test)


    model_dict['best_model'] = model_dict['GridSearchCV'].best_estimator_
    model_dict['best_params'] = model_dict['GridSearchCV'].best_params_
    model_dict['best_cv_score'] = model_dict['GridSearchCV'].best_score_
    
    if 'compiler' not in model_dict.keys(): #neural networks save in their own gridsearch function
        JL_ML_model_dict.save(path_model_dir, model_dict)
    
    return model_dict
                      

def multi_model(models_dict, 
                 X_train,
                 y_train, 
                 X_test, 
                 y_test, 
                 cv = 5,
                 scoring=None,
                 metrics = {None:None},
                 retrain = True,
                 path_root_dir = './outputs/GridSearchCV',
                 n_jobs = -1,
                 verbose = 1,
                 **kwargs):
    """
    Run GridSearchCV on all 'models' and their 'param_grid' in the models_dict argument.
    
    Arguments:
        models_dict: dictionary containing all models and their param_grid (see JLutils.ML_models.model_selection.fetch_models_dict...)
        X_train, y_train, X_test, y_test: train & test datasets
        cv: cross-validation index.
        scoring: Default: None.
            - If scoring = None, use default score for given sklearn model, or use 'loss' for neural network. 
            - For custom scoring functions, pass 'scoring = {'metric':INSERT FUNCTION, 'maximize':True/False}
        metrics: dictionary with formating like {metric name (str), metric function (sklearn.metrics...)}. The metric will be evaluated after CV on the test set
        retrain: Boolean. whether or not you want to retrain the model if it is already been saved in the path_root_dir folder
        path_root_dir: root directory where the GridSearchCV outputs will be dumped.
    metrics: '
    """
    
    #import libs
    import sys, os
    sys.path.insert(0,  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    import JL_NeuralNet as NeuralNet
    import sklearn, sklearn.model_selection
    import JL_ML_model_dict
    
    for key in models_dict.keys():
        print('\n----',key,'----')
        
        #define model directory
        path_model_dir = os.path.join(path_root_dir, key)
        print('path_model_dir:',path_model_dir)
        
        if 'Net' not in key:
            path_file = os.path.join(path_model_dir,'model_dict.dill')
        else:
            path_file = os.path.join(path_model_dir,'best_params_.dill')
            
        if retrain or os.path.isfile(path_file)==False:
            models_dict[key] = single_model(models_dict[key], 
                                            X_train, y_train, X_test, y_test, 
                                            cv, scoring, 
                                            path_model_dir,
                                            n_jobs = n_jobs,
                                            verbose = verbose,
                                            **kwargs)
            
        else: #reload previously trained model
            if 'Net' not in key:
                models_dict[key] = JL_ML_model_dict.load(path_model_dir)
            else:
                #check kwargs for epochs
                epochs = 100
                for item in kwargs.items():
                    if 'epochs' in item[0]: epochs = item[1]
                models_dict[key] = JL_ML_model_dict.load_NeuralNet(path_model_dir, X_train, y_train, epochs)
        
        models_dict[key]['y_test'] = y_test
        models_dict[key]['y_pred'] = models_dict[key]['best_model'].predict(X_test)
        
        if 'Net' not in key:
            models_dict[key]['best_pred_score'] = models_dict[key]['best_model'].score(X_test, y_test)
        else:
            models_dict[key]['best_pred_score'] = models_dict[key]['best_model'].evaluate(X_test, y_test, verbose =0)

        print('\tbest_cv_score:',models_dict[key]['best_cv_score'])
        print('\tbest_pred_score:',models_dict[key]['best_pred_score'])

        for metric_key in metrics.keys():
            if metrics[metric_key] !=None:
                models_dict[key][metric_key] = metrics[metric_key](y_test, models_dict[key]['y_pred'])
                print('\t',metric_key,':',models_dict[key][metric_key])
                
        if 'Net' not in key:
            JL_ML_model_dict.save(path_model_dir, models_dict[key])
        else:
            model_dict_subset = models_dict[key].copy()
            for key in models_dict[key].keys():
                if key not in ['y_test','y_pred','best_pred_score'] +list(metrics.keys()):
                    model_dict_subset.pop(key)
                    
    return models_dict