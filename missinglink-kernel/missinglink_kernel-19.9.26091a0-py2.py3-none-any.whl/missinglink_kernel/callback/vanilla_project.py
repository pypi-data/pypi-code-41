# -*- coding: utf-8 -*-
from __future__ import absolute_import
import abc
from contextlib import contextmanager
import six

from .queries import QueriesStore
from .exceptions import MissingLinkException, ExperimentStopped
from .phase import ExperimentCounters, PhaseEpoch
from .base_callback import BaseCallback, BaseContextValidator, Context


@six.add_metaclass(abc.ABCMeta)
class BaseVanillaProject(BaseCallback):
    @abc.abstractmethod
    def _enter_experiment(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

    @abc.abstractmethod
    def _create_experiment_scope(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

    @contextmanager
    def experiment(self, display_name=None, description=None, class_mapping=None, hyperparams=None, stopped_callback=None, **kwargs):
        self.set_properties(display_name=display_name, description=description, class_mapping=class_mapping)
        self._enter_experiment(**kwargs)

        if hyperparams is not None:
            self.set_hyperparams(**hyperparams)

        self.stopped_callback = stopped_callback or self.stopped_callback
        contextless_queries = self.get_query_objects()

        with self._create_experiment_scope(queries=contextless_queries, **kwargs) as experiment:
            try:
                yield experiment
            except ExperimentStopped:
                self._handle_stopped()


class VanillaProject(BaseVanillaProject):
    def __init__(self, owner_id=None, project_token=None, stopped_callback=None, **kwargs):
        framework = kwargs.pop('framework', 'vanilla')
        super(VanillaProject, self).__init__(
            owner_id, project_token, stopped_callback=stopped_callback, framework=framework, **kwargs)

    def _enter_experiment(self, **kwargs):
        pass

    # noinspection PyMethodMayBeStatic
    def _create_experiment_scope(self, **kwargs):
        return VanillaExperiment(self, **kwargs)


@six.add_metaclass(abc.ABCMeta)
class ModelHashInterface(object):
    def __wrap_method_with_warning(self, func, message):
        try:
            return func()
        except AttributeError:
            raise
        except Exception as ex:
            self._logger.warning(message, ex)
            return None

    def get_weights_hash(self):
        return self.__wrap_method_with_warning(self._get_weights_hash, 'Failed to calculate weights hash %s')

    def get_structure_hash(self):
        return self.__wrap_method_with_warning(self._get_structure_hash, 'Failed to calculate structure hash %s')

    @abc.abstractmethod
    def _get_weights_hash(self):
        pass

    @abc.abstractmethod
    def _get_structure_hash(self):
        pass


class ZeroIndexedGenerators(object):
    @staticmethod
    def range_generator(limit):
        for index in range(limit):
            yield index

    @staticmethod
    def condition_generator(condition):
        index = 0
        while condition(index):
            yield index
            index += 1

    @staticmethod
    def iterable_generator(iterable):
        index = 0
        for x in iterable:
            yield index, x
            index += 1


@six.add_metaclass(abc.ABCMeta)
class BaseVanillaExperiment(ModelHashInterface):
    def __init__(self, project, every_n_secs=None, every_n_iter=None, queries=None, **kwargs):
        self._project = project
        self._current_epoch = 0
        self._context_validator = ContextValidator(self._project.logger)
        self._experiment_counters = ExperimentCounters(every_n_secs, every_n_iter)
        self._epochs = None
        self._queries = QueriesStore()

        if queries is not None:
            self._queries.add_query_objects(queries)

    def __enter__(self):
        self._context_validator.enter(Context.EXPERIMENT)
        return self

    def __exit__(self, *exc):
        self._context_validator.exit(Context.EXPERIMENT)

        return False

    def _has_train_context(self):
        return self._context_validator.is_in_context(Context.TRAIN)

    def set_properties(self, **kwargs):
        self._project.set_properties(**kwargs)

    @property
    def _logger(self):
        return self._project.logger

    def log_metric(self, name, value):
        self._phase.log_metric(name, value, is_custom=True)

    add_metric = log_metric

    def get_average_metrics(self):
        return self._context_validator.get_average_metrics()

    def __start_new_experiment_if_needed(self):
        if not self._project.has_experiment:
            self._project.new_experiment(throw_exceptions=False)

    @contextmanager
    def __enter_train_context_if_needed(self):
        if self._context_validator.in_train_context:
            yield
        else:
            with self.train() as train_scope:
                yield train_scope

    @staticmethod
    def _remove_false(**kwargs):
        return {key: val for key, val in kwargs.items() if val}

    @contextmanager
    def train(self):
        self.__start_new_experiment_if_needed()

        def end_epilog():
            self._queries.add_query_objects(self._phase.get_query_objects())

            params = self._remove_false(
                data_management=self._phase.get_queries_data(),
                iterations=self._iteration,
                metricData=self.get_average_metrics())

            # noinspection PyProtectedMember
            self._project._train_end(**params)

        train_params = self._remove_false(queries=self._queries.get_all_query_obj())
        with self._context_validator.context(Context.TRAIN, **train_params) as train_phase:
            structure_hash = self.get_structure_hash()

            # noinspection PyProtectedMember
            self._project._train_begin(structure_hash=structure_hash)
            try:
                yield train_phase
            except ExperimentStopped:
                end_epilog()
                raise

            end_epilog()

    @contextmanager
    def _validation_scope_wrapper(self, phase, *args, **kwargs):
        yield

    @contextmanager
    def validation(self, **kwargs):
        with self._context_validator.context(Context.VALIDATION) as phase:
            with self._validation_scope_wrapper(phase, **kwargs) as val_phase:
                yield val_phase or phase

    def _test_scope_prolog(self, steps, name):
        self._on_test_begin(steps, name)

    def _test_scope_epilog(self):
        query_data = self._phase.get_query_data()
        self.__on_test_end(self._phase.labels, query_data=query_data)

    @contextmanager
    def test(self, steps=None, name=None):
        self.__start_new_experiment_if_needed()

        with self._context_validator.context(Context.TEST) as test_phase:
            self._test_scope_prolog(steps, name)
            yield test_phase
            self._test_scope_epilog()

    def _on_enter_loop(self, iterable):
        pass

    def _is_epoch_iteration(self, epoch_size):
        return self._experiment_counters.is_epoch_iteration(epoch_size)

    @contextmanager
    def loop_context(self, max_iterations=None, condition=None, iterable=None, epoch_size=None):
        """Provides a training loop generator.

        This generator allows the MissingLinkAI SDK to correctly track each training iteration and its
        corresponding metrics.

        You would normally write the training loop as
        ```python
            for step in range(1000):
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step in experiment.loop(max_iterations=1000):
                # Perform a training step
        ```

        If you wants to run the training steps while a condition is satisfied, a while loop is preferred.
        ```python
            threshold = 10
            step = 0
            while loss > threshold:
                # Perform a training step
                step += 1
        ```

        This can be converted to
        ```python
            threshold = 10
            for step in experiment.loop(condition=lambda _: loss > threshold):
                # Perform a training step
        ```

        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for sample in data:
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step, sample in experiment.loop(iterable=data):
                # Perform a training step
        ```

        If you want to collect and analyze metrics with respect to epochs, specify the `epoch_size` param with
        the number of iterations per epoch.

        # Arguments:
            max_iterations: The maximum number of training iterations to be run. Cannot be provided
                together with `condition` or `iterable`.
            condition: The condition function to run the training steps. Once the condition fails, the
                training will terminate immediately. This function takes 1 parameter: a 0-based index
                indicating how many iterations have been run.
                Cannot be provided together with `max_iterations` or `iterable`.
            iterable: The iterable to iterate over in the loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `max_iterations` or `condition`.
            epoch_size: (Optional.) The number of iterations per epoch.

        # Yields:
            A 0-based index, if provided with `max_iterations` or with `condition`.
            A tuple of 0-based index and a sample, if provided with `iterable`.
        """
        message = '`loop` should be called with one of max_iterations, condition, or iterable.' \
                  ' Called with: max_iterations=%s, condition=%s, iterable=%s instead.' % \
                  (max_iterations, condition, iterable)
        self.__assert_single_argument((max_iterations, condition, iterable), message)

        self._project.set_hyperparams(
            max_iterations=max_iterations,
            epoch_size=epoch_size,
            total_epochs=self._total_epochs(max_iterations, epoch_size))

        with self.__enter_train_context_if_needed():
            with self._context_validator.context(Context.LOOP):
                self._on_enter_loop(iterable)

                # In the case of multiple loops on the same experiment,
                # you might expect index to start at `self._iteration - 1`,
                # so the index of the loops keeps incrementing from loop to loop.
                # However, we decided to keep it this way, to keep on consistency with the `range` function.
                generator = self._choose_generator(max_iterations, condition, iterable)

                def post_data():
                    is_epoch_iteration = self._is_epoch_iteration(epoch_size)

                    weights_hash = self.get_weights_hash() \
                        if self._is_iteration_with_validation or is_epoch_iteration else None

                    batch_weights_hash = weights_hash if self._is_iteration_with_validation else None

                    self._project.batch_end2(
                        self._iteration,
                        self.get_average_metrics(),
                        batch=self._batch,
                        epoch=self._epoch,
                        weights_hash=batch_weights_hash,
                        is_test=self._is_iteration_with_validation)

                    should_increment_epoch = False

                    if is_epoch_iteration:
                        should_increment_epoch = True

                        self._project.epoch_end(self._epoch, self.get_average_metrics(), weights_hash=weights_hash)

                    return should_increment_epoch

                yield self._experiment_counters.get_loop(self._context_validator, generator, post_data)

    @contextmanager
    def batch_loop_context(self, batches=None, condition=None, iterable=None):
        """Provides a batch loop generator.

        This generator should be nested in a `epoch_loop` generator. Please see `epoch_loop` for more details.

        This generator can be used like the `range` function:
        ```python
        for batch_index in experiment.batch_loop(batches):
            # Preform training on a single batch
        ```

        Also, this generator can be used to iterate over an iterable, like so:
        ```python
        for batch_index, batch_data in experiment.bath_loop(iterable=data):
            # Preform training on a single batch
        ```

        # Arguments:
            batches: The total number of batches. Cannot be provided with `iterable`.
            iterable: The iterable to iterate over in the batch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `batches`.
        # Yields:
            A 0-based index, if provided with `batches`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """
        message = '`batch_loop` should be called with one of batches, condition, or iterable.' \
                  ' Called with: batches=%s, condition=%s, iterable=%s instead.' % \
                  (batches, condition, iterable)
        self.__assert_single_argument((batches, condition, iterable), message)

        with self._context_validator.context(Context.BATCH_LOOP):
            epoch_size = self._epoch_batch_loop_total_iterations(batches, iterable)
            max_iterations = self._batch_loop_max_iterations(self._epochs, epoch_size)
            self._project.set_hyperparams(epoch_size=epoch_size, max_iterations=max_iterations)

            # noinspection PyProtectedMember
            self._on_enter_loop(iterable)

            generator = self._choose_generator(batches, condition, iterable)

            def post_data():
                weights_hash = self.get_weights_hash() if self._is_iteration_with_validation else None

                self._project.batch_end2(
                    self._iteration, self.get_average_metrics(), batch=self._batch, epoch=self._epoch,
                    weights_hash=weights_hash, is_test=self._is_iteration_with_validation)

            yield self._experiment_counters.get_batch_loop(self._context_validator, generator, post_data)

    def batch_loop(self, batches=None, condition=None, iterable=None):
        """Provides a batch loop generator.

        This generator should be nested in a `epoch_loop` generator. Please see `epoch_loop` for more details.

        This generator can be used like the `range` function:
        ```python
        for batch_index in experiment.batch_loop(batches):
            # Preform training on a single batch
        ```

        This generator can be used like a `while` loop:
        ```python
        threshold = 10
        for batch_index in experiment.batch_loop(condition=lambda _: loss > threshold):
            # Preform training on a single batch
        ```

        This generator can be used to iterate over an iterable, like so:
        ```python
        for batch_index, batch_data in experiment.bath_loop(iterable=data):
            # Preform training on a single batch
        ```
        # Arguments:
            batches: The total number of batches. Cannot be provided with `iterable` or with `condition`.
            condition: The condition function to run the training batches.
                The condition is evaluated every batch. If the condition is false, the loop terminates.
                This function takes 1 parameter: a 0-based index indicating how many batches have been run.
                Cannot be provided together with `batches` or with `iterable`.
            iterable: The iterable to iterate over in the batch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `batches` or with `condition`.
        # Yields:
            A 0-based index, if provided with `batches` or with `condition`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """

        with self.batch_loop_context(batches, condition, iterable) as loop:
            for result in loop:
                yield result

    @contextmanager
    def epoch(self, epoch):
        with self._context_validator.context(Context.EPOCH_LOOP, epoch=epoch) as epoch_phase:
            # noinspection PyNoneFunctionAssignment
            yield epoch_phase
            weights_hash = self.get_weights_hash()

            self._project.epoch_end(
                epoch,
                self.get_average_metrics(),
                weights_hash=weights_hash)

    @contextmanager
    def batch(self, iteration, batch=None, epoch=None):
        epoch = self._phase.epoch if isinstance(self._phase, PhaseEpoch) else epoch

        with self._context_validator.context(Context.BATCH_LOOP) as batch_phase:
            self._experiment_counters.set_iteration(iteration)

            yield batch_phase

            self._project.batch_end2(
                iteration,
                self.get_average_metrics(),
                epoch=epoch or 1,
                batch=batch or iteration)

    @contextmanager
    def epoch_loop_context(self, epochs=None, condition=None, iterable=None):
        """Provides a epoch loop generator.

        This generator is used together with the `batch_loop` generator to run your training with
        epochs and batches using nested loops.

        You would normally write your training loops as
        ```python
        for epoch in range(epochs):
            for batch in range(batches):
                # Perform a training step on a batch of data
        ```

        This can be converted to
        ```python
        for epoch in experiment.epoch_loop(epochs):
            for batch in experiment.batch_loop(batches):
                # Perform a training step on a batch of data
        ```

        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for epoch_data in data:
                # Perform an epoch
        ```

        This can be converted to
        ```python
            for step, epoch_data in experiment.epoch_loop(iterable=data):
                for batch in experiment.batch_loop(batches):
                    # Perform a training step on a batch of data
        ```

        # Arguments:
            epochs: The total number of epochs
            iterable: The iterable to iterate over in the epoch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `epochs`.
        # Yields:
            A 0-based index, if provided with `epochs`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """
        message = '`epoch_loop` should be called with one of epochs, condition, or iterable.' \
                  ' Called with: epochs=%s, condition=%s, iterable=%s instead.' % \
                  (epochs, condition, iterable)
        self.__assert_single_argument((epochs, condition, iterable), message)

        self._epochs = self._epoch_batch_loop_total_iterations(epochs, iterable)
        self._project.set_hyperparams(total_epochs=self._epochs)

        with self.__enter_train_context_if_needed():
            with self._context_validator.context(Context.EPOCH_LOOP):
                self._on_enter_loop(iterable)

                generator = self._choose_generator(epochs, condition, iterable)

                def post_data():
                    # noinspection PyNoneFunctionAssignment
                    weights_hash = self.get_weights_hash()

                    self._project.epoch_end(self._epoch, self.get_average_metrics(), weights_hash=weights_hash)

                yield self._experiment_counters.get_epoch_loop(self._context_validator, generator, post_data)

    def epoch_loop(self, epochs=None, condition=None, iterable=None):
        """Provides a epoch loop generator.

        This generator is used together with the `batch_loop` generator to run your training with
        epochs and batches using nested loops.

        You would normally write your training loops as
        ```python
        for epoch in range(epochs):
            for batch in range(batches):
                # Perform a training step on a batch of data
        ```

        This can be converted to
        ```python
        for epoch in experiment.epoch_loop(epochs):
            for batch in experiment.batch_loop(batches):
                # Perform a training step on a batch of data
        ```

        If you want to loop while a condition is satisfied:
        ```python
            threshold = 10
            while loss > threshold:
                for batch in range(batches):
                    # Perform a training step on a batch of data
        ```

        This can be converted to:
        ```python
            for epoch in experiment.epoch_loop(condition=lambda _: loss > threshold):
                for batch in experiment.batch_loop(batches):
                    # Perform a training step on a batch of data
        ```

        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for epoch_data in data:
                for batch in range(batches):
                    # Perform a training step on a batch of data
        ```

        This can be converted to
        ```python
            for step, epoch_data in experiment.epoch_loop(iterable=data):
                for batch in experiment.batch_loop(batches):
                    # Perform a training step on a batch of data
        ```
        # Arguments:
            epochs: The total number of epochs.
                Cannot be provided together with `condition` or with `iterable`.
            condition: The condition function to run the training epochs.
                The condition is evaluated every epoch. If the condition is false, the loop terminates.
                This function takes 1 parameter: a 0-based index indicating how many epochs have been run.
                Cannot be provided together with `epochs` or with `iterable`.
            iterable: The iterable to iterate over in the epoch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `epochs` or with `condition`.
        # Yields:
            A 0-based index, if provided with `epochs` or with `condition`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """

        with self.epoch_loop_context(epochs, condition, iterable) as loop:
            for result in loop:
                yield result

    def loop(self, max_iterations=None, condition=None, iterable=None, epoch_size=None):
        """Provides a training loop generator.

        This generator allows the MissingLinkAI SDK to correctly track each training iteration and its
        corresponding metrics.

        You would normally write the training loop as
        ```python
            for step in range(1000):
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step in experiment.loop(max_iterations=1000):
                # Perform a training step
        ```

        If you wants to run the training steps while a condition is satisfied, a while loop is preferred.
        ```python
            threshold = 10
            step = 0
            while loss > threshold:
                # Perform a training step
                step += 1
        ```

        This can be converted to
        ```python
            threshold = 10
            for step in experiment.loop(condition=lambda _: loss > threshold):
                # Perform a training step
        ```
        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for sample in data:
                # Perform a training step
        ```
        This can be converted to
        ```python
            for step, sample in experiment.loop(iterable=data):
                # Perform a training step
        ```
        If you want to collect and analyze metrics with respect to epochs, specify the `epoch_size` param with
        the number of iterations per epoch.

        # Arguments:
            max_iterations: The maximum number of training iterations to be run. Cannot be provided
                together with `condition` or `iterable`.
            condition: The condition function to run the training steps. Once the condition fails, the
                training will terminate immediately. This function takes 1 parameter: a 0-based index
                indicating how many iterations have been run.
                Cannot be provided together with `max_iterations` or `iterable`.
            iterable: The iterable to iterate over in the loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `max_iterations` or `condition`.
            epoch_size: (Optional.) The number of iterations per epoch.

        # Yields:
            A 0-based index, if provided with `max_iterations` or with `condition`.
            A tuple of 0-based index and a sample, if provided with `iterable`.
        """

        with self.loop_context(max_iterations, condition, iterable, epoch_size) as loop:
            for result in loop:
                yield result

    @staticmethod
    def _total_epochs(max_iterations, epoch_size):
        if not max_iterations or not epoch_size:
            return None

        return max_iterations // epoch_size

    def _on_test_begin(self, steps, name=None):
        # noinspection PyNoneFunctionAssignment
        weights_hash = self.get_weights_hash()

        # noinspection PyProtectedMember
        self._project._test_begin(steps, weights_hash, name=name)

    def __on_test_end(self, labels, query_data=None):
        params = self._remove_false(
            is_finished=True,
            metric_data=self.get_average_metrics(),
            class_mapping=labels,
            query_data=query_data)

        # noinspection PyProtectedMember
        self._project._test_iteration_end(
            self._phase.y_test, self._phase.y_pred, self._phase.probabilities, **params)

    @staticmethod
    def _choose_generator(iterations, condition, iterable):
        if iterations is not None:
            return ZeroIndexedGenerators.range_generator(iterations)

        if condition is not None:
            return ZeroIndexedGenerators.condition_generator(condition)

        if iterable is not None:
            return ZeroIndexedGenerators.iterable_generator(iterable)

        raise MissingLinkException('Provide batches, condition or iterable to batch_loop.')

    @property
    def _phase(self):
        return self._context_validator.last_phase

    @staticmethod
    def _batch_loop_max_iterations(epochs, epoch_size):
        try:
            return epochs * epoch_size
        except TypeError:
            return None

    @staticmethod
    def _epoch_batch_loop_total_iterations(iterations, iterable):
        # This function is called by:
        #   `epoch_loop` to calculate the number of total epochs
        #   `batch_loop` to calculate the epoch size (= batches per epoch)
        if iterable is None:
            return iterations

        if hasattr(iterable, '__len__'):
            return len(iterable)

        return None

    @classmethod
    def __assert_single_argument(cls, args, error_message=''):
        # count arguments
        args_count = len([arg for arg in args if arg is not None])

        if args_count != 1:
            raise MissingLinkException('Bad Arguments: ' + error_message)

    @property
    def _is_iteration_with_validation(self):
        return self._context_validator.is_iteration_with_validation

    @property
    def _batch(self):
        # noinspection PyProtectedMember
        return self._experiment_counters._batch

    @property
    def _epoch(self):
        # noinspection PyProtectedMember
        return self._experiment_counters._epoch

    @property
    def _iteration(self):
        # noinspection PyProtectedMember
        return self._experiment_counters._iteration

    def get_queries_data(self):
        return self._queries.get_all()


class VanillaExperiment(BaseVanillaExperiment):
    def _get_structure_hash(self):
        pass

    def _get_weights_hash(self):
        pass


class ContextValidator(BaseContextValidator):
    """
    This class validates if we can enter or exit a context.
    """

    def __init__(self, logger):
        super(ContextValidator, self).__init__(logger)

    def _validate_validation_context(self):
        if not self._contexts or self.last_context not in [Context.LOOP, Context.EPOCH_LOOP, Context.BATCH_LOOP]:
            # Do not raise exception because we don't want to halt the experiment halfway
            self._logger.error('`validation` context must be nested immediately in a `loop` '
                               'or `epoch_loop` or `batch_loop` generator. This context is ignored')

    def _validate_test_context(self):
        message = '`test` context cannot be inside `test` context or inside `validation` context, ' \
                  'and must be inside an `experiment` context. This context is ignored.'
        self._exclude_from_contexts([Context.VALIDATION, Context.TEST], message)

    def _validate_train_context(self):
        # Train context does nothing, so the user can do whatever he wants with it
        if not self._contexts or self.last_context not in [Context.LOOP, Context.BATCH_LOOP, Context.EXPERIMENT]:
            raise MissingLinkException('`train` context must be nested immediately in an `loop` '
                                       'or `batch_loop` generator.')

    def _exclude_from_contexts(self, excluded, error_message=''):
        if not self._contexts or self.last_context in excluded:
            # Do not raise exception because we don't want to halt the experiment halfway
            self._logger.error(error_message)
