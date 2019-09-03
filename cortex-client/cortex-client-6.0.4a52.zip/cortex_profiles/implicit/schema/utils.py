from itertools import product
from typing import List, Union

import attr
import pydash

from cortex_profiles.implicit.schema.implicit_templates import APP_ID, INTERACTION_TYPE, INSIGHT_TYPE, CONCEPT, EVENTS, EVENT_TARGET_TYPE
from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.types.attributes import DeclaredProfileAttribute
from cortex_profiles.types.schema import ProfileAttributeSchema, ProfileTagSchema, ProfileValueTypeSummary
from cortex_profiles.types.schema_config import SchemaConfig


def determine_detailed_type_of_attribute_value(attribute) -> ProfileValueTypeSummary:
    if attribute["attributeValue"]["context"] == CONTEXTS.DIMENSIONAL_PROFILE_ATTRIBUTE_VALUE:
        return ProfileValueTypeSummary(
            outerType = attribute["attributeValue"]["context"],
            innerTypes = [
                ProfileValueTypeSummary(outerType=attribute["attributeValue"]["contextOfDimension"]),
                ProfileValueTypeSummary(outerType=attribute["attributeValue"]["contextOfDimensionValue"])
            ]
        )
    else:
        return ProfileValueTypeSummary(outerType=attribute["attributeValue"]["context"])


def find_tag_in_group_for(group, key):
    return "{}/{}".format(group, key) if key else None


def prepare_schema_config_variable_names(config:dict) -> dict:
    """
    When new sections are added to the schema config, this method needs to be updated so that the proper vocab
    is constructed from candidates ... generated from the schema config ...
    :param config:
    :return:
    """
    renamer = {
        k: v
        for k, v in {
            attr.fields(SchemaConfig).apps.name: APP_ID,
            attr.fields(SchemaConfig).insight_types.name: INSIGHT_TYPE,
            attr.fields(SchemaConfig).concepts.name: CONCEPT,
            # Only one of the following two should be in the dictionary provided as input ...
            attr.fields(SchemaConfig).interaction_types.name: INTERACTION_TYPE,
            attr.fields(SchemaConfig).timed_interaction_types.name: INTERACTION_TYPE
        }.items()
        if k in config
    }

    renamed_config = pydash.rename_keys(config, renamer)

    if attr.fields(SchemaConfig).application_events.name in config:
        renamed_config.pop(attr.fields(SchemaConfig).application_events.name)
        renamed_config[EVENTS] = config[attr.fields(SchemaConfig).application_events.name].relationship
        renamed_config[EVENT_TARGET_TYPE] = config[attr.fields(SchemaConfig).application_events.name].relatedType

    if attr.fields(SchemaConfig).timed_application_events.name in config:
        renamed_config.pop(attr.fields(SchemaConfig).timed_application_events.name)
        renamed_config[EVENTS] = config[attr.fields(SchemaConfig).timed_application_events.name].relationship
        renamed_config[EVENT_TARGET_TYPE] = config[attr.fields(SchemaConfig).timed_application_events.name].relatedType

    return renamed_config


def prepare_template_candidates_from_schema_fields(schema_config:SchemaConfig, attr_fields:List) -> List[dict]:
    relevant_schema = attr.asdict(schema_config, recurse=False, filter=lambda a, v: a in attr_fields)
    candidates = [
        prepare_schema_config_variable_names(dict(zip(relevant_schema.keys(), z)))
        for z in list(product(*[x for x in relevant_schema.values()]))
    ]
    return candidates


def custom_attributes(
        attributes:List[dict],
        schema_config:SchemaConfig,
        valueType:Union[ProfileValueTypeSummary, type],
        attributeType:str=DeclaredProfileAttribute,
        tags:List[ProfileTagSchema]=[]) -> List[ProfileAttributeSchema]:
    set_fields_in_schema_config = [
        f
        for f in attr.fields(SchemaConfig)
        if attr.asdict(schema_config).get(f.name)
    ]
    candidates = prepare_template_candidates_from_schema_fields(schema_config, set_fields_in_schema_config )
    return list(set([
        ProfileAttributeSchema(
            name=attribute["name"].format(**cand),
            type=attr.fields(attributeType).context.default,
            valueType=valueType if isinstance(valueType, ProfileValueTypeSummary) else valueType.detailed_schema_type(),
            label=attribute["label"],
            description=attribute["description"],
            questions=[attribute["question"]],
            tags=[x.format(**cand) for x in tags],
        )
        for cand in candidates
        for attribute in attributes
    ]))