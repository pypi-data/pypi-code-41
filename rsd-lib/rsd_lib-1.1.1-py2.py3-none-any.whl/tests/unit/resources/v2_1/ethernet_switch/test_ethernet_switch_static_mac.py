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
import jsonschema
import mock
import testtools

from sushy import exceptions

from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_static_mac
from rsd_lib.tests.unit.fakes import request_fakes


class EthernetSwitchStaticMACTestCase(testtools.TestCase):
    def setUp(self):
        super(EthernetSwitchStaticMACTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_static_mac.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.static_mac_inst = ethernet_switch_static_mac.\
            EthernetSwitchStaticMAC(
                self.conn,
                "/redfish/v1/EthernetSwitches/Switch1/Ports/StaticMACs/1",
                redfish_version="1.0.2",
            )

    def test__parse_attributes(self):
        self.static_mac_inst._parse_attributes()
        self.assertEqual("1.0.2", self.static_mac_inst.redfish_version)
        self.assertEqual("1", self.static_mac_inst.identity)
        self.assertEqual("StaticMAC", self.static_mac_inst.name)
        self.assertEqual(
            "description-as-string", self.static_mac_inst.description
        )
        self.assertEqual("00:11:22:33:44:55", self.static_mac_inst.mac_address)
        self.assertEqual(112, self.static_mac_inst.vlan_id)

    def test_update(self):
        reqs = {"MACAddress": "00:11:22:33:44:55"}
        self.static_mac_inst.update("00:11:22:33:44:55")
        self.static_mac_inst._conn.patch.assert_called_once_with(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/StaticMACs/1",
            data=reqs,
        )

        self.static_mac_inst._conn.patch.reset_mock()
        reqs = {"MACAddress": "00:11:22:33:44:55", "VLANId": 69}
        self.static_mac_inst.update("00:11:22:33:44:55", vlan_id=69)
        self.static_mac_inst._conn.patch.assert_called_once_with(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/StaticMACs/1",
            data=reqs,
        )

    def test_update_invalid_reqs(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            ('The parameter "mac_address" value "True" is invalid'),
        ):
            self.static_mac_inst.update(True)

        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            ('The parameter "vlan_id" value "invalid-value" is invalid'),
        ):
            self.static_mac_inst.update(
                "00:11:22:33:44:55", vlan_id="invalid-value"
            )

    def test_delete(self):
        self.static_mac_inst.delete()
        self.static_mac_inst._conn.delete.assert_called_once_with(
            self.static_mac_inst.path
        )


class EthernetSwitchStaticMACCollectionTestCase(testtools.TestCase):
    def setUp(self):
        super(EthernetSwitchStaticMACCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_static_mac_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.conn.post.return_value = request_fakes.fake_request_post(
            None,
            headers={
                "Location": "https://localhost:8443/redfish/v1/"
                "EthernetSwitches/Switch1/Ports/Port1/StaticMACs/1"
            },
        )

        self.static_mac_col = ethernet_switch_static_mac.\
            EthernetSwitchStaticMACCollection(
                self.conn,
                "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs",
                redfish_version="1.1.0",
            )

    def test__parse_attributes(self):
        self.static_mac_col._parse_attributes()
        self.assertEqual("1.1.0", self.static_mac_col.redfish_version)
        self.assertEqual(
            ("/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs/1",),
            self.static_mac_col.members_identities,
        )

    @mock.patch.object(
        ethernet_switch_static_mac, "EthernetSwitchStaticMAC", autospec=True
    )
    def test_get_member(self, mock_static_mac):
        self.static_mac_col.get_member(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs/1"
        )
        mock_static_mac.assert_called_once_with(
            self.static_mac_col._conn,
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs/1",
            redfish_version=self.static_mac_col.redfish_version,
        )

    @mock.patch.object(
        ethernet_switch_static_mac, "EthernetSwitchStaticMAC", autopspec=True
    )
    def test_get_members(self, mock_static_mac):
        members = self.static_mac_col.get_members()
        calls = [
            mock.call(
                self.static_mac_col._conn,
                "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/"
                "StaticMACs/1",
                redfish_version=self.static_mac_col.redfish_version,
            )
        ]
        mock_static_mac.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test_create_static_mac(self):
        reqs = {"MACAddress": "00:11:22:33:44:55"}
        result = self.static_mac_col.create_static_mac("00:11:22:33:44:55")
        self.static_mac_col._conn.post.assert_called_once_with(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs",
            data=reqs,
        )
        self.assertEqual(
            result,
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs/1",
        )

        self.static_mac_col._conn.post.reset_mock()
        reqs = {"MACAddress": "00:11:22:33:44:55", "VLANId": 69}
        result = self.static_mac_col.create_static_mac(
            "00:11:22:33:44:55", vlan_id=69
        )
        self.static_mac_col._conn.post.assert_called_once_with(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs",
            data=reqs,
        )
        self.assertEqual(
            result,
            "/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs/1",
        )

    def test_create_static_mac_invalid_reqs(self):
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("True is not of type 'string'"),
        ):
            self.static_mac_col.create_static_mac(True)

        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid-value' is not of type 'number'"),
        ):
            self.static_mac_col.create_static_mac(
                "00:11:22:33:44:55", vlan_id="invalid-value"
            )
