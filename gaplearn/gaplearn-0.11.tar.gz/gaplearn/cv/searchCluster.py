# Things to add
    # Make sure that if n parameter sets are chosen, the n functions as a max and doesn't throw an error when there are fewer than n parameter sets in total

import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score, f1_score, accuracy_score
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from .utilities import unique_array, isiter
import random

class SearchCluster:

    def __init__(self):
        self.gs_complete = False

    def search_cluster(self, model, param_grid, X, cols = None, fit_function = None, label_function = None, centroid_function = None, score_function = None, metric_name = 'score', random = None, centroid = False, verbose = 0):
        
        if fit_function == None:
            def fit_function(model, params, X):
                model(**params).fit(X)
                return model

        if label_function == None:
            def label_function(model):
                labels = model.labels_
                return labels

        if centroid_function == None:
            def centroid_function(model):
                cluster_centers = model_test.cluster_centers_
                return cluster_centers

        if score_function == None:
            metric_name = 'silhouette score'
            def score_function(X, labels):
                s_score = silhouette_score(X, labels)
                return s_score

        # Format X
        isiter(X, 'X')
        if len(X.shape) != 2:
            raise TypeError('X is not a 2D array')
        if cols == None:
            try:
                cols = list(X.columns)
            except:
                cols = ['feature_{}'.format(i) for i in range(X.shape[1])]
        else:
            isiter(cols, 'cols')
        X = np.array(X)

        # Get parameter sets
        import itertools as it
        keys = sorted(param_grid)
        combinations = list(it.product(*(param_grid[key] for key in keys)))
        param_grid = []
        for combo in combinations:
            combo_dict = {}
            for i in range(len(combo)):
                combo_dict[keys[i]] = combo[i]
            param_grid.append(combo_dict)
        if verbose > 0 and random == None:
            print('Number of parameter sets: {:,}'.format(len(param_grid)))

        # Select a random subset of the parameter sets
        if random != None:
            if type(random) == int:
                param_grid = [random.choice(param_grid) for i in range(random)]
            elif type(random) == float:
                random = int(random * len(param_grid))
                param_grid = [random.choice(param_grid) for i in range(random)]
            else:
                raise ValueError('Parameter `random` must be a float or int')
            if verbose > 0:
                print('Number of parameter sets: {:,}'.format(len(param_grid)))

        # Calculate results for each param set
        scores = []
        models = []
        if centroid:
            cluster_centers = []
        for i, param_set in enumerate(param_grid):
            if verbose > 0:
                print('\nNow working on param set {:,}'.format(i))
                print(param_set)
            model_test = fit_function(model = model, params = param_set, X = X_trn, y = y_trn)
            labels = label_function(model)
            n_labels = len(unique_array(labels))
            labels_df['labels_{}'.format(i)] = labels
            # Calculate Silhouette Score
            if n_labels > 1 and n_labels < len(labels):
                score = score_function(X, labels)
            else:
                score = -1
            scores.append(score)
            models.append(model_test)
            if centroid:
                cluster_centers.append(centroid_function(model))
        param_results = pd.DataFrame({'param set': param_grid, score_name: scores, index = range(len(param_grid))})
        if centroid:
            param_results['cluster centers'] = cluster_centers
        best_m_id = param_results.sort_values(score_name, ascending = False).iloc[0]['index']

        self.score_name
        self.best_model = models[best_m_id]
        self.best_params = labels_df.iloc[best_m_id]['params'].values[0]
        self.labels_df = labels_df
        self.param_results = param_results
        self.models = models
        self.gs_complete = False

    def get_best_model(self, return_scores = False):
        if return_scores:
            best_model_df = self.sort_values(self.score_name, ascending = False).iloc[0]
            return self.best_model, best_model_df
        return self.best_model

    def get_best_models(self, n = 1, return_scores= False):
        best_model_df = self.sort_values(self.score_name, ascending = False).iloc[:n]
        best_model_ids = best_model_df['index']
        best_models = [self.models[i] for i in best_model_ids]
        if return_scores:
            return best_models, best_model_df
        return best_models

    def get_best_params(self):
        return self.best_params

    def get_labels(self):
        return self.labels_df

    def get_param_results(self):
        return self.param_results