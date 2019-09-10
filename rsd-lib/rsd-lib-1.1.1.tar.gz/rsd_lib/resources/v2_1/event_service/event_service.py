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
from sushy import utils

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.event_service import event_destination
from rsd_lib import utils as rsd_lib_utils


class EventService(rsd_lib_base.ResourceBase):
    """EventService resource class

       The Event Service resource contains properties for managing event
       subcriptions and generates the events sent to subscribers.  The
       resource has links to the actual collection of subscriptions (called
       Event Destinations).
    """

    service_enabled = base.Field("ServiceEnabled", adapter=bool)
    """This indicates whether this service is enabled."""

    delivery_retry_attempts = base.Field(
        "DeliveryRetryAttempts", adapter=rsd_lib_utils.num_or_none
    )
    """This is the number of attempts an event posting is retried before the
       subscription is terminated.
    """

    delivery_retry_interval_seconds = base.Field(
        "DeliveryRetryIntervalSeconds", adapter=rsd_lib_utils.num_or_none
    )
    """This represents the number of seconds between retry attempts for
       sending any given Event
    """

    event_types_for_subscription = base.Field("EventTypesForSubscription")
    """This is the types of Events that can be subscribed to."""

    status = rsd_lib_base.StatusField("Status")
    """This indicates the known state of the resource, such as if it is
       enabled.
    """

    # TODO(linyang): Add Action Field

    @property
    @utils.cache_it
    def subscriptions(self):
        """Property to provide reference to `EventDestinationCollection` instance

           It is calculated once when it is queried for the first time. On
           refresh, this property is reset.
        """
        return event_destination.EventDestinationCollection(
            self._conn,
            utils.get_sub_resource_path_by(self, "Subscriptions"),
            redfish_version=self.redfish_version,
        )
