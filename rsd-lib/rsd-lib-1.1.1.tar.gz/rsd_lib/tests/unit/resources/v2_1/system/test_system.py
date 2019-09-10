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

from sushy import exceptions

from rsd_lib import constants
from rsd_lib.resources.v2_1.system import ethernet_interface
from rsd_lib.resources.v2_1.system import memory
from rsd_lib.resources.v2_1.system import network_interface
from rsd_lib.resources.v2_1.system import pcie_device
from rsd_lib.resources.v2_1.system import pcie_function
from rsd_lib.resources.v2_1.system import processor
from rsd_lib.resources.v2_1.system import storage
from rsd_lib.resources.v2_1.system import system


class SystemTestCase(testtools.TestCase):
    def setUp(self):
        super(SystemTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/system.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.system_inst = system.System(
            self.conn, "/redfish/v1/Systems/System1", redfish_version="1.1.0"
        )

    def test__parse_attributes(self):
        self.system_inst._parse_attributes()
        self.assertEqual("1.1.0", self.system_inst.redfish_version)
        self.assertEqual("System1", self.system_inst.identity)
        self.assertEqual("My Computer System", self.system_inst.name)
        self.assertEqual("Description of server", self.system_inst.description)
        self.assertEqual("Physical", self.system_inst.system_type)
        self.assertEqual(
            ("/redfish/v1/Chassis/4",), self.system_inst.links.chassis
        )
        self.assertEqual(
            ("/redfish/v1/Managers/1",), self.system_inst.links.managed_by
        )
        self.assertEqual(None, self.system_inst.links.powered_by)
        self.assertEqual(None, self.system_inst.links.cooled_by)
        self.assertEqual(tuple(), self.system_inst.links.endpoints)
        self.assertEqual("free form asset tag", self.system_inst.asset_tag)
        self.assertEqual("Manufacturer Name", self.system_inst.manufacturer)
        self.assertEqual("Model Name", self.system_inst.model)
        self.assertEqual("SKU", self.system_inst.sku)
        self.assertEqual("2M220100SL", self.system_inst.serial_number)
        self.assertEqual("Computer1", self.system_inst.part_number)
        self.assertEqual(
            "00000000-0000-0000-0000-000000000000", self.system_inst.uuid
        )
        self.assertEqual(None, self.system_inst.host_name)
        self.assertEqual("Off", self.system_inst.indicator_led)
        self.assertEqual("On", self.system_inst.power_state)
        self.assertEqual(
            "Pxe", self.system_inst.boot.boot_source_override_target
        )
        self.assertEqual(
            ["None", "Pxe", "Hdd", "RemoteDrive"],
            self.system_inst.boot.boot_source_override_target_allowed_values,
        )
        self.assertEqual(
            "Once", self.system_inst.boot.boot_source_override_enabled
        )
        self.assertEqual(
            None, self.system_inst.boot.uefi_target_boot_source_override
        )
        self.assertEqual(
            "Legacy", self.system_inst.boot.boot_source_override_mode
        )
        self.assertEqual(
            ["Legacy", "UEFI"],
            self.system_inst.boot.boot_source_override_mode_allowed_values,
        )
        self.assertEqual(
            "P79 v1.00 (09/20/2013)", self.system_inst.bios_version
        )
        self.assertEqual(8, self.system_inst.processor_summary.count)
        self.assertEqual(
            "Multi-Core Intel(R) Xeon(R) processor 7xxx Series",
            self.system_inst.processor_summary.model,
        )
        self.assertEqual(
            "Enabled", self.system_inst.processor_summary.status.state
        )
        self.assertEqual(
            "OK", self.system_inst.processor_summary.status.health
        )
        self.assertEqual(
            "OK", self.system_inst.processor_summary.status.health_rollup
        )
        self.assertEqual(
            16, self.system_inst.memory_summary.total_system_memory_gib
        )
        self.assertEqual(
            "Enabled", self.system_inst.memory_summary.status.state
        )
        self.assertEqual("OK", self.system_inst.memory_summary.status.health)
        self.assertEqual(
            "OK", self.system_inst.memory_summary.status.health_rollup
        )
        self.assertEqual("Enabled", self.system_inst.status.state)
        self.assertEqual("OK", self.system_inst.status.health)
        self.assertEqual("OK", self.system_inst.status.health_rollup)
        self.assertEqual(None, self.system_inst.hosting_roles)
        self.assertEqual(
            ["XYZ1234567890"],
            self.system_inst.oem.intel_rackscale.pcie_connection_id,
        )
        self.assertEqual(
            "0x8086",
            self.system_inst.oem.intel_rackscale.pci_devices[0].vendor_id,
        )
        self.assertEqual(
            "0x1234",
            self.system_inst.oem.intel_rackscale.pci_devices[0].device_id,
        )
        self.assertEqual(
            "Basic", self.system_inst.oem.intel_rackscale.discovery_state
        )
        self.assertEqual(
            8, self.system_inst.oem.intel_rackscale.processor_sockets
        )
        self.assertEqual(
            8, self.system_inst.oem.intel_rackscale.memory_sockets
        )

    def test_get__reset_action_element(self):
        value = self.system_inst._get_reset_action_element()
        self.assertEqual(
            "/redfish/v1/Systems/System1/Actions/ComputerSystem.Reset",
            value.target_uri,
        )
        self.assertEqual(
            [
                "On",
                "ForceOff",
                "GracefulShutdown",
                "ForceRestart",
                "Nmi",
                "GracefulRestart",
                "ForceOn",
                "PushPowerButton",
            ],
            value.allowed_values,
        )

    def test_get__reset_action_element_missing_reset_action(self):
        self.system_inst._actions.reset = None
        with self.assertRaisesRegex(
            exceptions.MissingActionError, "action #ComputerSystem.Reset"
        ):
            self.system_inst._get_reset_action_element()

    def test_get_allowed_reset_system_values(self):
        values = self.system_inst.get_allowed_reset_system_values()
        expected = set(
            [
                "On",
                "ForceOff",
                "GracefulShutdown",
                "GracefulRestart",
                "ForceRestart",
                "Nmi",
                "ForceOn",
                "PushPowerButton",
            ]
        )
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    @mock.patch.object(system.LOG, "warning", autospec=True)
    def test_get_allowed_reset_system_values_no_values_specified(
        self, mock_log
    ):
        self.system_inst._actions.reset.allowed_values = {}
        values = self.system_inst.get_allowed_reset_system_values()
        # Assert it returns all values if it can't get the specific ones
        expected = set(constants.RESET_TYPE_VALUE)
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)
        self.assertEqual(1, mock_log.call_count)

    def test_reset_system(self):
        self.system_inst.reset_system("ForceOff")
        self.system_inst._conn.post.assert_called_once_with(
            "/redfish/v1/Systems/System1/Actions/ComputerSystem.Reset",
            data={"ResetType": "ForceOff"},
        )

    def test_reset_system_invalid_value(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "value" value "invalid-value" is invalid',
        ):
            self.system_inst.reset_system("invalid-value")

    def test_get_allowed_system_boot_source_values(self):
        values = self.system_inst.get_allowed_system_boot_source_values()
        expected = set(["None", "Pxe", "Hdd", "RemoteDrive"])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    @mock.patch.object(system.LOG, "warning", autospec=True)
    def test_get_allowed_system_boot_source_values_no_values_specified(
        self, mock_log
    ):
        self.system_inst.boot.boot_source_override_target_allowed_values = None
        values = self.system_inst.get_allowed_system_boot_source_values()
        # Assert it returns all values if it can't get the specific ones
        expected = set(constants.BOOT_SOURCE_TARGET_VALUE)
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)
        self.assertEqual(1, mock_log.call_count)

    def test_get_allowed_system_boot_mode_values(self):
        values = self.system_inst.get_allowed_system_boot_mode_values()
        expected = set(["Legacy", "UEFI"])
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)

    @mock.patch.object(system.LOG, "warning", autospec=True)
    def test_get_allowed_system_boot_mode_values_no_values_specified(
        self, mock_log
    ):
        self.system_inst.boot.boot_source_override_mode_allowed_values = None
        values = self.system_inst.get_allowed_system_boot_mode_values()
        # Assert it returns all values if it can't get the specific ones
        expected = set(constants.BOOT_SOURCE_MODE_VALUE)
        self.assertEqual(expected, values)
        self.assertIsInstance(values, set)
        self.assertEqual(1, mock_log.call_count)

    def test_set_system_boot_source(self):
        self.system_inst.set_system_boot_source(
            target="Pxe", enabled="Continuous", mode="UEFI"
        )
        self.system_inst._conn.patch.assert_called_once_with(
            "/redfish/v1/Systems/System1",
            data={
                "Boot": {
                    "BootSourceOverrideEnabled": "Continuous",
                    "BootSourceOverrideTarget": "Pxe",
                    "BootSourceOverrideMode": "UEFI",
                }
            },
        )

    def test_set_system_boot_source_no_mode_specified(self):
        self.system_inst.set_system_boot_source(target="Hdd")
        self.system_inst._conn.patch.assert_called_once_with(
            "/redfish/v1/Systems/System1",
            data={
                "Boot": {
                    "BootSourceOverrideEnabled": "Once",
                    "BootSourceOverrideTarget": "Hdd",
                }
            },
        )

    def test_set_system_boot_source_invalid_target(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "target" value "invalid-target" is invalid',
        ):
            self.system_inst.set_system_boot_source("invalid-target")

    def test_set_system_boot_source_invalid_enabled(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "enabled" value "invalid-enabled" is invalid',
        ):
            self.system_inst.set_system_boot_source(
                "Hdd", enabled="invalid-enabled"
            )

    def test_set_system_boot_source_invalid_mode(self):
        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "mode" value "invalid-mode" is invalid',
        ):
            self.system_inst.set_system_boot_source("Hdd", mode="invalid-mode")

    def test_processors(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/processor_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_processor_col = self.system_inst.processors
        # | THEN |
        self.assertIsInstance(
            actual_processor_col, processor.ProcessorCollection
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_processor_col, self.system_inst.processors)
        self.conn.get.return_value.json.assert_not_called()

    def test_processors_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/processor_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.system_inst.processors, processor.ProcessorCollection
        )

        # On refreshing the system instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/system.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.system_inst.invalidate()
        self.system_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/processor_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.system_inst.processors, processor.ProcessorCollection
        )

    def test_ethernet_interfaces(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "system_ethernet_interface_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_ethernet_interface_col = self.system_inst.ethernet_interfaces
        # | THEN |
        self.assertIsInstance(
            actual_ethernet_interface_col,
            ethernet_interface.EthernetInterfaceCollection,
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(
            actual_ethernet_interface_col, self.system_inst.ethernet_interfaces
        )
        self.conn.get.return_value.json.assert_not_called()

    def test_ethernet_interfaces_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "system_ethernet_interface_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.system_inst.ethernet_interfaces,
            ethernet_interface.EthernetInterfaceCollection,
        )

        # on refreshing the system instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/system.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.system_inst.invalidate()
        self.system_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "system_ethernet_interface_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.son.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.system_inst.ethernet_interfaces,
            ethernet_interface.EthernetInterfaceCollection,
        )

    def test_memory(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/memory_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_memory_col = self.system_inst.memory
        # | THEN |
        self.assertIsInstance(actual_memory_col, memory.MemoryCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_memory_col, self.system_inst.memory)
        self.conn.get.return_value.json.assert_not_called()

    def test_memory_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/memory_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.system_inst.memory, memory.MemoryCollection)

        # On refreshing the system instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/system.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.system_inst.invalidate()
        self.system_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/memory_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.system_inst.memory, memory.MemoryCollection)

    def test_storage(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/storage_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_storage_col = self.system_inst.storage
        # | THEN |
        self.assertIsInstance(actual_storage_col, storage.StorageCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_storage_col, self.system_inst.storage)
        self.conn.get.return_value.json.assert_not_called()

    def test_storage_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/storage_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.system_inst.storage, storage.StorageCollection
        )

        # on refreshing the system instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/system.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.system_inst.invalidate()
        self.system_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/storage_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.system_inst.storage, storage.StorageCollection
        )

    def test_network_interfaces(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "network_interface_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_network_interface_col = self.system_inst.network_interfaces
        # | THEN |
        self.assertIsInstance(
            actual_network_interface_col,
            network_interface.NetworkInterfaceCollection,
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(
            actual_network_interface_col, self.system_inst.network_interfaces
        )
        self.conn.get.return_value.json.assert_not_called()

    def test_network_interfaces_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "network_interface_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.system_inst.network_interfaces,
            network_interface.NetworkInterfaceCollection,
        )

        # on refreshing the system instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/system.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.system_inst.invalidate()
        self.system_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/"
            "network_interface_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.son.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.system_inst.network_interfaces,
            network_interface.NetworkInterfaceCollection,
        )

    def test_pcie_devices(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/pcie_device.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_pcie_devices = self.system_inst.pcie_devices
        # | THEN |
        self.assertEqual(2, len(actual_pcie_devices))
        for pcie in actual_pcie_devices:
            self.assertIsInstance(pcie, pcie_device.PCIeDevice)
        self.assertEqual(2, self.conn.get.return_value.json.call_count)

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_pcie_devices, self.system_inst.pcie_devices)
        self.conn.get.return_value.json.assert_not_called()

    def test_pcie_devices_on_fresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/pcie_device.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        for pcie in self.system_inst.pcie_devices:
            self.assertIsInstance(pcie, pcie_device.PCIeDevice)

        # On refreshing the chassis instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/system.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.system_inst.invalidate()
        self.system_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/pcie_device.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        for pcie in self.system_inst.pcie_devices:
            self.assertIsInstance(pcie, pcie_device.PCIeDevice)

    def test_pcie_functions(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/pcie_function.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_pcie_functions = self.system_inst.pcie_functions
        # | THEN |
        self.assertEqual(2, len(actual_pcie_functions))
        for pcie in actual_pcie_functions:
            self.assertIsInstance(pcie, pcie_function.PCIeFunction)
        self.assertEqual(2, self.conn.get.return_value.json.call_count)

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_pcie_functions, self.system_inst.pcie_functions)
        self.conn.get.return_value.json.assert_not_called()

    def test_pcie_functions_on_fresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/pcie_function.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        for pcie in self.system_inst.pcie_functions:
            self.assertIsInstance(pcie, pcie_function.PCIeFunction)

        # On refreshing the chassis instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/system.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.system_inst.invalidate()
        self.system_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/pcie_function.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        for pcie in self.system_inst.pcie_functions:
            self.assertIsInstance(pcie, pcie_function.PCIeFunction)


