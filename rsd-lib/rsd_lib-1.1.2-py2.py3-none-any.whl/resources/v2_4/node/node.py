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

from jsonschema import validate
import logging

from sushy import exceptions
from sushy.resources import base

from rsd_lib.resources.v2_3.node import node
from rsd_lib.resources.v2_4.node import schemas as node_schemas


LOG = logging.getLogger(__name__)
PM_OPENATION_ON_DELETE_VALUES = [
    'PreserveConfiguration', 'SecureErase', 'OverwritePCD']


class AttachEndpointActionField(base.CompositeField):
    target_uri = base.Field('target', required=True)
    action_info_path = base.Field('@Redfish.ActionInfo')
    action_info = None


class DetachEndpointActionField(base.CompositeField):
    target_uri = base.Field('target', required=True)
    action_info_path = base.Field('@Redfish.ActionInfo')
    action_info = None


class NodeActionsField(node.NodeActionsField):
    attach_endpoint = AttachEndpointActionField('#ComposedNode.AttachResource')
    detach_endpoint = DetachEndpointActionField('#ComposedNode.DetachResource')


class Node(node.Node):

    persistent_memory_operation_on_delete = base.Field(
        'PersistentMemoryOperationOnDelete')
    """This property is used to specify what operation should be performed on
       Intel OptaneTM DC Persistent Memory on ComposedNode DELETE Request:
       - PreserveConfiguration
       - SecureErase
       - OverwritePCD
    """

    _actions = NodeActionsField('Actions', required=True)

    def update(self, clear_tpm_on_delete=None, pm_on_delete=None):
        """Update properties of this composed node

        :param clear_tpm_on_delete: This is used to specify if TPM module
            should be cleared on composed node DELETE request.
        :param pm_on_delete: This is used to specify what operation should be
            performed on Intel OptaneTM DC Persistent Memory on ComposedNode
            DELETE Request:
            - PreserveConfiguration
            - SecureErase
            - OverwritePCD
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        if clear_tpm_on_delete is None and pm_on_delete is None:
            raise ValueError('At least "clear_tpm_on_delete" or "pm_on_delete"'
                             ' parameter has to be specified')

        data = {}
        if clear_tpm_on_delete is not None:
            if not isinstance(clear_tpm_on_delete, bool):
                raise exceptions.InvalidParameterValueError(
                    parameter='clear_tpm_on_delete', value=clear_tpm_on_delete,
                    valid_values=[True, False])
            data['ClearTPMOnDelete'] = clear_tpm_on_delete

        if pm_on_delete is not None:
            if pm_on_delete not in PM_OPENATION_ON_DELETE_VALUES:
                raise exceptions.InvalidParameterValueError(
                    parameter='pm_on_delete', value=pm_on_delete,
                    valid_values=PM_OPENATION_ON_DELETE_VALUES)
            data['PersistentMemoryOperationOnDelete'] = pm_on_delete

        self._conn.patch(self.path, data=data)


class NodeCollection(node.NodeCollection):

    @property
    def _resource_type(self):
        return Node

    def _create_compose_request(self, name=None, description=None,
                                processor_req=None, memory_req=None,
                                remote_drive_req=None, local_drive_req=None,
                                ethernet_interface_req=None,
                                security_req=None, total_system_core_req=None,
                                total_system_memory_req=None):

        request = {}

        if name is not None:
            request['Name'] = name
        if description is not None:
            request['Description'] = description

        if processor_req is not None:
            validate(processor_req,
                     node_schemas.processor_req_schema)
            request['Processors'] = processor_req

        if memory_req is not None:
            validate(memory_req,
                     node_schemas.memory_req_schema)
            request['Memory'] = memory_req

        if remote_drive_req is not None:
            validate(remote_drive_req,
                     node_schemas.remote_drive_req_schema)
            request['RemoteDrives'] = remote_drive_req

        if local_drive_req is not None:
            validate(local_drive_req,
                     node_schemas.local_drive_req_schema)
            request['LocalDrives'] = local_drive_req

        if ethernet_interface_req is not None:
            validate(ethernet_interface_req,
                     node_schemas.ethernet_interface_req_schema)
            request['EthernetInterfaces'] = ethernet_interface_req

        if security_req is not None:
            validate(security_req,
                     node_schemas.security_req_schema)
            request['Security'] = security_req

        if total_system_core_req is not None:
            validate(total_system_core_req,
                     node_schemas.total_system_core_req_schema)
            request['TotalSystemCoreCount'] = total_system_core_req

        if total_system_memory_req is not None:
            validate(total_system_memory_req,
                     node_schemas.total_system_memory_req_schema)
            request['TotalSystemMemoryMiB'] = total_system_memory_req

        return request

    def compose_node(self, name=None, description=None,
                     processor_req=None, memory_req=None,
                     remote_drive_req=None, local_drive_req=None,
                     ethernet_interface_req=None, security_req=None,
                     total_system_core_req=None, total_system_memory_req=None):
        """Compose a node from RackScale hardware

        :param name: Name of node
        :param description: Description of node
        :param processor_req: JSON for node processors
        :param memory_req: JSON for node memory modules
        :param remote_drive_req: JSON for node remote drives
        :param local_drive_req: JSON for node local drives
        :param ethernet_interface_req: JSON for node ethernet ports
        :param security_req: JSON for node security requirements
        :param total_system_core_req: Total processor cores available in
            composed node
        :param total_system_memory_req: Total memory available in composed node
        :returns: The location of the composed node

        When the 'processor_req' is not none: it need a computer system
        contains processors whose each processor meet all conditions in the
        value.

        When the 'total_system_core_req' is not none: it need a computer
        system contains processors whose cores sum up to number equal or
        greater than 'total_system_core_req'.

        When both values are not none: it need meet all conditions.

        'memory_req' and 'total_system_memory_req' is the same.
        """
        target_uri = self._get_compose_action_element().target_uri
        properties = self._create_compose_request(
            name=name, description=description,
            processor_req=processor_req,
            memory_req=memory_req,
            remote_drive_req=remote_drive_req,
            local_drive_req=local_drive_req,
            ethernet_interface_req=ethernet_interface_req,
            security_req=security_req,
            total_system_core_req=total_system_core_req,
            total_system_memory_req=total_system_memory_req)
        resp = self._conn.post(target_uri, data=properties)
        LOG.info("Node created at %s", resp.headers['Location'])
        node_url = resp.headers['Location']
        return node_url[node_url.find(self._path):]
