import abc
import numpy as np
import six

from .base_keras_callback import KerasCallbackBase


@six.add_metaclass(abc.ABCMeta)
class KerasPatchers(KerasCallbackBase):
    _not_a_value = object()

    def _patch_test_function(self, generate_confusion_matrix, callback=None):
        training_model = self._get_training_model()

        # noinspection PyProtectedMember
        training_model._make_test_function()

        test_function = training_model.test_function

        training_model.test_function = self._create_test_function(test_function, generate_confusion_matrix, callback)

    def _unpatch_evaluate_generator(self):
        training_model = self._get_training_model()

        training_model.evaluate_generator = self._evaluate_generator
        del self._evaluate_generator

        training_model.test_function = None

    def _unpatch_test_function(self):
        training_model = self._get_training_model()

        training_model.test_function = None

    def _create_standardize_user_data_func(self):
        from ...data_management.query_data_generator import DataPointWrapper

        def _standardize_user_data(x, y=None, **kwargs):
            metadata = None

            if isinstance(x, DataPointWrapper):
                metadata = x.metadata
                x = x.value

            if isinstance(y, DataPointWrapper):
                metadata = y.metadata
                y = y.value

            result = self.standardize_user_data_func(x, y, **kwargs)

            if metadata:
                result = DataPointWrapper(result, metadata)

            return result

        return _standardize_user_data

    def _patch_standardize_user_data(self):
        training_model = self._get_training_model()
        self.standardize_user_data_func = training_model._standardize_user_data
        training_model._standardize_user_data = self._create_standardize_user_data_func()

    def _unpatch_standardize_user_data(self):
        training_model = self._get_training_model()
        training_model._standardize_user_data = self.standardize_user_data_func
        del self.standardize_user_data_func

    @classmethod
    def search_param(cls, names, args_index, current_args, current_kwargs):
        if len(current_args) > args_index:
            return current_args[args_index]

        for name in names:
            value = current_kwargs.get(name, cls._not_a_value)

            if value is not cls._not_a_value:
                return value

    def _test_scope_prolog(self, steps, name):
        if steps is None:
            return

        super(KerasPatchers, self)._test_scope_prolog(steps, name)

    def __ml_test_loop_wrap(self, is_method_bounded, call_test_loop, test_name):
        def __ml_test_loop(ins_param_index, batch_size_param_index, steps_index):
            def wrap(*args, **kwargs):
                ins = self.search_param(('inputs', 'ins'), ins_param_index, args, kwargs)
                batch_size = self.search_param(('batch_size', ), batch_size_param_index, args, kwargs)
                steps = self.search_param(('steps', ), steps_index, args, kwargs)

                actual_steps = self.__calc_steps_if_possible(ins, batch_size, steps)

                self._test_scope_prolog(actual_steps, name=test_name)

                return self.__wrap_test_results(lambda: call_test_loop(*args, **kwargs))

            return wrap

        _ml_test_loop = __ml_test_loop(2, 3, 5)
        _ml_test_loop_bounded = __ml_test_loop(1, 2, 4)

        return _ml_test_loop_bounded if is_method_bounded else _ml_test_loop

    def __wrap_test_results(self, caller):
        results = caller()

        if not isinstance(results, (list, tuple)):
            actual_results = [results]
        else:
            actual_results = results

        metrics_names = getattr(self._model, 'metrics_names', None) or []
        for metrics_name, val in zip(metrics_names, actual_results):
            self._phase.add_metric(metrics_name, val, is_custom=False)

        return results

    @classmethod
    def __calc_steps_if_possible(cls, ins, batch_size, steps):
        temp_steps = steps
        if steps is None:
            test_samples_count = ins[0].shape[0] if ins and hasattr(ins[0], 'shape') else batch_size
            temp_steps = int(np.ceil(test_samples_count / float(batch_size)))

        return temp_steps

    def _patch_evaluate_generator(self):
        training_model = self._get_training_model()

        self._evaluate_generator = training_model.evaluate_generator
        training_model.evaluate_generator = self._create_ml_evaluate_generator()

    @classmethod
    def __import_training_arrays(cls, training_model):
        from missinglink_kernel.callback.vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(training_model)
        try:
            training_arrays = dynamic_import.bring('engine.training_arrays')
        except AttributeError:
            from tensorflow.python.keras.engine import training_arrays

        return training_arrays

    def _unpatch_test_loop(self):
        training_model = self._get_training_model()

        def unpatch_if_possible(obj, name):
            if not hasattr(obj, name):
                return False

            setattr(obj, name, self.__prev_test_loop)
            del self.__prev_test_loop

            return True

        if not unpatch_if_possible(training_model, '_test_loop'):
            training_arrays = self.__import_training_arrays(training_model)

            unpatch_if_possible(training_arrays, 'test_loop')

    def _patch_test_loop(self, call_test_loop=None, test_name=None):
        training_model = self._get_training_model()

        def patch_if_possible(obj, name):
            if not hasattr(obj, name):
                return None

            prev_test_loop = getattr(obj, name)

            def is_bound(method):
                return hasattr(method, 'im_self') or hasattr(method, '__self__')

            is_method_bounded = is_bound(prev_test_loop)

            ml_test_loop = self.__ml_test_loop_wrap(is_method_bounded, call_test_loop or prev_test_loop, test_name)
            setattr(obj, name, ml_test_loop)

            self.__prev_test_loop = prev_test_loop

            if is_method_bounded:
                def ml_test_loop_function(_self, f, ins, batch_size=None, verbose=0, steps=None):
                    return ml_test_loop(f, ins, batch_size, verbose, steps)

                return ml_test_loop_function

            # noinspection PyUnresolvedReferences
            return ml_test_loop

        # noinspection PyProtectedMember
        test_loop_method = patch_if_possible(training_model, '_test_loop')
        if not test_loop_method:  # keras 2.2
            training_arrays = self.__import_training_arrays(training_model)

            test_loop_method = patch_if_possible(training_arrays, 'test_loop')
            if not test_loop_method:
                self.logger.warning('failed to patch test loop')

        return test_loop_method

    def _get_training_model(self):
        if hasattr(self._model, 'test_function'):
            # Sequential.model is deprecated and throws a warning since 2018-05.
            # So prefer not to use `model.model` if possible.
            # https://github.com/keras-team/keras/blob/8e8f989b850d37a4cbec7a0409343262bd963d0d/keras/engine/sequential.py#L109
            return self._model

        if hasattr(self._model, 'model') and hasattr(self._model.model, 'test_function'):
            return self._model.model

        return self._model

    def _create_test_function(self, original_test_function, generate_confusion_matrix, callback=None):
        def invoke_callback(y, y_true):
            if callable(callback):
                return callback(y, y_true)

            return y, y_true

        def test_function(ins_batch):
            from missinglink_kernel.data_management.query_data_generator import DataPointWrapper

            number_of_inputs = len(self._model.inputs)

            points_info = None
            if isinstance(ins_batch, DataPointWrapper):
                ins_batch, points_info = ins_batch.unfold()

            batch_size = len(ins_batch[0])

            x = ins_batch[:number_of_inputs]
            y_true = ins_batch[number_of_inputs:number_of_inputs + number_of_inputs]

            y = self._model.predict(x, batch_size=batch_size)

            y, y_true = invoke_callback(y, y_true)

            number_of_outputs = len(self._model.inputs)

            if number_of_outputs == 1:
                y = [y]

            result = original_test_function(ins_batch)

            yy = y[0]
            predictions = yy.argmax(axis=-1)
            probabilities = yy.max(axis=-1)
            expected = np.argmax(y_true[0], axis=1)

            expected = expected.tolist()
            predictions = predictions.tolist()
            probabilities = probabilities.tolist()

            if generate_confusion_matrix:
                self._project._test_iteration_end(expected, predictions, probabilities)

            if points_info:
                self._project._log_test_report(expected, predictions, yy, points_info)

            return result

        return test_function

    def _create_ml_evaluate_generator(self):
        def _ml_evaluate_generator(
                generator,
                steps=None,
                max_queue_size=10,
                workers=1,
                use_multiprocessing=False):

            self._project.try_enable_test_report(generator)

            return self.__wrap_test_results(
                lambda: self._evaluate_generator(
                    generator, steps, max_queue_size=max_queue_size, workers=workers, use_multiprocessing=use_multiprocessing))

        return _ml_evaluate_generator
