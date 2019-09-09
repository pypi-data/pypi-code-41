"""
Fetch dictionary of default models for classification or regression tasks. The models_dict has the format of: 
    {model ID: {'model': model object,
                'param_grid': default parameter grid to run hypeparameter search on'}
     }
"""
def regression(n_features=None, n_labels=None, 
               models = ['Linear','SVM','KNN','DecisionTree','RandomForest','XGBoost','DenseNet'],
               ):
    """
    Fetch dictionary of standard regression models and their 'param_grid' dictionaries.     
    Arguments: 
    ---------
        n_features, n_labels: The number of features and labels used for the model. These parameters are only required if 'DenseNet' is selected
        models: list of models to fetch. Valid models include:
            - sklearn models: 'Linear', 'DecisionTree', 'RandomForest', 'GradBoost', 'SVM', 'KNN'
            - xgboost models: 'XGBoost'
            - keras modesl: 'DenseNet'
    """
    import sklearn
        
    models_dict = {}
    
    for model in models: #ensure the dictionary keys are in the order you specify in the models list
    
        if 'Linear' in model:
            models_dict['Linear'] = {'model':sklearn.linear_model.LinearRegression(),
                                     'param_grid': {'normalize': [False,True]}
                                    }
        if 'SVM' in model:
            import sklearn.svm
            models_dict['SVM'] = {'model':sklearn.svm.SVR(),
                                  'param_grid': {'kernel':['rbf', 'sigmoid']} #'linear', 'poly', 
                                 }

        if 'KNN' in model:
            import sklearn.neighbors
            models_dict['KNN'] = {'model': sklearn.neighbors.KNeighborsRegressor(),
                                  'param_grid': {'n_neighbors':[5, 10, 100],
                                                'weights':['uniform','distance'],
                                                'algorithm':['ball_tree','kd_tree','brute']}
                                 }

        if 'DecisionTree' in model:
            import sklearn.tree
            models_dict['DecisionTree'] = {'model':sklearn.tree.DecisionTreeRegressor(),
                                           'param_grid': {'criterion':     ['mse','friedman_mse','mae'],
                                                         'splitter':       ['best','random'],
                                                         'max_depth':      [None,5,10,100],
                                                         'max_features':   [None,0.25,0.5,0.75]}
                                          }
        if 'RandomForest' in model:
            import sklearn.ensemble
            models_dict['RandomForest'] = {'model': sklearn.ensemble.RandomForestRegressor(),
                                           'param_grid': {'criterion':      ['mse','mae'],
                                                          'n_estimators':  [10,100],
                                                          'max_depth':      [None,5,10],
                                                          'max_features':   [None,0.25,0.5,0.75]}
                                          }
        if 'GradBoost' in model:
            import sklearn.ensemble
            models_dict['GradBoost'] = {'model':sklearn.ensemble.GradientBoostingRegressor(),
                                        'param_grid':{'loss':['ls', 'lad', 'huber', 'quantile'],
                                                      'criterion':["friedman_mse",'mse','mae'],
                                                      'learning_rate':[0.01, 0.1, 1],
                                                      'n_estimators':[10, 100],
                                                      'subsample':[1.0,0.8,0.5],
                                                      'max_depth':[None, 5, 10]}
                                       }

        if 'XGBoost' in model or 'xgboost' in model:                
            import xgboost as xgb                                           
            models_dict['XGBoost'] = {'model':xgb.XGBRegressor(booster='gbtree',
                                                               objective='reg:linear',
                                                               verbosity=1,
                                                               n_jobs= -1,
                                                               ),
                                      'param_grid':{'max_depth': [3,10],
                                                    'learning_rate':[0.01, 0.1, 1],
                                                    'n_estimators':[10, 100, 1000],
                                                    'subsample':[1,0.9,0.5],
                                                    'colsample_bytree':[1.0,0.8,0.5],
                                                    #reg_alpha
                                                    #reg_lambda
                                                   }
                                 }

        if 'DenseNet' in model:
            from .. import NeuralNet
            models_dict['DenseNet'] = NeuralNet.DenseNet.model_dict(n_features=n_features,
                                                                     n_labels = n_labels,
                                                                    final_activation = 'elu',
                                                                    loss = 'mse',
                                                                    metrics=['mse','mae'])
    return models_dict                       
                    
