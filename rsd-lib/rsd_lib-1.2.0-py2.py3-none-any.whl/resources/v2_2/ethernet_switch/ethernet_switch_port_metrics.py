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

from sushy.resources import base

from rsd_lib import base as rsd_lib_base
from rsd_lib import utils as rsd_lib_utils


class MetricsField(base.CompositeField):

    packets = base.Field("Packets", adapter=rsd_lib_utils.num_or_none)
    """Packets counter"""

    dropped_packets = base.Field(
        "DroppedPackets", adapter=rsd_lib_utils.num_or_none
    )
    """Dropped packets counter"""

    error_packets = base.Field(
        "ErrorPackets", adapter=rsd_lib_utils.num_or_none
    )
    """Error packets counter"""

    broadcast_packets = base.Field(
        "BroadcastPackets", adapter=rsd_lib_utils.num_or_none
    )
    """Broadcast packets counter"""

    multicast_packets = base.Field(
        "MulticastPackets", adapter=rsd_lib_utils.num_or_none
    )
    """Multicats packets counter"""

    bytes = base.Field("Bytes", adapter=rsd_lib_utils.num_or_none)
    """Bytes counter"""

    errors = base.Field("Errors", adapter=rsd_lib_utils.num_or_none)
    """Error counter"""


class EthernetSwitchPortMetrics(rsd_lib_base.ResourceBase):

    received = MetricsField("Received")
    """Port Receive metrics"""

    transmitted = MetricsField("Transmitted")
    """Port Transmit metrics."""

    collisions = base.Field("Collisions", adapter=rsd_lib_utils.num_or_none)
    """Collisions counter"""
