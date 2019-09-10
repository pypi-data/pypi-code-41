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

from jsonschema import validate
import logging

from sushy.resources import base
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_2.telemetry_service import metric
from rsd_lib.resources.v2_2.telemetry_service import metric_report
from rsd_lib.resources.v2_2.telemetry_service \
    import metric_report_definition_schemas
from rsd_lib import utils as rsd_lib_utils


LOG = logging.getLogger(__name__)


class ScheduleField(base.CompositeField):
    """Schedule field

       Schedule a series of occurrences.
    """

    name = base.Field("Name")
    """The Schedule name."""

    lifetime = base.Field("Lifetime")
    """The time after provisioning when the schedule as a whole expires."""

    max_occurrences = base.Field(
        "MaxOccurrences", adapter=rsd_lib_utils.num_or_none
    )
    """Maximum number of scheduled occurrences."""

    initial_start_time = base.Field("InitialStartTime")
    """Time for initial occurrence."""

    recurrence_interval = base.Field("RecurrenceInterval")
    """Distance until the next occurrences."""

    enabled_days_of_week = base.Field("EnabledDaysOfWeek")
    """Days of the week when scheduled occurrences are enabled, for enabled
       days of month and months of year.
    """

    enabled_days_of_month = base.Field("EnabledDaysOfMonth")
    """Days of month when scheduled occurrences are enabled."""

    enabled_months_of_year = base.Field("EnabledMonthsOfYear")
    """Months of year when scheduled occurrences are enabled."""

    enabled_intervals = base.Field("EnabledIntervals")
    """Intervals when scheduled occurrences are enabled."""


class WildcardCollectionField(base.ListField):

    name = base.Field("Name")
    """The name of Wildcard."""

    keys = base.Field("Keys")
    """An array of Key values to substitute for the wildcard."""


class MetricReportDefinition(rsd_lib_base.ResourceBase):
    """MetricReportDefinition resource class

       A set of metrics that are collected periodically.
    """

    schedule = ScheduleField("Schedule")
    """A schedule for collecting metric values."""

    metric_report_type = base.Field("MetricReportType")
    """The collection type for the corresponding metric values."""

    collection_time_scope = base.Field("CollectionTimeScope")
    """Time scope for collecting the corresponding metric values."""

    report_actions = base.Field("ReportActions")
    """This property specifies what action is perform when a metric  report is
       generated.
    """

    volatile = base.Field("Volatile", adapter=bool)
    """Entries in the resulting metric value properties are reused on each
       scheduled interval.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    wildcards = WildcardCollectionField("Wildcards")
    """Wildcards used to replace values in MetricProperties array property."""

    metric_properties = base.Field("MetricProperties")
    """A collection of URI that relates to the metric properties that will be
       included in the metric report.
    """

    @property
    @utils.cache_it
    def metrics(self):
        """Property to provide collection to `Metric`

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return [
            metric.Metric(
                self._conn, path, redfish_version=self.redfish_version
            )
            for path in utils.get_sub_resource_path_by(
                self, "Metrics", is_collection=True
            )
        ]

    @property
    @utils.cache_it
    def metric_report(self):
        """Property to provide reference to `MetricReport` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return metric_report.MetricReport(
            self._conn,
            utils.get_sub_resource_path_by(self, "MetricReport"),
            redfish_version=self.redfish_version,
        )

    def delete(self):
        """Delete report definition"""
        self._conn.delete(self.path)


class MetricReportDefinitionCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return MetricReportDefinition

    def create_metric_report_definition(self, metric_report_definition_req):
        """Create a new report definition

        :param metric_report_definition_req: JSON for event subscription
        :returns: The uri of the new event report definition
        """
        target_uri = self._path
        validate(
            metric_report_definition_req,
            metric_report_definition_schemas.report_definition_req_schema,
        )

        resp = self._conn.post(target_uri, data=metric_report_definition_req)

        report_definition_url = resp.headers["Location"]
        LOG.info("report definition created at %s", report_definition_url)
        return report_definition_url[report_definition_url.find(self._path):]
