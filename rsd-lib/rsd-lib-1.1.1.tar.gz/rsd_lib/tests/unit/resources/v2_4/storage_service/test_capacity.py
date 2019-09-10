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

from rsd_lib.resources.v2_3.storage_service import drive
from rsd_lib.resources.v2_3.storage_service import storage_pool
from rsd_lib.resources.v2_4.storage_service import capacity
from rsd_lib.resources.v2_4.storage_service import volume


class CapacitySourceTestCase(testtools.TestCase):
    def setUp(self):
        super(CapacitySourceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_4/capacity_sources.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.capacity_sources_inst = capacity.CapacitySource(
            self.conn,
            "/redfish/v1/StorageServices/1/Volumes/1/CapacitySources/1",
            redfish_version="1.0.2",
        )

    def test__parse_attributes(self):
        self.capacity_sources_inst._parse_attributes()
        self.assertEqual("1.0.2", self.capacity_sources_inst.redfish_version)
        self.assertEqual(
            "Volume capacity source", self.capacity_sources_inst.description
        )
        self.assertEqual("1", self.capacity_sources_inst.identity)
        self.assertEqual("CapacitySource", self.capacity_sources_inst.name)
        self.assertEqual(
            3071983104,
            self.capacity_sources_inst.provided_capacity.data.allocated_bytes,
        )

    def test_providing_volumes(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_4/volume_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_providing_volumes = self.capacity_sources_inst.providing_volumes
        # | THEN |
        self.assertIsInstance(actual_providing_volumes, list)
        self.assertIsInstance(
            actual_providing_volumes[0], volume.VolumeCollection
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(
            actual_providing_volumes,
            self.capacity_sources_inst.providing_volumes,
        )
        self.conn.get.return_value.json.assert_not_called()

    def test_providing_volumes_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_4/volume_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.capacity_sources_inst.providing_volumes, list
        )
        self.assertIsInstance(
            self.capacity_sources_inst.providing_volumes[0],
            volume.VolumeCollection,
        )

        # On refreshing the chassis instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_4/capacity_sources.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.capacity_sources_inst.invalidate()
        self.capacity_sources_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_4/volume_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.capacity_sources_inst.providing_volumes, list
        )
        self.assertIsInstance(
            self.capacity_sources_inst.providing_volumes[0],
            volume.VolumeCollection,
        )

    def test_providing_pools(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_3/"
            "storage_pool_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_providing_pools = self.capacity_sources_inst.providing_pools
        # | THEN |
        self.assertIsInstance(actual_providing_pools, list)
        self.assertIsInstance(
            actual_providing_pools[0], storage_pool.StoragePoolCollection
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(
            actual_providing_pools, self.capacity_sources_inst.providing_pools
        )
        self.conn.get.return_value.json.assert_not_called()

    def test_providing_pools_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_3/"
            "storage_pool_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.capacity_sources_inst.providing_pools, list)
        self.assertIsInstance(
            self.capacity_sources_inst.providing_pools[0],
            storage_pool.StoragePoolCollection,
        )

        # On refreshing the chassis instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_4/capacity_sources.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.capacity_sources_inst.invalidate()
        self.capacity_sources_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_3/"
            "storage_pool_collection.json",
            "r",
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.capacity_sources_inst.providing_pools, list)
        self.assertIsInstance(
            self.capacity_sources_inst.providing_pools[0],
            storage_pool.StoragePoolCollection,
        )

    def test_providing_drives(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_3/drive_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_providing_drives = self.capacity_sources_inst.providing_drives
        # | THEN |
        self.assertIsInstance(actual_providing_drives, list)
        self.assertIsInstance(
            actual_providing_drives[0], drive.DriveCollection
        )
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(
            actual_providing_drives,
            self.capacity_sources_inst.providing_drives,
        )
        self.conn.get.return_value.json.assert_not_called()

    def test_providing_drives_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_3/drive_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.capacity_sources_inst.providing_drives, list
        )
        self.assertIsInstance(
            self.capacity_sources_inst.providing_drives[0],
            drive.DriveCollection,
        )

        # On refreshing the chassis instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_4/capacity_sources.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.capacity_sources_inst.invalidate()
        self.capacity_sources_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_3/drive_collection.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.capacity_sources_inst.providing_drives, list
        )
        self.assertIsInstance(
            self.capacity_sources_inst.providing_drives[0],
            drive.DriveCollection,
        )
