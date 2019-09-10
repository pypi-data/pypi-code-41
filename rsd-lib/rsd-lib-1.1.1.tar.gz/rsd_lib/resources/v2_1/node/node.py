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

from jsonschema import validate
import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib import constants
from rsd_lib.resources.v2_1.node import schemas as node_schemas
from rsd_lib.resources.v2_1.system import system
from rsd_lib import utils as rsd_lib_utils


LOG = logging.getLogger(__name__)


class AssembleActionField(base.CompositeField):

    target_uri = base.Field("target", required=True)


class AttachEndpointActionField(common.ActionField):

    allowed_values = base.Field(
        "Resource@Redfish.AllowableValues",
        default=(),
        adapter=utils.get_members_identities,
    )


class DetachEndpointActionField(common.ActionField):

    allowed_values = base.Field(
        "Resource@Redfish.AllowableValues",
        default=(),
        adapter=utils.get_members_identities,
    )


class NodeActionsField(base.CompositeField):

    reset = common.ResetActionField("#ComposedNode.Reset")
    assemble = common.ActionField("#ComposedNode.Assemble")
    attach_endpoint = AttachEndpointActionField("#ComposedNode.AttachEndpoint")
    detach_endpoint = DetachEndpointActionField("#ComposedNode.DetachEndpoint")


class NodeCollectionActionsField(base.CompositeField):

    compose = common.ActionField("#ComposedNodeCollection.Allocate")


class LinksField(base.CompositeField):

    computer_system = base.Field(
        "ComputerSystem", adapter=rsd_lib_utils.get_resource_identity
    )
    """Link to base computer system of this node"""

    processors = base.Field("Processors", adapter=utils.get_members_identities)
    """Link to processors of this node"""

    memory = base.Field("Memory", adapter=utils.get_members_identities)
    """Link to memory of this node"""

    ethernet_interfaces = base.Field(
        "EthernetInterfaces", adapter=utils.get_members_identities
    )
    """Link to ethernet interfaces of this node"""

    local_drives = base.Field(
        "LocalDrives", adapter=utils.get_members_identities
    )
    """Link to local driver of this node"""

    remote_drives = base.Field(
        "RemoteDrives", adapter=utils.get_members_identities
    )
    """Link to remote drives of this node"""

    managed_by = base.Field("ManagedBy", adapter=utils.get_members_identities)


