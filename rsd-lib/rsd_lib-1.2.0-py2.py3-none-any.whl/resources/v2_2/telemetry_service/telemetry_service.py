# Copyright 2018 Intel, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sushy.resources import base
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_2.telemetry_service import metric_definition
from rsd_lib.resources.v2_2.telemetry_service import metric_report
from rsd_lib.resources.v2_2.telemetry_service import metric_report_definition
from rsd_lib.resources.v2_2.telemetry_service import triggers
from rsd_lib import utils as rsd_lib_utils


class TelemetryService(rsd_lib_base.ResourceBase):
    """TelemetryService resource class

       This is the schema definition for the Metrics Service. It represents
       the properties for the service itself and has links to collections of
       metric definitions and metric report definitions.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    max_reports = base.Field("MaxReports", adapter=rsd_lib_utils.num_or_none)
    """The maximum number of MetricReports that are supported by this service.
    """

    min_collection_interval = base.Field("MinCollectionInterval")
    """The minimum supported interval between collections."""

    supported_collection_functions = base.Field("SupportedCollectionFunctions")
    """Function to perform over each sample."""

    @property
    @utils.cache_it
    def metric_definitions(self):
        """Property to provide reference to `MetricDefinitionCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return metric_definition.MetricDefinitionCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "MetricDefinitions"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def metric_report_definitions(self):
        """Property to provide reference to `MetricReportDefinitionCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return metric_report_definition.MetricReportDefinitionCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "MetricReportDefinitions"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def metric_reports(self):
        """Property to provide reference to `MetricReportCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return metric_report.MetricReportCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "MetricReports"),
            redfish_version=self.redfish_version,
        )

    @property
    @utils.cache_it
    def triggers(self):
        """Property to provide reference to `TriggersCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return triggers.TriggersCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Triggers"),
            redfish_version=self.redfish_version,
        )
