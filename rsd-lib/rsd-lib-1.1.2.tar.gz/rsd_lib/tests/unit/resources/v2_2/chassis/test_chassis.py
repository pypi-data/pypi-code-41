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

from rsd_lib.resources.v2_2.chassis import chassis
from rsd_lib.resources.v2_2.chassis import power
from rsd_lib.resources.v2_2.chassis import thermal


class ChassisTestCase(testtools.TestCase):
    def setUp(self):
        super(ChassisTestCase, self).setUp()
        self.conn = mock.Mock()

        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/chassis.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.chassis_inst = chassis.Chassis(
            self.conn, "/redfish/v1/Chassis/chassis1", redfish_version="1.0.2"
        )

    def test_power(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open("rsd_lib/tests/unit/json_samples/v2_2/power.json", "r") as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_power = self.chassis_inst.power
        # | THEN |
        self.assertIsInstance(actual_power, power.Power)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_power, self.chassis_inst.power)
        self.conn.get.return_value.json.assert_not_called()

    def test_power_on_refresh(self):
        # | GIVEN |
        with open("rsd_lib/tests/unit/json_samples/v2_2/power.json", "r") as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.chassis_inst.power, power.Power)

        # On refreshing the chassis instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/chassis.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.chassis_inst.invalidate()
        self.chassis_inst.refresh(force=False)

        # | GIVEN |
        with open("rsd_lib/tests/unit/json_samples/v2_2/power.json", "r") as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.chassis_inst.power, power.Power)

    def test_thermal(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/thermal.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_thermal = self.chassis_inst.thermal
        # | THEN |
        self.assertIsInstance(actual_thermal, thermal.Thermal)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_thermal, self.chassis_inst.thermal)
        self.conn.get.return_value.json.assert_not_called()

    def test_thermal_on_refresh(self):
        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/thermal.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.chassis_inst.thermal, thermal.Thermal)

        # On refreshing the chassis instance...
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/chassis.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.chassis_inst.invalidate()
        self.chassis_inst.refresh(force=False)

        # | GIVEN |
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/thermal.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.chassis_inst.thermal, thermal.Thermal)
