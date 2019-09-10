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

from rsd_lib.resources.v2_1.chassis import thermal
from rsd_lib import utils as rsd_lib_utils


class IntelRackScaleField(base.CompositeField):
    """Thermal field

       Extended Thermal resource.
    """

    volumetric_airflow_cfm = base.Field(
        "VolumetricAirflowCfm", adapter=rsd_lib_utils.num_or_none
    )
    """Volumetric Air Flow measured in Cubic Feet per Minute"""

    desired_speed_pwm = base.Field(
        "DesiredSpeedPwm", adapter=rsd_lib_utils.num_or_none
    )
    """This property represent desired speed of all FANs in current chassis as
       percentage of max speed.
    """


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class Thermal(thermal.Thermal):
    """Thermal resource class

       This is the schema definition for the Thermal properties.  It
       represents the properties for Temperature and Cooling.
    """

    oem = OemField("Oem")
    """Oem specific properties."""
