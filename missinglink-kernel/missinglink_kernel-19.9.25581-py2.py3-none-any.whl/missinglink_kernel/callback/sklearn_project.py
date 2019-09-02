# -*- coding: utf-8 -*-
import json

from .interfaces import ModelHashInterface
from .settings import HyperParamTypes
from .base_callback import BaseCallback, BaseContextValidator, Context
import six
import types

try:
    from contextlib import contextmanager
except ImportError:
    # noinspection PyUnresolvedReferences
    from contextlib2 import contextmanager


class SkLearnProject(BaseCallback, ModelHashInterface):
    """A class for communicating with MissingLinkAI backend.

    A TensorFlowProject instance corresponds to a project created in the backend. This instance
    is used to create new experiments and send the data to the backend.
    """

    def __init__(self, owner_id=None, project_token=None, host=None, **kwargs):
        super(self.__class__, self).__init__(owner_id, project_token, host=host, framework='sklearn', **kwargs)

        self._context_validator = SkLearnContextValidator(self.logger)

    @classmethod
    def _get_total_epoch(cls, clf, default_value=0):
        return getattr(clf, 'max_iter', default_value)

    @classmethod
    def _get_current_epoch(cls, clf):
        n_iter_ = getattr(clf, 'n_iter_', None)

        if n_iter_ is None and cls._get_total_epoch(clf) > 0:
            return cls._get_total_epoch(clf)

        if isinstance(n_iter_, six.integer_types):
            epoch = n_iter_
        else:
            epoch = clf.n_iter_[0] if n_iter_ else 1

        return epoch

    @contextmanager
    def train(self, clf):
        with self._context_validator.context(Context.TRAIN):
            self._internal_train_begin(clf)

            phase = self._context_validator.last_phase
            yield phase
            metric_data = phase.get_average_metrics()

            epoch = 1
            self.epoch_end(epoch, metric_data=metric_data)
            self._train_end()

    @contextmanager
    def test(self, name=None):
        self._test_begin(0, None, name=name)
        with self._context_validator.context(Context.TEST):
            phase = self._context_validator.last_phase
            yield phase
            self._test_iteration_end(phase.y_test, phase.y_pred, None, is_finished=True, metric_data=phase.get_average_metrics())

    def _extract_hyperparams_from_clf(self, clf):
        params = self.__get_params(clf)

        self._set_hyperparams(HyperParamTypes.OPTIMIZER, **params)

    @classmethod
    def __get_params(cls, val):
        out = {'class': type(val).__name__}

        if not hasattr(val, '_get_param_names'):
            return out

        for key in val._get_param_names():
            value = getattr(val, key, None)
            if hasattr(value, '_get_param_names'):
                out[key] = cls.__get_params(value)
            else:
                out[key] = value

        return out

    def get_weights_hash(self, net):
        pass

    @ModelHashInterface.wrap_all_get_structure_hash_exceptions
    def _get_structure_hash(self, clf):
        from sklearn.base import BaseEstimator

        if not isinstance(clf, BaseEstimator):
            return

        params = self.__get_params(clf)

        params_json = json.dumps(params, sort_keys=True)

        return self._hash(params_json)

    def _internal_train_begin(self, clf):
        max_iter = self._get_total_epoch(clf)
        if max_iter <= 0:
            max_iter = 1

        self.set_hyperparams(total_epochs=1)
        self.set_hyperparams(sklearn_epochs=max_iter)
        self._extract_hyperparams_from_clf(clf)

        structure_hash = self._get_structure_hash(clf)
        self.train_begin(structure_hash=structure_hash)


class SkLearnContextValidator(BaseContextValidator):
    """
    This class validates if we can enter or exit a context.
    """

    def __init__(self, logger):
        super(SkLearnContextValidator, self).__init__(logger)

    def _validate_test_context(self):
        pass

    def _validate_train_context(self):
        pass

    def _validate_validation_context(self):
        pass
