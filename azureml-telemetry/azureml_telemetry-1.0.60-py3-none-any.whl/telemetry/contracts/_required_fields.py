# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines Part A of the logging schema, keys that have a common meaning across telemetry data."""
from typing import Any, List

import uuid
from datetime import datetime


class RequiredFieldsKeys:
    """Keys for required fields."""

    CLIENT_SESSION_ID_KEY = 'ClientSessionId'
    CLIENT_TYPE_KEY = 'ClientType'
    CLIENT_VERSION_KEY = 'ClientVersion'
    COMPONENT_NAME_KEY = 'ComponentName'
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
            RequiredFieldsKeys.COMPONENT_NAME_KEY,
            RequiredFieldsKeys.CORRELATION_ID_KEY,
            RequiredFieldsKeys.EVENT_ID_KEY,
            RequiredFieldsKeys.EVENT_TIME_KEY,
            RequiredFieldsKeys.SUBSCRIPTION_ID_KEY,
            RequiredFieldsKeys.WORKSPACE_ID_KEY
        ]


class RequiredFields(dict):
    """Defines Part A of the logging schema, keys that have a common meaning across telemetry data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize a new instance of the RequiredFields."""
        super(RequiredFields, self).__init__(*args, **kwargs)
        self[RequiredFieldsKeys.EVENT_ID_KEY] = str(uuid.uuid4())
        self[RequiredFieldsKeys.EVENT_TIME_KEY] = str(datetime.utcnow())

    @property
    def client_session_id(self):
        """Client session ID."""
        return self.get(RequiredFieldsKeys.CLIENT_SESSION_ID_KEY, None)

    @client_session_id.setter
    def client_session_id(self, value):
        """Set client session ID."""
        self[RequiredFieldsKeys.CLIENT_SESSION_ID_KEY] = value

    @property
    def client_type(self):
        """Client session ID."""
        return self.get(RequiredFieldsKeys.CLIENT_TYPE_KEY, None)

    @client_type.setter
    def client_type(self, value):
        """Set client session ID."""
        self[RequiredFieldsKeys.CLIENT_TYPE_KEY] = value

    @property
    def client_version(self):
        """Client version."""
        return self.get(RequiredFieldsKeys.CLIENT_VERSION_KEY, None)

    @client_version.setter
    def client_version(self, value):
        """Set client version."""
        self[RequiredFieldsKeys.CLIENT_VERSION_KEY] = value

    @property
    def component_name(self):
        """Client component name."""
        return self.get(RequiredFieldsKeys.COMPONENT_NAME_KEY, None)

    @component_name.setter
    def component_name(self, value):
        """Set component name."""
        self[RequiredFieldsKeys.COMPONENT_NAME_KEY] = value

    @property
    def correlation_id(self):
        """Correlation ID."""
        return self.get(RequiredFieldsKeys.CORRELATION_ID_KEY, None)

    @correlation_id.setter
    def correlation_id(self, value):
        """Set correlation ID."""
        self[RequiredFieldsKeys.CORRELATION_ID_KEY] = value

    @property
    def event_id(self):
        """Event ID."""
        return self.get(RequiredFieldsKeys.EVENT_ID_KEY, None)

    @event_id.setter
    def event_id(self, value):
        """Set event ID."""
        self[RequiredFieldsKeys.EVENT_ID_KEY] = value

    @property
    def subscription_id(self):
        """Subscription ID."""
        return self.get(RequiredFieldsKeys.SUBSCRIPTION_ID_KEY, None)

    @subscription_id.setter
    def subscription_id(self, value):
        """Set subscription ID."""
        self[RequiredFieldsKeys.SUBSCRIPTION_ID_KEY] = value

    @property
    def workspace_id(self):
        """Workspace ID."""
        return self.get(RequiredFieldsKeys.WORKSPACE_ID_KEY, None)

    @workspace_id.setter
    def workspace_id(self, value):
        """Set workspace ID."""
        self[RequiredFieldsKeys.WORKSPACE_ID_KEY] = value
