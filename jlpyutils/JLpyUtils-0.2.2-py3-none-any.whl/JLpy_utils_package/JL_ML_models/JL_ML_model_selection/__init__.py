import sys as __sys__ 
import os as __os__
if __os__.path.dirname(__os__.path.abspath(__file__)) not in __sys__.path:
    __sys__.path.insert(0,  __os__.path.dirname(__os__.path.abspath(__file__)))
    
import JL_ML_default_models_dict as default_models_dict

class GridSearchCV():
    """
    Wrapper to sklearn GridSearchCV that allows running GridSearchCV on different types of models contained in the models_dict argument

    Arguments:
    ----------
        models_dict: dictionary containing all models and their param_grid. 
            - Dictionary Format: {'model name':{'model':model object,
                                                'param_grid': {parameter name, parameter list}]
        cv: cross-validation index.
        scoring: Default: None.
            - If scoring = None, use default score for given sklearn model, or use 'loss' for neural network. 
            - For custom scoring functions, pass 'scoring = {'metric':INSERT FUNCTION, 'maximize':True/False}
        metrics: dictionary with formating like {metric name (str), metric function (sklearn.metrics...)}. The metric will be evaluated after CV on the test set
        retrain: Boolean. whether or not you want to retrain the model if it is already been saved in the path_root_dir folder
        path_root_dir: root directory where the GridSearchCV outputs will be dumped.
        n_jobs: int. Defualt: -1. number of parallel jobs to run. If -1, all available threads will be used
            - Note: parallel computing is not supported for Neural Net models
        verbose: verbosity of prints.
    """
    
    def __init__(self,
                 models_dict, 
                 cv = 5,
                 scoring=None,
                 metrics = {None:None},
                 retrain = True,
                 path_root_dir = './outputs/GridSearchCV',
                 n_jobs = -1,
                 verbose = 2,
                 **kwargs):
        
        self.models_dict = models_dict
        self.cv = cv
        self.scoring = scoring
        self.metrics = metrics
        self.retrain = retrain
        self.path_root_dir = path_root_dir
        self.n_jobs = n_jobs
        self.verbose = verbose
        self.kwargs = kwargs
        
        import sys, os
        if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
            sys.path.insert(0,  os.path.dirname(os.path.abspath(os.path.join(__file__,'..','..'))))
        import JL_file_utils as file_utils
        
        self.save = file_utils.save
        self.load = file_utils.load

    def load_NeuralNet(self, path_model_dir, X_train, y_train, epochs):
        """
        load model_dict for Nueral Net case
        """
        import JL_NeuralNet as NeuralNet

        #fetch best params
        best_params_ = self.load('best_params_', 'dill', path_model_dir)   
        
        #rebuild model_dict
        model_dict = NeuralNet.DenseNet.model_dict(**best_params_)
        model_dict['model'].fit(X_train, y_train, epochs, verbose = 0)
        model_dict['best_model'] = model_dict['model']
        model_dict['best_params'] = best_params_ 
        model_dict['best_cv_score'] = np.nan

        return model_dict

        
    def __single_model_GridSearchCV__(self, 
                                      model_dict_, 
                                      X_train, y_train, X_test, y_test,
                                      path_model_dir):
        """
        Run Grid Search CV on a single model specified by the "key" argument
        """

        #import libs
        import sklearn.model_selection
        import numpy as np
        import sys, os
        sys.path.insert(0,  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
        import JL_NeuralNet as NeuralNet
        
        if 'sklearn' in str(type(model_dict_['model'])):
            GridSearchCV = sklearn.model_selection.GridSearchCV(model_dict_['model'],
                                                                              model_dict_['param_grid'],
                                                                              n_jobs= self.n_jobs,
                                                                              cv = self.cv,
                                                                              scoring= self.scoring,
                                                                              verbose = np.max((0,self.verbose-1))
                                                                             )
            GridSearchCV.fit(X_train,y_train)

        else: #run gridsearch using neural net function
            if self.scoring == None:
                self.scoring={'metric': 'loss', 'maximize': False}

            #check kwargs for epochs
            epochs = 100
            for item in self.kwargs.items():
                if 'epochs' in item[0]: epochs = item[1]

            GridSearchCV = NeuralNet.search.GridSearchCV(model_dict_['model'],
                                                           model_dict_['param_grid'],
                                                           cv = self.cv,
                                                           scoring=self.scoring,
                                                           epochs =  epochs,
                                                           path_report_folder = path_model_dir,
                                                           verbose = np.max((0,self.verbose-1))
                                                        )

            GridSearchCV.fit(X_train,y_train, X_test, y_test)

        model_dict_['best_model'] = GridSearchCV.best_estimator_
        model_dict_['best_params'] = GridSearchCV.best_params_
        model_dict_['best_cv_score'] = GridSearchCV.best_score_

        if 'sklearn' in str(type(model_dict_['model'])):
            self.save(model_dict_, 'model_dict', 'dill', path_model_dir)

        return model_dict_
        
       
    def fit(self,
            X_train,
            y_train, 
            X_test, 
            y_test):
        """
        Fit the X_train, y_train dataset & evaluate metrics on X_test, y_test for each of the best models found in each individual models GridSearchCV
        
        Arguments:
        ---------
            X_train, y_train, X_test, y_test: train & test datasets
        """
        
        import os
        
        #instantiate path_model_dirs dictionary so we can know where the models are saved
        self.path_model_dirs = {}

        for key in self.models_dict.keys():
            
            if self.verbose >=1: print('\n----',key,'----')

            #define model directory
            path_model_dir = os.path.join(self.path_root_dir, key)
            self.path_model_dirs[key] = path_model_dir
            if self.verbose >=1: print('path_model_dir:',path_model_dir)

            if 'sklearn' in str(type(self.models_dict[key]['model'])):
                path_file = os.path.join(path_model_dir,'model_dict.dill')
            elif 'Net' in key:
                path_file = os.path.join(path_model_dir,'best_params_.dill')

            if self.retrain or os.path.isfile(path_file)==False:
                self.models_dict[key] = self.__single_model_GridSearchCV__(self.models_dict[key], 
                                                                            X_train, y_train, 
                                                                            X_test, y_test,
                                                                            path_model_dir)

            else: #reload previously trained model
                if 'sklearn' in str(type(self.models_dict[key]['model'])):
                    self.models_dict[key] = self.load('model_dict', 'dill', path_model_dir)
                elif 'Net' in key:
                    #check kwargs for epochs
                    epochs = 100
                    for item in self.kwargs.items():
                        if 'epochs' in item[0]: epochs = item[1]
                    self.models_dict[key] = self.load_NeuralNet(path_model_dir, 
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

            if 'sklearn' in str(type(self.models_dict[key]['model'])):
                self.save(self.models_dict[key], 'model_dict', 'dill', path_model_dir)
            elif 'Net' in key:
                model_dict_subset = self.models_dict[key].copy()
                for key in models_dict[key].keys():
                    if key not in ['y_test','y_pred','best_pred_score'] +list(self.metrics.keys()):
                        model_dict_subset.pop(key)
                    