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

from rsd_lib.resources.v2_2.ethernet_switch import ethernet_switch_port
from rsd_lib.resources.v2_2.ethernet_switch import ethernet_switch_port_metrics


class PortTestCase(testtools.TestCase):
    def setUp(self):
        super(PortTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "ethernet_switch_port.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_inst = ethernet_switch_port.EthernetSwitchPort(
            self.conn,
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1",
            redfish_version="1.0.2",
        )

    def test_metrics(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "ethernet_switch_port_metrics.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_metrics = self.port_inst.metrics
        # | THEN |
        self.assertIsInstance(
            actual_metrics,
            ethernet_switch_port_metrics.EthernetSwitchPortMetrics,
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_metrics, self.port_inst.metrics)
        self.conn.get.return_value.json.assert_not_called()

    def test_metrics_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "ethernet_switch_port_metrics.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.port_inst.metrics,
            ethernet_switch_port_metrics.EthernetSwitchPortMetrics,
        )

        # On refreshing the port instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "ethernet_switch_port.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_inst.invalidate()
        self.port_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "ethernet_switch_port_metrics.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.port_inst.metrics,
            ethernet_switch_port_metrics.EthernetSwitchPortMetrics,
        )


class PortCollectionTestCase(testtools.TestCase):
    def setUp(self):
        super(PortCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/"
            "ethernet_switch_port_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.port_col = ethernet_switch_port.EthernetSwitchPortCollection(
                self.conn,
                "/redfish/v1/EthernetSwitches/Switch1/Ports",
                redfish_version="1.0.2",
            )

    def test__parse_attributes(self):
        self.port_col._parse_attributes()
        self.assertEqual("1.0.2", self.port_col.redfish_version)
        self.assertEqual("Ethernet Switch Port Collection", self.port_col.name)
        self.assertEqual(
            ("/redfish/v1/EthernetSwitches/Switch1/Ports/Port1",),
            self.port_col.members_identities,
        )

    @mock.patch.object(
        ethernet_switch_port, "EthernetSwitchPort", autospec=True
    )
    def test_get_member(self, mock_port):
        self.port_col.get_member(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1"
        )
        mock_port.assert_called_once_with(
            self.port_col._conn,
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1",
            redfish_version=self.port_col.redfish_version,
        )

    @mock.patch.object(
        ethernet_switch_port, "EthernetSwitchPort", autospec=True
    )
    def test_get_members(self, mock_port):
        members = self.port_col.get_members()
        mock_port.assert_called_with(
            self.port_col._conn,
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1",
            redfish_version=self.port_col.redfish_version,
        )
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
