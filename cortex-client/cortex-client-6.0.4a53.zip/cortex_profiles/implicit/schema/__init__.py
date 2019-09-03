from typing import List, Optional

import attr

from cortex_profiles.implicit.schema import implicit_attributes
from cortex_profiles.implicit.schema.implicit_groups import ImplicitGroups
from cortex_profiles.implicit.schema.implicit_hierarchy import derive_hierarchy_from_attribute_tags
from cortex_profiles.implicit.schema.implicit_tags import expand_tags_for_profile_attribute, ImplicitTags, \
    ImplicitTagTemplates, ImplicitTagLabels
from cortex_profiles.implicit.schema.utils import prepare_schema_config_variable_names
from cortex_profiles.types.schema import ProfileAttributeSchema, ProfileGroupSchema, ProfileSchema, ProfileTagSchema
from cortex_profiles.types.schema_config import SchemaConfig
from cortex_profiles.utils import utc_timestamp, unique_id, group_objects_by, dervie_set_by_element_id


def implicitly_generate_group_schemas(schema_config:SchemaConfig, additional_tags:Optional[List[ProfileTagSchema]]=None) -> List[ProfileGroupSchema]:
    all_groups = list(ImplicitGroups.values())
    all_tags = implicitly_generate_tag_schemas(schema_config, additional_tags )
    tags_grouped_by_group = group_objects_by(all_tags, lambda t: t.group)
    groups_grouped_by_id = group_objects_by(all_groups, lambda g: g.id)
    tag_groups = [
        attr.evolve(
            group_schemas[0],
            tags=list(sorted(map(lambda x: x.id, tags_grouped_by_group.get(group_id, []))))
        )
        for group_id, group_schemas in groups_grouped_by_id.items()
    ]
    return [x for x in tag_groups if len(x.tags) > 0]


def implicitly_generate_attribute_schemas(schema_config:SchemaConfig, disabledAttributes:Optional[List[str]]=None, include_tags:bool=True, profile_link_contexts:Optional[List[str]]=None) -> List[ProfileAttributeSchema]:
    dags = [] if disabledAttributes is None else disabledAttributes
    plc = [] if profile_link_contexts is None else profile_link_contexts
    return (
          (implicit_attributes.schemas_for_universal_attributes(include_tags=include_tags, profile_link_contexts=plc) if "universal_attributes" not in dags else [])
        + (implicit_attributes.schema_for_concept_specific_interaction_attributes(schema_config, include_tags=include_tags, profile_link_contexts=plc) if "concept_specific_interaction_attributes" not in dags else [])
        + (implicit_attributes.schema_for_concept_specific_duration_attributes(schema_config, include_tags=include_tags, profile_link_contexts=plc) if "concept_specific_duration_attributes" not in dags else [])
        + (implicit_attributes.schema_for_interaction_attributes(schema_config, include_tags=include_tags, profile_link_contexts=plc) if "interaction_attributes" not in dags else [])
        + (implicit_attributes.schema_for_app_specific_attributes(schema_config, include_tags=include_tags, profile_link_contexts=plc) if "app_specific_attributes" not in dags else [])
        + (implicit_attributes.schema_for_interaction_instances(schema_config, include_tags=include_tags, profile_link_contexts=plc) if "interaction_instances" not in dags else [])
        + (implicit_attributes.schema_for_aggregated_relationships(schema_config, include_tags=include_tags, profile_link_contexts=plc) if "aggregated_relationships" not in dags else [])
        + (implicit_attributes.schema_for_aggregated_timed_relationships(schema_config, include_tags=include_tags, profile_link_contexts=plc) if "aggregated_timed_relationships" not in dags else [])
    )


def implicitly_generate_tag_schemas(schema_config:SchemaConfig, additional_tags:Optional[List[ProfileTagSchema]]=None) -> List[ProfileTagSchema]:
    additional_tags = additional_tags if additional_tags is None else []
    tags = [
        ImplicitTags.DECLARED,
        ImplicitTags.OBSERVED,
        ImplicitTags.INFERRED,
        ImplicitTags.ASSIGNED,
        ImplicitTags.INSIGHT_INTERACTIONS,
        ImplicitTags.APP_SPECIFIC,
        ImplicitTags.APP_INTERACTION,
        ImplicitTags.CONCEPT_SPECIFIC,
        ImplicitTags.CONCEPT_AGNOSTIC,
        ImplicitTags.APP_USAGE,
        ImplicitTags.GENERAL
    ]

    used_labels = list(ImplicitTagLabels.values())

    interactions = list(map(
        lambda interaction: prepare_schema_config_variable_names({attr.fields(SchemaConfig).interaction_types.name: interaction}),
        list(dervie_set_by_element_id(schema_config.interaction_types + schema_config.timed_interaction_types, lambda x: x.id))
    ))

    for interaction in interactions:
        new_tag = ImplicitTagTemplates.INTERACTION(interaction, used_labels)
        used_labels.append(new_tag.label)
        tags.append(new_tag)

    apps = list(map(
        lambda app: prepare_schema_config_variable_names({attr.fields(SchemaConfig).apps.name: app}),
        schema_config.apps
    ))

    for app in apps:
        new_tag = ImplicitTagTemplates.APP_ASSOCIATED(app, used_labels)
        used_labels.append(new_tag.label)
        tags.append(new_tag)

    algos = list(map(
        lambda algo: prepare_schema_config_variable_names({attr.fields(SchemaConfig).insight_types.name: algo}),
        schema_config.insight_types
    ))

    for algo in algos:
        new_tag = ImplicitTagTemplates.ALGO_ASSOCIATED(algo, used_labels)
        used_labels.append(new_tag.label)
        tags.append(new_tag)

    concepts = list(map(
        lambda concept: prepare_schema_config_variable_names({attr.fields(SchemaConfig).concepts.name: concept}),
        schema_config.concepts
    ))

    for concept in concepts:
        new_tag = ImplicitTagTemplates.CONCEPT_ASSOCIATED(concept, used_labels)
        used_labels.append(new_tag.label)
        tags.append(new_tag)

    return tags + additional_tags


def implicity_generate_tag_oriented_profile_schema_from_config(
        schema_config:SchemaConfig,
        tenantId,
        environmentId,
        disabledAttributes:Optional[List[str]]=None,
        additional_tags:Optional[List[ProfileTagSchema]]=None,
        profile_link_contexts:Optional[List[str]]=None,
        include_attributes:bool=True
    ) -> ProfileSchema:
    additional_tags = additional_tags if additional_tags is not None else []
    return ProfileSchema(
        id=unique_id(),
        tenantId=tenantId,
        environmentId=environmentId,
        createdAt=utc_timestamp(),
        attributes=implicitly_generate_attribute_schemas(
            schema_config,
            disabledAttributes=disabledAttributes,
            include_tags=True,
            profile_link_contexts=profile_link_contexts
        ) if include_attributes else [],
        tags=implicitly_generate_tag_schemas(schema_config, additional_tags),
        groups=implicitly_generate_group_schemas(schema_config, additional_tags)
    )


# def implicity_generate_heirarchical_profile_schema_from_config(schema_config:SchemaConfig, tenantId, environmentId) -> ProfileSchema:
#     return ProfileSchema(
#         id=unique_id(),
#         tenantId=tenantId,
#         environmentId=environmentId,
#         createdAt=utc_timestamp(),
#         attributes=implicitly_generate_attribute_schemas(schema_config, include_tags=False),
#         hierarchy=derive_hierarchy_from_attribute_tags(schema_config)
#     )
#
