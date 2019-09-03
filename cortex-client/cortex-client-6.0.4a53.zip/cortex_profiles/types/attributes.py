from enum import auto, unique
from typing import List, Union, Optional

import attr
from attr import attrs, validators, Factory

from cortex_profiles.schemas.schemas import CONTEXTS, VERSION
from cortex_profiles.types.attribute_values import BaseAttributeValue
from cortex_profiles.types.attribute_values import ProfileAttributeValue
from cortex_profiles.types.attribute_values import load_profile_attribute_value_from_dict
from cortex_profiles.types.utils import describableAttrib, CONTEXT_DESCRIPTION, ID_DESCRIPTION, VERSION_DESCRIPTION
from cortex_profiles.utils import unique_id, converter_for_classes, EnumWithNamesAsDefaultValue, utc_timestamp, \
    attr_instance_to_dict

ATTRIBUTE_KEY_DESCRIPTION = "What is the unqiue key for the attribute that distinguishes from the rest of the attributes captured w.r.t the profile?"

@unique
class ProfileAttributeClassifications(EnumWithNamesAsDefaultValue):
    inferred = auto()
    declared = auto()
    observed = auto()
    assigned = auto()


@attrs(frozen=True)
class BaseProfileAttribute(object):
    """
    General representation of an attribute in a profile.
    """
    profileId = describableAttrib(type=str, description="Which profile is the attribute applicable to?")
    attributeKey = describableAttrib(type=str, description=ATTRIBUTE_KEY_DESCRIPTION)
    attributeValue = describableAttrib(
        type=ProfileAttributeValue,
        validator=[validators.instance_of(BaseAttributeValue)],
        converter=lambda x: converter_for_classes(x, BaseAttributeValue, dict_constructor=load_profile_attribute_value_from_dict),
        description="What value is captured by the attribute?"
    )
    context = describableAttrib(type=str, description=CONTEXT_DESCRIPTION)
    # With Defaults
    createdAt = describableAttrib(type=str, factory=utc_timestamp, description="When was this attribute created?")
    tenantId = describableAttrib(type=Optional[str], default=None, description="What tenant does this attribute reside within?", internal=True)
    environmentId = describableAttrib(type=Optional[str], default=None, description="What environment does this attribute reside within?", internal=True)
    onLatestProfile = describableAttrib(type=bool, default=True, description="Is this attribute on the latest profile?", internal=True)
    commits = describableAttrib(type=List[str], factory=list, description="What commits is this attribute associated with?", internal=True)
    id = describableAttrib(type=str, default=Factory(unique_id), description=ID_DESCRIPTION)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION, internal=True)

    def __iter__(self):
        return iter(attr_instance_to_dict(self, hide_internal_attributes=True).items())


@attrs(frozen=True)
class InferredProfileAttribute(BaseProfileAttribute):
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.inferred.name, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=CONTEXTS.INFERRED_PROFILE_ATTRIBUTE, description=CONTEXT_DESCRIPTION)


@attrs(frozen=True)
class ObservedProfileAttribute(BaseProfileAttribute):
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.observed.name, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE, description=CONTEXT_DESCRIPTION)


@attrs(frozen=True)
class DeclaredProfileAttribute(BaseProfileAttribute):
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.declared.name, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=CONTEXTS.DECLARED_PROFILE_ATTRIBUTE, description=CONTEXT_DESCRIPTION)


@attrs(frozen=True)
class AssignedProfileAttribute(BaseProfileAttribute):
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.assigned.name, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=CONTEXTS.ASSIGNED_PROFILE_ATTRIBUTE, description=CONTEXT_DESCRIPTION)

# ProfileAttribute = Union[InferredProfileAttribute, DeclaredProfileAttribute, ObservedProfileAttribute]
# ProfileAttributeKinds = Union[
#     PercentageAttributeContent,
#     CounterAttributeContent,
#     DimensionalAttributeContent,
#     MultiDimensionalAttributeContent
# ]


ProfileAttributeTypes = (DeclaredProfileAttribute, ObservedProfileAttribute, InferredProfileAttribute, AssignedProfileAttribute)
ProfileAttribute: type = Union[ProfileAttributeTypes]


def load_profile_attribute_from_dict(d: dict) -> Optional[ProfileAttribute]:
    """
    Uses the context to load the appropriate profile attribute from a dict.
    :param d:
    :return:
    """
    context_to_attribute_type = {
        attr.fields(x).context.default: x
        for x in ProfileAttributeTypes
    }
    attribute_type_to_use = context_to_attribute_type.get(d.get("context"), None)
    if attribute_type_to_use is None:
        return None
    return attribute_type_to_use(**d)