class Node(rsd_lib_base.ResourceBase):
    """ComposedNode resource class

       This schema defines a node and its respective properties.
    """

    links = LinksField("Links")
    """Contains links to other resources that are related to this resource."""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    composed_node_state = base.Field("ComposedNodeState")

    asset_tag = base.Field("AssetTag")
    """The user definable tag that can be used to track this computer system
       for inventory or other client purposes
    """

    uuid = base.Field("UUID")
    """The universal unique identifier (UUID) for this system"""

    power_state = base.Field("PowerState")
    """This is the current power state of the system"""

    boot = system.BootField("Boot")
    """Information about the boot settings for this system"""

    processors = system.ProcessorSummaryField("Processors")
    """This object describes the central processors of the system in general
       detail.
    """

    memory = system.MemorySummaryField("Memory")
    """This object describes the central memory of the system in general
       detail.
    """

    _actions = NodeActionsField("Actions", required=True)

    def _get_reset_action_element(self):
        reset_action = self._actions.reset

        if not reset_action:
            raise exceptions.MissingActionError(
                action="#ComposedNode.Reset", resource=self._path
            )
        return reset_action

    def _get_assemble_action_element(self):
        assemble_action = self._actions.assemble
        if not assemble_action:
            raise exceptions.MissingActionError(
                action="#ComposedNode.Assemble", resource=self._path
            )
        return assemble_action

    def get_allowed_reset_node_values(self):
        """Get the allowed values for resetting the node.

        :returns: A set with the allowed values.
        """
        reset_action = self._get_reset_action_element()

        if not reset_action.allowed_values:
            LOG.warning(
                "Could not figure out the allowed values for the "
                "reset node action for Node %s",
                self.identity,
            )
            return set(constants.RESET_TYPE_VALUE)

        return set(constants.RESET_TYPE_VALUE).intersection(
            reset_action.allowed_values
        )

    def reset_node(self, value):
        """Reset the node.

        :param value: The target value.
        :raises: InvalidParameterValueError, if the target value is not
            allowed.
        """
        valid_resets = self.get_allowed_reset_node_values()
        if value not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter="value", value=value, valid_values=valid_resets
            )

        target_uri = self._get_reset_action_element().target_uri

        self._conn.post(target_uri, data={"ResetType": value})

    def assemble_node(self):
        """Assemble the composed node."""
        target_uri = self._get_assemble_action_element().target_uri

        self._conn.post(target_uri)

    def get_allowed_node_boot_source_values(self):
        """Get the allowed values for changing the boot source.

        :returns: A set with the allowed values.
        """
        if not self.boot.boot_source_override_target_allowed_values:
            LOG.warning(
                "Could not figure out the allowed values for "
                "configuring the boot source for Node %s",
                self.identity,
            )
            return set(constants.BOOT_SOURCE_TARGET_VALUE)

        return set(constants.BOOT_SOURCE_TARGET_VALUE).intersection(
            self.boot.boot_source_override_target_allowed_values
        )

    def get_allowed_node_boot_mode_values(self):
        """Get the allowed values for the boot source mode.

        :returns: A set with the allowed values.
        """
        if not self.boot.boot_source_override_mode_allowed_values:
            LOG.warning(
                "Could not figure out the allowed values for "
                "configuring the boot mode for Node %s",
                self.identity,
            )
            return set(constants.BOOT_SOURCE_MODE_VALUE)

        return set(constants.BOOT_SOURCE_MODE_VALUE).intersection(
            self.boot.boot_source_override_mode_allowed_values
        )

    def set_node_boot_source(self, target, enabled="Once", mode=None):
        """Set the boot source.

        Set the boot source to use on next reboot of the Node.

        :param target: The target boot source.
        :param enabled: The frequency, whether to set it for the next
            reboot only ("Once") or persistent to all future reboots
            ("Continuous") or disabled ("Disabled").
        :param mode: The boot mode, UEFI ("UEFI") or BIOS ("Legacy").
        :raises: InvalidParameterValueError, if any information passed is
            invalid.
        """
        valid_targets = self.get_allowed_node_boot_source_values()
        if target not in valid_targets:
            raise exceptions.InvalidParameterValueError(
                parameter="target", value=target, valid_values=valid_targets
            )

        if enabled not in constants.BOOT_SOURCE_ENABLED_VALUE:
            raise exceptions.InvalidParameterValueError(
                parameter="enabled",
                value=enabled,
                valid_values=constants.BOOT_SOURCE_ENABLED_VALUE,
            )

        data = {
            "Boot": {
                "BootSourceOverrideTarget": target,
                "BootSourceOverrideEnabled": enabled,
            }
        }

        if mode is not None:
            valid_modes = self.get_allowed_node_boot_mode_values()
            if mode not in valid_modes:
                raise exceptions.InvalidParameterValueError(
                    parameter="mode", value=mode, valid_values=valid_modes
                )

            data["Boot"]["BootSourceOverrideMode"] = mode

        self._conn.patch(self.path, data=data)

    def _get_attach_endpoint_action_element(self):
        attach_endpoint_action = self._actions.attach_endpoint
        if not attach_endpoint_action:
            raise exceptions.MissingActionError(
                action="#ComposedNode.AttachEndpoint", resource=self._path
            )
        return attach_endpoint_action

    def get_allowed_attach_endpoints(self):
        """Get the allowed endpoints for attach action.

        :returns: A set with the allowed attach endpoints.
        """
        attach_action = self._get_attach_endpoint_action_element()
        return attach_action.allowed_values

    def attach_endpoint(self, endpoint=None, capacity=None):
        """Attach endpoint from available pool to composed node

        :param endpoint: Link to endpoint to attach.
        :param capacity: Requested capacity of the drive in GiB.
        :raises: InvalidParameterValueError
        :raises: BadRequestError if at least one param isn't specified
        """
        attach_action = self._get_attach_endpoint_action_element()
        valid_endpoints = attach_action.allowed_values
        target_uri = attach_action.target_uri

        if endpoint and endpoint not in valid_endpoints:
            raise exceptions.InvalidParameterValueError(
                parameter="endpoint",
                value=endpoint,
                valid_values=valid_endpoints,
            )

        data = {}
        if endpoint is not None:
            data["Resource"] = {"@odata.id": endpoint}
        if capacity is not None:
            data["CapacityGiB"] = capacity

        self._conn.post(target_uri, data=data)

    def _get_detach_endpoint_action_element(self):
        detach_endpoint_action = self._actions.detach_endpoint
        if not detach_endpoint_action:
            raise exceptions.MissingActionError(
                action="#ComposedNode.DetachEndpoint", resource=self._path
            )
        return detach_endpoint_action

    def get_allowed_detach_endpoints(self):
        """Get the allowed endpoints for detach action.

        :returns: A set with the allowed detach endpoints.
        """
        detach_action = self._get_detach_endpoint_action_element()
        return detach_action.allowed_values

    def detach_endpoint(self, endpoint):
        """Detach already attached endpoint from composed node

        :param endpoint: Link to endpoint to detach
        :raises: InvalidParameterValueError
        :raises: BadRequestError
        """
        detach_action = self._get_detach_endpoint_action_element()
        valid_endpoints = detach_action.allowed_values
        target_uri = detach_action.target_uri

        if endpoint not in valid_endpoints:
            raise exceptions.InvalidParameterValueError(
                parameter="endpoint",
                value=endpoint,
                valid_values=valid_endpoints,
            )

        data = {"Resource": endpoint}

        self._conn.post(target_uri, data=data)

    def delete_node(self):
        """Delete (disassemble) the node.

        When this action is called several tasks are performed. A graceful
        shutdown is sent to the computer system, all VLANs except reserved ones
        are removed from associated ethernet switch ports, the computer system
        is deallocated and the remote target is deallocated.
        """
        self._conn.delete(self.path)


