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

import jsonschema
import logging

from sushy.resources import base
from sushy import utils

from rsd_lib import common as rsd_lib_common
from rsd_lib.resources.v2_4.fabric import endpoint_schemas
from rsd_lib import utils as rsd_lib_utils


LOG = logging.getLogger(__name__)


class IdentifiersField(base.ListField):
    name_format = base.Field('DurableNameFormat')
    name = base.Field('DurableName')


class PciIdField(base.ListField):
    device_id = base.Field('DeviceId')
    vendor_id = base.Field('VendorId')
    subsystem_id = base.Field('SubsystemId')
    subsystem_vendor_id = base.Field('SubsystemVendorId')


class ConnectedEntitiesField(base.ListField):
    entity_type = base.Field('EntityType')
    entity_role = base.Field('EntityRole')
    entity_link = base.Field('EntityLink',
                             adapter=rsd_lib_utils.get_resource_identity)
    identifiers = IdentifiersField('Identifiers')
    entity_pci_id = PciIdField('EntityPciId')
    pci_function_number = base.Field(
        'PciFunctionNumber', adapter=rsd_lib_utils.num_or_none)
    pci_class_code = base.Field('PciClassCode')


class LinksOemIntelRackScaleField(base.CompositeField):
    zones = base.Field('Zones', adapter=utils.get_members_identities)
    interfaces = base.Field('Interfaces', adapter=utils.get_members_identities)


class LinksOemField(base.CompositeField):
    intel_rackscale = LinksOemIntelRackScaleField('Intel_RackScale')


class LinksField(base.CompositeField):
    ports = base.Field('Ports', adapter=utils.get_members_identities)
    endpoints = base.Field('Endpoints', adapter=utils.get_members_identities)
    oem = LinksOemField('Oem')


class IPTransportDetailsField(base.ListField):
    transport_protocol = base.Field('TransportProtocol')
    ipv4_address = base.Field(['IPv4Address', 'Address'])
    ipv6_address = base.Field(['IPv6Address', 'Address'])
    port = base.Field('Port', adapter=rsd_lib_utils.num_or_none)


class AuthenticationField(base.CompositeField):
    username = base.Field('Username')
    password = base.Field('Password')


class OemIntelRackScaleField(base.CompositeField):
    authentication = AuthenticationField('Authentication')

    endpoint_protocol = base.Field('EndpointProtocol')
    """Protocol for endpoint (i.e. PCIe)"""

    pcie_function = base.Field(
        'PCIeFunction', adapter=rsd_lib_utils.get_resource_identity)
    """A reference to the PCIe function that provides this processor
       functionality
    """


class OemField(base.CompositeField):
    intel_rackscale = OemIntelRackScaleField('Intel_RackScale')


class Endpoint(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The endpoint identity string"""

    name = base.Field('Name')
    """The endpoint name"""

    description = base.Field('Description')
    """The endpoint description"""

    endpoint_protocol = base.Field('EndpointProtocol')
    """Protocol for endpoint (i.e. PCIe)"""

    connected_entities = ConnectedEntitiesField('ConnectedEntities')
    """Entities connected to endpoint"""

    identifiers = IdentifiersField('Identifiers')
    """Identifiers for endpoint"""

    status = rsd_lib_common.StatusField('Status')
    """The endpoint status"""

    pci_id = PciIdField('PciId')
    """PCI ID of the endpoint"""

    host_reservation_memory_bytes = base.Field('HostReservationMemoryBytes')
    """The amount of memory in bytes that the Host should allocate to connect
       to this endpoint
    """

    ip_transport_details = IPTransportDetailsField('IPTransportDetails')
    """IP transport details info of this endpoint"""

    links = LinksField('Links')
    """These links to related components of this endpoint"""

    oem = OemField('Oem')
    """The OEM additional info of this endpoint"""

    def delete(self):
        """Delete this endpoint"""
        self._conn.delete(self.path)


class EndpointCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Endpoint

    def _create_endpoint_request(self, connected_entities, identifiers=None,
                                 protocol=None, pci_id=None,
                                 host_reservation_memory_bytes=None,
                                 ip_transport_details=None, links=None,
                                 oem=None):

        request = {}

        jsonschema.validate(connected_entities,
                            endpoint_schemas.connected_entities_req_schema)
        request['ConnectedEntities'] = connected_entities

        if identifiers is not None:
            jsonschema.validate(identifiers,
                                endpoint_schemas.identifiers_req_schema)
            request['Identifiers'] = identifiers

        if protocol is not None:
            jsonschema.validate(protocol, endpoint_schemas.protocol_req_schema)
            request['EndpointProtocol'] = protocol

        if pci_id is not None:
            jsonschema.validate(pci_id, endpoint_schemas.pci_id_req_schema)
            request['PciId'] = pci_id

        if host_reservation_memory_bytes is not None:
            jsonschema.validate(
                host_reservation_memory_bytes,
                endpoint_schemas.host_reservation_memory_bytes_req_schema)
            request['HostReservationMemoryBytes'] = \
                host_reservation_memory_bytes

        if ip_transport_details is not None:
            jsonschema.validate(
                ip_transport_details,
                endpoint_schemas.ip_transport_details_req_schema)
            request['IPTransportDetails'] = ip_transport_details

        if links is not None:
            jsonschema.validate(links, endpoint_schemas.links_req_schema)
            request['Links'] = links

        if oem is not None:
            jsonschema.validate(oem, endpoint_schemas.oem_req_schema)
            request['Oem'] = oem

        return request

    def create_endpoint(self, connected_entities, identifiers=None,
                        protocol=None, pci_id=None,
                        host_reservation_memory_bytes=None,
                        ip_transport_details=None, links=None, oem=None):
        """Create a new endpoint

        :param connected_entities: provides information about entities
                                   connected to the endpoint
        :param identifiers: provides iQN or NQN of created entity
        :param protocol: the protocol used by the endpoint
        :param pci_id: the PCI ID of the endpoint
        :param ip_transport_details: the transport used for accessing the
                                     endpoint
        :param oem: the oem fields of this endpoint creation request
        :returns: The uri of the new endpoint
        """
        properties = self._create_endpoint_request(
            connected_entities, identifiers, protocol, pci_id,
            host_reservation_memory_bytes, ip_transport_details, links, oem)

        resp = self._conn.post(self._path, data=properties)
        LOG.info("Endpoint created at %s", resp.headers['Location'])
        endpoint_url = resp.headers['Location']
        return endpoint_url[endpoint_url.find(self._path):]
