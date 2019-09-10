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

from sushy.resources import base

from rsd_lib import base as rsd_lib_base
from rsd_lib.resources.v2_1.event_service import schemas \
    as event_service_schemas


LOG = logging.getLogger(__name__)


class HttpHeaderPropertyCollectionField(base.ListField):
    """HttpHeaderProperty field

       The value of the HTTP header is the property value.  The header name is
       the property name.
    """

    pattern = base.Field("Pattern")

    type = base.Field("Type")


class EventDestination(rsd_lib_base.ResourceBase):
    """EventDestination resource class

       An Event Destination desribes the target of an event subscription,
       including the types of events subscribed and context to provide to the
       target in the Event payload.
    """

    destination = base.Field("Destination")
    """The URI of the destination Event Service."""

    event_types = base.Field("EventTypes")
    """This property shall contain the types of events that shall be sent to
       the desination.
    """

    context = base.Field("Context")
    """A client-supplied string that is stored with the event destination
       subscription.
    """

    protocol = base.Field("Protocol")
    """The protocol type of the event connection."""

    http_headers = HttpHeaderPropertyCollectionField("HttpHeaders")
    """This is for setting HTTP headers, such as authorization information.
       This object will be null on a GET.
    """

    message_ids = base.Field("MessageIds")
    """A list of MessageIds that the service will only send."""

    def delete(self):
        """Delete this event subscription"""
        self._conn.delete(self._path)


class EventDestinationCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return EventDestination

    def create_event_subscription(self, event_subscription_req):
        """Create a new event subscription

        :param event_subscription_req: JSON for event subscription
        :returns: The uri of the new event subscription
        """
        target_uri = self._path

        validate(
            event_subscription_req,
            event_service_schemas.event_subscription_req_schema,
        )

        resp = self._conn.post(target_uri, data=event_subscription_req)
        event_subscription_url = resp.headers["Location"]
        LOG.info("event subscription created at %s", event_subscription_url)

        return event_subscription_url[
            event_subscription_url.find(self._path):
        ]
