import six
import numpy as np
import abc


@six.add_metaclass(abc.ABCMeta)
class TensorFlowPatchers(object):
    def _patch_tf_session_for_test(self):
        def after_session_run(session, monitored_results):
            if 'expected' in monitored_results and 'predicted' in monitored_results:
                expected, predicted = monitored_results['expected'], monitored_results['predicted']
                predicted_classes = predicted
                probabilities = predicted

                expected = expected.tolist()
                if len(predicted_classes.shape) == 1:
                    predicted_classes = predicted_classes.tolist()
                else:
                    predicted_classes = np.argmax(predicted_classes, axis=1).tolist()

                if len(probabilities.shape) == 1:
                    probabilities = probabilities.tolist()
                else:
                    probabilities = np.max(probabilities, axis=1).tolist()

                self._phase.add_test_data(predicted_classes, expected, probabilities)

        return after_session_run

    def _patch_tf_session_for_train(self, phase):
        def wrap():
            def after_session_run(session, monitored_results):
                self._train_session = session

                phase.log_metrics(monitored_results, is_custom=False)

            return after_session_run

        return wrap

    @classmethod
    def _patch_tf_session_for_validation(cls, phase):
        def wrap():
            def after_session_run(_session, monitored_results):
                phase.log_metrics(monitored_results, is_custom=False)

            return after_session_run

        return wrap
