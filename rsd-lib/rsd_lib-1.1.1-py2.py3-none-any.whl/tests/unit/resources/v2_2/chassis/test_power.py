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

from rsd_lib.resources.v2_2.chassis import power


class PowerTestCase(testtools.TestCase):
    def setUp(self):
        super(PowerTestCase, self).setUp()
        self.conn = mock.Mock()
        with open("rsd_lib/tests/unit/json_samples/v2_2/power.json", "r") as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.power_inst = power.Power(
            self.conn,
            "/redfish/v1/Chassis/Rack1/Power",
            redfish_version="1.1.0",
        )

    def test__parse_attributes(self):
        self.power_inst._parse_attributes()
        self.assertEqual(
            "Off", self.power_inst.power_supplies[0].indicator_led
        )
        self.assertEqual(
            245, self.power_inst.oem.intel_rackscale.input_ac_power_watts
        )
