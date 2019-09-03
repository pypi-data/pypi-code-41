import json
from functools import total_ordering
from typing import List, Union, Optional

import attr
import arrow
import numpy as np
import pandas as pd
import pydash
from attr import attrs, fields

from cortex_profiles.schemas.schemas import CONTEXTS, VERSION
from cortex_profiles.types.insights import Insight
from cortex_profiles.types.schema import ProfileValueTypeSummary
from cortex_profiles.types.utils import describableAttrib, CONTEXT_DESCRIPTION, VERSION_DESCRIPTION, \
    ATTRIBUTE_SUMMARY_DESCRIPTION
from cortex_profiles.types.utils import str_or_context
from cortex_profiles.utils import converter_for_list_of_classes, converter_for_union_type, union_type_validator, \
    converter_for_classes, unique_id

# Bool is getting consumes by the union since it is a subclass of int ...

PrimitiveJSONTypes = (str, int, float, bool, type(None))
PrimitiveJSONUnionType = Union[PrimitiveJSONTypes]
PrimitiveJSONTypeHandlers = pydash.merge(dict(zip(PrimitiveJSONTypes[:-1], PrimitiveJSONTypes[:-1])), {type(None): lambda x: None})

ObjectJSONTypes = (dict, type(None))
ObjectJSONUnionType = Union[ObjectJSONTypes]
ObjectJSONTypeHandlers = pydash.merge(dict(zip(ObjectJSONTypes[:-1], ObjectJSONTypes[:-1])), {type(None): lambda x: None})

ListJSONTypes = (list, type(None))
ListJSONUnionType = Union[ListJSONTypes]
ListJSONTypeHandlers = pydash.merge(dict(zip(ListJSONTypes[:-1], ListJSONTypes[:-1])), {type(None): lambda x: None})

JSONUnionTypes = Union[str, int, float, bool, type(None), dict, list]


