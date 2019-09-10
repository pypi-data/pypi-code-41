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

from rsd_lib.resources.v2_1.chassis import chassis
from rsd_lib.resources.v2_1.chassis import log_entry
from rsd_lib.resources.v2_1.chassis import log_service
from rsd_lib.resources.v2_1.chassis import power
from rsd_lib.resources.v2_1.chassis import power_zone
from rsd_lib.resources.v2_1.chassis import thermal
from rsd_lib.resources.v2_1.chassis import thermal_zone

from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_acl
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_acl_rule
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_port
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch_static_mac
from rsd_lib.resources.v2_1.ethernet_switch import vlan_network_interface

from rsd_lib.resources.v2_1.event_service import event_destination
from rsd_lib.resources.v2_1.event_service import event_service

from rsd_lib.resources.v2_1.fabric import endpoint
from rsd_lib.resources.v2_1.fabric import fabric
from rsd_lib.resources.v2_1.fabric import port
from rsd_lib.resources.v2_1.fabric import switch
from rsd_lib.resources.v2_1.fabric import zone

from rsd_lib.resources.v2_1.manager import manager
from rsd_lib.resources.v2_1.manager import manager_network_protocol
from rsd_lib.resources.v2_1.manager import serial_interface
from rsd_lib.resources.v2_1.manager import virtual_media

from rsd_lib.resources.v2_1.node import node

from rsd_lib.resources.v2_1.registries import message_registry_file

from rsd_lib.resources.v2_1.storage_service import logical_drive
from rsd_lib.resources.v2_1.storage_service import physical_drive
from rsd_lib.resources.v2_1.storage_service import remote_target
from rsd_lib.resources.v2_1.storage_service import storage_service

from rsd_lib.resources.v2_1.system import drive
from rsd_lib.resources.v2_1.system import ethernet_interface
from rsd_lib.resources.v2_1.system import memory
from rsd_lib.resources.v2_1.system import network_device_function
from rsd_lib.resources.v2_1.system import network_interface
from rsd_lib.resources.v2_1.system import pcie_device
from rsd_lib.resources.v2_1.system import pcie_function
from rsd_lib.resources.v2_1.system import processor
from rsd_lib.resources.v2_1.system import simple_storage
from rsd_lib.resources.v2_1.system import storage
from rsd_lib.resources.v2_1.system import system
from rsd_lib.resources.v2_1.system import volume

from rsd_lib.resources.v2_1.task import task
from rsd_lib.resources.v2_1.task import task_service

RESOURCE_CLASS = {
    'Chassis': chassis.Chassis,
    'ChassisCollection': chassis.ChassisCollection,
    'ComposedNode': node.Node,
    'ComposedNodeCollection': node.NodeCollection,
    'ComputerSystem': system.System,
    'ComputerSystemCollection': system.SystemCollection,
    'Drive': drive.Drive,
    'Endpoint': endpoint.Endpoint,
    'EndpointCollection': endpoint.EndpointCollection,
    'EthernetInterface': ethernet_interface.EthernetInterface,
    'EthernetInterfaceCollection':
        ethernet_interface.EthernetInterfaceCollection,
    'EthernetSwitch': ethernet_switch.EthernetSwitch,
    'EthernetSwitchACL': ethernet_switch_acl.EthernetSwitchACL,
    'EthernetSwitchACLCollection':
        ethernet_switch_acl.EthernetSwitchACLCollection,
    'EthernetSwitchACLRule': ethernet_switch_acl_rule.EthernetSwitchACLRule,
    'EthernetSwitchACLRuleCollection':
        ethernet_switch_acl_rule.EthernetSwitchACLRuleCollection,
    'EthernetSwitchCollection': ethernet_switch.EthernetSwitchCollection,
    'EthernetSwitchPort': ethernet_switch_port.EthernetSwitchPort,
    'EthernetSwitchPortCollection':
        ethernet_switch_port.EthernetSwitchPortCollection,
    'EthernetSwitchStaticMAC':
        ethernet_switch_static_mac.EthernetSwitchStaticMAC,
    'EthernetSwitchStaticMACCollection':
        ethernet_switch_static_mac.EthernetSwitchStaticMACCollection,
    'EventDestination': event_destination.EventDestination,
    'EventDestinationCollection': event_destination.EventDestinationCollection,
    'EventService': event_service.EventService,
    'Fabric': fabric.Fabric,
    'FabricCollection': fabric.FabricCollection,
    'LogEntry': log_entry.LogEntry,
    'LogEntryCollection': log_entry.LogEntryCollection,
    'LogService': log_service.LogService,
    'LogServiceCollection': log_service.LogServiceCollection,
    'LogicalDrive': logical_drive.LogicalDrive,
    'LogicalDriveCollection': logical_drive.LogicalDriveCollection,
    'Manager': manager.Manager,
    'ManagerCollection': manager.ManagerCollection,
    'ManagerNetworkProtocol': manager_network_protocol.ManagerNetworkProtocol,
    'Memory': memory.Memory,
    'MemoryCollection': memory.MemoryCollection,
    'MessageRegistryFile': message_registry_file.MessageRegistryFile,
    'MessageRegistryFileCollection':
        message_registry_file.MessageRegistryFileCollection,
    'NetworkDeviceFunction': network_device_function.NetworkDeviceFunction,
    'NetworkDeviceFunctionCollection':
        network_device_function.NetworkDeviceFunctionCollection,
    'NetworkInterface': network_interface.NetworkInterface,
    'NetworkInterfaceCollection': network_interface.NetworkInterfaceCollection,
    'PCIeDevice': pcie_device.PCIeDevice,
    'PCIeFunction': pcie_function.PCIeFunction,
    'PhysicalDrive': physical_drive.PhysicalDrive,
    'PhysicalDriveCollection': physical_drive.PhysicalDriveCollection,
    'Port': port.Port,
    'PortCollection': port.PortCollection,
    'Power': power.Power,
    'PowerZone': power_zone.PowerZone,
    'PowerZoneCollection': power_zone.PowerZoneCollection,
    'Processor': processor.Processor,
    'ProcessorCollection': processor.ProcessorCollection,
    'RemoteTarget': remote_target.RemoteTarget,
    'RemoteTargetCollection':
        remote_target.RemoteTargetCollection,
    'SerialInterface': serial_interface.SerialInterface,
    'SerialInterfaceCollection': serial_interface.SerialInterfaceCollection,
    'SimpleStorage': simple_storage.SimpleStorage,
    'SimpleStorageCollection': simple_storage.SimpleStorageCollection,
    'Storage': storage.Storage,
    'StorageCollection': storage.StorageCollection,
    'StorageService': storage_service.StorageService,
    'StorageServiceCollection': storage_service.StorageServiceCollection,
    'Switch': switch.Switch,
    'SwitchCollection': switch.SwitchCollection,
    'Task': task.Task,
    'TaskCollection': task.TaskCollection,
    'TaskService': task_service.TaskService,
    'Thermal': thermal.Thermal,
    'ThermalZone': thermal_zone.ThermalZone,
    'ThermalZoneCollection':
        thermal_zone.ThermalZoneCollection,
    'VLanNetworkInterface':
        vlan_network_interface.VLanNetworkInterface,
    'VLanNetworkInterfaceCollection':
        vlan_network_interface.VLanNetworkInterfaceCollection,
    'VirtualMedia': virtual_media.VirtualMedia,
    'VirtualMediaCollection': virtual_media.VirtualMediaCollection,
    'Volume': volume.Volume,
    'VolumeCollection': volume.VolumeCollection,
    'Zone': zone.Zone,
    'ZoneCollection': zone.ZoneCollection
}
