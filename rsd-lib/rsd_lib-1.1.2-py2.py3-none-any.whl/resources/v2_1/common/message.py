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


class MessageCollectionField(base.ListField):

    message_id = base.Field("MessageId")
    """This is the key for this message which can be used to look up the
       message in a message registry.
    """

    message = base.Field("Message")
    """This is the human readable message, if provided."""

    related_properties = base.Field("RelatedProperties")
    """This is an array of properties described by the message."""

    message_args = base.Field("MessageArgs")
    """This array of message arguments are substituted for the arguments in
       the message when looked up in the message registry.
    """

    severity = base.Field("Severity")
    """This is the severity of the errors."""

    resolution = base.Field("Resolution")
    """Used to provide suggestions on how to resolve the situation that caused
       the error.
    """
