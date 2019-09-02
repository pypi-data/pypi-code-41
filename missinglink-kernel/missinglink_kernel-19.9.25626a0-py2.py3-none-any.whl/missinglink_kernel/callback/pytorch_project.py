# -*- coding: utf-8 -*-
import copy

from .vanilla_project import BaseVanillaExperiment, BaseVanillaProject
from .phase import ExperimentCounters
from .settings import HyperParamTypes
from contextlib import contextmanager
from .utilities.utils import get_nested_attribute_if_exists
import numpy as np


class PyTorchProject(BaseVanillaProject):
    def __init__(self, owner_id=None, project_token=None, host=None, **kwargs):
        super(PyTorchProject, self).__init__(owner_id, project_token, host=host, framework='pytorch', **kwargs)

    def variable_to_value(self, variable):
        import torch

        if isinstance(variable, torch.Tensor):
            return variable.item()

        return super(PyTorchProject, self).variable_to_value(variable)

    def _hyperparams_from_optimizer(self, optimizer):
        optimizer_to_attrs = {
            'Adadelta': ['rho', 'eps', 'lr', 'weight_decay'],
            'Adagrad': ['lr', 'lr_decay', 'weight_decay'],
            'Adam': ['lr', 'beta_1', 'beta_2', 'eps', 'weight_decay'],
            'Adamax': ['lr', 'beta_1', 'beta_2', 'eps', 'weight_decay'],
            'ASGD': ['lr', 'lambd', 'alpha', 't0', 'weight_decay'],
            'LBFGS': ['lr', 'max_iter', 'max_eval', 'tolerance_grad', 'tolerance_change', 'history_size'],
            'RMSprop': ['lr', 'alpha', 'eps', 'weight_decay'],
            'Rprop': ['lr', 'etaminus', 'etaplus', 'minimum_step_size', 'maximum_step_size'],
            'SGD': ['lr', 'dampening', 'weight_decay'],
        }
        attr_to_hyperparam = {
            'lr': 'learning_rate',
            'lr_decay': 'learning_rate_decay',
            'eps': 'epsilon',
            'lambd': 'lambda',
            'max_iter': 'max_iteration',
            'max_eval': 'max_evaluation',
            'tolerance_grad': 'tolerance_gradient',
        }

        optimizer_type = optimizer.__class__.__name__
        params_groups = optimizer.param_groups

        if len(params_groups) < 1:
            return

        hyperparams = copy.copy(params_groups[0])

        expansions = {
            'betas': ['beta_1', 'beta_2'],
            'etas': ['etaminus', 'etaplus'],
            'step_sizes': ['minimum_step_size', 'maximum_step_size']
        }

        for name, names in expansions.items():
            values = hyperparams.get(name)
            if values is not None and len(values) == len(names):
                for key, val in zip(names, values):
                    hyperparams[key] = val

        self.set_hyperparams(optimizer_algorithm=optimizer_type)
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, hyperparams, optimizer_to_attrs,
                                  attr_to_hyperparam, object_type=optimizer_type)

    def _hyperparams_from_data_object(self, data_object):
        if data_object is None:
            return

        iterator_attributes = ['train', 'repeat', 'shuffle', 'sort', 'sort_within_batch', 'device']
        object_to_attributes = {
            'DataLoader': ['num_workers', 'pin_memory', 'drop_last'],
            'Iterator': iterator_attributes,
            'BucketIterator': iterator_attributes,
            'BPTTIterator': iterator_attributes,
        }

        object_type = data_object.__class__.__name__
        if object_type not in object_to_attributes:
            return

        attribute_to_hyperparam = {}  # hyperparams will have the same names as the attributes

        self._extract_hyperparams(HyperParamTypes.CUSTOM, data_object, object_to_attributes, attribute_to_hyperparam)

        hyperparams = {'data_object': object_type}

        # maps hyperparams names to the attribute that holds their value
        extraction_map = {
            'dataset': ['dataset', '__class__', '__name__'],
            'batch_size': ['batch_size']
        }

        if object_type == 'DataLoader':
            extraction_map['collate_function'] = ['collate_fn', '__name__']
            extraction_map['sampler'] = ['sampler', '__class__', '__name__']

        elif object_type in object_to_attributes:
            extraction_map['batch_size_function'] = ['batch_size_fn', '__name__']

        for hyperparam_name, attributes_path in extraction_map.items():
            hyperparam_value = get_nested_attribute_if_exists(data_object, attributes_path)
            if hyperparam_value is not None:
                hyperparams[hyperparam_name] = hyperparam_value

        if hasattr(data_object, '__len__'):
            hyperparams['epoch_size'] = len(data_object)

        try:
            hyperparams['samples_count'] = len(data_object.dataset)
        except (TypeError, AttributeError):
            pass

        self.set_hyperparams(**hyperparams)

    # noinspection PyMethodMayBeStatic
    def _create_experiment_scope(self, **kwargs):
        model = kwargs.pop('model')
        metrics = kwargs.pop('metrics')
        return _Experiment(self, model, metrics, **kwargs)

    def _enter_experiment(self, **kwargs):
        optimizer = kwargs.pop('optimizer', None)
        train_data_object = kwargs.pop('train_data_object', None)

        if optimizer:
            self._hyperparams_from_optimizer(optimizer)

        self._hyperparams_from_data_object(train_data_object)

    @contextmanager
    def create_experiment(
            self,
            model,
            display_name=None,
            description=None,
            class_mapping=None,
            optimizer=None,
            train_data_object=None,
            hyperparams=None,
            metrics=None,
            stopped_callback=None):

        with self.experiment(
                display_name=display_name,
                description=description,
                class_mapping=class_mapping,
                hyperparams=hyperparams,
                metrics=metrics,
                stopped_callback=stopped_callback,
                model=model,
                optimizer=optimizer,
                train_data_object=train_data_object) as experiment:
            yield experiment

    @classmethod
    def _get_structure_hash(cls, net):
        layers = []
        for m in net.modules():
            layers.append(str(m))
        layers = tuple(layers)
        hash_string = cls._hash(layers)

        return hash_string

    @staticmethod
    def _get_weights_hash(net):
        from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine

        hashes = list()
        for m in net.modules():
            layer_hashes = [hasharray(i.data.cpu().numpy()) for i in m.parameters()]
            hashes.extend(layer_hashes)

        hash_key = hashcombine(*hashes)

        # noinspection PyProtectedMember
        return PyTorchProject._WEIGHTS_HASH_PREFIX + hash_key

    def calculate_weights_hash(self, net):
        return self._get_weights_hash(net)


