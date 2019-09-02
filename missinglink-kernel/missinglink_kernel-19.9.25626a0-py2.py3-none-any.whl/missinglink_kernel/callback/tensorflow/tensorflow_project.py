# -*- coding: utf-8 -*-
from __future__ import absolute_import
import warnings
from .tensorflow_patchers import TensorFlowPatchers
from .tensorflow_vis import TensorFlowVis

try:
    from contextlib import contextmanager
except ImportError:
    # noinspection PyUnresolvedReferences
    from contextlib2 import contextmanager

import six

from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine, hash_value, calc_tf_variable_value
from ..exceptions import MissingLinkException
from ..settings import HyperParamTypes
from ..vanilla_project import BaseVanillaProject, BaseVanillaExperiment


class TensorFlowProject(BaseVanillaProject):
    """A class for communicating with MissingLinkAI backend.

    A TensorFlowProject instance corresponds to a project created in the backend. This instance
    is used to create new experiments and send the data to the backend.
    """

    def __init__(self, owner_id=None, project_token=None, **kwargs):
        """Construct an new instance.

        # Arguments:
            owner_id: The owner's ID which can be obtained from the web dashboard
            project_token: The project's token which can be obtained from the web dashboard
            host: (Optional.) The backend endpoint
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise MissingLinkException('Please install TensorFlow library')

        super(self.__class__, self).__init__(owner_id, project_token, framework='tensorflow', **kwargs)

    def _create_experiment_scope(self, **kwargs):
        self.__experiment = _Experiment(self, **kwargs)

        return self.__experiment

    def _enter_experiment(self, **kwargs):
        optimizer = kwargs.pop('optimizer', None)

        if optimizer:
            self._hyperparams_from_optimizer(optimizer)

    def estimator_hooks(
            self,
            display_name=None,
            description=None,
            class_mapping=None,
            optimizer=None,
            hyperparams=None,
            monitored_metrics=None,
            custom_metrics=None,
            stopped_callback=None,
            every_n_iter=100,
            every_n_secs=None):

        from .tensorflow_hooks import EstimatorsHooks

        return EstimatorsHooks(
            self,
            display_name=display_name,
            description=description,
            class_mapping=class_mapping,
            optimizer=optimizer,
            hyperparams=hyperparams,
            monitored_metrics=monitored_metrics,
            custom_metrics=custom_metrics,
            stopped_callback=stopped_callback,
            every_n_iter=every_n_iter,
            every_n_secs=every_n_secs
        )

    @contextmanager
    def create_experiment(self,
                          display_name=None,
                          description=None,
                          class_mapping=None,
                          optimizer=None,
                          hyperparams=None,
                          monitored_metrics=None,
                          custom_metrics=None,
                          stopped_callback=None,
                          every_n_iter=None,
                          every_n_secs=None):
        """Create an experiment context.

        This context defines a new experiment and allows the SDK to monitor the progress of the experiment.

        ```python
            # Setup the model

            # Add the optimizer op
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
            train_op = optimizer.minimize(loss)

            project = TensorFlowProject(owner_id='owner_id', project_token='project_token')

            with project.create_experiment(
                display_name='MNIST multilayer perception',
                description='Two fully connected hidden layers',
                class_mapping={0: 'zero', 1: 'one', 2: 'two'},
                optimizer=optimizer,
                hyperparams={'batch_size': 100},
                monitored_metrics={'loss': loss},
                custom_metrics={'custom_loss': custom_loss_func}) as experiment:

                # Run the training loop
        ```

        # Arguments:
            display_name: (Optional.) The display name of the experiment
            description: (Optional.) The description of the experiment
            class_mapping: (Optional.) The class mapping of the experiment
            optimizer: (Optional.) The optimizer used to train the model. This should be an instance of
                `tf.Optimizer` or its subclasses.
            hyperparams: (Optional.) A dictionary of hyper-parameters whose keys are the parameter names. The
                values are the parameter's values.
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            An experiment context manager
        """

        with self.experiment(
                display_name=display_name,
                description=description,
                class_mapping=class_mapping,
                hyperparams=hyperparams,
                optimizer=optimizer,
                monitored_metrics=monitored_metrics,
                custom_metrics=custom_metrics,
                every_n_iter=every_n_iter,
                every_n_secs=every_n_secs,
                stopped_callback=stopped_callback) as experiment:
            yield experiment

    def variable_to_value(self, variable):
        import tensorflow as tf

        # noinspection PyBroadException
        try:
            if isinstance(variable, tf.Variable):
                sess = tf.get_default_session()
                if sess is not None:
                    return sess.run(variable)
                else:
                    return variable.eval()
            elif isinstance(variable, tf.Tensor):
                return getattr(variable, "name")
        except Exception:
            warnings.warn("was not able to get variable %s" % variable.name)
            return calc_tf_variable_value(variable)

        return super(TensorFlowProject, self).variable_to_value(variable)

    # noinspection SpellCheckingInspection
    def _hyperparams_from_optimizer(self, optimizer):
        optimizer_to_attrs = {
            'AdadeltaOptimizer': ['_lr', '_rho', '_epsilon'],
            'AdagradOptimizer': ['_learning_rate', '_initial_accumulator_value'],
            'AdagradDAOptimizer': ['_learning_rate', '_initial_gradient_squared_accumulator_value',
                                   '_l1_regularization_strength', '_l2_regularization_strength'],
            'AdamOptimizer': ['_lr', '_beta1', '_beta2', '_epsilon'],
            'FtrlOptimizer': ['_learning_rate', '_learning_rate_power', '_initial_accumulator_value',
                              '_l1_regularization_strength', '_l2_regularization_strength'],
            'GradientDescentOptimizer': ['_learning_rate'],
            'MomentumOptimizer': ['_learning_rate', '_momentum', '_use_nesterov'],
            'ProximalAdagradOptimizer': ['_learning_rate', '_initial_accumulator_value',
                                         '_l1_regularization_strength', '_l2_regularization_strength'],
            'ProximalGradientDescentOptimizer': ['_learning_rate', '_l1_regularization_strength',
                                                 '_l2_regularization_strength'],
            'RMSPropOptimizer': ['_learning_rate', '_decay', '_momentum', '_epsilon']
        }

        attr_to_hyperparams = {
            '_lr': 'learning_rate',
            '_decay': 'learning_rate_decay'
        }

        for attrs in optimizer_to_attrs.values():
            for attr in attrs:
                if attr not in attr_to_hyperparams and attr.startswith('_'):
                    hyperparam = attr[1:]
                    attr_to_hyperparams[attr] = hyperparam

        self.set_hyperparams(optimizer_algorithm=optimizer.get_name())
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, optimizer, optimizer_to_attrs, attr_to_hyperparams)

    @classmethod
    def _get_weights(cls, session):
        import tensorflow as tf

        variables = tf.trainable_variables()

        return session.run(variables)

    @classmethod
    def _get_weights_hash(cls, session):
        return cls.calculate_weights_hash(session)

    @classmethod
    def _get_structure_hash(cls, session):
        import tensorflow as tf

        variables = tf.trainable_variables()
        shapes = tuple([tuple(x.get_shape().as_list()) for x in variables])
        return hash_value(shapes)

    @classmethod
    def calculate_weights_hash(cls, session):
        if session is None:
            return None

        weights = cls._get_weights(session)

        weights_hashes = []
        for weight in weights:
            weight_hash = hasharray(weight)
            weights_hashes.append(weight_hash)

        hash_key = hashcombine(*weights_hashes)
        return cls._WEIGHTS_HASH_PREFIX + hash_key


# noinspection PyAbstractClass
class _Experiment(BaseVanillaExperiment, TensorFlowVis, TensorFlowPatchers):
    """Context manager for an experiment."""

    def __init__(self, project, monitored_metrics=None, custom_metrics=None, **kwargs):
        super(_Experiment, self).__init__(project, **kwargs)

        self._validate_monitored_fetches(monitored_metrics)
        self._validate_custom_metrics(custom_metrics)

        self._monitored_fetches = monitored_metrics or {}
        self._custom_metrics = custom_metrics or {}
        self._train_session = None
        self._tf_properties = {}

    def _get_structure_hash(self):
        session = self._train_session
        # noinspection PyProtectedMember
        return self._project._get_structure_hash(session)

    def _get_weights_hash(self):
        session = self._train_session
        # noinspection PyProtectedMember
        return self._project._get_weights_hash(session)

    def _update_train_validation_params(self, monitored_metrics, custom_metrics):
        monitored_fetches = monitored_metrics or {}
        monitored_fetches.update(self._monitored_fetches)

        custom_metrics = custom_metrics or {}
        custom_metrics.update(self._custom_metrics)

        return monitored_fetches, custom_metrics

    def set_properties(self, **kwargs):
        if 'output_layer' in kwargs:
            output_layer = kwargs.pop('output_layer')
            self._tf_properties['output_layer'] = output_layer

        super(_Experiment, self).set_properties(**kwargs)

    @contextmanager
    def train(self, monitored_metrics=None, custom_metrics=None, session_instance=None):
        """Marks a training context.

        This context allows the SDK to patch the `tf.Session.run` and calculate training metrics if needed.
        As such, there must be only 1 `tf.Session.run` call within this context. Otherwise, the training
        iteration might be incorrectly incremented.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as training metrics.

        # Arguments:
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            None
        """

        if self._has_train_context():
            phase = self._phase
            with self._train_scope_wrapper(phase, monitored_metrics, custom_metrics, session_instance):
                yield phase
        else:
            with super(_Experiment, self).train() as train_phase:
                yield train_phase

    def _update_test_params(self, monitored_metrics=None, custom_metrics=None, expected=None, predicted=None):
        monitored_fetches = monitored_metrics or {}
        if expected is not None and predicted is not None:
            monitored_fetches['expected'] = expected
            monitored_fetches['predicted'] = predicted

        return self._update_train_validation_params(monitored_fetches, custom_metrics)

    @contextmanager
    def test(self, expected=None, predicted=None, test_iterations=None, monitored_metrics=None, custom_metrics=None, session_instance=None):
        """
        Marks a test context.

        This context allows the SDK to patch the `tf.Session.run` and calculate test metrics if needed.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as test metrics.

        :param predicted: a tensor for predictions
        :param expected: a tensor for expected values
        :param monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
        :param custom_metrics: (Optional.) A dictionary whose values are metric functions.
        :return None
        """
        from .tensorflow_patch_session import TfSessionRunPatchContext

        steps = test_iterations or -1  # calc test steps if possible

        with super(_Experiment, self).test(steps=steps) as test_phase:
            self._validate_monitored_fetches(monitored_metrics)
            self._validate_custom_metrics(custom_metrics)

            monitored_fetches, custom_metrics = self._update_test_params(monitored_metrics, custom_metrics, expected, predicted)

            with TfSessionRunPatchContext(self._patch_tf_session_for_test, monitored_fetches, session_instance):
                yield test_phase

    @contextmanager
    def _run_scope_wrapper(self, patcher, phase, monitored_metrics, custom_metrics, session_instance):
        from .tensorflow_patch_session import TfSessionRunPatchContext

        self._validate_monitored_fetches(monitored_metrics, raise_exception=False)
        self._validate_custom_metrics(custom_metrics, raise_exception=False)

        monitored_fetches, custom_metrics = self._update_train_validation_params(monitored_metrics, custom_metrics)

        with TfSessionRunPatchContext(patcher(phase), monitored_fetches, session_instance):
            yield
            phase.log_metrics(custom_metrics, is_custom=True)

    @contextmanager
    def _train_scope_wrapper(self, phase, monitored_metrics, custom_metrics, session_instance):
        with self._run_scope_wrapper(self._patch_tf_session_for_train, phase, monitored_metrics, custom_metrics, session_instance):
            yield

    # noinspection PyMethodOverriding
    @contextmanager
    def _validation_scope_wrapper(self, phase, monitored_metrics, custom_metrics, session_instance):
        with self._run_scope_wrapper(self._patch_tf_session_for_validation, phase, monitored_metrics, custom_metrics, session_instance):
            yield

    @contextmanager
    def validation(self, monitored_metrics=None, custom_metrics=None, session_instance=None, **kwargs):
        """Marks a validation context.

        This context allows the SDK to patch the `tf.Session.run` to calculate validation metrics.
        Unlike the `train` scope, you can include multiple runs e.g. by using a for-loop looping over a
        validation dataset by batches. The SDK will average out the validation metrics across these runs
        and collect the averaged value.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as training metrics.

        # Arguments:
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            None
        """
        with super(_Experiment, self).validation(monitored_metrics=monitored_metrics,
                                                 custom_metrics=custom_metrics,
                                                 session_instance=session_instance, **kwargs) as validation_phase:
            yield validation_phase

    @classmethod
    def _validate_monitored_item(cls, default_graph, name, fetch):
        if not isinstance(name, six.string_types):
            raise ValueError("monitored metrics key %s is not a string" % name)

        try:
            default_graph.as_graph_element(fetch, allow_operation=False)
        except TypeError as e:
            raise TypeError('Fetch %r has invalid type %r, must be a string or Tensor. (%s)'
                            % (fetch, type(fetch), str(e)))
        except ValueError as e:
            raise ValueError('Fetch %r cannot be interpreted as a Tensor. (%s)' % (fetch, str(e)))
        except KeyError as e:
            raise ValueError('Fetch %r cannot be found in the default graph. (%s)' % (fetch, str(e)))

    def _validate_monitored_fetches(self, monitored_fetches, raise_exception=True):
        import tensorflow as tf

        if monitored_fetches is None:
            return

        if not isinstance(monitored_fetches, dict):
            raise ValueError('Fetches %s must be a dictionary.' % monitored_fetches)

        default_graph = tf.get_default_graph()

        invalid_keys = []
        for name, fetch in monitored_fetches.items():
            try:
                self._validate_monitored_item(default_graph, name, fetch)
            except (ValueError, KeyError, TypeError) as ex:
                self._logger.warning(ex)

                if raise_exception:
                    raise

                invalid_keys.append(name)

        for invalid_key_name in invalid_keys:
            del monitored_fetches[invalid_key_name]

    @staticmethod
    def _validate_custom_metrics_dict(custom_metrics):
        if custom_metrics is None:
            return

        if not isinstance(custom_metrics, dict):
            raise ValueError('Custom metrics %s must be a dictionary.' % custom_metrics)

        for name, metric_func in custom_metrics.items():
            if not isinstance(name, six.string_types):
                raise ValueError("Custom metric's key %s is not a string" % name)

            if not callable(metric_func):
                raise ValueError('Custom metric function of %s must be callable' % name)

    def _validate_custom_metrics(self, custom_metrics, raise_exception=True):
        try:
            self._validate_custom_metrics_dict(custom_metrics)
        except Exception as ex:
            self._logger.warning(ex)
            if raise_exception:
                raise

    # endregion
