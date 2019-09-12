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

from copy import deepcopy

from rsd_lib.resources.v2_2.types import RESOURCE_CLASS as RESOURCE_CLASS_V22
from rsd_lib.resources.v2_3.chassis import chassis
from rsd_lib.resources.v2_3.ethernet_switch import ethernet_switch
from rsd_lib.resources.v2_3.fabric import endpoint
from rsd_lib.resources.v2_3.fabric import fabric
from rsd_lib.resources.v2_3.fabric import zone
from rsd_lib.resources.v2_3.manager import manager
from rsd_lib.resources.v2_3.node import attach_action_info
from rsd_lib.resources.v2_3.node import node
from rsd_lib.resources.v2_3.storage_service import drive
from rsd_lib.resources.v2_3.storage_service import drive_metrics
from rsd_lib.resources.v2_3.storage_service import storage_pool
from rsd_lib.resources.v2_3.storage_service import storage_service
from rsd_lib.resources.v2_3.storage_service import volume
from rsd_lib.resources.v2_3.storage_service import volume_metrics
from rsd_lib.resources.v2_3.system import ethernet_interface
from rsd_lib.resources.v2_3.system import system

RESOURCE_CLASS = deepcopy(RESOURCE_CLASS_V22)
RESOURCE_CLASS.update(
    {
        "ActionInfo": attach_action_info.AttachResourceActionInfo,
        "Chassis": chassis.Chassis,
        "ChassisCollection": chassis.ChassisCollection,
        "ComposedNode": node.Node,
        "ComposedNodeCollection": node.NodeCollection,
        "ComputerSystem": system.System,
        "ComputerSystemCollection": system.SystemCollection,
        "Drive": drive.Drive,
        "DriveCollection": drive.DriveCollection,
        "DriveMetrics": drive_metrics.DriveMetrics,
        "Endpoint": endpoint.Endpoint,
        "EndpointCollection": endpoint.EndpointCollection,
        "EthernetInterface": ethernet_interface.EthernetInterface,
        "EthernetInterfaceCollection":
            ethernet_interface.EthernetInterfaceCollection,
        "EthernetSwitch": ethernet_switch.EthernetSwitch,
        "EthernetSwitchCollection": ethernet_switch.EthernetSwitchCollection,
        "Fabric": fabric.Fabric,
        "FabricCollection": fabric.FabricCollection,
        "Manager": manager.Manager,
        "ManagerCollection": manager.ManagerCollection,
        "StoragePool": storage_pool.StoragePool,
        "StoragePoolCollection": storage_pool.StoragePoolCollection,
        "StorageService": storage_service.StorageService,
        "StorageServiceCollection": storage_service.StorageServiceCollection,
        "Volume": volume.Volume,
        "VolumeCollection": volume.VolumeCollection,
        "VolumeMetrics": volume_metrics.VolumeMetrics,
        "Zone": zone.Zone,
        "ZoneCollection": zone.ZoneCollection,
    }
)
for k in (
    "LogicalDrive",
    "LogicalDriveCollection",
    "PhysicalDrive",
    "PhysicalDriveCollection",
    "RemoteTarget",
    "RemoteTargetCollection",
):
    RESOURCE_CLASS.pop(k)