class _Experiment(BaseVanillaExperiment):
    def __init__(self, project, model, metrics=None, every_n_secs=None, every_n_iter=None, **kwargs):
        metrics = metrics or {}
        self._wrapped_metrics = {}
        self.wrap_metrics(metrics)

        self.model = model
        super(_Experiment, self).__init__(project, every_n_secs, every_n_iter)

    @property
    def metrics(self):
        return self._wrapped_metrics

    def _get_metric_data(self, result):
        variable = result.data.item() if hasattr(result.data, 'item') else result.data[0]
        return self._project.variable_to_value(variable)

    def _wrap(self, key, base):
        def wrapped(*args, **kwargs):
            result = base(*args, **kwargs)

            # Do not monitor metrics if inside test context
            if self._context_validator.in_test_context:
                return result

            is_custom_metric = not (hasattr(result, 'data') and hasattr(result.data, '__getitem__'))

            metric_data = result if is_custom_metric else self._get_metric_data(result)

            self.log_metric(key, metric_data)

            return result

        return wrapped

    def _wrap_metrics_dict(self, metrics_dict):
        wrapped = copy.copy(metrics_dict)

        for key, base in wrapped.items():
            wrapped[key] = self._wrap(key, base)

        self._wrapped_metrics.update(wrapped)

        return wrapped

    def _wrap_metrics_list(self, metrics_list):
        wrapped = []

        for base in metrics_list:
            key = base.__name__
            wrapped_function = self._wrap(key, base)

            wrapped.append(wrapped_function)
            self._wrapped_metrics[key] = wrapped_function

        return wrapped

    def _wrap_metric(self, base):
        key = base.__name__
        wrapped = self._wrap(key, base)
        self._wrapped_metrics[key] = wrapped

        return wrapped

    def wrap_metrics(self, metrics):
        """
        :param metrics: Single, list or dictionary of pytorch functionals
        """
        wrapped = None
        if isinstance(metrics, dict):
            wrapped = self._wrap_metrics_dict(metrics)
        elif isinstance(metrics, (list, tuple)):
            wrapped = self._wrap_metrics_list(metrics)
        elif metrics is not None:
            wrapped = self._wrap_metric(metrics)

        return wrapped

    def _get_structure_hash(self):
        net = self.model
        # noinspection PyProtectedMember
        return self._project._get_structure_hash(net)

    def _get_weights_hash(self):
        net = self.model
        # noinspection PyProtectedMember
        return self._project._get_weights_hash(net)

    def _on_enter_loop(self, iterable):
        # noinspection PyProtectedMember
        self._project._hyperparams_from_data_object(iterable)

    @contextmanager
    def test(self, model=None, test_data_object=None, target_attribute_name='label', steps=None, **kwargs):
        """
        `test` context for generating a confusion matrix.

        if you use a `DataLoader`, use like so:

            with test(model, test_data_object=test_loader):
                # test code

        if you use a `Iterator`, a `BucketIterator`, or a `BPTTIterator`, use like so:

            with test(model, test_data_object=test_iterator, target_attribute_name='label'):
                # test code

        Otherwise, test manually, like so:

            with test(model, steps=1000):
                # call here `test_iterations` times to `confusion_matrix`

        :param model: The tested model. If not specified, defaults to the experiment's model.
        :param test_data_object: A `DataLoader` or a `Iterator` that provides the test data.
        :param target_attribute_name: The attribute name of the target of every batch,
            so that `batch.target_attribute_name` is the target. Defaults to 'label'.
        :param steps: For manual test. number of test iterations.
            Should be equal to the amount of times `confusion_matrix` will be called.
        :return: None
        """

        if test_data_object:
            steps = len(test_data_object)

        steps = steps or kwargs.pop('test_iterations', None)

        with super(_Experiment, self).test(steps) as test_phase:
            if model is None:
                model = self.model

            if test_data_object:
                with self._test_with_patched_object(model, test_data_object, target_attribute_name):
                    yield test_phase
            else:
                yield test_phase

    @contextmanager
    def _test_with_patched_object(self, model, object_to_patch, target_attribute_name=None):
        map_type_to_patch_function = {
            'Iterator': self._patch_torchtext_iterator,
            'BPTTIterator': self._patch_torchtext_iterator,
            'BucketIterator': self._patch_torchtext_iterator,
            'DataLoader': self._patch_data_loader,
        }

        object_type = type(object_to_patch).__name__

        try:
            patch_function = map_type_to_patch_function[object_type]
        except KeyError:
            message = "TypeError: object of type %s is not supported for test. Please use manual test."
            self._logger.warning(message)
            yield
        else:
            # this is just to access the variables from the inner scopes
            # noinspection PyClassHasNoInit
            class OuterScope:
                target = []

            map_patch_function_to_arguments = {
                self._patch_torchtext_iterator: [object_to_patch, target_attribute_name, OuterScope, self._logger],
                self._patch_data_loader: [object_to_patch, OuterScope]
            }

            patch_function_args = map_patch_function_to_arguments[patch_function]
            unpatch_function = patch_function(*patch_function_args)

            def hook(_module, _input, output):
                # this is invoked after the model is forwarded
                self.confusion_matrix(output, OuterScope.target)

            handle = model.register_forward_hook(hook)

            yield

            handle.remove()
            unpatch_function()

    @staticmethod
    def _patch_data_loader(data_loader, outer_scope):
        base_iter = type(data_loader).__iter__

        def patched_iter(*args, **kwargs):
            data_loader_iter = base_iter(*args, **kwargs)
            base_next = type(data_loader_iter).__next__

            outer_scope.data_loader_iter = data_loader_iter
            outer_scope.base_next = base_next

            def patched_next(*args_, **kwargs_):
                outer_scope.data, outer_scope.target = base_next(*args_, **kwargs_)

                return outer_scope.data, outer_scope.target

            type(data_loader_iter).__next__ = type(data_loader_iter).next = patched_next

            return data_loader_iter

        type(data_loader).__iter__ = patched_iter

        def unpatch():
            type(data_loader).__iter__ = base_iter
            type(outer_scope.data_loader_iter).__next__ = type(
                outer_scope.data_loader_iter).next = outer_scope.base_next

        return unpatch

    @staticmethod
    def _patch_torchtext_iterator(iterator, target_attribute_name, outer_scope, logger):
        base_iter = type(iterator).__iter__

        def patched_iter(*args, **kwargs):
            for batch in base_iter(*args, **kwargs):
                outer_scope.target = getattr(batch, target_attribute_name, None)

                if outer_scope.target is None:
                    outer_scope.target = []
                    logger.warning(
                        "Could not find %s in batch. Make sure target_attribute_name is correct" % target_attribute_name
                    )

                yield batch

        type(iterator).__iter__ = patched_iter

        def unpatch():
            type(iterator).__iter__ = base_iter

        return unpatch

    def _can_call_confusion_matrix(self):
        if not self._context_validator.in_test_context:
            self._logger.warning("Failed to generate confusion matrix: Not in `test` context")
            return

        return True

    def _target_to_expected(self, target):
        try:
            target = target.data if type(target).__name__ == 'Variable' else target
            expected = [int(x) for x in target]
        except (ValueError, TypeError) as e:
            self._logger.warning("Failed to generate confusion matrix: `target` is not good: %s" % str(e))
            return None

        return expected

    def _output_to_expected(self, output):
        try:
            output_numpy = output.cpu().data.numpy()

            predictions = np.argmax(output_numpy, axis=1).tolist() if len(output_numpy) > 0 else []
            probabilities = np.max(output_numpy, axis=1).tolist() if len(output_numpy) > 0 else []
        except (AttributeError, np.AxisError, TypeError) as e:
            self._logger.warning("Failed to generate confusion matrix: `output` is not good: %s" % str(e))
            return None, None

        return predictions, probabilities

    def confusion_matrix(self, output, target):
        """
        Explicit function to generate a confusion matrix. Call only inside a `test` context.
        :param output: A 2D `torch.autograd.Variable`. The output of the model for a single batch.
        :param target: A 1D `torch.autograd.Variable` or Array-Like. The targets (labels) of a single batch.
        :return: None
        """

        if not self._can_call_confusion_matrix():
            return

        expected = self._target_to_expected(target)
        predictions, probabilities = self._output_to_expected(output)

        self._phase.add_test_data(expected, predictions, probabilities)
