# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines classes for collecting structured metrics and events telemetry.

Structured telemetry is collected based on a common schema instead of free text logging of the data. Using a
schema enables easier post-analysis of the data. Metrics and events in a common schema are collected with
:class:`azureml.telemetry.contracts.RequiredFields`, :class:`azureml.telemetry.contracts.StandardFields`,
and :class:`azureml.telemetry.contracts.ExtensionFields`.
"""

from ._telemetry_object_base import TelemetryObjectBase
from ._event import Event
from ._metric import Metric
from ._required_fields import RequiredFields
from ._standard_fields import StandardFields
from ._extension_fields import ExtensionFields

__all__ = [
    'TelemetryObjectBase',
    'Event',
    'Metric',
    'RequiredFields',
    'StandardFields',
    'ExtensionFields'
]
