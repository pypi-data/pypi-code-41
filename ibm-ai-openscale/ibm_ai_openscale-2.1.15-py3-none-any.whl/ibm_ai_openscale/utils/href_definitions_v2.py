# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


APPLICATIONS_HREF_PATTERN = u'{}/{}/v2/business_applications'
APPLICATION_DETAILS_HREF_PATTERN = u'{}/{}/v2/business_applications/{}'
MONITOR_DEFINITIONS_HREF_PATTERN = u'{}/{}/v2/monitor_definitions'
MONITOR_DEFINITION_DETAILS_HREF_PATTERN = u'{}/{}/v2/monitor_definitions/{}'
MONITOR_INSTANCES_HREF_PATTERN = u'{}/{}/v2/monitor_instances'
MONITOR_INSTANCE_DETAILS_HREF_PATTERN = u'{}/{}/v2/monitor_instances/{}'
MONITOR_INSTANCE_RUN_HREF_PATTERN = u'{}/{}/v2/monitoring_services/{}/monitor_instances/{}/runs/{}'
DATA_SETS_HREF_PATTERN = u'{}/{}/v2/data_sets'
DATA_SET_RECORDS_HREF_PATTERN = u'{}/{}/v2/data_sets/{}/records'
DATA_SET_DETAILS_HREF_PATTERN = u'{}/{}/v2/data_sets/{}'
MEASUREMENTS_HREF_PATTERN = u"{}/{}/v2/monitor_instances/{}/measurements"


class AIHrefDefinitionsV2:
    def __init__(self, service_credentials):
        self._service_credentials = service_credentials

    def get_applications_href(self):
        return APPLICATIONS_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'])

    def get_application_details_href(self, application_id):
        return APPLICATION_DETAILS_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'], application_id)

    def get_monitor_definitions_href(self):
        return MONITOR_DEFINITIONS_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'])

    def get_monitor_definitions_details_href(self, monitor_definition_id):
        return MONITOR_DEFINITION_DETAILS_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'], monitor_definition_id)

    def get_monitor_instances_href(self):
        return MONITOR_INSTANCES_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'])

    def get_monitor_instance_details_href(self, monitor_instance_id):
        return MONITOR_INSTANCE_DETAILS_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'], monitor_instance_id)

    def get_data_sets_href(self):
        return DATA_SETS_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'])

    def get_data_set_details_href(self, data_set_id):
        return DATA_SET_DETAILS_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'], data_set_id)

    def get_data_set_records_href(self, data_set_id):
        return DATA_SET_RECORDS_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'], data_set_id)

    def get_measurements_href(self, monitor_instance_id):
        return MEASUREMENTS_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'], monitor_instance_id)

    def get_monitor_instance_run_href(self, monitor_id, monitor_instance_id, run_id):
        return MONITOR_INSTANCE_RUN_HREF_PATTERN.format(self._service_credentials['url'], self._service_credentials['data_mart_id'], monitor_id, monitor_instance_id, run_id)
