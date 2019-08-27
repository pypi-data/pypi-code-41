# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.configuration.monitoring import Monitoring
from ibm_ai_openscale.supporting_classes.enums import MetricTypes
from ibm_ai_openscale.utils import *


_DEFAULT_LIST_LENGTH = 50


@logging_class
class DriftMonitoring:
    """Manage drift monitoring for asset."""

    def __init__(self, subscription, ai_client):
        self._monitoring = Monitoring(subscription, ai_client)
        self._subscription = subscription
        self._ai_client = ai_client

    def enable(self, threshold, min_records, model_path=None):
        """
        Enables drift monitoring. The monitor is being run hourly.

        :param threshold: the threshold for drift metric.
        :type threshold: float

        :param min_records: minial payload record count that triggers monitoring
        :type min_records: int

        :param model_path: path to archive tar.gz with trained drift model.
        :type model_path: str

        A way you might use me is:

        >>> subscription.drift_monitoring.enable(threshold=0.7, min_records=100)
        """

        if model_path is None:
            train_model = True
        else:
            train_model = False
            self._upload_model(model_path)

        response = requests_session.post(
            self._ai_client._href_definitions.get_drift_config_href(self._subscription.binding_uid,
                                                                    self._subscription.uid, train_model=train_model),
            json={
                "drift_threshold": threshold,
                "min_samples": min_records
            },
                headers=self._ai_client._get_headers()
            )

        return handle_response(200, u'drift configuration', response)

    def _upload_model(self, model_path):
        drift_model = open(model_path, mode="rb").read()
        response = requests_session.put(
            self._ai_client._href_definitions.get_drift_model_href(self._subscription.binding_uid, self._subscription.uid),
            data=drift_model,
            headers=self._ai_client._get_headers(content_type='application/octet-stream')
        )

        handle_response(204, u'drift model upload', response, json_response=False)

    def _wait_for_model(self):
        state, stage = self._get_configuration_state()
        while state not in ['finished', 'error']:
            time.sleep(5)
            state, stage = self._get_configuration_state()

        return state, stage

    def _get_configuration_state(self):
        details = self.get_details()
        state = details['parameters']['config_status']['state']

        if 'train_drift_model_stage' in details['parameters']:
            stage = details['parameters']['train_drift_model_stage']
        else:
            stage = None

        return state, stage

    def get_details(self):
        """
        Returns details of drift monitoring configuration.

        :return: configuration of drift monitoring
        :rtype: dict
        """

        return self._monitoring.get_details(monitor_uid=MetricTypes.DRIFT_MONITORING)

    def disable(self):
        """
        Disables drift monitoring.
        """

        self._monitoring.disable(monitor_uid=MetricTypes.DRIFT_MONITORING)

    def run(self, background_mode=True):
        """
        Runs drift check.

        :param background_mode: if set to True, run will be in asynchronous mode, if set to False it will wait for result
        :type background_mode: bool

        :return: result of run, or run details if in background mode
        :rtype: str
        """

        self._wait_for_model()

        response = requests_session.post(
            self._ai_client._href_definitions.get_drift_run_href(
                self._subscription.binding_uid,
                self._subscription.uid
                ),
            data={},
            headers=self._ai_client._get_headers()
        )

        result = handle_response(202, u'drift monitoring run', response)

        if background_mode:
            return result

        success_states = ['COMPLETED']
        failure_states = ['ERROR']
        running_states = ['RUNNING']

        def check_status():
            parameters = self.get_details()['parameters']

            if 'run_status' in parameters:
                return parameters['run_status']
            else:
                return 'INITIALIZING'

        def get_result():
            details = self.get_details()
            status = check_status()

            if status in success_states:
                return "Successfully finished run", None, details
            elif status in running_states:
                return "Drift monitoring is still in RUNNING state", None, details
            else:
                return "Run failed with status: {}".format(status), 'Reason: {}'.format(details), {}

        return print_synchronous_run(
            'Waiting for end of drift monitoring run {}'.format(''),
            check_state=check_status,
            get_result=get_result,
            success_states=success_states,
            failure_states=failure_states
        )

    def get_metrics(self, deployment_uid, format='samples', start_time=None):
        """
        Returns drift metrics of specified type and format for selected subscription

        :param deployment_uid: deployment uid for which the metrics will be retrieved
        :type deployment_uid: str

        :param format: format of returned metrics, possible values: `samples`, `time_series` (optional, default value: `samples`)
        :type format: str

        :param start_time: start time ("2019-05-22T00:00:00Z")- returns metrics from that timestamp to current time. By default last 3 months are used.
        :type start_time: str

        :return: metrics for deployment
        :rtype: dict
        """
        return self._monitoring.get_metrics(deployment_uid=deployment_uid, monitor_uid=MetricTypes.DRIFT_MONITORING,
                                                        format=format, start_time=start_time)

    def show_table(self, limit=10):
        """
        Show records in drift metrics view. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.drift_monitoring.show_table()
        >>> subscription.drift_monitoring.show_table(limit=20)
        >>> subscription.drift_monitoring.show_table(limit=None)
        """

        self._monitoring.show_table(monitor_uid=MetricTypes.DRIFT_MONITORING, limit=limit)

    def print_table_schema(self):
        """
        Show drift metrics view schema.
        """

        self._monitoring.print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of drift metrics view in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas' (optional)
        :type format: {str_type}

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        :return: drift table content
        :rtype: pandas or dict depending on format

        A way you might use me is:

        >>> pandas_table_content = subscription.drift_monitoring.get_table_content()
        >>> table_content = subscription.drift_monitoring.get_table_content(format='python')
        >>> pandas_table_content = subscription.drift_monitoring.get_table_content(format='pandas')
        """

        return self._monitoring.get_table_content(monitor_uid=MetricTypes.DRIFT_MONITORING, format=format, limit=limit)

    def describe_table(self, limit=None):
        """
        Prints description of the content of drift monitoring table (pandas style). It will remove columns with unhashable values.

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.drift_metrics.describe_table()
        """
        self._monitoring.describe_table(monitor_uid=MetricTypes.DRIFT_MONITORING, limit=limit)
