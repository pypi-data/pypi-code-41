# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Required fields in the logging schema. a.k.a Part A."""
from typing import Any, List

import uuid
from datetime import datetime


class RequiredFieldsKeys:
    """Keys for required fields."""

    CLIENT_SESSION_ID_KEY = 'ClientSessionId'
    CLIENT_TYPE_KEY = 'ClientType'
    CLIENT_VERSION_KEY = 'ClientVersion'
    COMPONENT_TYPE_KEY = 'ComponentType'
    CORRELATION_ID_KEY = 'CorrelationId'
    EVENT_ID_KEY = 'EventId'
    EVENT_TIME_KEY = 'EventTime'
    SUBSCRIPTION_ID_KEY = 'SubscriptionId'
    WORKSPACE_ID_KEY = 'WorkspaceId'

    @classmethod
    def keys(cls) -> List[str]:
        """Keys for required fields."""
        return [
            RequiredFieldsKeys.CLIENT_SESSION_ID_KEY,
            RequiredFieldsKeys.CLIENT_TYPE_KEY,
            RequiredFieldsKeys.CLIENT_VERSION_KEY,
            RequiredFieldsKeys.COMPONENT_TYPE_KEY,
            RequiredFieldsKeys.CORRELATION_ID_KEY,
            RequiredFieldsKeys.EVENT_ID_KEY,
            RequiredFieldsKeys.EVENT_TIME_KEY,
            RequiredFieldsKeys.SUBSCRIPTION_ID_KEY,
            RequiredFieldsKeys.WORKSPACE_ID_KEY
        ]


class RequiredFields(dict):
    """Required fields in the logging schema. a.k.a Part A."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize a new instance of the RequiredFields."""
        super(RequiredFields, self).__init__(*args, **kwargs)
        self[RequiredFieldsKeys.EVENT_ID_KEY] = str(uuid.uuid4())
        self[RequiredFieldsKeys.EVENT_TIME_KEY] = str(datetime.utcnow())

    @property
    def client_session_id(self):
        """Client session id."""
        return self.get(RequiredFieldsKeys.CLIENT_SESSION_ID_KEY, None)

    @client_session_id.setter
    def client_session_id(self, value):
        """Set Client session id."""
        self[RequiredFieldsKeys.CLIENT_SESSION_ID_KEY] = value

    @property
    def client_type(self):
        """Client session id."""
        return self.get(RequiredFieldsKeys.CLIENT_TYPE_KEY, None)

    @client_type.setter
    def client_type(self, value):
        """Set Client session id."""
        self[RequiredFieldsKeys.CLIENT_TYPE_KEY] = value

    @property
    def client_version(self):
        """Client Type."""
        return self.get(RequiredFieldsKeys.CLIENT_VERSION_KEY, None)

    @client_version.setter
    def client_version(self, value):
        """Set Client Type."""
        self[RequiredFieldsKeys.CLIENT_VERSION_KEY] = value

    @property
    def component_type(self):
        """Client Type."""
        return self.get(RequiredFieldsKeys.COMPONENT_TYPE_KEY, None)

    @component_type.setter
    def component_type(self, value):
        """Set Client Type."""
        self[RequiredFieldsKeys.COMPONENT_TYPE_KEY] = value

    @property
    def correlation_id(self):
        """Client session id."""
        return self.get(RequiredFieldsKeys.CORRELATION_ID_KEY, None)

    @correlation_id.setter
    def correlation_id(self, value):
        """Set Client session id."""
        self[RequiredFieldsKeys.CORRELATION_ID_KEY] = value

    @property
    def event_id(self):
        """Event Name."""
        return self.get(RequiredFieldsKeys.EVENT_ID_KEY, None)

    @event_id.setter
    def event_id(self, value):
        """Set Event Name."""
        self[RequiredFieldsKeys.EVENT_ID_KEY] = value

    @property
    def subscription_id(self):
        """Subscription Id."""
        return self.get(RequiredFieldsKeys.SUBSCRIPTION_ID_KEY, None)

    @subscription_id.setter
    def subscription_id(self, value):
        """Set Subscription Id."""
        self[RequiredFieldsKeys.SUBSCRIPTION_ID_KEY] = value

    @property
    def workspace_id(self):
        """Workspace Id."""
        return self.get(RequiredFieldsKeys.WORKSPACE_ID_KEY, None)

    @workspace_id.setter
    def workspace_id(self, value):
        """Set Workspace Id."""
        self[RequiredFieldsKeys.WORKSPACE_ID_KEY] = value
