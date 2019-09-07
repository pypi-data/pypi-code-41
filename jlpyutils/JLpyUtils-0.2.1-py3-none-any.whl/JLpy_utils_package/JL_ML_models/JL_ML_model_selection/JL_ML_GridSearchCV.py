"""
GridSearchCV methods to run on a single model or mult_model cases
methods:
    single_model
    multi_model
"""

#############################
# UPDATE MODEL DICT TO REMOVE GRID SEARCH (MINIMIZE MODEL SIZE)
#############################

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
                      

class multi_model():
    
    def __init__(self,
                 models_dict, 
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
            cv: cross-validation index.
            scoring: Default: None.
                - If scoring = None, use default score for given sklearn model, or use 'loss' for neural network. 
                - For custom scoring functions, pass 'scoring = {'metric':INSERT FUNCTION, 'maximize':True/False}
            metrics: dictionary with formating like {metric name (str), metric function (sklearn.metrics...)}. The metric will be evaluated after CV on the test set
            retrain: Boolean. whether or not you want to retrain the model if it is already been saved in the path_root_dir folder
            path_root_dir: root directory where the GridSearchCV outputs will be dumped.
        metrics: '
        """
        
        self.models_dict = models_dict
        self.cv = cv
        self.scoring = scoring
        self.metrics = metrics
        self.retrain = retrain
        self.path_root_dir = path_root_dir
        self.n_jobs = n_jobs
        self.verbose = verbose
        self.kwargs = kwargs
        
       
    def fit(self,
            X_train,
            y_train, 
            X_test, 
            y_test):
        """
        Fit the X_train, y_train dataset & evaluate metrics on X_test, y_test for each of the best models found in each individual models GridSearchCV
        
        X_train, y_train, X_test, y_test: train & test datasets
        """
        
        #import libs
        import sys, os
        import numpy as np
        import sklearn, sklearn.model_selection
        
        sys.path.insert(0,  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
        import JL_NeuralNet as NeuralNet
        import JL_ML_model_dict
        
        #instantiate path_model_dirs dictionary so we can know where the models are saved
        self.path_model_dirs = {}

        for key in self.models_dict.keys():
            
            if self.verbose >=1: print('\n----',key,'----')

            #define model directory
            path_model_dir = os.path.join(self.path_root_dir, key)
            self.path_model_dirs[key] = path_model_dir
            if self.verbose >=1: print('path_model_dir:',path_model_dir)

            if 'Net' not in key:
                path_file = os.path.join(path_model_dir,'model_dict.dill')
            else:
                path_file = os.path.join(path_model_dir,'best_params_.dill')

            if self.retrain or os.path.isfile(path_file)==False:
                self.models_dict[key] = single_model(self.models_dict[key], 
                                                     X_train, y_train, X_test, y_test, 
                                                     self.cv, 
                                                     self.scoring, 
                                                     path_model_dir,
                                                     n_jobs = self.n_jobs,
                                                     verbose = np.max((0,self.verbose-1)),
                                                     **self.kwargs)

            else: #reload previously trained model
                if 'Net' not in key:
                    self.models_dict[key] = JL_ML_model_dict.load(path_model_dir)
                else:
                    #check kwargs for epochs
                    epochs = 100
                    for item in self.kwargs.items():
                        if 'epochs' in item[0]: epochs = item[1]
                    self.models_dict[key] = JL_ML_model_dict.load_NeuralNet(path_model_dir, 
                                                                            X_train, y_train, 
                                                                            epochs)

            self.models_dict[key]['y_test'] = y_test
            self.models_dict[key]['y_pred'] = self.models_dict[key]['best_model'].predict(X_test)

            if 'Net' not in key:
                self.models_dict[key]['best_pred_score'] = self.models_dict[key]['best_model'].score(X_test, y_test)
            else:
                self.models_dict[key]['best_pred_score'] = self.models_dict[key]['best_model'].evaluate(X_test, y_test, verbose =0)
            
            if self.verbose >=1:
                print('\tbest_cv_score:',self.models_dict[key]['best_cv_score'])
                print('\tbest_pred_score:',self.models_dict[key]['best_pred_score'])

            for metric_key in self.metrics.keys():
                if self.metrics[metric_key] !=None:
                    self.models_dict[key][metric_key] = self.metrics[metric_key](y_test, self.models_dict[key]['y_pred'])
                    print('\t',metric_key,':',self.models_dict[key][metric_key])

            if 'Net' not in key:
                JL_ML_model_dict.save(path_model_dir, self.models_dict[key])
            else:
                model_dict_subset = self.models_dict[key].copy()
                for key in models_dict[key].keys():
                    if key not in ['y_test','y_pred','best_pred_score'] +list(self.metrics.keys()):
                        model_dict_subset.pop(key)
                    