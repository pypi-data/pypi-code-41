# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import re

from azureml.widgets._constants import MULTIRUN_WIDGET_REFRESH_SLEEP_TIME, WIDGET_REFRESH_SLEEP_TIME_DATABRICKS
from azureml.widgets.run_details import PLATFORM
# noinspection PyProtectedMember
from azureml._restclient.metrics_client import MetricsClient
# noinspection PyProtectedMember
from azureml.widgets._userrun._run_details import _UserRunDetails


if PLATFORM == 'JUPYTER':
    # noinspection PyProtectedMember
    from azureml.widgets._rl_run._widget import _RLWidget
    REFRESH_SLEEP_TIME = MULTIRUN_WIDGET_REFRESH_SLEEP_TIME
else:
    assert PLATFORM == "DATABRICKS"
    # noinspection PyProtectedMember
    from azureml.widgets._rl_run._universal_widget import _RLWidget
    REFRESH_SLEEP_TIME = WIDGET_REFRESH_SLEEP_TIME_DATABRICKS


class _RLRunDetails(_UserRunDetails):
    """RL run details widget."""

    def __init__(self, run_instance):
        """Initialize a RL run widget call.

        :param run_instance: The RL run instance.
        :type run_instance: RLRun
        """
        super().__init__(run_instance, "reinforcementlearning", refresh_time=REFRESH_SLEEP_TIME,
                         widget=_RLWidget)

    def _add_additional_properties(self, run_properties):

        super()._add_additional_properties(run_properties)
        tags = run_properties['tags']
        if 'queue_timeout_seconds' in tags:
            run_properties['queue_timeout_seconds'] = tags['queue_timeout_seconds']
        if 'startup_grace_period_seconds' in tags:
            run_properties['startup_grace_period_seconds'] = tags['startup_grace_period_seconds']

    def _get_child_runs(self):
        _child_runs = super()._get_child_runs()
        prepRunSuccess = None
        for run in _child_runs:
            run_id = run['run_id']
            run_type = run['run_type']
            run_status = run['status']
            if run_type == 'preparation' and run_status != 'Failed':
                prepRunSuccess = run
                continue

            if run_id in self.tags:
                arguments = json.loads(self.tags[run_id])
                if arguments:
                    for name, value in arguments.items():
                        run['param_' + name] = value

        if prepRunSuccess is not None:
            _child_runs.remove(prepRunSuccess)

        return _child_runs

    def _post_process_log(self, log_name: str, log_content: str) -> str:
        # TODO: Change log name
        if "hyperdrive" in log_name:
            lines = re.findall(r'(?<=<START>)(.*?)(?=<END>)', log_content)
            if lines:
                log_content = '\r\n'.join(lines)
        return super()._post_process_log(log_name, log_content)

    # For RL run, the parent run metrics should be the metrics of the first child run.
    # RL run can have atmost 3 child runs - Trainer, worker and simulator
    # Trainer and worker runs have the same result for get_metrics()
    # Simulator run has no metrics logged.
    def _get_run_metrics(self):
        _child_runs = super()._get_child_runs()
        if len(_child_runs) > 0:
            child_run_id = _child_runs[0]['run_id']
            child_run_metrics = self.metrics_client.get_metrics_for_widgets([child_run_id])
            run_metrics = MetricsClient.convert_metrics_to_objects(child_run_metrics[child_run_id])
            transformed_run_metrics = []

            for key, value in run_metrics.items():
                metric_data = {
                    'name': key,
                    'run_id': self.run_instance.id,
                    # get_metrics can return array or not based on metrics being series or scalar value
                    'categories': list(range(len(value))) if isinstance(value, list) else [0],
                    'series': [{'data': value if isinstance(value, list) else [value]}]}
                transformed_run_metrics.append(metric_data)

            model_explanation_metric = self._get_model_explanation_metric()
            if (model_explanation_metric):
                transformed_run_metrics.append(model_explanation_metric)

            return transformed_run_metrics
