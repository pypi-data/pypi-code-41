from typing import List, Union
from collections import Counter
import pandas as pd

from cortex_profiles.builders.attributes.utils import implicit_attribute_builder_utils
from cortex_profiles import utils
from cortex_profiles.schemas.schemas import UNIVERSAL_ATTRIBUTES, TIMEFRAMES, PROFILE_TYPES
from cortex_profiles.types.attribute_values import ListAttributeValue
from cortex_profiles.types.attributes import ProfileAttribute, AssignedProfileAttribute, ObservedProfileAttribute
from cortex_profiles.types.attribute_values import EntityEvent

from cortex_profiles.builders.attributes.utils.attribute_builder_utils import state_modifier
from cortex_profiles.builders.attributes.declared import derive_declared_attributes_from_value_only_df


def derive_implict_attributes_for_counts_of_concepts_present_in_insights(insights_df: pd.DataFrame, conceptType) -> List[ProfileAttribute]:
    # Generic ...
    # Count of concepts of a specific type present in an insight ...
    df = pd.DataFrame([
        {"profileId": profileId, "count": count}
        for profileId, count in Counter([
            tag["concept"]["id"] for tags in insights_df["tags"] for tag in tags if tag["concept"]["context"] == conceptType
        ]).items()
    ])
    return derive_declared_attributes_from_value_only_df(
        df, "count", key=f"occurances.{conceptType}.inInsights"
    )


def derive_implicit_attributes_from_insight_interactions(insights_df: pd.DataFrame, interactions_df: pd.DataFrame, sessions_df: pd.DataFrame, conceptToMakeInstancesFor:List[str]) -> List[ProfileAttribute]:
    """
    Derives all of the implicitly generated attributes for a user ...
    Recency has been pulled out ... if you want a recent profile vs a historic profile ... make a seperate schema for it ...

    :param insights_df:
    :param interactions_df:
    :param sessions_df:
    :param conceptToMakeInstancesFor: List of Type Identifier to generate Event Instances in the profile for ... with regards to tags on insights
    :return:
    """
    attributes = implicit_attribute_builder_utils.derive_implicit_attributes_from_insight_interactions(
        insights_df, interactions_df, sessions_df, conceptToMakeInstancesFor
    )
    return utils.flatten_list_recursively([attributes])


def derive_implicit_attributes_from_application_interactions(events:List[EntityEvent]) -> List[ProfileAttribute]:
    """
    :param events:
    :return:
    """
    implicit_attribute_builder_utils.derive_implicit_attribute_from_application_interactions(events)


def derive_implicit_profile_type_attribute(profileId:str, profileTypes:List[str]=[PROFILE_TYPES.END_USER]) -> AssignedProfileAttribute:
    return AssignedProfileAttribute(
        profileId = profileId,
        attributeKey = UNIVERSAL_ATTRIBUTES.TYPES,
        attributeValue = ListAttributeValue(profileTypes)
    )


class ImplicitAttributesBuilder(object):

    def __init__(self):
        self.attributes = [ ]

    @state_modifier(derive_implicit_attributes_from_insight_interactions, (lambda self, results: self.attributes.extend(results)))
    def append_implicit_insight_interaction_attributes(self, *args, **kwargs):
        """
        See :func:`.derive_declared_attributes_from_key_value_df` for input argument instructions.
        :return: The builder itself, after its state has been modified with the appended attributes ...
        """
        return self

    @state_modifier(derive_implicit_profile_type_attribute, (lambda self, results: self.attributes.append(results)))
    def append_implicit_type_attribute(self, *args, **kwargs):
        """
        See :func:`.derive_declared_attributes_from_value_only_df` for input argument instructions.
        :return: The builder itself, after its state has been modified with the appended attributes ...
        """
        return self


    def get(self) -> List[Union[AssignedProfileAttribute, ObservedProfileAttribute]]:
        return self.attributes


if __name__ == '__main__':
    from cortex_profiles import create_profile_synthesizer
    synth = create_profile_synthesizer()
    profileId, sessions_df, insights_df, interactions_df = synth.dfs_to_build_single_profile()
    attributes = (
        ImplicitAttributesBuilder()
            .append_implicit_insight_interaction_attributes(insights_df, interactions_df, sessions_df)
            .append_implicit_type_attribute(profileId)
            .get()
    )
    for attribute in attributes:
        print(attribute)