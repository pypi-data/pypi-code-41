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

import json
import mock
import testtools

from rsd_lib.resources.v2_2.telemetry_service import metric_definition
from rsd_lib.resources.v2_2.telemetry_service import metric_report
from rsd_lib.resources.v2_2.telemetry_service import metric_report_definition
from rsd_lib.resources.v2_2.telemetry_service import telemetry_service
from rsd_lib.resources.v2_2.telemetry_service import triggers


class TelemetryTestCase(testtools.TestCase):
    def setUp(self):
        super(TelemetryTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/telemetry_service.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_service_inst = telemetry_service.TelemetryService(
            self.conn, "/redfish/v1/TelemetryService", redfish_version="1.1.0"
        )

    def test__parse_attributes(self):
        self.telemetry_service_inst._parse_attributes()
        self.assertEqual("1.1.0", self.telemetry_service_inst.redfish_version)
        self.assertEqual("Enabled", self.telemetry_service_inst.status.state)
        self.assertEqual("OK", self.telemetry_service_inst.status.health)
        self.assertEqual(
            None, self.telemetry_service_inst.status.health_rollup
        )
        self.assertEqual(None, self.telemetry_service_inst.max_reports)
        self.assertEqual(
            None, self.telemetry_service_inst.min_collection_interval
        )
        self.assertEqual(
            None, self.telemetry_service_inst.supported_collection_functions
        )

    def test_metric_definitions(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "metric_definition_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_metric_definitions = (
            self.telemetry_service_inst.metric_definitions
        )
        # | THEN |
        self.assertIsInstance(
            actual_metric_definitions,
            metric_definition.MetricDefinitionCollection,
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(
            actual_metric_definitions,
            self.telemetry_service_inst.metric_definitions,
        )
        self.conn.get.return_value.json.assert_not_called()

    def test_metric_definitions_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "metric_definition_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_service_inst.metric_definitions,
            metric_definition.MetricDefinitionCollection,
        )

        # On refreshing the telemetry service instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/telemetry_service.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_service_inst.invalidate()
        self.telemetry_service_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "metric_definition_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_service_inst.metric_definitions,
            metric_definition.MetricDefinitionCollection,
        )

    def test_metric_report_definitions(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "metric_report_definition_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_report_definitions = (
            self.telemetry_service_inst.metric_report_definitions
        )
        # | THEN |
        self.assertIsInstance(
            actual_report_definitions,
            metric_report_definition.MetricReportDefinitionCollection,
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(
            actual_report_definitions,
            self.telemetry_service_inst.metric_report_definitions,
        )
        self.conn.get.return_value.json.assert_not_called()

    def test_metric_report_definitions_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "metric_report_definition_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_service_inst.metric_report_definitions,
            metric_report_definition.MetricReportDefinitionCollection,
        )

        # On refreshing the telemetry service instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/telemetry_service.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_service_inst.invalidate()
        self.telemetry_service_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "metric_report_definition_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_service_inst.metric_report_definitions,
            metric_report_definition.MetricReportDefinitionCollection,
        )

    def test_metric_reports(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "metric_report_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_metric_reports = self.telemetry_service_inst.metric_reports
        # | THEN |
        self.assertIsInstance(
            actual_metric_reports, metric_report.MetricReportCollection
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(
            actual_metric_reports, self.telemetry_service_inst.metric_reports
        )
        self.conn.get.return_value.json.assert_not_called()

    def test_metric_reports_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "metric_report_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_service_inst.metric_reports,
            metric_report.MetricReportCollection,
        )

        # On refreshing the telemetry service instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/telemetry_service.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_service_inst.invalidate()
        self.telemetry_service_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "metric_report_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_service_inst.metric_reports,
            metric_report.MetricReportCollection,
        )

    def test_triggers(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/triggers_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_triggers = self.telemetry_service_inst.triggers
        # | THEN |
        self.assertIsInstance(actual_triggers, triggers.TriggersCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_triggers, self.telemetry_service_inst.triggers)
        self.conn.get.return_value.json.assert_not_called()

    def test_triggers_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/triggers_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_service_inst.triggers, triggers.TriggersCollection
        )

        # On refreshing the telemetry service instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/telemetry_service.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_service_inst.invalidate()
        self.telemetry_service_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/triggers_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_service_inst.triggers, triggers.TriggersCollection
        )
