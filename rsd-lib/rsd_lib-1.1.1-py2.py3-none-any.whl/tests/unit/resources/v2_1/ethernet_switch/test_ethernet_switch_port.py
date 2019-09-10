# Copyright 2018 99cloud, Inc.
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

from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_port
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_static_mac
from rsd_lib.resources.v2_1.ethernet_switch import vlan_network_interface
from rsd_lib.tests.unit.fakes import request_fakes


class EthernetSwitchPortTestCase(testtools.TestCase):
    def setUp(self):
        super(EthernetSwitchPortTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/ethernet_switch_port.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_inst = ethernet_switch_port.EthernetSwitchPort(
            self.conn,
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1",
            redfish_version="1.0.2",
        )

    def test__parse_attributes(self):
        self.port_inst._parse_attributes()
        self.assertEqual("1.0.2", self.port_inst.redfish_version)
        self.assertEqual("Port1", self.port_inst.identity)
        self.assertEqual("Switch Port", self.port_inst.name)
        self.assertEqual("description-as-string", self.port_inst.description)
        self.assertEqual("sw0p10", self.port_inst.port_id)
        self.assertEqual("Enabled", self.port_inst.status.state)
        self.assertEqual("OK", self.port_inst.status.health)
        self.assertEqual("OK", self.port_inst.status.health_rollup)
        self.assertEqual("Ethernet", self.port_inst.link_type)
        self.assertEqual("Up", self.port_inst.operational_state)
        self.assertEqual("Up", self.port_inst.administrative_state)
        self.assertEqual(10000, self.port_inst.link_speed_mbps)
        self.assertEqual("sw2", self.port_inst.neighbor_info.switch_id)
        self.assertEqual("11", self.port_inst.neighbor_info.port_id)
        self.assertEqual(
            "CustomerWritableThing", self.port_inst.neighbor_info.cable_id
        )
        self.assertEqual("00:11:22:33:44:55", self.port_inst.neighbor_mac)
        self.assertEqual(1520, self.port_inst.frame_size)
        self.assertEqual(True, self.port_inst.autosense)
        self.assertEqual(True, self.port_inst.full_duplex)
        self.assertEqual("2c:60:0c:72:e6:33", self.port_inst.mac_address)
        self.assertEqual(
            "192.168.0.10", self.port_inst.ipv4_addresses[0].address
        )
        self.assertEqual(
            "255.255.252.0", self.port_inst.ipv4_addresses[0].subnet_mask
        )
        self.assertEqual(
            "Static", self.port_inst.ipv4_addresses[0].address_origin
        )
        self.assertEqual(
            "192.168.0.1", self.port_inst.ipv4_addresses[0].gateway
        )
        self.assertEqual(
            "fe80::1ec1:deff:fe6f:1e24",
            self.port_inst.ipv6_addresses[0].address,
        )
        self.assertEqual(64, self.port_inst.ipv6_addresses[0].prefix_length)
        self.assertEqual(
            "Static", self.port_inst.ipv6_addresses[0].address_origin
        )
        self.assertEqual(
            "Preferred", self.port_inst.ipv6_addresses[0].address_state
        )
        self.assertEqual("Logical", self.port_inst.port_class)
        self.assertEqual("LinkAggregationStatic", self.port_inst.port_mode)
        self.assertEqual("Upstream", self.port_inst.port_type)
        self.assertEqual(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/VLANs/VLAN1",
            self.port_inst.links.primary_vlan,
        )
        self.assertEqual(
            "/redfish/v1/EthernetSwitches/Switch1", self.port_inst.links.switch
        )
        self.assertEqual(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/LAG1",
            self.port_inst.links.member_of_port,
        )
        self.assertEqual((), self.port_inst.links.port_members)
        self.assertEqual(
            "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1",
            self.port_inst.links.active_acls[0],
        )
        self.assertEqual(
            "/redfish/v1/Systems/1/EthernetInterfaces/3",
            self.port_inst.links.oem.intel_rackscale.neighbor_interface,
        )

    def test_delete(self):
        self.port_inst.delete()
        self.port_inst._conn.delete.assert_called_once_with(
            self.port_inst.path
        )

    def test_static_mac(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_static_mac_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_static_macs = self.port_inst.static_macs
        # | THEN |
        self.assertIsInstance(
            actual_static_macs,
            ethernet_switch_static_mac.EthernetSwitchStaticMACCollection,
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        self.assertIs(actual_static_macs, self.port_inst.static_macs)
        self.conn.get.return_value.json.assert_not_called()

    def test_static_mac_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_static_mac_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.port_inst.static_macs,
            ethernet_switch_static_mac.EthernetSwitchStaticMACCollection,
        )

        # On refreshing...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_port.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_inst.invalidate()
        self.port_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_static_mac_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.port_inst.static_macs,
            ethernet_switch_static_mac.EthernetSwitchStaticMACCollection,
        )

    def test_vlans(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_port_vlan_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_vlans = self.port_inst.vlans
        # | THEN |
        self.assertIsInstance(
            actual_vlans, vlan_network_interface.VLanNetworkInterfaceCollection
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        self.assertIs(actual_vlans, self.port_inst.vlans)
        self.conn.get.return_value.json.assert_not_called()

    def test_vlans_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_port_vlan_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.port_inst.vlans,
            vlan_network_interface.VLanNetworkInterfaceCollection,
        )

        # On refreshing...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_port.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_inst.invalidate()
        self.port_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_port_vlan_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.port_inst.vlans,
            vlan_network_interface.VLanNetworkInterfaceCollection,
        )

    def test_update(self):
        data = {
            "AdministrativeState": "Up",
            "LinkSpeedMbps": 1000,
            "FrameSize": 1500,
            "Autosense": False,
            "Links": {
                "PrimaryVLAN": {
                    "@odata.id": "/redfish/v1/EthernetSwitches/"
                    "Switch1/Ports/Port11/VLans/VLan1"
                },
                "PortMembers": [
                    {
                        "@odata.id": "/redfish/v1/EthernetSwitches/"
                        "Switch1/Ports/Port10"
                    },
                    {
                        "@odata.id": "/redfish/v1/EthernetSwitches/"
                        "Switch1/Ports/Port12"
                    },
                ],
            },
        }
        self.port_inst.update(data)
        self.port_inst._conn.patch.assert_called_once_with(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1", data=data
        )


class EthernetSwitchPortCollectionTestCase(testtools.TestCase):
    def setUp(self):
        super(EthernetSwitchPortCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_port_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.conn.post.return_value = request_fakes.fake_request_post(
                None,
                headers={
                    "Location": "https://localhost:8443/redfish/v1/"
                    "EthernetSwitches/Switch1/Ports/Port1"
                },
            )
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

    def test_create_port_reqs(self):
        reqs = {
            "PortId": 1,
            "PortMode": "LinkAggregationStatic",
            "Links": {
                "PortMembers": [
                    {
                        "@odata.id": "/redfish/v1/EthernetSwitches/"
                        "Switch1/Ports/Port10"
                    },
                    {
                        "@odata.id": "/redfish/v1/EthernetSwitches/"
                        "Switch1/Ports/Port11"
                    },
                ]
            },
        }
        result = self.port_col.create_port(reqs)
        self.port_col._conn.post.assert_called_once_with(
            "/redfish/v1/EthernetSwitches/Switch1/Ports", data=reqs
        )
        self.assertEqual(
            result, "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1"
        )
