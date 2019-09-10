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
import jsonschema
import mock
import testtools

from sushy import exceptions

from rsd_lib.resources.v2_4.node import node
from rsd_lib.tests.unit.fakes import request_fakes


class NodeTestCase(testtools.TestCase):

    def setUp(self):
        super(NodeTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_4/node.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst = node.Node(
            self.conn, '/redfish/v1/Nodes/Node1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.node_inst._parse_attributes()
        self.assertEqual(True, self.node_inst.clear_tpm_on_delete)
        self.assertEqual(
            'OverwritePCD',
            self.node_inst.persistent_memory_operation_on_delete)

    def test_update_node(self):
        self.node_inst.update(clear_tpm_on_delete=True)
        self.node_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Nodes/Node1', data={'ClearTPMOnDelete': True})

        self.node_inst._conn.patch.reset_mock()
        self.node_inst.update(pm_on_delete='OverwritePCD')
        self.node_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Nodes/Node1',
            data={'PersistentMemoryOperationOnDelete': 'OverwritePCD'})

        self.node_inst._conn.patch.reset_mock()
        self.node_inst.update(
            clear_tpm_on_delete=True, pm_on_delete='OverwritePCD')
        self.node_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Nodes/Node1',
            data={'ClearTPMOnDelete': True,
                  'PersistentMemoryOperationOnDelete': 'OverwritePCD'})

    def test_update_node_with_invalid_parameter(self):
        with self.assertRaisesRegex(
            ValueError,
            'At least "clear_tpm_on_delete" or "pm_on_delete" parameter has to'
                ' be specified'):
            self.node_inst.update()

        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "clear_tpm_on_delete" value "fake-value" is '
                'invalid'):
            self.node_inst.update(clear_tpm_on_delete='fake-value')

        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            'The parameter "pm_on_delete" value "fake-value" is invalid'):
            self.node_inst.update(
                clear_tpm_on_delete=True, pm_on_delete='fake-value')

    def test__get_attach_endpoint_action_element(self):
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        value = self.node_inst._get_attach_endpoint_action_element()
        self.assertEqual('/redfish/v1/Nodes/Node1/Actions/'
                         'ComposedNode.AttachResource',
                         value.target_uri)
        self.assertEqual('/redfish/v1/Nodes/Node1/Actions/'
                         'AttachResourceActionInfo',
                         value.action_info_path)
        expected = [
            {
                "name": "Resource",
                "required": True,
                "data_type": "Object",
                "object_data_type": "#Resource.Resource",
                "allowable_values": (
                    "/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1",
                )
            },
            {
                "name": "Protocol",
                "required": False,
                "data_type": "String",
                "object_data_type": None,
                "allowable_values": ["NVMeOverFabrics"]
            }
        ]
        self.assertEqual(expected, value.action_info.parameters)

    def test_get_allowed_attach_endpoints(self):
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        expected = self.node_inst.get_allowed_attach_endpoints()
        result = ("/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1",)
        self.assertEqual(expected, result)

    def test_attach_endpoint(self):
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst.attach_endpoint(
            resource='/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1',
            protocol='NVMeOverFabrics')
        self.node_inst._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Node1/Actions/ComposedNode.AttachResource',
            data={'Resource': {'@odata.id': '/redfish/v1/StorageServices'
                                            '/1-sv-1/Volumes/1-sv-1-vl-1'},
                  'Protocol': 'NVMeOverFabrics'})

    def test_attach_endpoint_only_with_resource_uri(self):
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst.attach_endpoint(
            resource='/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1')
        self.node_inst._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Node1/Actions/ComposedNode.AttachResource',
            data={'Resource': {'@odata.id': '/redfish/v1/StorageServices'
                                            '/1-sv-1/Volumes/1-sv-1-vl-1'}})

    def test_attach_endpoint_invalid_parameter(self):
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            '"resource" value.*{0}'.format(
                '/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1')):

            self.node_inst.attach_endpoint(resource='invalid-resource')

    def test__get_detach_endpoint_action_element(self):
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        value = self.node_inst._get_detach_endpoint_action_element()
        self.assertEqual('/redfish/v1/Nodes/Node1/Actions/'
                         'ComposedNode.DetachResource',
                         value.target_uri)
        self.assertEqual('/redfish/v1/Nodes/Node1/Actions/'
                         'DetachResourceActionInfo',
                         value.action_info_path)
        expected = [
            {
                "name": "Resource",
                "required": True,
                "data_type": "Object",
                "object_data_type": "#Resource.Resource",
                "allowable_values": (
                    "/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1",
                )
            },
            {
                "name": "Protocol",
                "required": False,
                "data_type": "String",
                "object_data_type": None,
                "allowable_values": ["NVMeOverFabrics"]
            }
        ]
        self.assertEqual(expected, value.action_info.parameters)

    def test_get_allowed_detach_endpoints(self):
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        expected = self.node_inst.get_allowed_detach_endpoints()
        result = ("/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1",)
        self.assertEqual(expected, result)

    def test_detach_endpoint(self):
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst.detach_endpoint(
            resource='/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1')
        self.node_inst._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Node1/Actions/ComposedNode.DetachResource',
            data={'Resource': {'@odata.id': '/redfish/v1/StorageServices'
                                            '/1-sv-1/Volumes/1-sv-1-vl-1'}})

    def test_detach_endpoint_invalid_parameter(self):
        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            '"resource" value.*{0}'.format(
                '/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1')):

            self.node_inst.detach_endpoint(resource='invalid-resource')

    def test_refresh(self):
        self.assertIsNone(self.node_inst._actions.attach_endpoint.action_info)
        self.assertIsNone(self.node_inst._actions.detach_endpoint.action_info)

        with open('rsd_lib/tests/unit/json_samples/v2_4/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst._get_attach_endpoint_action_element()
        self.node_inst._get_detach_endpoint_action_element()

        self.assertIsNotNone(
            self.node_inst._actions.attach_endpoint.action_info)
        self.assertIsNotNone(
            self.node_inst._actions.detach_endpoint.action_info)

        with open('rsd_lib/tests/unit/json_samples/v2_4/node.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.node_inst.refresh()

        self.assertIsNone(self.node_inst._actions.attach_endpoint.action_info)
        self.assertIsNone(self.node_inst._actions.detach_endpoint.action_info)


class NodeCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(NodeCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_4/node_collection.json',
                  'r') as f:
            self.conn.get.return_value = request_fakes.fake_request_get(
                json.loads(f.read()))
            self.conn.post.return_value = request_fakes.fake_request_post(
                None, headers={"Location": "https://localhost:8443/"
                                           "redfish/v1/Nodes/1"})

        self.node_col = node.NodeCollection(
            self.conn, '/redfish/v1/Nodes', redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.node_col._parse_attributes()
        self.assertEqual('1.0.2', self.node_col.redfish_version)
        self.assertEqual('Composed Node Collection', self.node_col.name)
        self.assertEqual(('/redfish/v1/Nodes/1',),
                         self.node_col.members_identities)

    @mock.patch.object(node, 'Node', autospec=True)
    def test_get_member(self, mock_node):
        self.node_col.get_member('/redfish/v1/Nodes/1')
        mock_node.assert_called_once_with(
            self.node_col._conn, '/redfish/v1/Nodes/1',
            redfish_version=self.node_col.redfish_version)

    @mock.patch.object(node, 'Node', autospec=True)
    def test_get_members(self, mock_node):
        members = self.node_col.get_members()
        mock_node.assert_called_once_with(
            self.node_col._conn, '/redfish/v1/Nodes/1',
            redfish_version=self.node_col.redfish_version)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test__get_compose_action_element(self):
        value = self.node_col._get_compose_action_element()
        self.assertEqual('/redfish/v1/Nodes/Actions/Allocate',
                         value.target_uri)

    def test_compose_node_no_reqs(self):
        result = self.node_col.compose_node()
        self.node_col._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Actions/Allocate', data={})
        self.assertEqual(result, '/redfish/v1/Nodes/1')

    def test_compose_node(self):
        reqs = {
            'Name': 'test',
            'Description': 'this is a test node',
            "Processors": [{
                "@odata.type":
                    "AllocationComposedNodeRequest.v1_1_0.Processor",
                "Model": "Multi-Core Intel(R) Xeon(R) processor 7xxx Series",
                "TotalCores": 2,
                "AchievableSpeedMHz": 3700,
                "InstructionSet": "x86-64",
                "Oem": {
                    "Intel_RackScale": {
                        "@odata.type": "AllocationComposedNodeRequest.v1_1_0."
                                       "ProcessorExtensions",
                        "Brand": "E5",
                        "Capabilities": ["sse"]
                    }
                },
                "Resource": {
                    "@odata.id": "/redfish/v1/Systems/1/Processors/1"
                },
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/1"
                },
                "ProcessorType": "CPU",
                "Connectivity": ["Local", "RemotePCIe"]
            }],
            "Memory": [{
                "@odata.type": "AllocationComposedNodeRequest.v1_1_0.Memory",
                "CapacityMiB": 16000,
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR3",
                "SpeedMHz": 1600,
                "Manufacturer": "Intel",
                "DataWidthBits": 64,
                "Resource": {
                    "@odata.id": "/redfish/v1/Systems/1/Memory/1"
                },
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/1"
                }
            }],
            "RemoteDrives": [{
                "CapacityGiB": 80,
                "Protocol": "iSCSI",
                "Master": {
                    "@odata.type":
                        "AllocationComposedNodeRequest.v1_1_0.Master",
                    "Type": "Snapshot",
                    "Resource": {
                        "@odata.id":
                            "/redfish/v1/StorageServices/iscsi1/Volumes/1"
                    }
                }
            }],
            "LocalDrives": [{
                "CapacityGiB": 100,
                "Type": "HDD",
                "MinRPM": 5400,
                "SerialNumber": "12345678",
                "Interface": "SATA",
                "Resource": {
                    "@odata.id": "redfish/v1/Chassis/Blade1/Drives/Disk1"
                },
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/Blade1"
                },
                "FabricSwitch": False
            }],
            "EthernetInterfaces": [{
                "SpeedMbps": 1000,
                "PrimaryVLAN": 100,
                "VLANs": [{
                    "VLANId": 100,
                    "Tagged": False
                }],
                "Resource": {
                    "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/1"
                },
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/1"
                }
            }],
            'Security': {
                'TpmPresent': True,
                'TpmInterfaceType': 'TPM2_0',
                'TxtEnabled': True,
                'ClearTPMOnDelete': True,
                "PersistentMemoryOperationOnDelete": "OverwritePCD"
            },
            'TotalSystemCoreCount': 8,
            'TotalSystemMemoryMiB': 16000
        }
        result = self.node_col.compose_node(
            name='test', description='this is a test node',
            processor_req=[{
                "@odata.type":
                    "AllocationComposedNodeRequest.v1_1_0.Processor",
                "Model": "Multi-Core Intel(R) Xeon(R) processor 7xxx Series",
                "TotalCores": 2,
                "AchievableSpeedMHz": 3700,
                "InstructionSet": "x86-64",
                "Oem": {
                    "Intel_RackScale": {
                        "@odata.type": "AllocationComposedNodeRequest.v1_1_0."
                                       "ProcessorExtensions",
                        "Brand": "E5",
                        "Capabilities": ["sse"]
                    }
                },
                "Resource": {
                    "@odata.id": "/redfish/v1/Systems/1/Processors/1"
                },
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/1"
                },
                "ProcessorType": "CPU",
                "Connectivity": ["Local", "RemotePCIe"]
            }],
            memory_req=[{
                "@odata.type": "AllocationComposedNodeRequest.v1_1_0.Memory",
                "CapacityMiB": 16000,
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR3",
                "SpeedMHz": 1600,
                "Manufacturer": "Intel",
                "DataWidthBits": 64,
                "Resource": {
                    "@odata.id": "/redfish/v1/Systems/1/Memory/1"
                },
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/1"
                }
            }],
            remote_drive_req=[{
                "CapacityGiB": 80,
                "Protocol": "iSCSI",
                "Master": {
                    "@odata.type":
                        "AllocationComposedNodeRequest.v1_1_0.Master",
                    "Type": "Snapshot",
                    "Resource": {
                        "@odata.id": "/redfish/v1/StorageServices/iscsi1/"
                                     "Volumes/1"
                    }
                }
            }],
            local_drive_req=[{
                "CapacityGiB": 100,
                "Type": "HDD",
                "MinRPM": 5400,
                "SerialNumber": "12345678",
                "Interface": "SATA",
                "Resource": {
                    "@odata.id": "redfish/v1/Chassis/Blade1/Drives/Disk1"
                },
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/Blade1"
                },
                "FabricSwitch": False
            }],
            ethernet_interface_req=[{
                "SpeedMbps": 1000,
                "PrimaryVLAN": 100,
                "VLANs": [{
                    "VLANId": 100,
                    "Tagged": False
                }],
                "Resource": {
                    "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/1"
                },
                "Chassis": {
                    "@odata.id": "/redfish/v1/Chassis/1"
                }
            }],
            security_req={
                'TpmPresent': True,
                'TpmInterfaceType': 'TPM2_0',
                'TxtEnabled': True,
                'ClearTPMOnDelete': True,
                "PersistentMemoryOperationOnDelete": "OverwritePCD"
            },
            total_system_core_req=8,
            total_system_memory_req=16000)
        self.node_col._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Actions/Allocate', data=reqs)
        self.assertEqual(result, '/redfish/v1/Nodes/1')

    def test_compose_node_with_invalid_reqs(self):
        # Wrong processor type
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not one of \['CPU', 'FPGA', 'GPU', 'DSP', "
             "'Accelerator', 'OEM'\]")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                processor_req=[{
                    'TotalCores': 4,
                    'ProcessorType': 'invalid'}])

        # Wrong processor Oem Brand
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not one of \['E3', 'E5'")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                processor_req=[{
                    'TotalCores': 4,
                    'Oem': {
                        "Intel_RackScale": {
                            'Brand': 'invalid',
                            'Capabilities': ['sse']
                        }
                    }
                }])

        # Wrong processor Oem Capabilities
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'sse' is not of type 'array'")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                processor_req=[{
                    'TotalCores': 4,
                    'Oem': {
                        "Intel_RackScale": {
                            'Brand': 'E3',
                            'Capabilities': 'sse'
                        }
                    }
                }])

        # Wrong processor Oem Capabilities
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("0 is not of type 'string'")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                processor_req=[{
                    'TotalCores': 4,
                    'Oem': {
                        "Intel_RackScale": {
                            'Brand': 'E3',
                            'Capabilities': [0]
                        }
                    }
                }])

        # Wrong processor Connectivity
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid-value' is not one of \['Local', 'Ethernet', "
             "'RemotePCIe'\]")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                processor_req=[{
                    'TotalCores': 4,
                    "Connectivity": ["invalid-value"]
                }])

        # Wrong memory MemoryType
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid-value' is not one of \['DRAM', 'NVDIMM_N', 'NVDIMM_F', "
             "'NVMDIMM_P', 'IntelOptane'\]")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                memory_req=[{
                    "CapacityMiB": 16000,
                    "MemoryType": "invalid-value",
                }])

        # Wrong remote drive CapacityGiB
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not of type 'number'")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                remote_drive_req=[{
                    'CapacityGiB': 'invalid',
                    'Protocol': 'NVMeOverFabrics',
                    'Master': {
                        'Type': 'Snapshot',
                        'Resource': {
                            '@odata.id':
                                '/redfish/v1/StorageServices/NVMeoE1/Volumes/'
                                '102'
                        }
                    },
                    'Resource': {
                        '@odata.id':
                            '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
                        }
                }])

        # Wrong remote drive Protocol
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not one of \['iSCSI', 'NVMeOverFabrics'\]")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                remote_drive_req=[{
                    'CapacityGiB': 80,
                    'Protocol': 'invalid',
                    'Master': {
                        'Type': 'Snapshot',
                        'Resource': {
                            '@odata.id':
                                '/redfish/v1/StorageServices/NVMeoE1/Volumes/'
                                '102'
                        }
                    },
                    'Resource': {
                        '@odata.id':
                            '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
                        }
                }])

        # Wrong remote drive Master Type
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not one of \['Snapshot', 'Clone'\]")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                remote_drive_req=[{
                    'CapacityGiB': 80,
                    'Protocol': 'iSCSI',
                    'Master': {
                        'Type': 'invalid',
                        'Resource': {
                            '@odata.id':
                                '/redfish/v1/StorageServices/NVMeoE1/Volumes/'
                                '102'
                        }
                    },
                    'Resource': {
                        '@odata.id':
                            '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
                        }
                }])

        # Wrong security parameter "TpmPresent"
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            "'invalid' is not of type 'boolean'"):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': 'invalid',
                    'TpmInterfaceType': 'TPM2_0',
                    'TxtEnabled': True,
                    'ClearTPMOnDelete': True
                })

        # Wrong security parameter "TpmInterfaceType"
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            "True is not of type 'string'"):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': False,
                    'TpmInterfaceType': True,
                    'TxtEnabled': True,
                    'ClearTPMOnDelete': True
                })

        # Wrong security parameter "TxtEnabled"
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            "'invalid' is not of type 'boolean'"):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': True,
                    'TpmInterfaceType': 'TPM2_0',
                    'TxtEnabled': 'invalid',
                    'ClearTPMOnDelete': True
                })

        # Wrong security parameter "ClearTPMOnDelete"
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            "'invalid' is not of type 'boolean'"):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': True,
                    'TpmInterfaceType': 'TPM2_0',
                    'TxtEnabled': True,
                    'ClearTPMOnDelete': 'invalid'
                })

        # Wrong security parameter "PersistentMemoryOperationOnDelete"
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not one of \['PreserveConfiguration', "
             "'SecureErase', 'OverwritePCD'\]")):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': True,
                    'TpmInterfaceType': 'TPM2_0',
                    'TxtEnabled': True,
                    'PersistentMemoryOperationOnDelete': 'invalid'
                })

        # Wrong additional security parameter
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("Additional properties are not allowed \('invalid-key' was "
             "unexpected\)")):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': True,
                    'TpmInterfaceType': 'TPM2_0',
                    'TxtEnabled': False,
                    'invalid-key': 'invalid-value'
                })
