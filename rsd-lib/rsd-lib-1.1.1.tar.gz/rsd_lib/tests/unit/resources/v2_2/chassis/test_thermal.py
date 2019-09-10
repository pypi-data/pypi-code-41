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

from rsd_lib.resources.v2_2.chassis import thermal


class ThermalTestCase(testtools.TestCase):
    def setUp(self):
        super(ThermalTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            "rsd_lib/tests/unit/json_samples/v2_2/thermal.json", "r"
        ) as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.thermal = thermal.Thermal(
            self.conn,
            "/redfish/v1/Chassis/Rack1/Thermal",
            redfish_version="1.1.0",
        )

    def test__parse_attributes(self):
        self.thermal._parse_attributes()
        self.assertEqual(
            12, self.thermal.oem.intel_rackscale.volumetric_airflow_cfm
        )
        self.assertEqual(
            80, self.thermal.oem.intel_rackscale.desired_speed_pwm
        )
