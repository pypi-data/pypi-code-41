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

from rsd_lib.resources.v2_4.system import processor


class ProcessorTestCase(testtools.TestCase):

    def setUp(self):
        super(ProcessorTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_4/processor.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.processor_inst = processor.Processor(
            self.conn, '/redfish/v1/Systems/System1/Processors/CPU1',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.processor_inst._parse_attributes()
        self.assertEqual('1.1.0', self.processor_inst.redfish_version)
        self.assertEqual('CPU1', self.processor_inst.identity)
        self.assertEqual('Processor', self.processor_inst.name)
        self.assertEqual(None, self.processor_inst.description)
        self.assertEqual('CPU 1', self.processor_inst.socket)
        self.assertEqual('CPU', self.processor_inst.processor_type)
        self.assertEqual('x86', self.processor_inst.processor_architecture)
        self.assertEqual('x86-64', self.processor_inst.instruction_set)
        self.assertEqual('Intel(R) Corporation',
                         self.processor_inst.manufacturer)
        self.assertEqual('Multi-Core Intel(R) Xeon(R) processor 7xxx Series',
                         self.processor_inst.model)
        self.assertEqual(3700, self.processor_inst.max_speed_mhz)
        self.assertEqual(
            '0x42', self.processor_inst.processor_id.effective_family)
        self.assertEqual(
            '0x61', self.processor_inst.processor_id.effective_model)
        self.assertEqual(
            '0x34AC34DC8901274A',
            self.processor_inst.processor_id.identification_registers)
        self.assertEqual(
            '0x429943', self.processor_inst.processor_id.microcode_info)
        self.assertEqual('0x1', self.processor_inst.processor_id.step)
        self.assertEqual(
            'GenuineIntel', self.processor_inst.processor_id.vendor_id)
        self.assertEqual('OK', self.processor_inst.status.health)
        self.assertEqual('OK', self.processor_inst.status.health_rollup)
        self.assertEqual('Enabled', self.processor_inst.status.state)
        self.assertEqual(8, self.processor_inst.total_cores)
        self.assertEqual(16, self.processor_inst.total_threads)
        self.assertEqual('E5', self.processor_inst.oem.intel_rackscale.brand)
        self.assertEqual(
            ['sse', 'sse2', 'sse3'],
            self.processor_inst.oem.intel_rackscale.capabilities)
        self.assertEqual(
            'L2Cache',
            self.processor_inst.oem.intel_rackscale.on_package_memory[0].
            memory_type)
        self.assertEqual(
            2,
            self.processor_inst.oem.intel_rackscale.on_package_memory[0].
            capacity_mb)
        self.assertEqual(
            None,
            self.processor_inst.oem.intel_rackscale.on_package_memory[0].
            speed_mhz)
        self.assertEqual(
            'L3Cache',
            self.processor_inst.oem.intel_rackscale.on_package_memory[1].
            memory_type)
        self.assertEqual(
            20,
            self.processor_inst.oem.intel_rackscale.on_package_memory[1].
            capacity_mb)
        self.assertEqual(
            None,
            self.processor_inst.oem.intel_rackscale.on_package_memory[1].
            speed_mhz)
        self.assertEqual(
            160,
            self.processor_inst.oem.intel_rackscale.thermal_design_power_watt)
        self.assertEqual(
            '/redfish/v1/Systems/System1/Processors/CPU1/Metrics',
            self.processor_inst.oem.intel_rackscale.metrics)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_00h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_01h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_02h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_03h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_04h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_05h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_07h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_80000000h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_80000001h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_80000002h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_80000003h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_80000004h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_80000005h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_80000006h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_80000007h)
        self.assertEqual(
            "0x0429943FFFFFFFFF",
            self.processor_inst.oem.intel_rackscale.
            extended_identification_registers.eax_80000008h)
        self.assertEqual(
            "/redfish/v1/Chassis/1/PCIeDevices/Devices/1/Functions/1",
            self.processor_inst.oem.intel_rackscale.pcie_function)

        self.assertEqual(
            'Discrete', self.processor_inst.oem.intel_rackscale.fpga.fpga_type)
        self.assertEqual(
            'Stratix10', self.processor_inst.oem.intel_rackscale.fpga.model)
        self.assertEqual(
            '0x6400002fc614bb9',
            self.processor_inst.oem.intel_rackscale.fpga.fw_id)
        self.assertEqual(
            'Intel(R) Corporation',
            self.processor_inst.oem.intel_rackscale.fpga.fw_manufacturer)
        self.assertEqual(
            "Blue v.1.00.86",
            self.processor_inst.oem.intel_rackscale.fpga.fw_version)
        self.assertEqual(
            "8xPCIe-4",
            self.processor_inst.oem.intel_rackscale.fpga.host_interface)
        self.assertEqual(
            ["4x10G"],
            self.processor_inst.oem.intel_rackscale.fpga.external_interfaces)
        self.assertEqual(
            "I2C",
            self.processor_inst.oem.intel_rackscale.fpga.sideband_interface)
        self.assertEqual(
            1,
            self.processor_inst.oem.intel_rackscale.fpga.
            pcie_virtual_functions)
        self.assertEqual(
            True,
            self.processor_inst.oem.intel_rackscale.fpga.
            programmable_from_host)
        self.assertEqual(
            1,
            self.processor_inst.oem.intel_rackscale.fpga.reconfiguration_slots)
        self.assertEqual(
            "/redfish/v1/Systems/System1/Processors/FPGA1/Functions",
            self.processor_inst.oem.intel_rackscale.fpga.
            acceleration_functions)
        self.assertEqual(
            "AFU0",
            self.processor_inst.oem.intel_rackscale.fpga.
            reconfiguration_slots_details[0].slot_id)
        self.assertEqual(
            "00000000-0000-0000-0000-000000000000",
            self.processor_inst.oem.intel_rackscale.fpga.
            reconfiguration_slots_details[0].uuid)
        self.assertEqual(
            True,
            self.processor_inst.oem.intel_rackscale.fpga.
            reconfiguration_slots_details[0].programmable_from_host)
        self.assertEqual(
            '/redfish/v1/Chassis/Chassis1', self.processor_inst.links.chassis)
        self.assertEqual(
            '/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Down1',
            self.processor_inst.links.oem.intel_rackscale.connected_port)
        self.assertEqual(
            ('/redfish/v1/Fabrics/FPGAoF/Endpoints/1',),
            self.processor_inst.links.oem.intel_rackscale.endpoints)
        self.assertEqual(
            ('/redfish/v1/Systems/System1/Processors/1',),
            self.processor_inst.links.oem.intel_rackscale.connected_processors)

    def test__get_sub_processors_path(self):
        self.assertEqual(
            '/redfish/v1/Systems/System1/Processors/CPU1/SubProcessors',
            self.processor_inst._get_sub_processors_path())

    def test__get_sub_processors_path_missing_attr(self):
        self.processor_inst._json.pop('SubProcessors')
        with self.assertRaisesRegex(exceptions.MissingAttributeError,
                                    'attribute SubProcessors'):
            self.processor_inst._get_sub_processors_path()

    def test_sub_processors(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'processor_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_processor_col = self.processor_inst.sub_processors
        # | THEN |
        self.assertIsInstance(actual_processor_col,
                              processor.ProcessorCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_processor_col,
                      self.processor_inst.sub_processors)
        self.conn.get.return_value.json.assert_not_called()

    def test_sub_processors_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'processor_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.processor_inst.sub_processors,
                              processor.ProcessorCollection)

        # On refreshing the processor instance...
        with open('rsd_lib/tests/unit/json_samples/v2_4/processor.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.processor_inst.invalidate()
        self.processor_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'processor_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.processor_inst.sub_processors,
                              processor.ProcessorCollection)


class ProcessorCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(ProcessorCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'processor_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.processor_col = processor.ProcessorCollection(
            self.conn, '/redfish/v1/Systems/System1/Processors',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.processor_col._parse_attributes()
        self.assertEqual('1.1.0', self.processor_col.redfish_version)
        self.assertEqual(('/redfish/v1/Systems/System1/Processors/CPU1',
                          '/redfish/v1/Systems/System1/Processors/FPGA1'),
                         self.processor_col.members_identities)

    @mock.patch.object(processor, 'Processor', autospec=True)
    def test_get_member(self, mock_system):
        self.processor_col.get_member(
            '/redfish/v1/Systems/System1/Processors/CPU1')
        mock_system.assert_called_once_with(
            self.processor_col._conn,
            '/redfish/v1/Systems/System1/Processors/CPU1',
            redfish_version=self.processor_col.redfish_version)

    @mock.patch.object(processor, 'Processor', autospec=True)
    def test_get_members(self, mock_system):
        members = self.processor_col.get_members()
        calls = [
            mock.call(self.processor_col._conn,
                      '/redfish/v1/Systems/System1/Processors/CPU1',
                      redfish_version=self.processor_col.redfish_version),
            mock.call(self.processor_col._conn,
                      '/redfish/v1/Systems/System1/Processors/FPGA1',
                      redfish_version=self.processor_col.redfish_version)
        ]
        mock_system.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(2, len(members))
