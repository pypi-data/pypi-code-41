# -*- coding: utf-8 -*-
from __future__ import absolute_import
import copy
import warnings
from contextlib import contextmanager
import numpy as np
from ..base_callback import Context, ContextStacks
from .keras_patchers import KerasPatchers
from .keras_vis import KerasVis
from ..vanilla_project import BaseVanillaProject, BaseVanillaExperiment
from ..utilities.utils import hasharray, hashcombine, has_base_class, calc_tf_variable_value
from ..settings import HyperParamTypes


class KerasCallback(BaseVanillaProject, KerasVis):

    SHOULD_USE_INFINITE_GENERATOR = True

    def __init__(self, owner_id=None, project_token=None, stopped_callback=None, **kwargs):
        super(KerasCallback, self).__init__(
            owner_id, project_token, stopped_callback=stopped_callback, framework='keras', **kwargs)
        self.__params = {}
        self.__experiment = None
        self.__model = None
        self.__stacks = ContextStacks()

        warnings.filterwarnings('ignore', r'Method on_batch_begin\(\) is slow compared to the batch update')
        warnings.filterwarnings('ignore', r'Method on_batch_end\(\) is slow compared to the batch update')

    @property
    def _model(self):
        return self.__model

    @property
    def _params(self):
        return self.__params

    def _enter_experiment(self, **kwargs):
        self._extract_hyperparams_from_optimizer(self.__model.optimizer)

        params = copy.copy(self.__params)

        if 'steps' in params and params['steps'] is None:
            del params['steps']

        self.set_hyperparams(
            total_epochs=params.pop('epochs', None),
            batch_size=params.pop('batch_size', None),
            samples_count=params.pop('samples', None) or params.pop('sample', None),
            params=params)

    def _create_experiment_scope(self, **kwargs):
        model = kwargs.pop('model', self.__model)
        self.__experiment = _Experiment(self, model=model, **kwargs)

        return self.__experiment

    # Deprecated. To support Keras v1
    def _set_params(self, params):
        self.__params = self._params_v2_from_v1(params)

    # Deprecated. To support Keras v1
    def _set_model(self, model):
        self.__model = model

    def set_params(self, params):
        self.__params = params

    set_model = _set_model

    def __enter_xp_scope_if_needed(self, model=None):
        if self.__experiment is not None:
            return

        if model is not None:
            self.set_model(model)

        self.__experiment = self.__stacks.enter(Context.EXPERIMENT, self.experiment)

    @property
    def __metrics(self):
        return self.__params.get('metrics', [])

    def __handle_logs_from_metrics(self, logs):
        metric_data = {metric: logs[metric] for metric in self.__metrics if metric in logs}
        self.__handle_logs(metric_data)

    def __handle_logs(self, logs):
        for name, value in (logs or {}).items():
            if isinstance(value, (np.float32, np.float64)):
                value = float(value)

            self.__stacks.top_scope.log_metric(name, value, is_custom=False)

    def on_train_begin(self, logs=None):
        self.__enter_xp_scope_if_needed()
        self.__stacks.enter(Context.TRAIN, self.__experiment.train)

    def on_train_end(self, logs=None):
        self.__handle_logs(logs)
        self.__stacks.exit(Context.TRAIN)

    def on_epoch_begin(self, epoch, logs=None):
        self.__stacks.enter(Context.EPOCH_LOOP, self.__experiment.epoch, epoch + 1)

    # noinspection PyBroadException
    def on_epoch_end(self, epoch, logs=None):
        self.__handle_logs(logs)
        self.__stacks.exit(Context.EPOCH_LOOP)

    def on_batch_begin(self, batch, logs=None):
        # noinspection PyProtectedMember
        self.__experiment._experiment_counters.begin_iteration()
        # noinspection PyProtectedMember
        self.__stacks.enter(Context.BATCH_LOOP, self.__experiment.batch, self.__experiment._iteration, batch=batch + 1)

    def on_batch_end(self, batch, logs=None):
        self.__handle_logs_from_metrics(logs)
        self.__stacks.exit(Context.BATCH_LOOP)

    on_train_batch_begin = on_batch_begin
    on_train_batch_end = on_batch_end

    # endregion
    @contextmanager
    def test(self, model, callback=None, generate_confusion_matrix=True, name=None):
        self.__enter_xp_scope_if_needed(model)
        with self.__experiment.test(callback=callback, generate_confusion_matrix=generate_confusion_matrix, name=name) as phase:
            yield phase

    def variable_to_value(self, variable):
        var_classes = ['Variable', 'RefVariable']
        is_tf_var = variable.__class__.__name__ in var_classes or has_base_class(variable, var_classes)

        if is_tf_var:
            try:
                from ..vis.dynamic_import import DynamicImport

                dynamic_import = DynamicImport(self._model)

                if dynamic_import.module.__name__ == 'keras':
                    keras_backend = dynamic_import.bring('backend')
                else:
                    keras_backend = dynamic_import.bring('keras').backend

                return keras_backend.eval(variable)
            except Exception:
                warnings.warn("was not able to get variable %s" % variable.name)
                return calc_tf_variable_value(variable)

        return super(KerasCallback, self).variable_to_value(variable)

    @classmethod
    def _params_v2_from_v1(cls, params_v1):
        params_v2 = params_v1.copy()
        params_v2['epochs'] = params_v1['nb_epoch']
        params_v2['samples'] = params_v1['nb_sample']
        return params_v2

    def _extract_hyperparams_from_optimizer(self, optimizer):
        optimizer_hyperparams = {
            'SGD': ['lr', 'momentum', 'decay', 'nesterov'],
            'RMSprop': ['lr', 'rho', 'epsilon', 'decay'],
            'Adagrad': ['lr', 'epsilon', 'decay'],
            'Adadelta': ['lr', 'rho', 'epsilon', 'decay'],
            'Adam': ['lr', 'beta_1', 'beta_2', 'epsilon', 'decay'],
            'Adamax': ['lr', 'beta_1', 'beta_2', 'epsilon', 'decay'],
            'Nadam': ['lr', 'beta_1', 'beta_2', 'epsilon', 'schedule_decay'],
        }
        hyperparam_names = {
            'lr': 'learning_rate',
            'decay': 'learning_rate_decay',
        }

        self.set_hyperparams(optimizer_algorithm=optimizer.__class__.__name__)
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, optimizer, optimizer_hyperparams, hyperparam_names)

    @classmethod
    def calculate_weights_hash(cls, net):
        weight_hashes = []
        for layer in net.layers:
            weights = layer.get_weights()
            if weights is None:
                continue

            for weight in weights:
                weight_hashes.append(hasharray(weight))

        return cls._WEIGHTS_HASH_PREFIX + hashcombine(*weight_hashes)

    @classmethod
    def _get_weights_hash(cls, net):
        return cls.calculate_weights_hash(net)

    @classmethod
    def _get_structure_hash(cls, net):
        layers_repr = []
        for i, layer in enumerate(net.layers):
            inbound_nodes = layer._inbound_nodes if hasattr(layer, '_inbound_nodes') else layer.inbound_nodes
            if not inbound_nodes:
                continue

            inbound_node_shapes = [tuple(layer.get_input_shape_at(index)) for index in range(len(inbound_nodes))]
            inbound_node_shapes = tuple(inbound_node_shapes) if len(inbound_node_shapes) > 1 else inbound_node_shapes[0]

            layer_bias = getattr(layer, 'use_bias', None)
            layer_type = type(layer)
            layers_repr.append((layer_type, inbound_node_shapes, layer_bias))

        return cls._hash(tuple(layers_repr))

    def on_test_batch_begin(self, batch, logs=None):
        """Called at the beginning of a batch in `evaluate` methods.

        Also called at the beginning of a validation batch in the `fit`
        methods, if validation data is provided.

        Subclasses should override for any actions to run.

        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: dict. Has keys `batch` and `size` representing the current batch
              number and the size of the batch.
        """

    def on_test_batch_end(self, batch, logs=None):
        """Called at the end of a batch in `evaluate` methods.

        Also called at the end of a validation batch in the `fit`
        methods, if validation data is provided.

        Subclasses should override for any actions to run.

        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: dict. Metric results for this batch.
        """

    def on_predict_batch_begin(self, batch, logs=None):
        """Called at the beginning of a batch in `predict` methods.

        Subclasses should override for any actions to run.

        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: dict. Has keys `batch` and `size` representing the current batch
              number and the size of the batch.
        """

    def on_predict_batch_end(self, batch, logs=None):
        """Called at the end of a batch in `predict` methods.

        Subclasses should override for any actions to run.

        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: dict. Metric results for this batch.
        """

    def on_test_begin(self, logs=None):
        """Called at the beginning of evaluation or validation.

        Subclasses should override for any actions to run.

        Arguments:
            logs: dict. Currently no data is passed to this argument for this method
              but that may change in the future.
        """

    def on_test_end(self, logs=None):
        """Called at the end of evaluation or validation.

        Subclasses should override for any actions to run.

        Arguments:
            logs: dict. Currently no data is passed to this argument for this method
              but that may change in the future.
        """

    def on_predict_begin(self, logs=None):
        """Called at the beginning of prediction.

        Subclasses should override for any actions to run.

        Arguments:
            logs: dict. Currently no data is passed to this argument for this method
              but that may change in the future.
        """

    def on_predict_end(self, logs=None):
        """Called at the end of prediction.

        Subclasses should override for any actions to run.

        Arguments:
            logs: dict. Currently no data is passed to this argument for this method
              but that may change in the future.
        """


class _Experiment(BaseVanillaExperiment, KerasPatchers):
    def __init__(self, project, model=None, **kwargs):
        self.__model = model
        super(_Experiment, self).__init__(project, **kwargs)

    @property
    def _model(self):
        return self.__model

    def _get_structure_hash(self):
        # noinspection PyProtectedMember
        return self._project._get_structure_hash(self._model)

    def _get_weights_hash(self):
        # noinspection PyProtectedMember
        return self._project._get_weights_hash(self._model)

    @contextmanager
    def test(self, callback=None, generate_confusion_matrix=True, name=None):
        with super(_Experiment, self).test(name=name) as test_phase:
            self._patch_evaluate_generator()
            self._patch_test_loop(test_name=name)
            self._patch_test_function(generate_confusion_matrix, callback)
            self._patch_standardize_user_data()

            yield test_phase

            self._unpatch_standardize_user_data()
            self._unpatch_evaluate_generator()
            self._unpatch_test_loop()
            self._unpatch_test_function()
