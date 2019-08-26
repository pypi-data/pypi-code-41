import os
import dill
from copy import deepcopy

from malemba import ArrayModelBase
from jsondler import JsonEntry
import numpy as np
import pandas as pd
import xgboost as xgb


NUM_THREADS = 4


class ModelXGB(ArrayModelBase):

    def __init__(self, params=None, **kwargs):
        self.model = None
        super(ModelXGB, self).__init__(params=params, **kwargs)

    def fit(self, X, Y, **kwargs):
        """
        :param X: list or iterator of dicts with features {feat1: v1, feat2: v2, ...}
        :param Y: list of labels
        """
        X, Y, data_shape = super(ModelXGB, self).fit(X=X, Y=Y, **kwargs)
        data = self.np_array(X, data_shape, low_memory=self.low_memory)
        dtrain = xgb.DMatrix(data=pd.DataFrame(data).values, label=np.array(list(Y)), missing=np.nan)
        self.model = xgb.train(params=self.params, dtrain=dtrain)

    def predict(self, X, **kwargs):
        """
        :param X: list or iterator of dicts with features {feat1: v1, feat2: v2, ...}
        :return: list of dicts with labels scores
        """
        X, data_shape = super(ModelXGB, self).predict(X=X, **kwargs)
        data = self.np_array(X, data_shape)
        dpred = xgb.DMatrix(data=pd.DataFrame(data).values, missing=np.nan)
        return list(map(lambda p: dict((self.labels[i], p[i]) for i in range(len(p))),
                        self.model.predict(dpred, output_margin=True)))

    def dump(self, scheme_path, **kwargs):
        if not os.path.exists(scheme_path):
            os.makedirs(scheme_path)
        model = self.__dict__.pop("model")
        meta_f = open(os.path.join(scheme_path, "meta.m"), "wb")
        dill.dump(self.__dict__, meta_f)
        meta_f.close()
        self.model = model

        self.model.save_model(fname=os.path.join(scheme_path, "model.m"))

    @classmethod
    def load(cls, scheme_path, params=None, **kwargs):
        model_xgb = cls(params=params, **kwargs)
        with open(os.path.join(scheme_path, "meta.m"), "rb") as meta_f:
            model_xgb.__dict__ = dill.load(meta_f)
        if params is not None:
            if model_xgb.params is not None:
                model_xgb.params.update(params)
            else:
                model_xgb.params = params
        model_xgb.model = xgb.Booster(params=model_xgb.params)
        model_xgb.model.load_model(fname=os.path.join(scheme_path, "model.m"))
        return model_xgb

    @staticmethod
    def _convert_str_to_factors():
        return True

    @property
    def num_threads(self):
        return self.params.get("nthread", NUM_THREADS)


class XGBoostParams(JsonEntry):

    method_name = "XGBoost"

    max_depth_key = "max_depth"
    min_child_weight_key = "min_child_weight"
    colsample_bytree_key = "colsample_bytree"
    gamma_key = "gamma"
    eta_key = "eta"
    reg_lambda_key = "reg_lambda"
    reg_alpha_key = "reg_alpha"
    objective_key = "objective"
    nthread_key = "nthread"
    tree_method_key = "tree_method"
    silent_key = "silent"

    max_depth_0 = 6
    min_child_weight_0 = 1.0
    colsample_bytree_0 = 1.0
    gamma_0 = 0.5
    eta_0 = 0.1
    reg_lambda_0 = 3
    reg_alpha_0 = 0.0
    objective_0 = 'multi:softmax'
    nthread_0 = NUM_THREADS
    tree_method_0 = 'auto'
    silent_0 = 1

    def __init__(self,
                 max_depth=max_depth_0,
                 min_child_weight=min_child_weight_0,
                 colsample_bytree=colsample_bytree_0,
                 gamma=gamma_0,
                 eta=eta_0,
                 reg_lambda=reg_lambda_0,
                 reg_alpha=reg_alpha_0,
                 objective=None,
                 nthread=nthread_0,
                 tree_method=None,
                 silent=silent_0):

        if tree_method is None:
            tree_method = self.tree_method_0
        if objective is None:
            objective = self.objective_0

        self.max_depth = max_depth
        self.min_child_weight = min_child_weight
        self.colsample_bytree = colsample_bytree
        self.gamma = gamma
        self.eta = eta
        self.reg_lambda = reg_lambda
        self.reg_alpha = reg_alpha
        self.objective = objective
        self.nthread = nthread
        self.tree_method = tree_method
        self.silent = silent

    @classmethod
    def attr_scheme(cls):
        attr_scheme = {
            "max_depth": (cls.max_depth_key,),
            "min_child_weight": (cls.min_child_weight_key,),
            "colsample_bytree": (cls.colsample_bytree_key,),
            "gamma": (cls.gamma_key,),
            "eta": (cls.eta_key,),
            "reg_lambda": (cls.reg_lambda_key,),
            "reg_alpha": (cls.reg_alpha_key,),
            "objective": (cls.objective_key,),
            "nthread": (cls.nthread_key,),
            "tree_method": (cls.tree_method_key,),
            "silent": (cls.silent_key,),
        }
        return attr_scheme

    @property
    def params(self):
        return super(XGBoostParams, self).get_json()
