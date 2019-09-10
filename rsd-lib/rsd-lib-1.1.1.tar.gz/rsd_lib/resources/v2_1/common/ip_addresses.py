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


class IPv6AddressCollectionField(base.ListField):

    address = base.Field("Address")
    """This is the IPv6 Address."""

    prefix_length = base.Field("PrefixLength")
    """This is the IPv6 Address Prefix Length."""

    address_origin = base.Field("AddressOrigin")
    """This indicates how the address was determined."""

    address_state = base.Field("AddressState")
    """The current state of this address as defined in RFC 4862."""


class IPv6StaticAddressCollectionField(base.ListField):
    """IPv6StaticAddress field

       This object represents a single IPv6 static address to be assigned on a
       network interface.
    """

    address = base.Field("Address")
    """A valid IPv6 address."""

    prefix_length = base.Field("PrefixLength")
    """The Prefix Length of this IPv6 address."""


class IPv4AddressCollectionField(base.ListField):

    address = base.Field("Address")
    """This is the IPv4 Address."""

    subnet_mask = base.Field("SubnetMask")
    """This is the IPv4 Subnet mask."""

    address_origin = base.Field("AddressOrigin")
    """This indicates how the address was determined."""

    gateway = base.Field("Gateway")
    """This is the IPv4 gateway for this address."""
