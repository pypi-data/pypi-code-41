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

from sushy import exceptions

from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_acl
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_acl_rule
from rsd_lib.tests.unit.fakes import request_fakes


class EthernetSwitchACLTestCase(testtools.TestCase):
    def setUp(self):
        super(EthernetSwitchACLTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/ethernet_switch_acl.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.acl_inst = ethernet_switch_acl.EthernetSwitchACL(
            self.conn,
            "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1",
            redfish_version="1.0.2",
        )

    def test__parse_attributes(self):
        self.acl_inst._parse_attributes()
        self.assertEqual("1.0.2", self.acl_inst.redfish_version)
        self.assertEqual("ACL1", self.acl_inst.identity)
        self.assertEqual(
            "Ethernet Switch Access Control List", self.acl_inst.name
        )
        self.assertEqual("Switch ACL", self.acl_inst.description)
        self.assertEqual(
            ("/redfish/v1/EthernetSwitches/Switch1/Ports/sw0p1",),
            self.acl_inst.links.bound_ports,
        )

    def test__get_bind_action_element(self):
        value = self.acl_inst._get_bind_action_element()
        self.assertEqual(
            "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1/Actions/"
            "EthernetSwitchACL.Bind",
            value.target_uri,
        )

        self.assertEqual(
            (
                "/redfish/v1/EthernetSwitches/Switch1/Ports/sw0p2",
                "/redfish/v1/EthernetSwitches/Switch1/Ports/sw0p3",
            ),
            value.allowed_values,
        )

    def test_get_allowed_bind_ports(self):
        expected = self.acl_inst.get_allowed_bind_ports()
        result = (
            "/redfish/v1/EthernetSwitches/Switch1/Ports/sw0p2",
            "/redfish/v1/EthernetSwitches/Switch1/Ports/sw0p3",
        )
        self.assertEqual(expected, result)

    def test_bind_port(self):
        self.acl_inst.bind_port(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/sw0p2"
        )
        self.acl_inst._conn.post.assert_called_once_with(
            "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1/Actions/"
            "EthernetSwitchACL.Bind",
            data={
                "Port": {
                    "@odata.id": "/redfish/v1/EthernetSwitches/Switch1/Ports/"
                    "sw0p2"
                }
            },
        )

    def test_bind_port_invalid_enabled(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "port" value "invalid-port" is invalid',
        ):
            self.acl_inst.bind_port("invalid-port")

    def test__get_unbind_action_element(self):
        value = self.acl_inst._get_unbind_action_element()
        self.assertEqual(
            "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1/Actions/"
            "EthernetSwitchACL.Unbind",
            value.target_uri,
        )

        self.assertEqual(
            ("/redfish/v1/EthernetSwitches/Switch1/Ports/sw0p1",),
            value.allowed_values,
        )

    def test_get_allowed_unbind_ports(self):
        expected = self.acl_inst.get_allowed_unbind_ports()
        result = ("/redfish/v1/EthernetSwitches/Switch1/Ports/sw0p1",)
        self.assertEqual(expected, result)

    def test_unbind_port(self):
        self.acl_inst.unbind_port(
            "/redfish/v1/EthernetSwitches/Switch1/Ports/sw0p1"
        )
        self.acl_inst._conn.post.assert_called_once_with(
            "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1/Actions/"
            "EthernetSwitchACL.Unbind",
            data={
                "Port": {
                    "@odata.id": "/redfish/v1/EthernetSwitches/Switch1/Ports/"
                    "sw0p1"
                }
            },
        )

    def test_unbind_port_invalid_enabled(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "port" value "invalid-port" is invalid',
        ):
            self.acl_inst.unbind_port("invalid-port")

    def test_delete(self):
        self.acl_inst.delete()
        self.acl_inst._conn.delete.assert_called_once_with(self.acl_inst.path)

    def test_acl_rule(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/" "ethernet_switch_acl.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_acl_rules = self.acl_inst.rules
        # | THEN |
        self.assertIsInstance(
            actual_acl_rules,
            ethernet_switch_acl_rule.EthernetSwitchACLRuleCollection,
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_acl_rules, self.acl_inst.rules)
        self.conn.get.return_value.json.assert_not_called()

    def test_acl_rule_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_acl_rule_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.acl_inst.rules,
            ethernet_switch_acl_rule.EthernetSwitchACLRuleCollection,
        )

        # On refreshing the acl_rule instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/" "ethernet_switch_acl.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.acl_inst.invalidate()
        self.acl_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_acl_rule_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.acl_inst.rules,
            ethernet_switch_acl_rule.EthernetSwitchACLRuleCollection,
        )


class EthernetSwitchACLCollectionTestCase(testtools.TestCase):
    def setUp(self):
        super(EthernetSwitchACLCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "ethernet_switch_acl_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.conn.post.return_value = request_fakes.fake_request_post(
            None,
            headers={
                "Location": "https://localhost:8443/redfish/v1/"
                "EthernetSwitches/Switch1/ACLs/ACL1"
            },
        )
        self.acl_col = ethernet_switch_acl.EthernetSwitchACLCollection(
            self.conn,
            "/redfish/v1/EthernetSwitches/Switch1/ACLs",
            redfish_version="1.0.2",
        )

    def test__parse_attributes(self):
        self.acl_col._parse_attributes()
        self.assertEqual("1.0.2", self.acl_col.redfish_version)
        self.assertEqual(
            "Ethernet Switch Access Control List Collection", self.acl_col.name
        )
        self.assertEqual(
            ("/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1",),
            self.acl_col.members_identities,
        )

    @mock.patch.object(ethernet_switch_acl, "EthernetSwitchACL", autospec=True)
    def test_get_member(self, mock_acl):
        self.acl_col.get_member(
            "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1"
        )
        mock_acl.assert_called_once_with(
            self.acl_col._conn,
            "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1",
            redfish_version=self.acl_col.redfish_version,
        )

    @mock.patch.object(ethernet_switch_acl, "EthernetSwitchACL", autospec=True)
    def test_get_members(self, mock_acl):
        members = self.acl_col.get_members()
        mock_acl.assert_called_with(
            self.acl_col._conn,
            "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1",
            redfish_version=self.acl_col.redfish_version,
        )
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test_create_acl(self):
        result = self.acl_col.create_acl()
        self.acl_col._conn.post.assert_called_once_with(
            "/redfish/v1/EthernetSwitches/Switch1/ACLs", data={}
        )
        self.assertEqual(
            result, "/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1"
        )
