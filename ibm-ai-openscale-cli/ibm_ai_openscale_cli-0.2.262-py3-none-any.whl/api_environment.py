# coding=utf-8
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2019
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from distutils.util import strtobool
from pathlib import Path
import logging
import configparser
import os

logger = logging.getLogger(__name__)

class ApiEnvironment():

    # initialize only once
    initialized = False

    # properties
    json_enabled = False
    logging_from_api = False
    icp_gateway_url = None
    icp4d_namespace = None
    properties = None
    is_running_on_icp = False
    log_source_crn = None
    save_service_copy = False

    def __init__(self):
        if not ApiEnvironment.initialized:
            try:
                properties_file = 'fastpath.properties'
                properties_file = os.path.join(os.path.dirname(__file__), '..','..', 'openscale_fastpath_api', 'openscale_fastpath_api', properties_file)
                if Path(properties_file).is_file():
                    config = configparser.ConfigParser()
                    config.read(properties_file)
                    if config.has_section("properties"):
                        ApiEnvironment.properties = config["properties"]
                # set all the properties
                ApiEnvironment.json_enabled = self.get_property_boolean_value('FASTPATH_CLI_JSON_LOGGING_ENABLED', False)
                ApiEnvironment.logging_from_api = self.get_property_boolean_value('FASTPATH_CLI_LOGGING_FROM_API', False)
                ApiEnvironment.icp_gateway_url = self.get_property_value('GATEWAY_URL', 'http://ai-open-scale-ibm-aios-nginx-internal')
                ApiEnvironment.icp4d_namespace = self.get_property_value('ICP4D_NAMESPACE', 'zen')
                ApiEnvironment.is_running_on_icp = self.get_property_boolean_value('ENABLE_ICP', False)
                ApiEnvironment.log_source_crn = self.get_property_value('LOG_SOURCE_CRN', None)
                ApiEnvironment.save_service_copy = self.get_property_boolean_value('SAVE_SERVICE_COPY', False)
                # mark intialization done
                ApiEnvironment.initialized = True
            except Exception as e:
                logger.warning('unable to read api environment: {}'.format(str(e)))

    def is_cli_json_logging_enabled(self):
        return ApiEnvironment.json_enabled

    def is_cli_logging_from_api_enabled(self):
        return ApiEnvironment.logging_from_api

    def get_icp_gateway_url(self):
        return ApiEnvironment.icp_gateway_url

    def get_icp4d_namespace(self):
        return ApiEnvironment.icp4d_namespace

    def is_running_on_icp(self):
        return ApiEnvironment.is_running_on_icp

    def get_log_source_crn(self):
        return ApiEnvironment.log_source_crn

    def get_save_service_copy(self):
        return ApiEnvironment.save_service_copy

    def get_property_value(self, property_name, default=None):
        if os.environ.get(property_name):
            return os.environ.get(property_name)
        elif ApiEnvironment.properties and ApiEnvironment.properties.get(property_name):
            return ApiEnvironment.properties.get(property_name)
        else:
            return default

    def get_property_boolean_value(self, property_name, default=None):
        val = self.get_property_value(property_name, default)
        if val:
            # True values are y, yes, t, true, on and 1;
            # False values are n, no, f, false, off and 0
            try:
                return bool(strtobool(val))
            except ValueError:
                return False