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

from rsd_lib import base as rsd_lib_base


class EthernetSwitchMetrics(rsd_lib_base.ResourceBase):
    """EthernetSwitchMetrics resource class

       EthernetSwitchMetrics contains usage and health statistics of an
       Ethernet Switch .
    """

    health = base.Field("Health")
    """Health of Ethernet Switch as a discrete sensor reading"""
