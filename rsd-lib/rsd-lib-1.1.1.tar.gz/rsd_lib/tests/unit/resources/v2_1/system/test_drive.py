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

import json
import mock
import testtools

from sushy import exceptions

from rsd_lib.resources.v2_1.system import drive


class DriveTestCase(testtools.TestCase):
    def setUp(self):
        super(DriveTestCase, self).setUp()
        self.conn = mock.Mock()
        with open("rsd_lib/tests/unit/json_samples/v2_1/drive.json", "r") as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.drive_inst = drive.Drive(
            self.conn,
            "/redfish/v1/Chassis/Blade1/Drives/1",
            redfish_version="1.1.0",
        )

    def test__parse_attributes(self):
        self.drive_inst._parse_attributes()
        self.assertEqual("1.1.0", self.drive_inst.redfish_version)
        self.assertEqual("OK", self.drive_inst.status_indicator)
        self.assertEqual("Lit", self.drive_inst.indicator_led)
        self.assertEqual("Drive Model string", self.drive_inst.model)
        self.assertEqual("revision string", self.drive_inst.revision)
        self.assertEqual("Enabled", self.drive_inst.status.state)
        self.assertEqual("OK", self.drive_inst.status.health)
        self.assertEqual(None, self.drive_inst.status.health_rollup)
        self.assertEqual(899527000000, self.drive_inst.capacity_bytes)
        self.assertEqual(False, self.drive_inst.failure_predicted)
        self.assertEqual("SATA", self.drive_inst.protocol)
        self.assertEqual("SSD", self.drive_inst.media_type)
        self.assertEqual("Intel", self.drive_inst.manufacturer)
        self.assertEqual("SKU version", self.drive_inst.sku)
        self.assertEqual("72D0A037FRD27", self.drive_inst.serial_number)
        self.assertEqual(
            "SG0GP8811253178M02GJA00", self.drive_inst.part_number
        )
        self.assertEqual(None, self.drive_inst.asset_tag)
        self.assertEqual(
            "123e4567-e89b-12d3-a456-426655440000",
            self.drive_inst.identifiers[0].durable_name,
        )
        self.assertEqual(
            "UUID", self.drive_inst.identifiers[0].durable_name_format
        )
        self.assertEqual("4", self.drive_inst.location[0].info)
        self.assertEqual("Hdd index", self.drive_inst.location[0].info_format)
        self.assertEqual(None, self.drive_inst.hotspare_type)
        self.assertEqual(None, self.drive_inst.encryption_ability)
        self.assertEqual(None, self.drive_inst.encryption_status)
        self.assertEqual(None, self.drive_inst.rotation_speed_rpm)
        self.assertEqual(None, self.drive_inst.block_size_bytes)
        self.assertEqual(6, self.drive_inst.capable_speed_gbs)
        self.assertEqual(6, self.drive_inst.negotiated_speed_gbs)
        self.assertEqual(
            None, self.drive_inst.predicted_media_life_left_percent
        )
        self.assertEqual(tuple(), self.drive_inst.links.volumes)
        self.assertEqual(tuple(), self.drive_inst.links.endpoints)
        self.assertEqual(None, self.drive_inst.operations)
        self.assertEqual(
            False, self.drive_inst.oem.intel_rackscale.erase_on_detach
        )
        self.assertEqual(
            True, self.drive_inst.oem.intel_rackscale.drive_erased
        )
        self.assertEqual(
            "1.17", self.drive_inst.oem.intel_rackscale.firmware_version
        )
        self.assertEqual(
            "/redfish/v1/Systems/1/Storage/NVMe",
            self.drive_inst.oem.intel_rackscale.storage,
        )
        self.assertEqual(
            "/redfish/v1/Chassis/1/PCIeDevices/Device1/Functions/1",
            self.drive_inst.oem.intel_rackscale.pcie_function,
        )

    def test__get_secure_erase_action_element(self):
        value = self.drive_inst._get_secure_erase_action_element()
        self.assertEqual(
            "/redfish/v1/Chassis/Blade1/Drives/1/Actions/Drive.SecureErase",
            value.target_uri,
        )

    def test_get__get_secure_erase_action_element_missing_reset_action(self):
        self.drive_inst._actions.secure_erase = None
        with self.assertRaisesRegex(
            exceptions.MissingActionError, "action #Drive.SecureErase"
        ):
            self.drive_inst._get_secure_erase_action_element()

    def test_secure_erase(self):
        self.drive_inst.secure_erase()
        self.drive_inst._conn.post.assert_called_once_with(
            "/redfish/v1/Chassis/Blade1/Drives/1/Actions/Drive.SecureErase",
            data={},
        )

    def test_update(self):
        self.drive_inst.update(
            asset_tag="Asset Tag", erase_on_detach=True, erased=False
        )
        self.drive_inst._conn.patch.assert_called_once_with(
            "/redfish/v1/Chassis/Blade1/Drives/1",
            data={
                "Oem": {
                    "Intel_RackScale": {
                        "EraseOnDetach": True,
                        "DriveErased": False,
                    }
                },
                "AssetTag": "Asset Tag",
            },
        )

        self.drive_inst._conn.patch.reset_mock()
        self.drive_inst.update(asset_tag="Asset Tag")
        self.drive_inst._conn.patch.assert_called_once_with(
            "/redfish/v1/Chassis/Blade1/Drives/1",
            data={"AssetTag": "Asset Tag"},
        )

        self.drive_inst._conn.patch.reset_mock()
        self.drive_inst.update(erase_on_detach=True, erased=False)
        self.drive_inst._conn.patch.assert_called_once_with(
            "/redfish/v1/Chassis/Blade1/Drives/1",
            data={
                "Oem": {
                    "Intel_RackScale": {
                        "EraseOnDetach": True,
                        "DriveErased": False,
                    }
                }
            },
        )

    def test_update_invalid_values(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "erase_on_detach" value "invalid string" is '
            "invalid",
        ):
            self.drive_inst.update(erase_on_detach="invalid string")

        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "erased" value "invalid string" is invalid',
        ):
            self.drive_inst.update(erased="invalid string")