class SystemCollectionTestCase(testtools.TestCase):
    def setUp(self):
        super(SystemCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_1/system_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.system_col = system.SystemCollection(
            self.conn, "/redfish/v1/Systems", redfish_version="1.1.0"
        )

    def test__parse_attributes(self):
        self.system_col._parse_attributes()
        self.assertEqual("1.1.0", self.system_col.redfish_version)
        self.assertEqual(
            ("/redfish/v1/Systems/System1", "/redfish/v1/Systems/System2"),
            self.system_col.members_identities,
        )

    @mock.patch.object(system, "System", autospec=True)
    def test_get_member(self, mock_system):
        self.system_col.get_member("/redfish/v1/Systems/System1")
        mock_system.assert_called_once_with(
            self.system_col._conn,
            "/redfish/v1/Systems/System1",
            redfish_version=self.system_col.redfish_version,
        )

    @mock.patch.object(system, "System", autospec=True)
    def test_get_members(self, mock_system):
        members = self.system_col.get_members()
        calls = [
            mock.call(
                self.system_col._conn,
                "/redfish/v1/Systems/System1",
                redfish_version=self.system_col.redfish_version,
            ),
            mock.call(
                self.system_col._conn,
                "/redfish/v1/Systems/System2",
                redfish_version=self.system_col.redfish_version,
            ),
        ]
        mock_system.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))
