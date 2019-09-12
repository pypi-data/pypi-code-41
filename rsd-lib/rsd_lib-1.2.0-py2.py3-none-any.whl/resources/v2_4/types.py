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

from rsd_lib.resources.v2_3.types import RESOURCE_CLASS as RESOURCE_CLASS_V23
from rsd_lib.resources.v2_4.fabric import endpoint
from rsd_lib.resources.v2_4.fabric import fabric
from rsd_lib.resources.v2_4.node import node
from rsd_lib.resources.v2_4.storage_service import capacity_source
from rsd_lib.resources.v2_4.storage_service import storage_service
from rsd_lib.resources.v2_4.storage_service import volume
from rsd_lib.resources.v2_4.system import processor
from rsd_lib.resources.v2_4.system import system

RESOURCE_CLASS = deepcopy(RESOURCE_CLASS_V23)
RESOURCE_CLASS.update(
    {
        "CapacitySource": capacity_source.CapacitySource,
        "ComposedNode": node.Node,
        "ComposedNodeCollection": node.NodeCollection,
        "ComputerSystem": system.System,
        "ComputerSystemCollection": system.SystemCollection,
        "Endpoint": endpoint.Endpoint,
        "EndpointCollection": endpoint.EndpointCollection,
        "Fabric": fabric.Fabric,
        "FabricCollection": fabric.FabricCollection,
        "Processor": processor.Processor,
        "ProcessorCollection": processor.ProcessorCollection,
        "StorageService": storage_service.StorageService,
        "StorageServiceCollection": storage_service.StorageServiceCollection,
        "Volume": volume.Volume,
        "VolumeCollection": volume.VolumeCollection,
    }
)
