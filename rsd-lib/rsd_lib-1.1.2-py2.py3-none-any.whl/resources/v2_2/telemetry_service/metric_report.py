# Copyright 2019 Intel, Inc.
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
from rsd_lib import utils as rsd_lib_utils


class MetricValueCollectionField(base.ListField):
    """MetricValue field

       A metric Value.
    """

    metric_id = base.Field("MetricId")
    """The value shall be the MetricId of the source metric within the
       associated MetricDefinition
    """

    metric_value = base.Field("MetricValue")
    """The value of the metric represented as a string. Its  data type is
       specified in including MetricResult.MetricDefinition.
    """

    time_stamp = base.Field("TimeStamp")
    """The value shall be an ISO 8601 date time for when the metric value was
       computed. Note that this may be different from the time when this
       instance is created. If Volatile is true for a given metric value
       instance, the TimeStamp changes whenever a new measurement snapshot
       is taken. A management application may establish a time series of metric
       data by retrieving the instances of metric value and sorting them
       according to their TimeStamp.
    """

    metric_property = base.Field("MetricProperty")
    """The value shall be a URI of a property contained in the scope of the
       MetricScope
    """

    metric_definition = base.Field(
        "MetricDefinition", adapter=rsd_lib_utils.get_resource_identity
    )
    """The value shall be a URI to the metric definition of the property"""


class MetricReport(rsd_lib_base.ResourceBase):
    """MetricReport resource class

       A metric report resource that is output from Metric Report Definition.
    """

    metric_values = MetricValueCollectionField("MetricValues")
    """An array of metric values for the metered items of this Metric."""

    @property
    @utils.cache_it
    def metric_report_definition(self):
        """Property to provide reference to `MetricReportDefinition` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        from rsd_lib.resources.v2_2.telemetry_service import \
            metric_report_definition

        return metric_report_definition.MetricReportDefinition(
            self._conn,
            utils.get_sub_resource_path_by(self, "MetricReportDefinition"),
            redfish_version=self.redfish_version,
        )


class MetricReportCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return MetricReport
