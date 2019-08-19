# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for telemetry objects."""
from typing import Any, Dict, Optional

from ._required_fields import RequiredFields
from ._standard_fields import StandardFields

EVENT_SCHEMA_VERSION_KEY = "EventSchemaVersion"
EVENT_SCHEMA_VERSION_VALUE = "0.1"


class TelemetryObjectBase(dict):
    """Base class for telemetry objects."""

    def __init__(self,
                 required_fields: RequiredFields,
                 standard_fields: StandardFields,
                 extension_fields: Optional[Dict[str, Any]] = None,
                 *args: Any, **kwargs: Any):
        """
        Initialize telemetry object base.

        :param required_fields: Required fields for the schema.
        :param standard_fields: Standard fields for the schema.
        :param extension_fields: Extension fields a.k.a Part C.
        """
        super(TelemetryObjectBase, self).__init__(*args, **kwargs)
        self[EVENT_SCHEMA_VERSION_KEY] = EVENT_SCHEMA_VERSION_VALUE
        self.required_fields = required_fields or RequiredFields()
        self.standard_fields = standard_fields or StandardFields()
        self.extension_fields = extension_fields

    def get_all_properties(self):
        """Retrieve all the properties from the metric."""
        properties = {
            EVENT_SCHEMA_VERSION_KEY: EVENT_SCHEMA_VERSION_VALUE
        }

        properties.update(self.required_fields)
        properties.update(self.standard_fields)
        if self.extension_fields and len(self.extension_fields) > 0:
            properties.update(self.extension_fields)
        return properties

    def __str__(self):
        return self.get_all_properties().__str__()
