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

from sushy.resources import base

from rsd_lib.resources.v2_1.chassis import power
from rsd_lib import utils as rsd_lib_utils


class IntelRackScaleField(base.CompositeField):
    """Power field

       Extended Power resource.
    """

    input_ac_power_watts = base.Field(
        "InputACPowerWatts", adapter=rsd_lib_utils.num_or_none
    )
    """The global power level on AC side in Watts."""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class PowerSupplyCollectionField(power.PowerSupplyCollectionField):
    """PowerSupply field

       Details of a power supplies associated with this system or device
    """

    indicator_led = base.Field("IndicatorLED")
    """The state of the indicator LED, used to identify the power supply."""


class Power(power.Power):
    """Power resource class

       This is the schema definition for the Power Metrics.  It represents the
       properties for Power Consumption and Power Limiting.
    """

    power_supplies = PowerSupplyCollectionField("PowerSupplies")
    """Details of the power supplies associated with this system or device"""

    oem = OemField("Oem")
    """Oem specific properties."""
