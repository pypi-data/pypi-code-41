"""
fetch dictionaries containing sklearn model objects and relevant hyperparameter grid dictionaries for regression or classification models.
"""

import sklearn, sklearn.linear_model, sklearn.tree, sklearn.neighbors
import sys, os

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0,  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))


def regression(n_features=None, n_labels=None, NeuralNets=False, verbose = 0):
    """
    Fetch dictionary of standard regression models and their 'param_grid' dictionaries. Standard models are scit-kit learn based objects, while Neural Nets are keras+tensorflow based
    
    Arguments: 
        n_features, n_labels: The number of features and labels used for the model. These parameters are only required if NeuralNets == True
        NeuralNets: boolean. Whether or not to fetch the neural net models + param_grid
    """
        
    models_dict = {}
    
    models_dict['Linear'] = {'model':sklearn.linear_model.LinearRegression(),
                             'param_grid': {'normalize': [False,True]}
                            }

    models_dict['DecisionTree'] = {'model':sklearn.tree.DecisionTreeRegressor(),
                                   'param_grid': {'criterion':     ['mse','friedman_mse','mae'],
                                                 'splitter':       ['best','random'],
                                                 'max_depth':      [None,5,10,100],
                                                 'max_features':   [None,0.25,0.5,0.75],
                                                 'max_leaf_nodes': [None,10,100]}
                                  }

    models_dict['RandomForest'] = {'model': sklearn.ensemble.RandomForestRegressor(verbose = verbose),
                                   'param_grid': {'n_estimators':  [10,100,1000],
                                                 'criterion':      ['mse','mae'],
                                                 'max_depth':      [None,5,10,100],
                                                 'max_features':   [None,0.25,0.5,0.75],
                                                 'max_leaf_nodes': [None,10,100]}}

    models_dict['GradBoost'] = {'model':sklearn.ensemble.GradientBoostingRegressor(verbose = verbose),
                                'param_grid':{'loss':['ls', 'lad', 'huber', 'quantile'],
                                              'learning_rate':[0.01, 0.1, 1],
                                              'n_estimators':[10, 100, 1000],
                                              'subsample':[1.0,0.8,0.5],
                                              'criterion':["friedman_mse",'mse','mae'],
                                              'max_depth':[None, 5, 10]}
                               }

    models_dict['SVM'] = {'model':sklearn.svm.SVR(verbose = verbose),
                          'param_grid': {'kernel':['linear', 'poly', 'rbf', 'sigmoid']
                                        }
                         }

    models_dict['KNN'] = {'model': sklearn.neighbors.KNeighborsRegressor(),
                          'param_grid': {'n_neighbors':[5, 10, 100],
                                        'weights':['uniform','distance'],
                                        'algorithm':['ball_tree','kd_tree','brute']}}

    if NeuralNets:
        import JL_NeuralNet as NeuralNet
        models_dict['DenseNet'] = NeuralNet.DenseNet.model_dict(n_features=n_features,
                                                                 n_labels = n_labels)
    return models_dict


def classification(n_features=None, n_labels=None, NeuralNets=False, verbose = 0):
    
    """
    Fetch dictionary of standard classification models and their 'param_grid' dictionaries. Standard models are scit-kit learn based objects, while Neural Nets are keras+tensorflow based
    
    Arguments: 
        n_features, n_labels: The number of features and labels used for the model. These parameters are only required if NeuralNets == True
        NeuralNets: boolean. Whether or not to fetch the neural net models + param_grid
    """
    models_dict = {}
    models_dict['DecisionTree'] = {'model':sklearn.tree.DecisionTreeClassifier(),
                                   'param_grid': {'criterion':['gini','entropy'],
                                                  'max_depth':[None,1,10,100],
                                                  'max_features':[None,0.25,0.5,0.75],
                                                  'max_leaf_nodes':[None,10,100]}
                                  }
    
    models_dict['RandomForest'] = {'model': sklearn.ensemble.RandomForestClassifier(verbose = verbose),
                                   'param_grid':{'n_estimators':[10,100,1000],
                                                  'criterion':['gini','entropy'],
                                                  'max_depth':[None,1,10,100],
                                                   'max_leaf_nodes':[None,10,100]}
                                   }
    
    models_dict['GradBoost'] = {'model': sklearn.ensemble.GradientBoostingClassifier(verbose = verbose),
                                'param_grid': {'loss':['deviance','exponential'],
                                              'learning_rate':[0.01, 0.1, 1],
                                              'n_estimators':[10, 100, 1000],
                                              'subsample':[1.0,0.8,0.5],
                                              'criterion':["friedman_mse",'mse','mae'],
                                              'max_depth':[None, 5, 10]}
                               }
    
    models_dict['SVM'] = {'model':sklearn.svm.SVC(probability=True, verbose = verbose),
                          'param_grid': {'kernel':['linear', 'poly', 'rbf', 'sigmoid'],
                                         'gamma':['auto','scale']}
                         }
    
    models_dict['KNN'] = {'model': sklearn.neighbors.KNeighborsClassifier(),
                          'param_grid': {'n_neighbors':[5,10,100],
                                         'weights':['uniform','distance'],
                                         'algorithm':['ball_tree','kd_tree','brute']}
                         }
    if NeuralNets:
        import JL_NeuralNet as NeuralNet
        models_dict['DenseNet'] = NeuralNet.DenseNet.model_dict(n_features=n_features,
                                                                 n_labels = n_labels)
    return models_dict