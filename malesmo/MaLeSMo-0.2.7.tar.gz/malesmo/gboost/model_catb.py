import os
import dill
from copy import deepcopy
from collections import defaultdict

from jsondler import JsonEntry
import numpy as np
import pandas as pd
from malemba import ArrayModelBase
from catboost import CatBoost


NUM_THREADS = 4


class ModelCatBoost(ArrayModelBase):

    def __init__(self, params=None, **kwargs):
        self.model = CatBoost(params=params)
        self.cat_features = set()
        super(ModelCatBoost, self).__init__(params=params, **kwargs)

    def fit(self, X, Y, **kwargs):
        """
        :param X: list or iterator of dicts with features {feat1: v1, feat2: v2, ...}
        :param Y: list of labels
        """
        X = self.get_cat_features(X=X)
        print("got categorial features")
        X, Y, data_shape = super(ModelCatBoost, self).fit(X=X, Y=Y, **kwargs)
        print("got features array shape")
        data = self.np_array(X, data_shape, low_memory=self.low_memory)
        self.model.fit(X=pd.DataFrame(data).values,
                       y=np.array(list(Y)),
                       cat_features=sorted([self._features[feat] for feat in self.cat_features]))

    def predict(self, X, **kwargs):
        """
        :param X: list or iterator of dicts with features {feat1: v1, feat2: v2, ...}
        :return: list of dicts with labels scores
        """
        X = self.get_cat_features(X=X)
        print("got categorial features")
        X, data_shape = super(ModelCatBoost, self).predict(X=X, **kwargs)
        print("got features array shape")
        data = self.np_array(X, data_shape)
        return list(map(lambda p: dict((self.labels[i],
                                        p[i]**(1.0/self.label_weights[self.labels[i]])) for i in range(len(p))),
                        self.model.predict(data=pd.DataFrame(data).values, prediction_type="Probability")))

    def dump(self, scheme_path, **kwargs):
        if not os.path.exists(scheme_path):
            os.makedirs(scheme_path)
        model = self.__dict__.pop("model")
        meta_f = open(os.path.join(scheme_path, "meta.m"), "wb")
        dill.dump(self.__dict__, meta_f)
        meta_f.close()
        self.model = model

        self.model.save_model(fname=os.path.join(scheme_path, "model.m"), format="cbm")

    @classmethod
    def load(cls, scheme_path, params=None, **kwargs):
        model_catboost = cls(params=params, **kwargs)
        with open(os.path.join(scheme_path, "meta.m"), "rb") as meta_f:
            model_catboost.__dict__ = dill.load(meta_f)
        if params is not None:
            if model_catboost.params is not None:
                model_catboost.params.update(params)
            else:
                model_catboost.params = params
        model_catboost.model = CatBoost(params=model_catboost.params)
        model_catboost.model.load_model(fname=os.path.join(scheme_path, "model.m"), format="cbm")
        return model_catboost

    @staticmethod
    def _convert_str_to_factors():
        return False

    @property
    def num_threads(self):
        return self.params.get("thread_count", NUM_THREADS)

    def get_cat_features(self, X):
        for x in X:
            x_cat = dict()
            for feat in x:
                if type(x[feat]) in (str, np.str, np.str_):
                    self.cat_features.add(feat)
                if type(x[feat]) in (bool, np.bool, np.bool_):
                    x_cat[feat] = int(x[feat])
                else:
                    x_cat[feat] = x[feat]
            yield x_cat


class CatBoostParams(JsonEntry):

    method_name = "CatBoost"

    max_depth_key = "max_depth"
    n_estimators_key = "n_estimators"
    eta_key = "eta"
    reg_lambda_key = "reg_lambda"
    objective_key = "objective"
    thread_count_key = "thread_count"
    task_type_key = "task_type"

    max_depth_0 = 6
    n_estimators_0 = 1000
    eta_0 = 0.1
    reg_lambda_0 = 3
    objective_0 = 'MultiClass'
    thread_count_0 = NUM_THREADS
    task_type_0 = "CPU"

    def __init__(self,
                 max_depth=max_depth_0,
                 n_estimators=n_estimators_0,
                 eta=eta_0,
                 reg_lambda=reg_lambda_0,
                 objective=None,
                 thread_count=thread_count_0,
                 task_type=None):

        if task_type is None:
            task_type = self.task_type_0
        if objective is None:
            objective = self.objective_0

        self.max_depth = max_depth
        self.n_estimators = n_estimators
        self.eta = eta
        self.reg_lambda = reg_lambda
        self.objective = objective
        self.thread_count = thread_count
        self.task_type = task_type

    @classmethod
    def attr_scheme(cls):
        attr_scheme = {
            "max_depth": (cls.max_depth_key,),
            "n_estimators": (cls.n_estimators_key,),
            "eta": (cls.eta_key,),
            "reg_lambda": (cls.reg_lambda_key,),
            "objective": (cls.objective_key,),
            "thread_count": (cls.thread_count_key,),
            "task_type": (cls.task_type_key,),
        }
        return attr_scheme

    @property
    def params(self):
        return super(CatBoostParams, self).get_json()
