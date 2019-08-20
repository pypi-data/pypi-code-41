# coding: utf-8
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.

import oci  # noqa: F401
from oci.util import WAIT_RESOURCE_NOT_FOUND  # noqa: F401


class TransferApplianceClientCompositeOperations(object):
    """
    This class provides a wrapper around :py:class:`~oci.dts.TransferApplianceClient` and offers convenience methods
    for operations that would otherwise need to be chained together. For example, instead of performing an action
    on a resource (e.g. launching an instance, creating a load balancer) and then using a waiter to wait for the resource
    to enter a given state, you can call a single method in this class to accomplish the same functionality
    """

    def __init__(self, client, **kwargs):
        """
        Creates a new TransferApplianceClientCompositeOperations object

        :param TransferApplianceClient client:
            The service client which will be wrapped by this object
        """
        self.client = client

    def create_transfer_appliance_and_wait_for_state(self, id, wait_for_states=[], operation_kwargs={}, waiter_kwargs={}):
        """
        Calls :py:func:`~oci.dts.TransferApplianceClient.create_transfer_appliance` and waits for the :py:class:`~oci.dts.models.TransferAppliance` acted upon
        to enter the given state(s).

        :param str id: (required)
            ID of the Transfer Job

        :param list[str] wait_for_states:
            An array of states to wait on. These should be valid values for :py:attr:`~oci.dts.models.TransferAppliance.lifecycle_state`

        :param dict operation_kwargs:
            A dictionary of keyword arguments to pass to :py:func:`~oci.dts.TransferApplianceClient.create_transfer_appliance`

        :param dict waiter_kwargs:
            A dictionary of keyword arguments to pass to the :py:func:`oci.wait_until` function. For example, you could pass ``max_interval_seconds`` or ``max_interval_seconds``
            as dictionary keys to modify how long the waiter function will wait between retries and the maximum amount of time it will wait
        """
        operation_result = self.client.create_transfer_appliance(id, **operation_kwargs)
        if not wait_for_states:
            return operation_result

        lowered_wait_for_states = [w.lower() for w in wait_for_states]
        wait_for_resource_id = operation_result.data.id

        try:
            waiter_result = oci.wait_until(
                self.client,
                self.client.get_transfer_appliance(wait_for_resource_id),
                evaluate_response=lambda r: getattr(r.data, 'lifecycle_state') and getattr(r.data, 'lifecycle_state').lower() in lowered_wait_for_states,
                **waiter_kwargs
            )
            result_to_return = waiter_result

            return result_to_return
        except Exception as e:
            raise oci.exceptions.CompositeOperationError(partial_results=[operation_result], cause=e)

    def update_transfer_appliance_and_wait_for_state(self, id, transfer_appliance_label, update_transfer_appliance_details, wait_for_states=[], operation_kwargs={}, waiter_kwargs={}):
        """
        Calls :py:func:`~oci.dts.TransferApplianceClient.update_transfer_appliance` and waits for the :py:class:`~oci.dts.models.TransferAppliance` acted upon
        to enter the given state(s).

        :param str id: (required)
            ID of the Transfer Job

        :param str transfer_appliance_label: (required)
            Label of the Transfer Appliance

        :param UpdateTransferApplianceDetails update_transfer_appliance_details: (required)
            fields to update

        :param list[str] wait_for_states:
            An array of states to wait on. These should be valid values for :py:attr:`~oci.dts.models.TransferAppliance.lifecycle_state`

        :param dict operation_kwargs:
            A dictionary of keyword arguments to pass to :py:func:`~oci.dts.TransferApplianceClient.update_transfer_appliance`

        :param dict waiter_kwargs:
            A dictionary of keyword arguments to pass to the :py:func:`oci.wait_until` function. For example, you could pass ``max_interval_seconds`` or ``max_interval_seconds``
            as dictionary keys to modify how long the waiter function will wait between retries and the maximum amount of time it will wait
        """
        operation_result = self.client.update_transfer_appliance(id, transfer_appliance_label, update_transfer_appliance_details, **operation_kwargs)
        if not wait_for_states:
            return operation_result

        lowered_wait_for_states = [w.lower() for w in wait_for_states]
        wait_for_resource_id = operation_result.data.id

        try:
            waiter_result = oci.wait_until(
                self.client,
                self.client.get_transfer_appliance(wait_for_resource_id),
                evaluate_response=lambda r: getattr(r.data, 'lifecycle_state') and getattr(r.data, 'lifecycle_state').lower() in lowered_wait_for_states,
                **waiter_kwargs
            )
            result_to_return = waiter_result

            return result_to_return
        except Exception as e:
            raise oci.exceptions.CompositeOperationError(partial_results=[operation_result], cause=e)