def classification(n_features=None, n_labels=None, 
               models = ['Logistic', 'SVM', 'KNN', 'DecisionTree', 'RandomForest', 'XGBoost', 'DenseNet'],
               ):
    
    """
    Fetch dictionary of standard classification models and their 'param_grid' dictionaries.     
    Arguments: 
    ---------
        n_features, n_labels: The number of features and labels used for the model. These parameters are only required if 'DenseNet' is selected
        models: list of models to fetch. Valid models include:
            - sklearn models: 'Linear', 'DecisionTree', 'RandomForest', 'GradBoost', 'SVM', 'KNN'
            - xgboost models: 'XGBoost'
            - keras modesl: 'DenseNet'
        Note: if running binary classfication, your labels should be 0 and 1. If running multiclass classifciation, your labels should be one-hot encoded
    """
    import sklearn
        
    models_dict = {}
    
    for model in models: #ensure the dictionary keys are in the order you specify in the models list

        if 'Logistic' in model:
            models_dict['Logistic'] = {'model':sklearn.linear_model.LogisticRegression(),
                                         'param_grid': {'penalty': ['l1', 'l2']}
                                        }
        if 'SVM' in model:
            import sklearn.svm
            models_dict['SVM'] = {'model':sklearn.svm.SVC(probability=True),
                                  'param_grid': {'kernel':['rbf', 'sigmoid'], #'linear', 'poly'
                                             }
                                 }
        if 'KNN' in model:
            import sklearn.neighbors
            models_dict['SVM'] = {'model':sklearn.svm.SVC(probability=True),
                                  'param_grid': {'kernel':['rbf', 'sigmoid'], #'linear', 'poly'
                                             }
                                 }

        if 'DecisionTree' in model:
            import sklearn.tree
            models_dict['DecisionTree'] = {'model':sklearn.tree.DecisionTreeRegressor(),
                                           'param_grid': {'criterion':     ['mse','friedman_mse','mae'],
                                                          'splitter':       ['best','random'],
                                                         'max_depth':      [None,5,10,100],
                                                         'max_features':   [None,0.25,0.5,0.75]}
                                          }
        if 'RandomForest' in model:
            import sklearn.ensemble
            models_dict['RandomForest'] = {'model': sklearn.ensemble.RandomForestClassifier(),
                                       'param_grid':{'criterion':['gini','entropy'],
                                                     'n_estimators':  [10,100],
                                                     'max_depth':      [None,5,10],
                                                     'max_features':   [None,0.25,0.5,0.75]}
                                       }
        if 'GradBoost' in model:
            import sklearn.ensemble
            models_dict['GradBoost'] = {'model': sklearn.ensemble.GradientBoostingClassifier(),
                                    'param_grid': {'loss':['deviance','exponential'],
                                                  'criterion':["friedman_mse",'mse','mae'],
                                                   'learning_rate':[0.01, 0.1, 1],
                                                   'n_estimators':[10, 100],
                                                   'subsample':[1.0,0.8,0.5],
                                                   'max_depth':[None, 5, 10]}
                                   }

        if 'XGBoost' in model or 'xgboost' in model:                
            import xgboost as xgb                                           
            models_dict['XGBoost'] = {'model':xgb.XGBClassifier(booster='gbtree',
                                                                objective = "reg:logistic"),
                                      'param_grid':{'max_depth': [3,10],
                                                    'learning_rate':[0.01, 0.1, 1],
                                                    'n_estimators':[10, 100, 1000],
                                                    'subsample':[1,0.9,0.5],
                                                    'colsample_bytree':[1.0,0.8,0.5],
                                                    #reg_alpha
                                                    #reg_lambda
                                                   }
                                 }

        if 'DenseNet' in model:
            from .. import NeuralNet
            if n_labels > 1:
                loss = 'categorical_crossentropy'
            else:
                loss = 'binary_crossentropy'

            models_dict['DenseNet'] = NeuralNet.DenseNet.model_dict(n_features=n_features,
                                                                     n_labels = n_labels,
                                                                    final_activation = 'softmax',
                                                                    loss = loss,
                                                                    metrics=['accuracy'])
    return models_dict

