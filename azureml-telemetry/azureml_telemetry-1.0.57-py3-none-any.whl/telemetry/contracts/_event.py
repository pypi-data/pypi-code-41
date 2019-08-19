# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Event for telemetry."""
from typing import Any, Optional

from ._telemetry_object_base import TelemetryObjectBase
from ._required_fields import RequiredFields
from ._standard_fields import StandardFields
from ._extension_fields import ExtensionFields


class Event(TelemetryObjectBase):
    """
    Event object for telemetry usage.

    :param name: Name of the event.
    :type name: str
    :param required_fields: Required fields for the schema.
    :type required_fields: azureml.telemetry.contracts.RequiredFields
    :param standard_fields: Standard fields for the schema.
    :type standard_fields: azureml.telemetry.contracts.StandardFields
    :param extension_fields: Extension fields a.k.a Part C.
    :type extension_fields: azureml.telemetry.contracts.ExtensionFields
    """

    def __init__(self, name: str, required_fields: Optional[RequiredFields] = None,
                 standard_fields: Optional[StandardFields] = None,
                 extension_fields: Optional[ExtensionFields] = None,
                 *args: Any, **kwargs: Any):
        """
        Initialize a new instance of the Event.

        :param name: Name of the event.
        :param required_fields: Required fields for the schema.
        :param standard_fields: Standard fields for the schema.
        :param extension_fields: Extension fields a.k.a Part C.
        """
        super(Event, self).__init__(required_fields, standard_fields, extension_fields, *args, **kwargs)
        self.name = name
