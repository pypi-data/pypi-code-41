# -*- coding: utf-8 -*-
import json

from .vanilla_project import BaseVanillaProject, BaseVanillaExperiment
from .settings import HyperParamTypes
import six
import types

try:
    from contextlib import contextmanager
except ImportError:
    # noinspection PyUnresolvedReferences
    from contextlib2 import contextmanager


class SkLearnProject(BaseVanillaProject):
    """A class for communicating with MissingLinkAI backend.

    A TensorFlowProject instance corresponds to a project created in the backend. This instance
    is used to create new experiments and send the data to the backend.
    """

    def __init__(self, owner_id=None, project_token=None, stopped_callback=None, **kwargs):
        super(SkLearnProject, self).__init__(owner_id, project_token, stopped_callback=stopped_callback, ramework='sklearn', **kwargs)

    def _enter_experiment(self, **kwargs):
        pass

    def _create_experiment_scope(self, **kwargs):
        clf = kwargs.pop('clf')
        return _Experiment(self, clf)

    def _get_weights_hash(self, net):
        pass

    @classmethod
    def _get_structure_hash(cls, clf):
        from sklearn.base import BaseEstimator

        if not isinstance(clf, BaseEstimator):
            return

        params = _Experiment.get_clf_params(clf)

        params_json = json.dumps(params, sort_keys=True)

        return cls._hash(params_json)


class _Experiment(BaseVanillaExperiment):
    def __init__(self, project, clf, **kwargs):
        self._clf = clf
        super(_Experiment, self).__init__(project, **kwargs)

    def _extract_hyperparams_from_clf(self):
        params = self.get_clf_params(self._clf)

        max_iter = self._get_total_epoch()
        if max_iter <= 0:
            max_iter = 1

        run_params = {
            'total_epochs': 1,
            'sklearn_epochs': max_iter
        }

        # noinspection PyProtectedMember
        self._project._set_hyperparams(HyperParamTypes.OPTIMIZER, **params)
        # noinspection PyProtectedMember
        self._project._set_hyperparams(HyperParamTypes.RUN, **run_params)

    def _get_weights_hash(self):
        # noinspection PyProtectedMember
        return self._project._get_weights_hash(self._clf)

    def _get_structure_hash(self):
        # noinspection PyProtectedMember
        return self._project._get_structure_hash(self._clf)

    def _get_total_epoch(self, default_value=0):
        return getattr(self._clf, 'max_iter', default_value)

    @contextmanager
    def train(self, clf=None, **kwargs):
        self._clf = clf or self._clf

        with super(_Experiment, self).train() as train_phase:
            self._extract_hyperparams_from_clf()

            yield train_phase

            n_iter_ = getattr(self._clf, 'n_iter_', None)
            if isinstance(n_iter_, six.integer_types):
                final_epoch = n_iter_
            else:
                final_epoch = self._clf.n_iter_[0] if n_iter_ else 1

            epoch = 1  # for now in sklearn we log everything on epoch 1

            # noinspection PyProtectedMember
            self._project._set_hyperparams(HyperParamTypes.RUN, final_epoch=final_epoch)

            metrics = train_phase.get_average_metrics()
            with self.epoch(epoch) as epoch_phase:
                for key, val in metrics.items():
                    epoch_phase.log_metric(key, val)

    @classmethod
    def get_clf_params(cls, val):
        out = {'class': type(val).__name__}

        if not hasattr(val, '_get_param_names'):
            return out

        # noinspection PyProtectedMember
        for key in val._get_param_names():
            value = getattr(val, key, None)
            if hasattr(value, '_get_param_names'):
                out[key] = cls.get_clf_params(value)
            else:
                out[key] = value

        return out
