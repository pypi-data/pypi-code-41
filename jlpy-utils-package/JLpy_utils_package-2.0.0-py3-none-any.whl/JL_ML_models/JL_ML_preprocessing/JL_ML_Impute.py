import numpy as np
import pandas as pd

import sklearn.preprocessing

def categorical_features(df, 
                        headers_dict, 
                        strategy = 'most_frequent', 
                        estimator = None,
                        verbose= 0):
        """
        Impute (fill nan) values for categorical features

        Arguments:
            df: pandas dataframe. If strategy = 'iterative', then all categorical features must be label encoded in a previous step, with nan values remaining after encoding.
            strategy : The imputation strategy.
                - If If “constant”, then replace missing values with fill_value. Can be used with strings or numeric data. fill_value will be 0 when imputing numerical data and “missing_value” for strings or object data types.
                - If "most_frequent", then replace missing using the most frequent value along each column. Can be used with strings or numeric data.
                - If 'iterative', then use sklearn.imputer.IterativeImputer with the specified estimator
            estimator: sklearn estimator object
                The estimator to be used if 'iterative' strategy chosen
        Note: sklearn.impute.IterativeImputer has a number of other options which could be varied/tuned, but for simplicity we just use the defaults
        """
        warnings.filterwarnings('ignore')

        df = df.copy()
        headers_dict = headers_dict.copy()

        if strategy in ['most_frequent','constant']:
            Imputer = sklearn.impute.SimpleImputer(strategy=strategy,
                                                   verbose = verbose)

        if strategy == 'iterative':
            n_nearest_features = np.min([10, len(headers_dict['categorical_features'])]) #use less than or equal to 10 features
            Imputer = sklearn.impute.IterativeImputer(estimator= estimator, 
                                                      initial_strategy = 'most_frequent',
                                                      verbose = verbose,
                                                      n_nearest_features = n_nearest_features)
            
        #create a dummy nan row to ensure any dataset containing nan for any of the features can be transformed
        df_nans = pd.DataFrame(np.array([[np.nan for header in headers_dict['categorical_features']]]), 
                               columns =  headers_dict['categorical_features'])
        df_fit = pd.concat((df[headers_dict['categorical_features']],df_nans))
                
        Imputer.fit(df_fit)

        df[headers_dict['categorical_features']] = Imputer.transform(df[headers_dict['categorical_features']])


        #ensure imputation worked correctly
        for header in headers_dict['categorical_features']:
            assert(len(df[df[header].isna()])==0), 'Found nan value for '+ header +' after imputing'

        warnings.filterwarnings('default')
        return df, headers_dict, Imputer

def continuous_features(df, 
                        headers_dict, 
                        strategy = 'median', 
                        estimator = None,
                        verbose= 0):
    """
    Impute (fill nan) values for continuous features

    Arguments:
        df: pandas dataframe. If strategy = 'iterative', then all categorical features must be label encoded in a previous step, with nan values remaining after encoding.
        strategy : The imputation strategy.
            - If If “constant”, then replace missing values with fill_value. fill_value will be 0 when imputing numerical data.
            - If "most_frequent", then replace missing using the most frequent value along each column.
            - If 'iterative', then use sklearn.imputer.IterativeImputer with the specified estimator
        estimator: sklearn estimator object
            The estimator to be used if 'iterative' strategy chosen
        Note: sklearn.impute.IterativeImputer has a number of other options which could be varied/tuned, but for simplicity we just use the defaults
    """
    warnings.filterwarnings('ignore')
    df = df.copy()
    headers_dict = headers_dict.copy()

    if strategy in ['most_frequent', 'constant', 'mean', 'median']:
        Imputer = sklearn.impute.SimpleImputer(strategy=strategy,
                                               verbose = verbose)
    if strategy == 'iterative':
        n_nearest_features = np.min([10, len(headers_dict['continuous_features'])]) 
        Imputer = sklearn.impute.IterativeImputer(estimator= estimator, 
                                                  initial_strategy = 'most_frequent',
                                                  verbose = verbose,
                                                  n_nearest_features = n_nearest_features)
    #create a dummy nan row to ensure any dataset containing nan for any of the features can be transformed
    df_nans = pd.DataFrame(np.array([[np.nan for header in headers_dict['continuous_features']]]), 
                           columns =  headers_dict['continuous_features'])
    df_fit = pd.concat((df[headers_dict['continuous_features']],df_nans))

    Imputer.fit(df_fit)

    df[headers_dict['continuous_features']] = Imputer.transform(df[headers_dict['continuous_features']])

    #ensure imputation worked correctly
    for header in headers_dict['continuous_features']:
        assert(len(df[df[header].isna()])==0), 'Found nan value for '+ header +' after imputing'

    warnings.filterwarnings('default')
    return df, headers_dict, Imputer

def fetch_iterative_estimators_dict(n_features):
    #focus on BayesianRidge (sklearn default) and RandomForest, since they generally perform better than simple linear or DecisionTree and scale better than KNN
    if n_features > 1000:
        max_features = 1000/n_features
    else:
        max_features = 'auto'

    iterative_estimators_dict = {'BayesianRidge':sklearn.linear_model.BayesianRidge(),
                                 'RandomForestRegressor':sklearn.ensemble.RandomForestRegressor(n_jobs=-1,
                                                                                                max_features= max_features)}

    #sklearn.linear_model.LinearRegression(n_jobs=-1), 
    #sklearn.neighbors.KNeighborsRegressor(n_jobs=-1)
    #sklearn.tree.DecisionTreeRegressor(),

    return iterative_estimators_dict

def validation_test(df, headers_dict, verbose =1 ):
    """
    Iterate over impute_categorical_feature and impute_continuous_features options & ensure everything works for this particular dataset
    """

    print('------running impute.continuous_features validation-------')
    for strategy in ['mean','median','iterative']:
        print('strategy:',strategy,)

        if strategy in ['most_frequent','mean','median']:
            df_imputed, headers_dict, Imputer = Impute.continuous_features(df, 
                                                                        headers_dict, 
                                                                        strategy = strategy, 
                                                                        estimator = None,
                                                                        verbose = verbose)
        else:
            iterative_estimators_dict = Impute.fetch_iterative_estimators_dict()
            for estimatorID in iterative_estimators_dict.keys():
                print('estimator:',estimatorID)

                df_imputed, headers_dict, Imputer = Impute.continuous_features(df, 
                                                                        headers_dict, 
                                                                        strategy = strategy, 
                                                                        estimator = iterative_estimators_dict[estimatorID],
                                                                        verbose = verbose)

    print('------running impute.categorical_features validation-------')
    for strategy in ['most_frequent', 'iterative']:
        print('strategy:',strategy,)

        if strategy == 'most_frequent':
            df_imputed, headers_dict, Imputer = Impute.categorical_features(df, 
                                                                headers_dict, 
                                                                strategy = strategy, 
                                                                estimator = None,
                                                                verbose = verbose)
        else:
            for estimator in impute.fetch_typical_iterative_estimators():
                print('estimator:',estimator)

                df_imputed, headers_dict, Imputer = Impute.categorical_features(df, 
                                                                    headers_dict, 
                                                                    strategy = strategy, 
                                                                    estimator = estimator,
                                                                    verbose = verbose)




    print('\nall imputation options validated!')