import pandas as pd
import numpy as np
from eli5.permutation_importance import get_score_importances
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier as RFC
import datetime
from .utilities import checkpoint, isiter

class SFS:

    def __init__(self):
        self.complete_be = False

    def kfold_model_perm(self, X, y, model, params, cols, indices, fit_function, predict_function, score_function, folds = 5, verbose = 0):

        kfold = KFold(folds, True)
        best_model_output = pd.DataFrame()
        fold_num = 0
        perm_df = pd.DataFrame()
        for trn, test in kfold.split(X):
            if verbose >= 2:
                print('Working on fold', fold_num)
            X_trn = X[trn, :]
            X_test = X[test, :]
            y_trn = y[trn]
            y_test = y[test]
            model = fit_function(model = model, X = X_trn, y = y_trn)
            preds = predict_function(model = model, X = X_test)
            score = score_function(y = y, preds = preds)
            df_dict = {
                       'pred': preds,
                       'actual': y_test,
                       'test_ind': test,
                       'fold_num': pd.Series([fold_num for i in range(y_test.shape[0])]),
                       score_name: pd.Series([score for i in range(y_test.shape[0])])
                      }

            def score(X, y):
                preds = predict_function(model = model, X = X_test)
                score = score_function(y = y, preds = preds)
                return score

            base_score, score_decreases = get_score_importances(score, X, y)
            feature_importances = np.mean(score_decreases, axis=0)

            best_model_output_temp = pd.DataFrame(df_dict)        
            best_model_output = pd.concat([best_model_output, best_model_output_temp])
            
            perm_df_temp = pd.DataFrame({
                                         'importance': feature_importances,
                                         'feature': cols,
                                         'index': indices,
                                         'fold': [fold_num for i in range(len(cols))]
                                        })
            perm_df_temp = perm_df_temp.sort_values('importance', ascending = False)
            
            perm_df = pd.concat([perm_df, perm_df_temp])

            fold_num += 1

        return best_model_output, perm_df

    def backwards_elimination(self, X, y, model, params = {}, fit_function = None, predict_function = None, score_function = None, score_name = 'score', cols = None, verbose = 0):

        if fit_function == None:
            def fit_function(model, X, y):
                model.fit(X, y)
                return model

        if predict_function == None:
            def predict_function(model, X):
                preds = model.predict(X)
                return preds

        if score_function == None:
            score_name = 'accuracy'
            def score_function(y, preds):
                # preds = model.predict(X)
                accuracy = sum([preds[i] == y[i] for i in range(y.shape[0])]) / y.shape[0]
                return accuracy

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

        # Format y
        isiter(y, 'y')
        if len(y.shape) > 2:
            raise TypeError('y has too many dimensions. The shape of y shold be (n, 1) or (n,).')
        elif len(y.shape) == 2:
            if y.shape[1] == 1:
                y = np.array([x[0] for x in y])
            else:
                raise TypeError('The shape of y shold be (n, 1) or (n,).')
        else:
            y = np.array(y)

        score_df = pd.DataFrame()
        cols_l = []
        indices = list(range(X.shape[1]))
        removed_features = []
        removed_indices = []
        begin_all = datetime.datetime.today()
        for i in range(X.shape[1]):
            if verbose >= 1:
                print('\n#### Working on step {:,} ####'.format(i))
                begin = datetime.datetime.today()
                print(begin)
            cols_l.append(cols.copy())
            # Getting permutation importances
            df_perm, perm_df = self.kfold_model_perm(X[:, indices], y, cols = cols, indices = indices, params = params, model = model, fit_function =fit_function, predict_function = predict_function, score_function = score_function, verbose = verbose)
            df_perm.insert(0, 'step', i)
            df_perm.insert(1, 'features used', [cols for i in range(df_perm.shape[0])])
            if verbose >= 1:
                current = datetime.datetime.today()
                checkpoint(current, begin)
                print(current)
                # Ranking features by importances and determining which to remove
                print('Ranking features by importances and determining which to remove...')
            worst_feature = perm_df.groupby(['feature', 'index']).mean()['importance'].reset_index().rename(columns = {'importance': 'mean importance'}).sort_values('mean importance').iloc[0]
            feature_to_remove = worst_feature['feature']
            index_to_remove = worst_feature['index']
            if verbose >= 1:
                print('Removing {}'.format(feature_to_remove))
            cols.remove(feature_to_remove)
            indices.remove(index_to_remove)
            removed_features.append(feature_to_remove)
            df_perm.insert(2, 'feature to remove', feature_to_remove)
            # Determining score for the set
            if verbose >= 1:
                print('Determining {} for the set...'.format(score_name))
            iter_score = df_perm.groupby('fold_num').first()[score_name].reset_index().T
            iter_score.columns = ['fold {} {}'.format(iteration, score_name) for iteration in range(iter_score.shape[1])]
            overall_score = df_perm.groupby('fold_num').first()[score_name].mean()
            if verbose >= 1:
                print('Overall Accuracy: {}%'.format(round(overall_score * 100, 2)))
            iter_score.insert(0, 'overall {}'.format(score_name), overall_score)
            iter_score.insert(0, 'step', i)
            score_df = pd.concat([score_df, iter_score])
            if verbose >= 1:
                print('Finished iteration. Total time elapsed:')
                current = datetime.datetime.today()
                checkpoint(current, begin_all)

        if verbose >= 1:
            print('\nPrepping final output...')

        score_df_original = score_df.copy()
        score_df = score_df_original.copy()
        score_df = score_df.reset_index()
        score_df = score_df[score_df['index'] != 'fold_num']
        score_df.insert(2, 'features used', cols_l)
        score_df.insert(3, 'feature to remove', removed_features)
        score_df = score_df.drop('index', axis = 1)
        score_df.index = list(range(len(score_df)))

        self.results_be = df_perm
        self.summary_be = score_df
        self.complete_be = True
        self.features_be = sorted(list(removed_features))
        self.score_name = score_name

    def get_summary_be(self):
        if self.complete_be:
            return self.summary_be
        else:
            raise Exception('`backwards_elimination` has not yet been run')

    def get_results_be(self):
        if self.complete_be:
            return self.results_be
        else:
            raise Exception('`backwards_elimination` has not yet been run')

    def get_features_be(self):
        if self.complete_be:
            return self.features_be
        else:
            raise Exception('`backwards_elimination` has not yet been run')

    def get_set_by_score_be(self, min_score = None, num_steps = 'all'):
        summary = self.summary_be
        overall_score_name = 'overall {}'.format(self.score_name)
        if min_score != None:
            summary = summary[summary[overall_score_name] > min_score].sort_values(overall_score_name, ascending = False)
            summary.index = range(len(summary))
        if num_steps != 'all':
            summary = summary[:num_steps]
        return summary

    def get_set_by_features_be(self, num_features, max_features = None):
        summary = self.summary_be
        overall_score_name = 'overall {}'.format(self.score_name)
        if max_features == None:
            summary = summary.iloc[-num_features]
        else:
            if max_features <= num_features:
                raise ValueError('`max_features` cannot be less than or equal to `num_features`')
            summary = summary[num_features:(max_features+1)]
        return summary