# -*- coding: utf-8 -*-
from os import path

import numpy as np
import six

from ..base_callback import Context, ContextStacks
from ..vanilla_project import BaseVanillaProject, BaseVanillaExperiment
from ..utilities.utils import enum, hasharray, hashcombine
from ..exceptions import MissingLinkException
from ..settings import HyperParamTypes
from .caffe_vis import CaffeVis


prototext_type = enum('solver', 'net')


# noinspection PyUnresolvedReferences
def create_caffe_solver():
    from caffe.proto import caffe_pb2

    return caffe_pb2.SolverParameter()


# noinspection PyUnresolvedReferences
def create_caffe_net():
    from caffe.proto import caffe_pb2

    return caffe_pb2.NetParameter()


class SolverParamsUtils(object):
    def __init__(self, solver_params):
        self.__solver_params = solver_params

    @property
    def max_iterations(self):
        return self.__solver_params.get('maxIter', 0)

    @property
    def snapshot_interval(self):
        return self.__solver_params.get('snapshot')


class PyCaffeCallback(BaseVanillaProject, CaffeVis):
    def __init__(self, owner_id=None, project_token=None, stopped_callback=None, **kwargs):
        super(PyCaffeCallback, self).__init__(owner_id, project_token, stopped_callback=stopped_callback, framework='pycaffe', **kwargs)

        self.test_iter = None
        self._expected_layer_name = 'label'
        self._predictions_layer_name = 'score'

    @property
    def _is_caffe_test_iteration(self):
        # this is true if Caffe does a test on this iteration.
        # it's not the same as _is_test_iteration
        return self.test_interval and \
            (self.iteration - 1) % self.test_interval == 0 and \
            (self.iteration > 1 or self.test_initialization)

    @classmethod
    def calculate_weights_hash(cls, net):
        layer_names = list(net._layer_names)
        layer_hashes = []
        for layer in layer_names:
            weights = net.params.get(layer)
            if not weights:
                continue

            weights = weights[0].data
            layer_hash = hasharray(weights)
            layer_hashes.append(layer_hash)

        return cls._WEIGHTS_HASH_PREFIX + hashcombine(*layer_hashes)

    @property
    def _run_hyperparameter(self):
        return self.get_hyperparams().get('run', {})

    @property
    def epoch_size(self):
        return self._run_hyperparameter.get('epoch_size')

    @property
    def batch_size(self):
        return self._run_hyperparameter.get('batch_size')

    def total_epochs(self, max_iterations):
        return int(max_iterations / self.epoch_size) if max_iterations is not None else None

    def _create_experiment_scope(self, solver, **kwargs):
        return _Experiment(self, net=solver.net, **kwargs)

    def _enter_experiment(self, **kwargs):
        solver_class = kwargs.pop('solver_class')
        solver_params = kwargs.pop('solver_params')

        self._hyperparams_from_solver(solver_class, solver_params)

        solver_params_utils = SolverParamsUtils(solver_params)

        max_iterations = solver_params_utils.max_iterations

        if self.epoch_size is None:
            self.logger.debug('Epoch size is None')
            self.set_hyperparams(total_batches=max_iterations)
            return

        if self.batch_size is None:
            raise MissingLinkException('batch_size cannot be None')

        self.set_hyperparams(total_epochs=self.total_epochs(max_iterations), total_batches=max_iterations)

    def set_expected_predictions_layers(self, expected_layer_name, predictions_layer_name):
        self._expected_layer_name = expected_layer_name
        self._predictions_layer_name = predictions_layer_name

    @staticmethod
    def parse_prototxt(prototext_path, file_type=prototext_type.solver):
        if not prototext_path:
            return

        if not path.exists(prototext_path):
            raise MissingLinkException('file not found %s' % prototext_path)

        from google.protobuf import json_format, text_format

        with open(prototext_path) as f:
            raw_solver = f.read()

        if file_type == prototext_type.solver:
            message = create_caffe_solver()
        elif file_type == prototext_type.net:
            message = create_caffe_net()
        else:
            raise MissingLinkException('unknown file_type %s' % file_type)

        text_format.Merge(raw_solver, message)
        solver = json_format.MessageToDict(message)

        return solver

    def create_wrapped_solver(self, solver_class, proto_path=None, solver_params=None):
        actual_solver_params = self.parse_prototxt(proto_path) or {}
        actual_solver_params.update(solver_params or {})

        class WrappedSolver(solver_class):
            def __init__(self, project, expected_layer_name, predictions_layer_name):
                super(WrappedSolver, self).__init__(proto_path)
                self.__project = project
                self.__train_scope = None
                self.__stacks = ContextStacks()

                self.__monitored_blobs = []
                self.__custom_monitored_blobs = []

                self.__test_net_index = 0

                self.__test_iter = actual_solver_params.get('testIter')
                self.__test_interval = actual_solver_params.get('testInterval')
                self.__test_initialization = actual_solver_params.get('testInitialization', False)
                self.__max_iterations = None
                self.__expected_layer_name = expected_layer_name
                self.__predictions_layer_name = predictions_layer_name
                self.__epoch_size = None
                self.__iteration = 0
                self.__experiment = None

            def set_monitored_blobs(self, blobs='loss'):
                if isinstance(blobs, six.string_types):
                    blobs = [blobs]

                for blob in blobs:
                    lst = self.__custom_monitored_blobs if callable(blob) else self.__monitored_blobs
                    lst.append(blob)

            @property
            def _is_test_iter(self):
                if self.__iteration == 1 and self._is_test_initialization:
                    return True

                if not self.__test_interval:
                    return False

                return self.__iteration % self.__test_interval == 0

            @property
            def _is_test_initialization(self):
                return self.__test_initialization

            def __enter_xp_scope_if_needed(self):
                if self.__experiment is not None:
                    return

                self.__experiment = self.__stacks.enter(Context.EXPERIMENT, self.__project.experiment, solver=self, solver_class=solver_class, solver_params=actual_solver_params)

            def __enter_train_scope_if_needed(self):
                if self.__train_scope is not None:
                    return

                self.__enter_xp_scope_if_needed()

                solver_params_utils = SolverParamsUtils(actual_solver_params)

                self.__epoch_size = self.__project.epoch_size
                self.__max_iterations = solver_params_utils.max_iterations
                self.__train_scope = self.__stacks.enter(Context.TRAIN, self.__experiment.train)

            def _get_current_epoch_batch(self):
                if self.__epoch_size is not None:
                    epoch = (self.__iteration / self.__epoch_size) + 1
                    batch = self.__iteration % self.__epoch_size
                else:
                    epoch = None
                    batch = None

                return epoch, batch

            def step(self, batches):
                if batches > 0:
                    self.__enter_train_scope_if_needed()

                epoch, batch = self._get_current_epoch_batch()

                ret = None

                for i in range(batches):
                    self.__iteration += 1
                    is_epoch_iteration = self.__experiment._is_epoch_iteration(self.__epoch_size)

                    with self.__experiment.batch(self.__iteration, batch=batch, epoch=epoch) as batch_phase:
                        if self._is_test_iter:
                            self._forward_test_net_all()

                        ret = solver_class.step(self, 1)
                        self._validate_monitor_blobs(self.net, self.__monitored_blobs)

                        self._accumulate_metrics(batch_phase, self.net)

                    if is_epoch_iteration:
                        with self.__experiment.epoch(epoch) as epoch_phase:
                            self._accumulate_metrics(epoch_phase, self.net)

                    if self.__iteration == self.__max_iterations:
                        self.__stacks.exit(Context.TRAIN)
                        break

                return ret

            @property
            def _logger(self):
                return self.__project.logger

            def solve(self):
                self.__enter_train_scope_if_needed()

                if not self.__max_iterations:
                    self._logger.warning('maxIter is 0. The experiment will not be monitored')

                self.step(self.__max_iterations)

            @property
            def _is_first_iteration(self):
                return self.__iteration == 1

            def _warn_no_outputs(self):
                # noinspection PyProtectedMember
                self.__experiment._logger.warning(
                    'your net doesn\'t have any outputs please check your configuration')

            def _warn_not_monitored(self, not_monitored):
                # noinspection PyProtectedMember
                self.__experiment._logger.warning(
                    'your net have outputs that you are not monitoring: %s', ', '.join(not_monitored))

            def _warn_not_exists(self, not_exists):
                # noinspection PyProtectedMember
                self.__experiment._logger.warning(
                    'your config have monitored metrics that not exists in the network: %s', ', '.join(not_exists))

            def _validate_monitor_blobs(self, net, monitored_blobs):
                if not self._is_first_iteration:
                    return

                if len(net.outputs) == 0:
                    self._warn_no_outputs()

                not_monitored = [out_blob for out_blob in net.outputs if out_blob not in monitored_blobs]
                not_exists = [out_blob for out_blob in monitored_blobs if out_blob not in net.outputs]

                if len(not_monitored) > 0:
                    self._warn_not_monitored(not_monitored)

                if len(not_exists) > 0:
                    self._warn_not_exists(not_exists)

            def _get_blobs(self, net):
                metric_data = {}

                monitored_blobs = self.__monitored_blobs
                custom_monitored_blobs = self.__custom_monitored_blobs

                if len(monitored_blobs) == 0:
                    monitored_blobs = net.outputs

                for blob_name in monitored_blobs:
                    blob = net.blobs.get(blob_name)
                    if blob is None:
                        self._logger.warning('%s blob does not exist in net and will not be monitored', blob_name)
                        continue

                    value = np.copy(blob.data)

                    if np.shape(value) == ():
                        metric_data[blob_name] = value
                        continue

                    blob_name += '_mean'
                    metric_data[blob_name] = np.mean(value)

                custom_metric_data = {}
                for blob_function in custom_monitored_blobs:
                    custom_metric_data[blob_function.__name__] = blob_function()

                return metric_data, custom_metric_data

            def _forward_test_net(self, blobs=None, start=None, end=None, index=0, **kwargs):
                net = self.test_nets[index]
                return net.forward(blobs, start, end, **kwargs)

            def has_layers(self, net, layer_names):
                for layer_name in layer_names:
                    try:
                        if layer_name not in net.blobs:
                            return False
                    except TypeError:
                        self._logger.warning("Layer name must be a string. Got a %s instead" % type(layer_name))

                        return False

                return True

            def _forward_test_net_all(self, blobs=None, start=None, end=None, index=0, **kwargs):
                net = self.test_nets[index]

                test_layers = [self.__expected_layer_name, self.__predictions_layer_name]
                found_layer_names = self.has_layers(net, test_layers)

                if not found_layer_names:
                    self._logger.warning(
                        'could not find layer "%s" and "%s" in test net #%s to generate confusion matrix',
                        self.__expected_layer_name,
                        self.__predictions_layer_name, index)

                test_steps = self.__test_iter[index]
                with self.__experiment.validation() as val_phase:
                    for _ in range(test_steps):
                        net.forward(blobs, start, end, **kwargs)
                        self._accumulate_metrics(val_phase, net)
                        # expected, predictions, probabilities = self._get_expected_predictions_probabilities(found_layer_names)
                        # noinspection PyProtectedMember
                        # self.__experiment._project._test_iteration_end(expected, predictions, probabilities)

            def _accumulate_metrics(self, phase, net):
                metric_data, custom_metric_data = self._get_blobs(net)
                phase.log_metrics(metric_data, is_custom=False)
                phase.log_metrics(custom_metric_data, is_custom=True)

            def _get_expected_predictions_probabilities(self, found_layer_names):
                net = self.test_nets[0]
                if found_layer_names:
                    expected = map(int, net.blobs[self.__expected_layer_name].data) \
                        if self.__expected_layer_name in net.blobs else []

                    predictions = np.argmax(net.blobs[self.__predictions_layer_name].data, axis=1) \
                        if self.__predictions_layer_name in net.blobs else []

                    probabilities = np.max(net.blobs[self.__predictions_layer_name].data, axis=1) \
                        if self.__predictions_layer_name in net.blobs else []

                    def unpack_nested_list(lst):
                        try:
                            result = list()
                            for x in lst:
                                result = unpack_nested_list(x)
                            return result
                        except TypeError:
                            return [lst]

                    # squash predictions and probabilities to 1D if needed
                    predictions = unpack_nested_list(predictions) \
                        if not np.array_equal(predictions, []) and len(predictions.shape) > 1 else predictions

                    probabilities = unpack_nested_list(probabilities) \
                        if not np.array_equal(probabilities, []) and len(probabilities.shape) > 1 else probabilities

                    # convert predictions and probabilities to list if needed
                    try:
                        predictions = predictions.tolist()
                    except AttributeError:
                        pass
                    try:
                        probabilities = probabilities.tolist()
                    except AttributeError:
                        pass

                else:
                    expected = []
                    predictions = []
                    probabilities = []

                return expected, predictions, probabilities

        solver = WrappedSolver(self, self._expected_layer_name, self._predictions_layer_name)

        batch_size = self._get_batch_size(solver.net)
        self.set_properties(batch_size=batch_size)

        return solver

    def _get_batch_size(self, net):
        try:
            if len(net.layer_dict.keys()) > 0:
                input_layer = net.layer_dict.keys()[0]
                input_shape = net.blobs[input_layer].shape
                return input_shape[0]
        except Exception as ex:
            if isinstance(ex, AttributeError):
                raise

            self.logger.warning('Failed to extract the batch_size %s', ex)

        return None

    def _hyperparams_from_solver(self, solver_class, solver_params):
        solver_to_attrs = {
            'any': ['baseLr', 'lrPolicy', 'gamma', 'momentum', 'weightDecay', 'testIter', 'testInterval',
                    'testInitialization']
        }

        attr_to_hyperparam = {
            'baseLr': 'learning_rate',
            'lrPolicy': 'learning_rate_policy',
            'weightDecay': 'weight_decay',
            'testIter': 'test_iterations',
            'testInterval': 'test_interval',
            'testInitialization': 'test_initialization',
        }

        solver_type = solver_class.__name__
        if solver_type.endswith('Solver'):
            solver_type = solver_type[:-6]

        self.set_hyperparams(optimizer_algorithm=solver_type, params=solver_params)
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, solver_params, solver_to_attrs,
                                  attr_to_hyperparam, object_type='any')

    @classmethod
    def __old_caffe_backward_workaround(cls, prob):
        if prob.ndim == 1:
            return prob.reshape(1, 1, 1, prob.shape[0])

        if prob.ndim == 2:
            return prob.reshape(1, 1, prob.shape[0], prob.shape[1])

        if prob.ndim == 3:
            return prob.reshape(1, prob.shape[0], prob.shape[1], prob.shape[1])

        raise MissingLinkException('unsupported shape %s' % prob.ndim)

    def _get_weights_hash(self, net):
        return self.calculate_weights_hash(net)

    def _get_structure_hash(self, net):
        layers = tuple([i.type for i in net.layers])
        hash_value = self._hash(layers)

        return hash_value

    # endregion


class _Experiment(BaseVanillaExperiment):
    def __init__(self, project, net, every_n_secs=None, every_n_iter=None, **kwargs):
        self.__net = net
        super(_Experiment, self).__init__(project, every_n_secs=every_n_secs, every_n_iter=every_n_iter, **kwargs)

    def _get_weights_hash(self):
        # noinspection PyProtectedMember
        return self._project._get_weights_hash(self.__net)

    def _get_structure_hash(self):
        # noinspection PyProtectedMember
        return self._project._get_structure_hash(self.__net)
