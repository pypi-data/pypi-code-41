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
from rsd_lib.resources.v2_3.storage_service import drive
from rsd_lib.resources.v2_3.storage_service import drive_metrics
from rsd_lib.resources.v2_3.storage_service import storage_pool
from rsd_lib.resources.v2_3.storage_service import volume_metrics

RESOURCE_CLASS = deepcopy(RESOURCE_CLASS_V22)
RESOURCE_CLASS.update(
    {
        'DriveCollection': drive.DriveCollection,
        'DriveMetrics': drive_metrics.DriveMetrics,
        'StoragePool': storage_pool.StoragePool,
        'StoragePoolCollection': storage_pool.StoragePoolCollection,
        'VolumeMetrics': volume_metrics.VolumeMetrics
    }
)
for k in (
        'LogicalDrive',
        'LogicalDriveCollection',
        'PhysicalDrive',
        'PhysicalDriveCollection',
        'RemoteTarget',
        'RemoteTargetCollection'):
    RESOURCE_CLASS.pop(k)
