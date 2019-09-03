from typing import List

import pandas as pd
import pydash

from cortex_profiles.builders.attributes.utils import attribute_builder_utils, implicit_attribute_builder_utils
from cortex_profiles.implicit.schema import implicit_attributes, implicit_templates
from cortex_profiles.schemas.dataframes import COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL, \
    TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL, INSIGHT_COLS, INTERACTIONS_COLS
from cortex_profiles.schemas.schemas import CONTEXTS, PROFILE_TYPES
from cortex_profiles.types.attribute_values import CounterAttributeValue, TotalAttributeValue, EntityAttributeValue, \
    EntityEvent
from cortex_profiles.types.attributes import ObservedProfileAttribute


def derive_counter_attributes_for_count_of_specific_insight_interactions_per_insight_type(interactions_df:pd.DataFrame, insights_df:pd.DataFrame) -> List[ObservedProfileAttribute]:

    insight_interactions_df = implicit_attribute_builder_utils.derive_count_of_insights_per_interactionType_per_insightType_per_profile(interactions_df, insights_df)

    if insight_interactions_df.empty:
        return []

    attribute_value_constructor = attribute_builder_utils.simple_counter_attribute_value_constructor(
        "total",
        lambda x: CounterAttributeValue(value=x, unitTitle="insights")
    )

    return attribute_builder_utils.derive_attributes_from_groups_in_df(
        insight_interactions_df,
        [
            INTERACTIONS_COLS.PROFILEID,
            INSIGHT_COLS.INSIGHTTYPE,
            INTERACTIONS_COLS.INTERACTIONTYPE
        ],
        implicit_attributes.NameTemplates.COUNT_OF_INSIGHT_INTERACTIONS,
        ObservedProfileAttribute,
        attribute_value_constructor,
        additional_identifiers={}
    )


def derive_dimensional_attributes_for_count_of_specific_insight_interactions_per_encountered_tag(interactions_df:pd.DataFrame, insights_df:pd.DataFrame) -> List[ObservedProfileAttribute]:

    tag_specific_interactions_df = implicit_attribute_builder_utils.derive_count_of_insights_per_interactionType_per_relatedConcepts_per_profile(interactions_df, insights_df)

    if tag_specific_interactions_df.empty:
        return []

    attribute_value_constructor =  attribute_builder_utils.simple_dimensional_attribute_value_constructor(
        f"{{{COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTYPE}}}",  # Use the TAGGEDCONCEPTTYPE column as the context of the dimensionId
        CounterAttributeValue,
        COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTID,
        COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TOTAL,
        dimension_value_constructor=lambda x: CounterAttributeValue(value=x, unitTitle="insights"),
    )

    return attribute_builder_utils.derive_attributes_from_groups_in_df(
        tag_specific_interactions_df[
            tag_specific_interactions_df[COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTRELATIONSHIP] == CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP
        ],
        [
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.PROFILEID,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.INSIGHTTYPE,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.INTERACTIONTYPE,
            COUNT_OF_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTYPE
        ],
        implicit_attributes.NameTemplates.COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS,
        ObservedProfileAttribute,
        attribute_value_constructor,
        additional_identifiers={}
    )


def derive_dimensional_attributes_for_total_duration_of_specific_insight_interactions_per_encountered_tag(interactions_df:pd.DataFrame, insights_df:pd.DataFrame) -> List[ObservedProfileAttribute]:

    tag_specific_interactions_with_times_df = implicit_attribute_builder_utils.derive_time_spent_on_insights_with_relatedConcepts(
        implicit_attribute_builder_utils.prepare_interactions_per_tag_with_times(interactions_df, insights_df)
    )

    if tag_specific_interactions_with_times_df.empty:
        return []

    attribute_value_constructor = attribute_builder_utils.simple_dimensional_attribute_value_constructor(
        f"{{{TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTYPE}}}",
        TotalAttributeValue,
        TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTID,
        TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TOTAL,
        dimension_value_constructor=lambda x: TotalAttributeValue(value=x, unitTitle="seconds"),
    )

    return attribute_builder_utils.derive_attributes_from_groups_in_df(
        tag_specific_interactions_with_times_df[
            tag_specific_interactions_with_times_df[TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTRELATIONSHIP] == CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP
        ],
        [
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.PROFILEID,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.INSIGHTTYPE,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.INTERACTIONTYPE,
            TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTYPE
        ],
        implicit_attributes.NameTemplates.TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT,
        ObservedProfileAttribute,
        attribute_value_constructor,
        additional_identifiers={}
    )


def derive_entity_event_attributes_for_each_interaction(interactions_df, insights_df, conceptTypesToConsider:str) -> List[ObservedProfileAttribute]:
    tag_specific_interactions_with_times_df = implicit_attribute_builder_utils.prepare_interactions_per_tag_with_times(interactions_df, insights_df)

    if tag_specific_interactions_with_times_df.empty:
        return []

    attribute_value_constructor = lambda x: EntityAttributeValue(value=EntityEvent(
        event=implicit_attributes.NameTemplates.ENTITY_INTERACTION_INSTANCE.format(**pydash.merge({}, x)),
        entityId=x[TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.PROFILEID],
        entityType=PROFILE_TYPES.END_USER,
        eventTime=x.get(TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.ISOUTCSTARTTIME),
        targetEntityId=x[TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTID],
        targetEntityType=x[TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTYPE],
        properties={
            "interaction": x[TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.INTERACTIONTYPE],
            "started": x.get(TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.ISOUTCSTARTTIME),
            "ended": x.get(TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.ISOUTCENDTIME),
        }
    ))

    return attribute_builder_utils.derive_attributes_from_df(
        tag_specific_interactions_with_times_df[
            (tag_specific_interactions_with_times_df[TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTRELATIONSHIP] == CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP)
          & (tag_specific_interactions_with_times_df[TIMES_SPENT_ON_TAG_SPECIFIC_INTERACTIONS_COL.TAGGEDCONCEPTTYPE] == conceptTypesToConsider)
        ],
        implicit_attributes.NameTemplates.ENTITY_INTERACTION_INSTANCE,
        ObservedProfileAttribute,
        attribute_value_constructor,
        additional_identifiers={}
    )