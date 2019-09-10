# Copyright 2017 Intel, Inc.
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

import logging

from sushy.resources import base
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.common import redundancy
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class LinksField(base.CompositeField):

    mutually_exclusive_endpoints = base.Field(
        "MutuallyExclusiveEndpoints", adapter=utils.get_members_identities
    )
    """An array of references to the endpoints that may not be used in zones
       if this endpoint is used in a zone.
    """

    ports = base.Field("Ports", adapter=utils.get_members_identities)
    """An array of references to the the physical ports associated with this
       endpoint.
    """


class PciIdField(base.CompositeField):

    device_id = base.Field("DeviceId")
    """The Device ID of this PCIe function."""

    vendor_id = base.Field("VendorId")
    """The Vendor ID of this PCIe function."""

    subsystem_id = base.Field("SubsystemId")
    """The Subsystem ID of this PCIe function."""

    subsystem_vendor_id = base.Field("SubsystemVendorId")
    """The Subsystem Vendor ID of this PCIe function."""


class ConnectedEntityCollectionField(base.ListField):
    """ConnectedEntity field

       Represents a remote resource that is connected to the network
       accessible to this endpoint.
    """

    entity_type = base.Field("EntityType")
    """The type of the connected entity."""

    entity_role = base.Field("EntityRole")
    """The role of the connected entity."""

    entity_link = base.Field(
        "EntityLink", adapter=rsd_lib_utils.get_resource_identity
    )
    """A link to the associated entity."""

    entity_pci_id = PciIdField("EntityPciId")
    """The PCI ID of the connected entity."""

    pci_function_number = base.Field(
        "PciFunctionNumber", adapter=rsd_lib_utils.num_or_none
    )
    """The PCI ID of the connected entity."""

    pci_class_code = base.Field("PciClassCode")
    """The Class Code and Subclass code of this PCIe function."""

    identifiers = rsd_lib_base.IdentifierCollectionField("Identifiers")
    """Identifiers for the remote entity."""


class Endpoint(rsd_lib_base.ResourceBase):
    """Endpoint resource class

       This is the schema definition for the Endpoint resource. It represents
       the properties of an entity that sends or receives protocol defined
       messages over a transport.
    """

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    endpoint_protocol = base.Field("EndpointProtocol")
    """The protocol supported by this endpoint."""

    connected_entities = ConnectedEntityCollectionField("ConnectedEntities")
    """All the entities connected to this endpoint."""

    identifiers = rsd_lib_base.IdentifierCollectionField("Identifiers")
    """Identifiers for this endpoint"""

    pci_id = PciIdField("PciId")
    """The PCI ID of the endpoint."""

    host_reservation_memory_bytes = base.Field(
        "HostReservationMemoryBytes", adapter=rsd_lib_utils.num_or_none
    )
    """The amount of memory in Bytes that the Host should allocate to connect
       to this endpoint.
    """

    links = LinksField("Links")
    """The links object contains the links to other resources that are related
       to this resource.
    """

    redundancy = redundancy.RedundancyCollectionField("Redundancy")
    """Redundancy information for the lower level endpoints supporting this
       endpoint
    """

    # TODO(linyang): Add Action Field


class EndpointCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Endpoint
