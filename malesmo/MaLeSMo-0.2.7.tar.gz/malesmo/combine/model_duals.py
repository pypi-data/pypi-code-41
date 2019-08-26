import os
import dill
from copy import deepcopy
from itertools import tee
from abc import ABCMeta, abstractmethod

from malemba import ModelBase
from malemba.ds_tools import ArrayHandler, group_array


class ModelDualStage(ModelBase):

    class Concatenator(object, metaclass=ABCMeta):

        @abstractmethod
        def concatenate(self, X, Y):
            return

    def __init__(self, model1, model2, concatenator, params1=None, params2=None, **kwargs):
        """

        :param model1: Boosting model object inherited from malemba.ArrayModelBase that is the first to be applied
        :param model2: Boosting model object inherited from malemba.ArrayModelBase that is the to be applied over model1
        :param concatenator: the object inherited from Concatenator class to be used to concatinate X and
             model1 prediction for model2 input
        :param params1: parameters dict for model1
        :param params2: parameters dict for model2
        :param kwargs:
        """

        self.model1 = model1
        self.model2 = model2
        assert isinstance(self.model1, ModelBase), \
            "Error: a value for model1 argument must be an object inherited from malemba.ModelBase"
        assert isinstance(self.model2, ModelBase), \
            "Error: a value for model2 argument must be an object inherited from malemba.ModelBase"
        self._model1_class = self.model1.__class__
        self._model2_class = self.model2.__class__
        self.concatenator = concatenator
        assert isinstance(concatenator, ModelDualStage.Concatenator), \
            "Error: a value for 'concatenator' argument must be an object inherited from ModelDualStage.Concatenator"
        self.params1 = params1
        self.params2 = params2
        super(ModelDualStage, self).__init__(params=None, **kwargs)
        self.aggr_level1 = kwargs.get("aggr_level1", 0)
        self.aggr_level2 = kwargs.get("aggr_level2", 0)
        self._data_l = 0
        self._model1_fract = 0.0

    def fit(self, X, Y, model1_fract=0.0, aggr_level1=None, aggr_level2=None, dump_scheme_path=None, **kwargs):
        """

        :param X: features data
        :param Y: labels data
        :param model1_fract: the fraction of data is to be used for model1 training
        :param aggr_level1: number of aggregation steps to turn the input data into appropriate for model1 input
        :param aggr_level2: number of aggregation steps to turn the input data into appropriate for model2 input
        :param dump_scheme_path: The path for models dump
        :param kwargs:
        :return:
        """
        super(ModelDualStage, self).fit(X=X, Y=Y, **kwargs)

        if aggr_level1 is not None:
            self.aggr_level1 = aggr_level1
        if aggr_level2 is not None:
            self.aggr_level2 = aggr_level2

        if model1_fract > 0.0:
            self._model1_fract = model1_fract
            self._data_l = kwargs.get("data_l", 0)
            if self._data_l <= 0:
                Y, Y_l = tee(Y)
                for y in Y_l:
                    self._data_l += 1

            X_1 = ModelDualStage._data_part(X, int(float(self._data_l) * self._model1_fract))
            Y_1 = ModelDualStage._data_part(Y, int(float(self._data_l) * self._model1_fract))
            if self.aggr_level1 > 0:
                data1_handler = ArrayHandler()
                Y_1 = data1_handler.aggregate(Y_1, aggr_level=self.aggr_level1)
                data1_handler.group_lims = None
                X_1 = data1_handler.aggregate(X_1, aggr_level=self.aggr_level1)
            self.model1.fit(X=X_1, Y=Y_1)
            if dump_scheme_path is not None:
                try:
                    self.model1.dump(scheme_path=os.path.join(dump_scheme_path, "model1"))
                except:
                    print("WARNING: model1 dump failed")

        if self._model1_fract >= 1.0:
            print("WARNING: model1 fraction >= 1.0 - model2 is model1")
            self.model2 = self.model1
        else:
            X = self._get_model2_data(X=X, aggr_level=self.aggr_level1)
            if self.aggr_level2 > 0:
                data2_handler= ArrayHandler()
                Y = data2_handler.aggregate(Y, aggr_level=self.aggr_level2)
                data2_handler.group_lims = None
                X = data2_handler.aggregate(X, aggr_level=self.aggr_level2)
            self.model2.fit(X=X, Y=Y)

        if dump_scheme_path is not None:
            try:
                self.model2.dump(scheme_path=os.path.join(dump_scheme_path, "model2"))
            except:
                print("WARNING: model2 dump failed")
            self.dump(scheme_path=dump_scheme_path, only_meta=True)

    @staticmethod
    def _data_part(data, part_l):
        l = 0
        for d in data:
            if l >= part_l:
                break
            l += 1
            yield d

    def predict(self, X, aggr_level1=None, aggr_level2=None, **kwargs):
        """

        :param X: features data
        :param concat_method: the function to be used to concatinate X and model1 prediction for model2 input
        :param aggr_level1: number of aggregation steps to turn the input data into one dimensional array
        :param kwargs:
        :return:
        """
        if aggr_level1 is not None:
            self.aggr_level1 = aggr_level1
        if aggr_level2 is not None:
            self.aggr_level2 = aggr_level2

        X = self._get_model2_data(X=X, aggr_level=self.aggr_level1)
        if self.aggr_level2 > 0:
            X_handler = ArrayHandler()
            X = X_handler.aggregate(X, aggr_level=self.aggr_level2)
            return group_array(self.model2.predict(X=X), group_lims=X_handler.group_lims)
        else:
            return self.model2.predict(X=X)

    def _get_model2_data(self, X, aggr_level=0):
        X, X_1 = tee(X)
        if aggr_level > 0:
            X_1_handler = ArrayHandler()
            X_1 = X_1_handler.aggregate(X_1, aggr_level=aggr_level)
            model1_pred = group_array(self.model1.predict(X=X_1), group_lims=X_1_handler.group_lims)
        else:
            model1_pred = self.model1.predict(X=X_1)

        return self.concatenator.concatenate(X, model1_pred)

    @staticmethod
    def _convert_str_to_factors():
        return False

    def str_to_factors(self, X):
        pass

    def validate(self, X_test, Y_test, labels_to_remove=None, aggr_level1=None, aggr_level2=None):
        if aggr_level1 is not None:
            self.aggr_level1 = aggr_level1
        if aggr_level2 is not None:
            self.aggr_level2 = aggr_level2

        X_test = self._get_model2_data(X=X_test, aggr_level=self.aggr_level1)
        if self.aggr_level1 > 0:
            data_handler = ArrayHandler()
            Y_test = data_handler.aggregate(Y_test, aggr_level=self.aggr_level2)
            data_handler.group_lims = None
            X_test = data_handler.aggregate(X_test, aggr_level=self.aggr_level2)
        return self.model2.validate(X_test=X_test, Y_test=Y_test, labels_to_remove=labels_to_remove)

    def validate_model1(self, X_test, Y_test, labels_to_remove=None, aggr_level=None):
        if aggr_level is not None:
            self.aggr_level1 = aggr_level

        if self.aggr_level1 > 0:
            data_handler = ArrayHandler()
            Y_test = data_handler.aggregate(Y_test, aggr_level=self.aggr_level1)
            data_handler.group_lims = None
            X_test = data_handler.aggregate(X_test, aggr_level=self.aggr_level1)
        return self.model1.validate(X_test=X_test, Y_test=Y_test, labels_to_remove=labels_to_remove)

    def validate_model2(self, X_test, Y_test, labels_to_remove=None, aggr_level1=None, aggr_level2=None):
        return self.validate(X_test=X_test,
                             Y_test=Y_test,
                             labels_to_remove=labels_to_remove,
                             aggr_level1=aggr_level1,
                             aggr_level2=aggr_level2)

    def dump(self, scheme_path, **kwargs):
        if not os.path.exists(scheme_path):
            os.makedirs(scheme_path)
        model1 = self.__dict__.pop("model1")
        model2 = self.__dict__.pop("model2")
        meta_f = open(os.path.join(scheme_path, "meta.m"), "wb")
        dill.dump(self.__dict__, meta_f)
        meta_f.close()
        self.model1 = model1
        self.model2 = model2

        if kwargs.get("only_meta", False):
            return
        self.model1.dump(scheme_path=os.path.join(scheme_path, "model1"), **kwargs)
        self.model2.dump(scheme_path=os.path.join(scheme_path, "model2"), **kwargs)

    @classmethod
    def load(cls, scheme_path, params1=None, params2=None, **kwargs):
        with open(os.path.join(scheme_path, "meta.m"), "rb") as meta_f:
            meta_dict = dill.load(meta_f)
        if params1 is not None:
            if meta_dict["params1"] is not None:
                meta_dict["params1"].update(params1)
            else:
                meta_dict["params1"] = params1
        if params2 is not None:
            if meta_dict["params2"] is not None:
                meta_dict["params2"].update(params2)
            else:
                meta_dict["params2"] = params2
        model1 = meta_dict["_model1_class"].load(scheme_path=os.path.join(scheme_path, "model1"),
                                                 params=meta_dict["params1"],
                                                 **kwargs)
        model2 = meta_dict["_model2_class"].load(scheme_path=os.path.join(scheme_path, "model2"),
                                                 params=meta_dict["params2"],
                                                 **kwargs)
        model_dual_stage = cls(model1=model1,
                               model2=model2,
                               concatenator=meta_dict["concatenator"],
                               params1=params1,
                               params2=params2)
        model_dual_stage.__dict__.update(meta_dict)
        return model_dual_stage

    @property
    def num_threads(self):
        return self.model2.num_threads

    def get_features(self, X):
        pass

    @property
    def features(self):
        return self.model1_features

    @property
    def model1_features(self):
        return self.model1.features

    @property
    def model2_features(self):
        return self.model2.features

    @property
    def feature_types(self):
        return self.model1_feature_types

    @property
    def model1_feature_types(self):
        return self.model1.feature_types

    @property
    def model2_feature_types(self):
        return self.model2.feature_types

    @property
    def labels(self):
        return self.model1.labels

    @property
    def label_freqs(self):
        if not self._label_freqs:
            for label in self.model1.label_freqs:
                self._label_freqs[label] = self.model1.label_freqs[label] * self._model1_fract
            for label in self.model2.label_freqs:
                self._label_freqs[label] += self.model2.label_freqs[label] * (1.0-self._model1_fract)
        return self._label_freqs
