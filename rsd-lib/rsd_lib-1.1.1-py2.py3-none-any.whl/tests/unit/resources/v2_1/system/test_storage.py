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

from rsd_lib.resources.v2_1.system import drive
from rsd_lib.resources.v2_1.system import storage


class StorageSubsystemTestCase(testtools.TestCase):
    def setUp(self):
        super(StorageSubsystemTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/" "storage.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.storage_inst = storage.Storage(
            self.conn,
            "/redfish/v1/Systems/1/Storage/SATA",
            redfish_version="1.1.0",
        )

    def test__parse_attributes(self):
        self.storage_inst._parse_attributes()
        self.assertEqual("SATA Storage System", self.storage_inst.name)
        self.assertEqual("1", self.storage_inst.identity)
        self.assertEqual("System SATA", self.storage_inst.description)
        self.assertEqual("Enabled", self.storage_inst.status.state)
        self.assertEqual("OK", self.storage_inst.status.health)
        self.assertEqual("OK", self.storage_inst.status.health_rollup)
        self.assertEqual(
            "0", self.storage_inst.storage_controllers[0].member_id
        )
        self.assertEqual(
            "Enabled", self.storage_inst.storage_controllers[0].status.state
        )
        self.assertEqual(
            "OK", self.storage_inst.storage_controllers[0].status.health
        )
        self.assertEqual(
            "ManufacturerName",
            self.storage_inst.storage_controllers[0].manufacturer,
        )
        self.assertEqual(
            "ProductModelName", self.storage_inst.storage_controllers[0].model
        )
        self.assertEqual("", self.storage_inst.storage_controllers[0].sku)
        self.assertEqual(
            "2M220100SL",
            self.storage_inst.storage_controllers[0].serial_number,
        )
        self.assertEqual(
            "", self.storage_inst.storage_controllers[0].part_number
        )
        self.assertEqual(
            "CustomerWritableThingy",
            self.storage_inst.storage_controllers[0].asset_tag,
        )
        self.assertEqual(
            6, self.storage_inst.storage_controllers[0].speed_gbps
        )
        self.assertEqual(
            None, self.storage_inst.storage_controllers[0].firmware_version
        )
        self.assertEqual(
            "PCIe",
            self.storage_inst.storage_controllers[
                0
            ].supported_controller_protocols[0],
        )
        self.assertEqual(
            "SATA",
            self.storage_inst.storage_controllers[
                0
            ].supported_device_protocols[0],
        )
        self.assertEqual(
            "123e4567-e89b-12d3-a456-426655440000",
            self.storage_inst.storage_controllers[0]
            .identifiers[0]
            .durable_name,
        )
        self.assertEqual(
            "UUID",
            self.storage_inst.storage_controllers[0]
            .identifiers[0]
            .durable_name_format,
        )

    def test_drives(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open("rsd_lib/tests/unit/json_samples/v2_1/drive.json", "r") as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_drives = self.storage_inst.drives
        # | THEN |
        self.assertIsInstance(actual_drives, list)
        self.assertEqual(1, len(actual_drives))
        self.assertIsInstance(actual_drives[0], drive.Drive)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_drives, self.storage_inst.drives)
        self.conn.get.return_value.json.assert_not_called()

    def test_drives_on_refresh(self):
        # | GIVEN |
        with open("rsd_lib/tests/unit/json_samples/v2_1/drive.json", "r") as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        actual_drives = self.storage_inst.drives
        self.assertIsInstance(actual_drives, list)
        self.assertEqual(1, len(actual_drives))
        self.assertIsInstance(actual_drives[0], drive.Drive)

        # On refreshing the system instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/storage.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.storage_inst.invalidate()
        self.storage_inst.refresh(force=True)

        # | GIVEN |
        with open("rsd_lib/tests/unit/json_samples/v2_1/drive.json", "r") as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.storage_inst.drives, list)
        self.assertEqual(1, len(self.storage_inst.drives))
        self.assertIsInstance(self.storage_inst.drives[0], drive.Drive)


class StorageSubsystemCollectionTestCase(testtools.TestCase):
    def setUp(self):
        super(StorageSubsystemCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/" "storage_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.storage_subsystem_col = storage.StorageCollection(
                self.conn,
                "/redfish/v1/Systems/1/Storage",
                redfish_version="1.1.0",
            )

    def test__parse_attributes(self):
        self.storage_subsystem_col._parse_attributes()
        self.assertEqual("1.1.0", self.storage_subsystem_col.redfish_version)
        self.assertEqual(
            ("/redfish/v1/Systems/1/Storage/SATA",),
            self.storage_subsystem_col.members_identities,
        )

    @mock.patch.object(storage, "Storage", autospec=True)
    def test_get_member(self, mock_storage_subsystem):
        self.storage_subsystem_col.get_member(
            "/redfish/v1/Systems/1/Storage/SATA"
        )
        mock_storage_subsystem.assert_called_once_with(
            self.storage_subsystem_col._conn,
            "/redfish/v1/Systems/1/Storage/SATA",
            redfish_version=self.storage_subsystem_col.redfish_version,
        )

    @mock.patch.object(storage, "Storage", autospec=True)
    def test_get_members(self, mock_storage_subsystem):
        members = self.storage_subsystem_col.get_members()
        calls = [
            mock.call(
                self.storage_subsystem_col._conn,
                "/redfish/v1/Systems/1/Storage/SATA",
                redfish_version=self.storage_subsystem_col.redfish_version,
            )
        ]
        mock_storage_subsystem.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
