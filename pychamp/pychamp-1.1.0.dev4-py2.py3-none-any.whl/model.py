"""
    Date        : 2019-07-25
    Author      : Sagar Paudel
    Description : This module is designed to perform classification problems.
"""

# Importing libraries
from imblearn.over_sampling import SMOTE
from imblearn.over_sampling import SMOTENC
from logger import logger
import numpy as np
import operator
import os
import pandas as pd
import pickle
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

# Pandas confuration
pd.options.mode.chained_assignment = None


class Classification(object):
    def __init__(self, cat_features=None, num_features=None,
                 label=None, exclude=None, sampling_percent=0.5,
                 test_size=0.30, cv=5, model="RandomForest",
                 model_path="current_directory",
                 cm_labels=[1, 0]):

        try:
            self.__label = label
            self.__cat_features = cat_features
            self.__num_features = num_features
            self.__exclude = exclude
            self.__sampling_percent = sampling_percent
            self.__test_size = test_size
            self.__cv = cv
            self.__cm_labels = cm_labels
            self.__model = model
            self.__model_path = model_path

            if self.__cat_features is None and self.__num_features is None:
                raise Exception("Please specify num_features or cat_features!!")

        except Exception as e:
            raise Exception(e)


    def train(self, df):
        if self.__label is None:
            raise Exception("Please specify label!!")
        try:
            self.__df = df

            try:
                # Filtering only given columns
                self.__filter_data()
            except Exception as e:
                raise Exception(e)

            try:
                # Cleaning data
                self.__clean_data()
            except Exception as e:
                raise Exception(e)

            self.__df_y = self.__df[self.__label]
            self.__df_X = self.__df.drop(self.__label, axis=1)

            del self.__df

            # Sampling
            label_counts = self.__df_y.value_counts().reset_index()
            label_counts = dict(zip(label_counts.iloc[:, 0],
                                    label_counts.iloc[:, 1]))
            max_key = max(label_counts.items(), key=operator.itemgetter(1))[0]
            min_key = [key for key in label_counts.keys() if key != max_key][0]

            self.__sampling_threshold = int(label_counts[max_key]*self.__sampling_percent)

            try:
                if self.__sampling_threshold > label_counts[min_key]:
                    label_counts[min_key] = self.__sampling_threshold
                    self.__sample(label_counts)
            except Exception as e:
                raise Exception(e)

            # Encoding
            try:
                if self.__cat_features is not None:
                    self.__encoding()
            except Exception as e:
                raise Exception(e)

            try:
                # Features Importance
                self.__import_features()
            except Exception as e:
                raise Exception(e)

            try:
                # Overall accuracy
                self.__accuracy()
            except Exception as e:
                raise Exception(e)

            try:
                # Splitting train and test dataset
                self.__split_train_test()
            except Exception as e:
                raise Exception(e)

            try:
                # Building model
                self.__build_model()
            except Exception as e:
                raise Exception(e)

            try:
                # Finding statistical summary
                self.__statistical_summary()
            except Exception as e:
                raise Exception(e)

        except Exception as e:
            logger.error(e)
            raise Exception(e)

    def __build_model(self):
        try:
            logger.info("Building {} model with hyperparameter tuning.."
                        .format(self.__model))

            if self.__model == "RandomForest":
                clf = RandomForestClassifier()

                grid_param = {'n_estimators': [50, 100, 200]}

                """
                grid_param = {'n_estimators': [50, 100, 200],
                              'criterion': ['gini', 'entropy'],
                              'bootstrap': [True, False],
                              'max_depth': [5, 10, 15]}
                """

            elif self.__model == "XGBoost":
                clf = GradientBoostingClassifier()
                grid_param = {"learning_rate": [0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
                              "max_depth": [3, 4, 5, 6, 8, 10, 12, 15],
                              }

            elif self.__model == "AdaBoost":
                clf = AdaBoostClassifier()
                grid_param = {'n_estimators': [500, 1000, 2000],
                              'learning_rate': [0.001, 0.01, 0.1]
                              }

            elif self.__model == "SVM":
                clf = SVC(probability=True)
                grid_param = [
                    {'kernel': ['rbf'], 'gamma': [1e-2, 1e-3, 1e-4, 1e-5],
                     'C': [0.001, 0.10, 0.1, 10, 25, 50, 100, 1000]},
                    {'kernel': ['sigmoid'], 'gamma': [1e-2, 1e-3, 1e-4, 1e-5],
                     'C': [0.001, 0.10, 0.1, 10, 25, 50, 100, 1000]},
                    {'kernel': ['linear'],
                     'C': [0.001, 0.10, 0.1, 10, 25, 50, 100, 1000]
                     }]

            self.__model_grid_search = GridSearchCV(
                estimator=clf, param_grid=grid_param, scoring='accuracy',
                cv=self.__cv, n_jobs=-1, verbose=1)
            self.__model_grid_search.fit(X=self.__X_train.values,
                                         y=self.__y_train.values)

            # Saving model
            self.__save_load_model("save")

            self.best_parameters = self.__model_grid_search.best_params_
            self.best_estimator = self.__model_grid_search.best_estimator_
            self.best_score = self.__model_grid_search.best_score_
            y_pred = self.__model_grid_search.predict(self.X_test.values)
            y_prob = self.__model_grid_search.predict_proba(self.X_test.values)
            y_prob = [j[i] for i, j in zip(y_pred, y_prob)]

            if self.__exclude is not None:
                for col in self.__exclude:
                    self.X_test[col] = self.__X_test_excluded[col]

            self.X_test.loc[:, "y"] = self.__y_test
            self.X_test.loc[:, "y_pred"] = y_pred
            self.X_test.loc[:, "probability"] = y_prob

            del self.__X_test_excluded
            del self.__X_train
            del self.__y_train
            del self.__y_test
            logger.info("Successfull..")

        except Exception as e:
            raise Exception(e)

    def __filter_data(self):
        try:
            logger.info("Filtering data..")
            features = []
            if self.__label is not None:
                label_y = [self.__label]
            else:
                label_y = None

            self.__features_type = [self.__cat_features, self.__num_features,
                                    self.__exclude, label_y]

            for feature in self.__features_type:
                if type(feature) == list:
                    features = features + feature

            self.__df = self.__df[features]

            logger.info("Successfull.")
        except Exception as e:
            raise Exception(e)

    def predict(self, df):
        try:
            self.__df = df

            try:
                # Filtering only given columns
                self.__filter_data()
            except Exception as e:
                raise Exception(e)

            try:
                # Cleaning data
                self.__clean_data()
            except Exception as e:
                raise Exception(e)

            if self.__exclude is not None:
                self.__df_exclude = self.__df[self.__exclude]
                self.__df_X = self.__df.drop(columns=self.__exclude, axis=1)
            else:
                self.__df_X = self.__df

            del self.__df

            try:
                # Saving model
                self.__save_load_model("load")
            except Exception as e:
                raise Exception(e)

            # Encoding
            try:
                if self.__cat_features is not None:
                    self.__encoding()
            except Exception as e:
                raise Exception(e)

            logger.info("Predicting result..")
            y_pred = self.__model_grid_search.predict(self.__df_X.values)
            y_prob = self.__model_grid_search.predict_proba(self.__df_X.values)
            y_prob = [j[i] for i, j in zip(y_pred, y_prob)]
            logger.info("Successfull.")

            del self.__df_X

            if self.__exclude is not None:
                self.X_test = self.__df_exclude
                self.X_test["y_pred"] = y_pred
                self.X_test["probability"] = y_prob

                del self.__df_exclude

            else:
                self.X_test = pd.DataFrame(y_pred, columns=["y_pred"])
                self.X_test["probability"] = y_prob
        except Exception as e:
            logger.error(e)
            raise Exception(e)

    def __accuracy(self):
        try:
            logger.info("Finding accuracy with cv={}..".format(self.__cv))
            if self.__exclude is not None:
                df_X_excluded = self.__df_X.drop(
                    columns=self.__exclude, axis=1)
            else:
                df_X_excluded = self.__df_X

            clf = RandomForestClassifier(n_estimators=100)
            all_accuracies = cross_val_score(
                estimator=clf, X=df_X_excluded.values,
                y=self.__df_y.values, cv=self.__cv)
            self.accuracy = pd.DataFrame(all_accuracies,
                                         columns=["Accuracy"]).reset_index()
            self.accuracy.columns = ["Iteration", "Accuracy"]

            del df_X_excluded
            logger.info("Successfull.")
        except Exception as e:
            raise Exception(e)

    def __sample(self, ratio):
        try:
            logger.info("Performing sampling operations..")
            if self.__num_features is None:
                logger.info("Sampling for categorial features is not supported!!")
            else:
                cols = []
                features = [self.__cat_features, self.__exclude, self.__num_features]
                for feature in features:
                    if type(feature) == list:
                        cols = cols + feature

                if self.__cat_features is not None or self.__exclude is not None:
                    CAT_FLAG = True
                else:
                    CAT_FLAG = False

                if CAT_FLAG:
                    self.__df_X = self.__df_X[cols]
                    cat_features_range = len(cols) - len(self.__num_features)

                    sampling = SMOTENC(categorical_features=
                                       [i for i in range(cat_features_range)],
                                       sampling_strategy=ratio, random_state=42,
                                       k_neighbors=5, n_jobs=-1)
                else:
                    sampling = SMOTE(ratio=ratio, n_jobs=-1, random_state=42)

                self.__df_X, self.__df_y = sampling.fit_resample(self.__df_X,
                                                                 self.__df_y)
                self.__df_X = pd.DataFrame(self.__df_X, columns=cols)
                self.__df_y = pd.Series(self.__df_y)
                logger.info("Successfull.")
        except Exception as e:
            raise Exception(e)

    def __import_features(self):
        try:
            logger.info("Finding features importance..")
            if self.__model == "RandomForest":
                clf = RandomForestClassifier(n_estimators=100)
            elif self.__model == "XGBoost":
                clf = GradientBoostingClassifier()
            elif self.__model == "AdaBoost":
                clf = AdaBoostClassifier()
            elif self.__model == "SVM":
                clf = SVC()

            if self.__exclude is not None:
                df_X_excluded = self.__df_X.drop(
                    columns=self.__exclude, axis=1)
            else:
                df_X_excluded = self.__df_X

            clf.fit(df_X_excluded.values, self.__df_y.values)
            self.features_importance = pd.DataFrame(
                {'FEATURE': df_X_excluded.columns,
                 'IMPORTANCE': np.round(clf.feature_importances_, 3)})

            self.features_importance.sort_values('IMPORTANCE',
                                                 ascending=False, inplace=True)

            del df_X_excluded
            logger.info("Successfull.")
        except Exception as e:
            raise Exception(e)

    def __encoding(self):
        try:
            if self.__cat_features is not None:
                logger.info("Encoding categorial features..")
                self.__df_X = pd.get_dummies(self.__df_X,
                                             columns=self.__cat_features)
                logger.info("Successfull.")
        except Exception as e:
            raise Exception(e)

    def __split_train_test(self):
        try:
            logger.info("Splitting train and test set of size {}.."
                        .format(self.__test_size))
            self.__X_train, self.X_test, self.__y_train, self.__y_test = (
                train_test_split(self.__df_X, self.__df_y,
                                 test_size=self.__test_size, random_state=42))

            if self.__exclude is not None:
                self.__X_test_excluded = self.X_test[self.__exclude]

            self.__X_train.drop(columns=self.__exclude, axis=1, inplace=True)
            self.X_test.drop(columns=self.__exclude, axis=1, inplace=True)

            del self.__df_X
            del self.__df_y
            logger.info("Successfull.")
        except Exception as e:
            raise Exception(e)

    def __clean_data(self):
        try:
            logger.info("Cleaning data..")
            df_null = self.__df.isnull().sum().reset_index()
            if not df_null[df_null.iloc[:, 1] > 0].empty:
                logger.info("Missing values info:")
                logger.info(df_null[df_null.iloc[:, 1] > 0])
                logger.info("Dropping null values..")
                self.__df.dropna(axis=0, how="any", inplace=True)

            if self.__df.shape[0] == 0:
                raise Exception("No records obtained after null values remove..")
            logger.info("Successfull.")

        except Exception as e:
            raise Exception(e)

    def __save_load_model(self, action="save"):
        try:
            if self.__model_path == "current_directory":
                self.__model_path = "models/"
                if not os.path.isdir(self.__model_path):
                    os.mkdir(self.__model_path)

            model_name = self.__model + ".pkl"
            full_model_path = self.__model_path + model_name
            if action == "save":
                logger.info("Saving model..")
                pickle.dump(self.__model_grid_search,
                            open(full_model_path, 'wb'))
                logger.info("Successfull.")

            elif action == "load":
                if os.path.isfile(full_model_path):
                    logger.info("Loading model..")
                    self.__model_grid_search = pickle.load(
                        open(full_model_path, 'rb'))
                    logger.info("Successfull.")
                else:
                    raise Exception("Model not found in the {} location!!"
                                    .format(full_model_path))
        except Exception as e:
            raise Exception(e)

    def __statistical_summary(self):
        try:
            logger.info("Calculating statistical summary..")
            self.cm = confusion_matrix(
                y_true=self.X_test["y"], y_pred=self.X_test["y_pred"],
                labels=self.__cm_labels)
            tp, fp, fn, tn = self.cm.ravel()
            self.df_cm = pd.DataFrame(self.cm, columns=self.__cm_labels,
                                      index=self.__cm_labels)
            self.accuracy_score = round((tp+tn)/(tp+tn+fp+fn), 4)
            self.error_rate = round((fp+fn)/(tp+tn+fp+fn), 4)
            self.recall = self.sensitivity = round(tp/(tp+fn), 4)
            self.precision = round(tp/(tp+fp), 4)
            self.f_measure = round((2*self.recall*self.precision)/(
                self.recall+self.precision), 4)
            logger.info("Successfull.")
        except Exception as e:
            raise Exception(e)


class Regression(object):
    def __init__(self):
        pass


class Clustering(object):
    def __init__(self):
        pass


class Miscellaneous(object):
    def __init(self):
        pass
