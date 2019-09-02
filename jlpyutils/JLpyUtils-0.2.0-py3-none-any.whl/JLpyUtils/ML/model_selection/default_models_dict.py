
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
    
    if 'Linear' in models:
        models_dict['Linear'] = {'model':sklearn.linear_model.LinearRegression(),
                                 'param_grid': {'normalize': [False,True]}
                                }
    if 'SVM' in models:
        import sklearn.svm
        models_dict['SVM'] = {'model':sklearn.svm.SVR(),
                              'param_grid': {'kernel':['rbf', 'sigmoid']} #'linear', 'poly', 
                             }
        
    if 'KNN' in models:
        import sklearn.neighbors
        models_dict['KNN'] = {'model': sklearn.neighbors.KNeighborsRegressor(),
                              'param_grid': {'n_neighbors':[5, 10, 100],
                                            'weights':['uniform','distance'],
                                            'algorithm':['ball_tree','kd_tree','brute']}
                             }
        
    if 'DecisionTree' in models:
        import sklearn.tree
        models_dict['DecisionTree'] = {'model':sklearn.tree.DecisionTreeRegressor(),
                                       'param_grid': {'criterion':     ['mse','friedman_mse','mae'],
                                                     'splitter':       ['best','random'],
                                                     'max_depth':      [None,5,10,100],
                                                     'max_features':   [None,0.25,0.5,0.75]}
                                      }
    if 'RandomForest' in models:
        import sklearn.ensemble
        models_dict['RandomForest'] = {'model': sklearn.ensemble.RandomForestRegressor(),
                                       'param_grid': {'criterion':      ['mse','mae'],
                                                      'n_estimators':  [10,100],
                                                      'max_depth':      [None,5,10],
                                                      'max_features':   [None,0.25,0.5,0.75]}
                                      }
    if 'GradBoost' in models:
        import sklearn.ensemble
        models_dict['GradBoost'] = {'model':sklearn.ensemble.GradientBoostingRegressor(),
                                    'param_grid':{'loss':['ls', 'lad', 'huber', 'quantile'],
                                                  'criterion':["friedman_mse",'mse','mae'],
                                                  'learning_rate':[0.01, 0.1, 1],
                                                  'n_estimators':[10, 100],
                                                  'subsample':[1.0,0.8,0.5],
                                                  'max_depth':[None, 5, 10]}
                                   }
                    
    if 'XGBoost' in models or 'xgboost' in models:                
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
        
    if 'DenseNet' in models:
        from .. import NeuralNet
        models_dict['DenseNet'] = NeuralNet.DenseNet.model_dict(n_features=n_features,
                                                                 n_labels = n_labels)
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
    """
    import sklearn
        
    models_dict = {}
    
    if 'Logistic' in models:
        models_dict['Logistic'] = {'model':sklearn.linear_model.LogisticRegression(),
                                     'param_grid': {'penalty': ['l1', 'l2', 'elasticnet']}
                                    }
    if 'SVM' in models:
        import sklearn.svm
        models_dict['SVM'] = {'model':sklearn.svm.SVC(probability=True),
                              'param_grid': {'kernel':['rbf', 'sigmoid'], #'linear', 'poly'
                                         }
                             }
    if 'KNN' in models:
        import sklearn.neighbors
        models_dict['SVM'] = {'model':sklearn.svm.SVC(probability=True),
                              'param_grid': {'kernel':['rbf', 'sigmoid'], #'linear', 'poly'
                                         }
                             }
        
    if 'DecisionTree' in models:
        import sklearn.tree
        models_dict['DecisionTree'] = {'model':sklearn.tree.DecisionTreeRegressor(),
                                       'param_grid': {'criterion':     ['mse','friedman_mse','mae'],
                                                      'splitter':       ['best','random'],
                                                     'max_depth':      [None,5,10,100],
                                                     'max_features':   [None,0.25,0.5,0.75]}
                                      }
    if 'RandomForest' in models:
        import sklearn.ensemble
        models_dict['RandomForest'] = {'model': sklearn.ensemble.RandomForestClassifier(),
                                   'param_grid':{'criterion':['gini','entropy'],
                                                 'n_estimators':  [10,100],
                                                 'max_depth':      [None,5,10],
                                                 'max_features':   [None,0.25,0.5,0.75]}
                                   }
    if 'GradBoost' in models:
        import sklearn.ensemble
        models_dict['GradBoost'] = {'model': sklearn.ensemble.GradientBoostingClassifier(),
                                'param_grid': {'loss':['deviance','exponential'],
                                              'criterion':["friedman_mse",'mse','mae'],
                                               'learning_rate':[0.01, 0.1, 1],
                                               'n_estimators':[10, 100],
                                               'subsample':[1.0,0.8,0.5],
                                               'max_depth':[None, 5, 10]}
                               }
                    
    if 'XGBoost' in models or 'xgboost' in models:                
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
        
    if 'DenseNet' in models:
        from .. import NeuralNet
        models_dict['DenseNet'] = NeuralNet.DenseNet.model_dict(n_features=n_features,
                                                                 n_labels = n_labels)
    return models_dict

