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

from rsd_lib import base as rsd_lib_base
from rsd_lib import utils as rsd_lib_utils


class DiscreteTriggerConditionCollectionField(base.ListField):

    name = base.Field("Name")
    """The name of trigger."""

    trigger_value = base.Field("TriggerValue")
    """This property contains the value that sets a trigger."""

    previous_value = base.Field("PreviousValue")
    """This property contains the previous value of the trigger."""


class NumericTriggerConditionCollectionField(base.ListField):

    name = base.Field("Name")
    """The name of trigger."""

    value = base.Field("Value", adapter=rsd_lib_utils.num_or_none)
    """This property contains the value of the trigger."""

    direction_of_crossing = base.Field("DirectionOfCrossing")
    """This property contains the direction that the previous value came from.
    """


class TriggerConditionField(base.CompositeField):
    """TriggerCondition field

       A trigger condition.
    """

    dwell_interval = base.Field("DwellInterval")
    """The time in the triggering state before the trigger is invoked."""

    trigger_type = base.Field("TriggerType")
    """The type of trigger."""

    discrete_trigger_conditions = DiscreteTriggerConditionCollectionField(
        "DiscreteTriggerConditions"
    )
    """A Trigger condition based on TriggerDiscreteCondition."""

    filter_trigger_condition = base.Field("FilterTriggerCondition")
    """A filter on the elements specified by OriginResources."""

    numeric_trigger_conditions = NumericTriggerConditionCollectionField(
        "NumericTriggerConditions"
    )
    """A Trigger condition based on TriggerNumericCondition."""


class Metric(rsd_lib_base.ResourceBase):
    """Metric resource class

       Defines the use of a set of properties as metrics.
    """

    metric_properties = base.Field("MetricProperties")
    """A collection of URI for the properties on which this metric is
       collected.
    """

    collection_function = base.Field("CollectionFunction")
    """Function to perform over each sample."""

    collection_duration = base.Field("CollectionDuration")
    """The value is the collection duration for each metric value."""

    trigger_condition = TriggerConditionField("TriggerCondition")
    """A Triggering condition for the event."""