@attrs(frozen=True)
class BaseAttributeValue(object):
    """
    Interface Attribute Values Need to Adhere to ...
    """
    value = describableAttrib(type=object, description="What value is captured in the attribute?")
    context = describableAttrib(type=str, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @classmethod
    def detailed_schema_type(cls) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(
            outerType=fields(cls).context.default,
            innerTypes=[]
        )


# - [ ] Do we put versions on everything ... even it its meant to be nested? or only stuff saved in db?
@attrs(frozen=True)
class Dimension(object):
    """
    Representing a single dimension in a dimensional attribute ...
    """
    dimensionId = describableAttrib(type=str, description="What entity does this dimension represent?")
    dimensionValue = describableAttrib(type=Union[str, list, dict, int, bool, float], description="What is the value of this dimension?")


@attrs(frozen=True)
class StringAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary string as their value
    """
    value = describableAttrib(type=str, default="", description="What is the value of the string itself?")
    context = describableAttrib(type=str, default=CONTEXTS.STRING_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return json.dumps(self.value)


@attrs(frozen=True)
class DecimalAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary decimal number as their value
    """
    value = describableAttrib(type=float, default=0.0, description="What is the value of the decimal number itself?")
    context = describableAttrib(type=str, default=CONTEXTS.DECIMAL_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return json.dumps(self.value)


@attrs(frozen=True)
class BooleanAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary boolean as their value
    """
    value = describableAttrib(type=bool, default=True, description="What is the value of the boolean itself?")
    context = describableAttrib(type=str, default=CONTEXTS.BOOLEAN_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return json.dumps(self.value)


@attrs(frozen=True)
class IntegerAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary integer number as their value
    """
    value = describableAttrib(type=int, default=0, description="What is the value of the integer number itself?")
    context = describableAttrib(type=str, default=CONTEXTS.INTEGER_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return json.dumps(self.value)


# @attrs(frozen=True)
# class PrimitiveAttributeValue(BaseAttributeValue):
#     """
#     Attributes that have an arbitrary JSON Object / Map / Hash as their value
#     """
#     value = describableAttrib(
#         type=PrimitiveJSONUnionType,
#         validator=union_type_validator(PrimitiveJSONUnionType),
#         converter=converter_for_union_type(PrimitiveJSONUnionType, PrimitiveJSONTypeHandlers),
#         description="What is the value of the object itself?")
#     context = describableAttrib(type=str, default=CONTEXTS.PRIMITIVE_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
#     version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
#     summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
#
#     @summary.default
#     def summarize(self):
#         return json.dumps(self.value)


# @attrs(frozen=True)
# class ObjectAttributeValue(BaseAttributeValue):
#     """
#     Attributes that have an arbitrary JSON Object / Map / Hash as their value
#     """
#     value = describableAttrib(
#         type=ObjectJSONUnionType,
#         validator=union_type_validator(ObjectJSONUnionType),
#         factory=dict,
#         converter=converter_for_union_type(ObjectJSONUnionType, ObjectJSONTypeHandlers),
#         description="What is the value of the object itself?")
#     context = describableAttrib(type=str, default=CONTEXTS.OBJECT_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
#     version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
#     summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
#
#     @summary.default
#     def summarize(self):
#         return json.dumps(self.value)


@attrs(frozen=True)
class ListAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary JSON List / Array as their value.
    """
    value = describableAttrib(
        type=ListJSONUnionType,
        validator=union_type_validator(ListJSONUnionType),
        factory=list,
        converter=converter_for_union_type(ListJSONUnionType, ListJSONTypeHandlers),
        description="What is the value of the object itself?")
    context = describableAttrib(type=str, default=CONTEXTS.LIST_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        template = "{} items exist within the list."
        if self.value is None:
            return template.format(0)
        return template.format(len(self.value))

    @classmethod
    def detailed_schema_type(cls, typeOfItems:Optional[Union[str,type]]=None) -> ProfileValueTypeSummary:
        innerTypes = [] if typeOfItems is None else [
            ProfileValueTypeSummary(outerType=str_or_context(typeOfItems))
        ]
        return ProfileValueTypeSummary(
            outerType = fields(cls).context.default,
            innerTypes = innerTypes
        )


@attrs(frozen=True)
class RelationshipAttributeValue(BaseAttributeValue):
    """
    Representing the content of a percentage attribute ...
    """
    value = describableAttrib(type=str, description="What is the id of the related concept to the profile?")
    relatedConceptType = describableAttrib(type=str, description="What is the type of the related concept?")
    relationshipType = describableAttrib(type=str, description="How is the related concept related to the profile? What is the type of relationship?")
    relationshipTitle = describableAttrib(type=str, description="What is a short, human readable description of the relationship between the profile and the related concept?")
    relatedConceptTitle = describableAttrib(type=str, description="What is a short, human readable description of the related concept to the profile?")
    relationshipProperties = describableAttrib(type=dict, factory=dict, description="What else do we need to know about the relationship?")
    context = describableAttrib(type=str, default=CONTEXTS.RELATIONSHIP_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return "Profile-{}->{}".format(self.relationshipTitle, self.relatedConceptTitle)


@attrs(frozen=True)
class NumericAttributeValue(BaseAttributeValue):
    """
    Representing the content of a numeric attribute ...
    """
    value = describableAttrib(type=Union[int, float], description="What is the number that we are interested in?")
    context = describableAttrib(type=str, default=CONTEXTS.NUMERICAL_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return "{:.3f}".format(self.value)


@attrs(frozen=True)
@total_ordering
class NumericWithUnitValue(NumericAttributeValue):
    """
    Representing the content of a numeric attribute as a measuring unit ...
    """
    value = describableAttrib(type=Union[int, float], default=0, description="What numeric value is captured by this attribute value?")
    unitId = describableAttrib(type=str, default=None, description="What is the unique id of the unit? i.e USD, GBP, %, ...")
    unitContext = describableAttrib(type=str, default=None, description="What type of unit is this? i.e currency, population of country, ...")
    unitTitle = describableAttrib(type=str, default=None, description="What is the symbol desired to represent the unit?")
    unitIsPrefix = describableAttrib(type=bool, default=False, description="Should the symbol be before or after the unit?")

    def __eq__(self, other):
        if other is None:
            return False
        return (self.value == other.value)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.value < other.value


@attrs(frozen=True)
class PercentileAttributeValue(NumericAttributeValue):
    """
    Representing the content of a percentile attribute ...
    """
    value = describableAttrib(type=float, description="What is the numeric value of the percentile?")
    context = describableAttrib(type=str, default=CONTEXTS.PERCENTILE_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return "{:.3f}%%".format(self.value)


@attrs(frozen=True)
class PercentageAttributeValue(NumericAttributeValue):
    """
    Representing the content of a percentage attribute ...
    """
    value = describableAttrib(type=float, description="What numeric value of the percentage?")
    context = describableAttrib(type=str, default=CONTEXTS.PERCENTAGE_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
    @summary.default
    def summarize(self):
        return "{:.2f}%".format(self.value)


# @attrs(frozen=True)
# class AverageAttributeValue(NumericAttributeValue):
#     """
#     Representing the content of a percentage attribute ...
#     """
#     value = describableAttrib(type=float, description="What numeric value of the average?")
#     context = describableAttrib(type=str, default=CONTEXTS.AVERAGE_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
#     version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
#     summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
#     @summary.default
#     def summarize(self):
#         return "Avg: {:.3f}".format(self.value)


@attrs(frozen=True)
class StatisticalSummaryValue(object):
    datapoints = describableAttrib(type=int, default=0, description="How many datapoints were considered?")
    min = describableAttrib(type=Optional[float], default=None, description="What is the minimum value considered in the data points?")
    max = describableAttrib(type=Optional[float], default=None, description="What is the maximum value considered in the data points?")
    average = describableAttrib(type=Optional[float], default=None, description="What is the average of the data points?")
    stddev = describableAttrib(type=Optional[float], default=None, description="What is the std deviation of the data points?")


def numpy_type_to_python_type(value):
    return int(value) if isinstance(value, (int, np.integer)) else (
        float(value) if isinstance(value, (float, np.floating)) else value
    )


@attrs(frozen=True)
class StatisticalSummaryAttributeValue(BaseAttributeValue):
    """
    Representing the content of a percentage attribute ...
    """
    value = describableAttrib(
        type=StatisticalSummaryValue,
        converter=lambda x: converter_for_classes(x, StatisticalSummaryValue),
        description="What is the statistical summary for a given range of data?"
    )
    context = describableAttrib(type=str, default=CONTEXTS.STATISTICAL_SUMMARY_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return "{:.3f} points: {:.3f}..{:.3f}..{:.3f}".format(
            self.value.datapoints, self.value.min, self.value.average, self.value.max
        )

    @staticmethod
    def fromListOfValues(values:List[Union[int, float]]) -> 'StatisticalSummaryAttributeValue' :
        return StatisticalSummaryAttributeValue(
            value=StatisticalSummaryValue(
                datapoints=numpy_type_to_python_type(np.size(values)),
                min=numpy_type_to_python_type(np.min(values)),
                max=numpy_type_to_python_type(np.max(values)),
                average=numpy_type_to_python_type(np.average(values)),
                stddev=numpy_type_to_python_type(np.std(values)),
            )
        )


@attrs(frozen=True)
class CounterAttributeValue(NumericWithUnitValue):
    """
    Representing the content of a counter attribute ...
    """
    value = describableAttrib(type=int, default=0, description="What is the numeric value of the current total?")
    context = describableAttrib(type=str, default=CONTEXTS.COUNTER_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
    @summary.default
    def summarize(self):
        return "{}{}{}".format(
            ("{} ".format(self.unitTitle) if (self.unitIsPrefix and self.unitTitle) else ""),
            ("{}".format(self.value)),
            (" {}".format(self.unitTitle) if (self.unitTitle and not self.unitIsPrefix) else "")
        )


@attrs(frozen=True)
class TotalAttributeValue(NumericWithUnitValue):
    """
    Representing the content of a total attribute ...
    """
    value = describableAttrib(type=float, default=0.0, description="What is the current total?")
    context = describableAttrib(type=str, default=CONTEXTS.TOTAL_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
    @summary.default
    def summarize(self):
        return "{}{}{}".format(
            ("{} ".format(self.unitTitle) if (self.unitIsPrefix and self.unitTitle) else ""),
            ("{:.3f}".format(self.value)),
            (" {}".format(self.unitTitle) if (self.unitTitle and not self.unitIsPrefix) else "")
        )

#
# @attrs(frozen=True)
# class ConceptAttributeValue(BaseAttributeValue):
#     """
#     Representing a concept ...
#     """
#     value = describableAttrib(type=str, description="What is the name of the concept?")
#     context = describableAttrib(type=str, default=CONTEXTS.CONCEPT_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
#     version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
#     summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)
#
#     @summary.default
#     def summarize(self):
#         return self.value


@attrs(frozen=True)
class DimensionalAttributeValue(BaseAttributeValue):
    """
    Representing the content of a 2-dimensional attribute.
    """

    value = describableAttrib(
        type=List[Dimension],
        converter=lambda x: converter_for_list_of_classes(x, Dimension),
        description="What are the different dimensions captured in the attribute value?"
    )
    contextOfDimension = describableAttrib(type=str, description="What type are the dimensions?")
    contextOfDimensionValue = describableAttrib(type=str, description="What type are the values associated with the dimension?")
    context = describableAttrib(type=str, default=CONTEXTS.DIMENSIONAL_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        average = None
        max = None
        min = None
        # TODO ... right now the value ... is just a value ... not an NumericAttributeValue ...
        # if all(map(lambda x: isinstance(x.dimensionValue, NumericAttributeValue), self.value)):
        #     average = np.mean(list(map(lambda x: x.dimensionValue.value, self.value)))
        #     max = np.max(list(map(lambda x: x.dimensionValue.value, self.value)))
        #     min = np.min(list(map(lambda x: x.dimensionValue.value, self.value)))
        # print(list(map(lambda x: x.dimensionValue, self.value)))
        # print(list(map(lambda x: isinstance(x.dimensionValue, (int, float)), self.value)))
        if all(map(lambda x: isinstance(x.dimensionValue, (int, float)), self.value)):
            average = np.mean(list(map(lambda x: x.dimensionValue, self.value)))
            max = np.max(list(map(lambda x: x.dimensionValue, self.value)))
            min = np.min(list(map(lambda x: x.dimensionValue, self.value)))
        return "{}{}{}{}".format(
            ("Dimensions: {}".format(len(self.value))),
            (", Avg: {:.3f}".format(average) if average else ""),
            (", Min: {:.3f}".format(min) if min else ""),
            (", Max: {:.3f}".format(max) if max else "")
        )

    @classmethod
    def detailed_schema_type(cls, firstDimensionType:Union[str,type], secondDimensionType:Union[str,type]) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(
            outerType = fields(cls).context.default,
            innerTypes = [
                ProfileValueTypeSummary(outerType=str_or_context(firstDimensionType)),
                ProfileValueTypeSummary(outerType=str_or_context(secondDimensionType))
            ]
        )


@attrs(frozen=True)
class WeightedAttributeValue(BaseAttributeValue):
    """
    Attributes that captures a weighted value.
    """
    value = describableAttrib(type=dict, factory=dict, description="What is the value of the weighted object?")
    weight = describableAttrib(type=float, default=1.00, description="How likely is it beleived that this value encapsulates reality?")
    context = describableAttrib(type=str, default=CONTEXTS.WEIGHTED_PROFILE_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return json.dumps(self.value)

    @classmethod
    def detailed_schema_type(cls, type_of_weighted_value:Union[str,type]) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(
            outerType = fields(cls).context.default,
            innerTypes = [
                ProfileValueTypeSummary(outerType=str_or_context(type_of_weighted_value)),
            ]
        )


@attrs(frozen=True)
class InsightAttributeValue(BaseAttributeValue):
    """
    Representing a concept ...
    """
    value = describableAttrib(type=Insight, converter=lambda x: converter_for_classes(x, Insight), description="What is the insight itself?")
    context = describableAttrib(type=str, default=CONTEXTS.INSIGHT_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        return "Insight<type={},id={}>\"".format(self.value.insightType, self.value.id)


def time_converter(time:Union[str,arrow.arrow.Arrow]) -> Optional[int]:
    """
    Converts a time into an epoch with millisecond resolution.
    :param time:
    :return:
    """
    # Assumption that its a utc timestamp ...
    if isinstance(time, (str)):
        return arrow.get(time).timestamp * 1000
    elif isinstance(time, (arrow.arrow.Arrow)):
        return time.timestamp * 1000
    elif isinstance(time, pd.Timestamp):
        return time.timestamp() * 1000
    else:
        print("{} type not yet supported for time_converter".format(type(time)))
        print(time)
    return None


@attrs(frozen=True)
class EntityEvent(object):
    """
    Representing an Event that Modifies a representation of an Entity.
    """
    event = describableAttrib(type=Optional[str], default=None, description="What is the name of the event?")
    entityId = describableAttrib(type=Optional[str], default=None, description="Does this event relate an entity to another entity?")
    entityType = describableAttrib(type=Optional[str], default=None, description="What is the type of the entity?")
    properties = describableAttrib(type=dict, factory=dict, description="What are the properties associated with this event?")
    meta = describableAttrib(type=dict, factory=dict, description="What is custom metadata associated with this event?")
    # With Defaults ...
    targetEntityId = describableAttrib(type=Optional[str], default=None, description="Does this event relate an entity to another entity?")
    targetEntityType = describableAttrib(type=Optional[str], default=None, description="What is the type of entity this event relates to?")
    eventLabel = describableAttrib(type=Optional[str], default=None, description="What is the name of the event?")
    eventTime = describableAttrib(
        type=Optional[int],
        default=None,  # The timestamp used in node is 1k times the arrow timestamp.
        converter=time_converter,
        description="When did the event occur?"
    )
    eventId = describableAttrib(type=Optional[str], factory=unique_id, description="What is id for this event?")
    triggerId = describableAttrib(type=Optional[str], factory=unique_id, description="What is id of the occurrence that triggered this event?")


@attrs(frozen=True)
class EntityAttributeValue(BaseAttributeValue):
    """
    Representing a concept ...
    """
    value = describableAttrib(type=EntityEvent, factory=dict, converter=lambda x: converter_for_classes(x, EntityEvent), description="What are the properties of the entity?")
    context = describableAttrib(type=str, default=CONTEXTS.ENTITY_ATTRIBUTE_VALUE, description=CONTEXT_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION)
    summary = describableAttrib(type=str, description=ATTRIBUTE_SUMMARY_DESCRIPTION)

    @summary.default
    def summarize(self):
        if self.value.targetEntityId is None:
            return "{}[{}]".format(self.value.entityType, self.value.entityId)
        return "{}[{}] -[{}]-> {}[{}]".format(
            self.value.entityType, self.value.entityId,
            self.value.event,
            self.value.targetEntityType, self.value.targetEntityId,
        )

# class PlacementAttributeContent 1st, 2nd, 3rd ...
# class {Rank/Score}AttributeContent

# TODO : Rename the attribute values ... some are AttributeContent and Some are AttributeVlaue ...


ProfileAttributeValueTypes = (
    StringAttributeValue,
    DecimalAttributeValue,
    BooleanAttributeValue,
    IntegerAttributeValue,
    # PrimitiveAttributeValue,
    # ObjectAttributeValue,
    ListAttributeValue,
    RelationshipAttributeValue,
    PercentileAttributeValue,
    PercentageAttributeValue,
    # AverageAttributeValue,
    CounterAttributeValue,
    TotalAttributeValue,
    # ConceptAttributeValue,
    DimensionalAttributeValue,
    WeightedAttributeValue,
    InsightAttributeValue,
    EntityAttributeValue,
    StatisticalSummaryAttributeValue,
)


ProfileAttributeValue = Union[ProfileAttributeValueTypes]


def load_profile_attribute_value_from_dict(d:dict) -> Optional[BaseAttributeValue]:
    """
    Uses the context to load the appropriate profile attribute value type from a dict.
    :param d:
    :return:
    """
    context_to_value_type = {
        attr.fields(x).context.default: x
        for x in ProfileAttributeValueTypes
    }
    value_type_to_use = context_to_value_type.get(d.get("context"), None)
    if value_type_to_use is None:
        return None
    return value_type_to_use(**d)