class NodeCollection(rsd_lib_base.ResourceCollectionBase):

    _actions = NodeCollectionActionsField("Actions", required=True)

    @property
    def _resource_type(self):
        return Node

    def _get_compose_action_element(self):
        compose_action = self._actions.compose
        if not compose_action:
            raise exceptions.MissingActionError(
                action="#ComposedNodeCollection.Allocate", resource=self._path
            )
        return compose_action

    def _create_compose_request(
        self,
        name=None,
        description=None,
        processor_req=None,
        memory_req=None,
        remote_drive_req=None,
        local_drive_req=None,
        ethernet_interface_req=None,
        total_system_core_req=None,
        total_system_memory_req=None,
    ):

        request = {}

        if name is not None:
            request["Name"] = name
        if description is not None:
            request["Description"] = description

        if processor_req is not None:
            validate(processor_req, node_schemas.processor_req_schema)
            request["Processors"] = processor_req

        if memory_req is not None:
            validate(memory_req, node_schemas.memory_req_schema)
            request["Memory"] = memory_req

        if remote_drive_req is not None:
            validate(remote_drive_req, node_schemas.remote_drive_req_schema)
            request["RemoteDrives"] = remote_drive_req

        if local_drive_req is not None:
            validate(local_drive_req, node_schemas.local_drive_req_schema)
            request["LocalDrives"] = local_drive_req

        if ethernet_interface_req is not None:
            validate(
                ethernet_interface_req,
                node_schemas.ethernet_interface_req_schema,
            )
            request["EthernetInterfaces"] = ethernet_interface_req

        if total_system_core_req is not None:
            validate(
                total_system_core_req,
                node_schemas.total_system_core_req_schema,
            )
            request["TotalSystemCoreCount"] = total_system_core_req

        if total_system_memory_req is not None:
            validate(
                total_system_memory_req,
                node_schemas.total_system_memory_req_schema,
            )
            request["TotalSystemMemoryMiB"] = total_system_memory_req

        return request

    def compose_node(
        self,
        name=None,
        description=None,
        processor_req=None,
        memory_req=None,
        remote_drive_req=None,
        local_drive_req=None,
        ethernet_interface_req=None,
        total_system_core_req=None,
        total_system_memory_req=None,
    ):
        """Compose a node from RackScale hardware

        :param name: Name of node
        :param description: Description of node
        :param processor_req: JSON for node processors
        :param memory_req: JSON for node memory modules
        :param remote_drive_req: JSON for node remote drives
        :param local_drive_req: JSON for node local drives
        :param ethernet_interface_req: JSON for node ethernet ports
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
            name=name,
            description=description,
            processor_req=processor_req,
            memory_req=memory_req,
            remote_drive_req=remote_drive_req,
            local_drive_req=local_drive_req,
            ethernet_interface_req=ethernet_interface_req,
            total_system_core_req=total_system_core_req,
            total_system_memory_req=total_system_memory_req,
        )
        resp = self._conn.post(target_uri, data=properties)
        LOG.info("Node created at %s", resp.headers["Location"])
        node_url = resp.headers["Location"]
        return node_url[node_url.find(self._path):]
