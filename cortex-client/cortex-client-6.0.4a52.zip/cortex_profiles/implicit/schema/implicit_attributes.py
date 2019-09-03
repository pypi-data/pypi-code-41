from enum import auto, unique
from typing import List, Optional, Union
import attr
import pydash

from cortex_profiles.implicit.schema.implicit_tags import expand_tags_for_profile_attribute, ImplicitAttributeSubjects, \
    ImplicitTags
from cortex_profiles.implicit.schema.implicit_templates import CONCEPT, attr_template, attr_name_template
from cortex_profiles.implicit.schema.utils import prepare_template_candidates_from_schema_fields
from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.schemas.schemas import UNIVERSAL_ATTRIBUTES
from cortex_profiles.types.attribute_values import DimensionalAttributeValue, CounterAttributeValue, \
    TotalAttributeValue, EntityAttributeValue
from cortex_profiles.types.profiles import ProfileLink
from cortex_profiles.types.attribute_values import ListAttributeValue, StatisticalSummaryAttributeValue
from cortex_profiles.types.schema import ProfileValueTypeSummary, ProfileAttributeSchema
from cortex_profiles.types.schema_config import SchemaConfig, CONCEPT_SPECIFIC_INTERACTION_FIELDS, \
    CONCEPT_SPECIFIC_DURATION_FIELDS, APP_SPECIFIC_FIELDS, INTERACTION_FIELDS, APP_INTERACTION_FIELDS, TIMED_APP_INTERACTION_FIELDS
from cortex_profiles.utils import AttrsAsDict
from cortex_profiles.utils import EnumWithNamesAsDefaultValue


@unique
class Patterns(EnumWithNamesAsDefaultValue):
    TYPE = auto()
    COUNT_OF_INSIGHT_INTERACTIONS = auto()
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = auto()
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = auto()
    COUNT_OF_APP_SPECIFIC_LOGINS = auto()
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = auto()
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = auto()
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = auto()
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = auto()
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = auto()
    STAT_SUMMARY_DAILY_APP_SPECIFIC_LOGINS = auto()
    STAT_SUMMARY_DAILY_APP_SPECIFIC_DURATIONS = auto()
    ENTITY_INTERACTION_INSTANCE = auto()
    TOTAL_ENTITY_RELATIONSHIPS = auto()
    TALLY_ENTITY_RELATIONSHIPS = auto()
    TOTAL_DURATION_ON_ENTITY_INTERACTION = auto()


class Metrics(AttrsAsDict):
    STAT_SUMMARY = pydash.strings.camel_case("STAT_SUMMARY")
    COUNT_OF = pydash.strings.camel_case("COUNT_OF")
    TALLY_OF = pydash.strings.camel_case("TALLY_OF")
    TOTAL_DURATION = pydash.strings.camel_case("TOTAL_DURATION")
    DURATION_OF = pydash.strings.camel_case("DURATION_OF")
    AVERAGE_COUNT_OF = pydash.strings.camel_case("AVERAGE_COUNT_OF")
    AVERAGE_DURATION_OF = pydash.strings.camel_case("AVERAGE_DURATION_OF")
    INSTANCE_OF = pydash.strings.camel_case("INSTANCE_OF")


class AttributeSections(AttrsAsDict):
    INSIGHTS            = attr_name_template("insights[{{{insight_type}}}]")
    INTERACTION         = attr_name_template("interaction")
    INTERACTED_WITH     = attr_name_template("interactedWith[{{{interaction_type}}}]")
    RELATED_TO_CONCEPT  = attr_name_template("relatedToConcept[{{{concept_title}}}]")
    LOGINS              = attr_name_template("logins[{{{app_id}}}]")
    DAILY_LOGINS        = attr_name_template("dailyLogins[{{{app_id}}}]")
    DAILY_APP_DURATION  = attr_name_template("dailyAppDuration[{{{app_id}}}]")
    RELATIONSHIP        = attr_name_template("relationship[{{{app_event}}}]")
    RELATIONSHIP_TARGET = attr_name_template("relatedTo[{{{app_event_target_type}}}]")


class NameTemplates(AttrsAsDict):
    TYPE = UNIVERSAL_ATTRIBUTES.TYPES
    COUNT_OF_INSIGHT_INTERACTIONS = ".".join([Metrics.COUNT_OF, AttributeSections.INSIGHTS, AttributeSections.INTERACTED_WITH])
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = ".".join([Metrics.COUNT_OF, AttributeSections.INSIGHTS,  AttributeSections.INTERACTED_WITH, AttributeSections.RELATED_TO_CONCEPT])
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = ".".join([Metrics.TOTAL_DURATION, AttributeSections.INSIGHTS,  AttributeSections.INTERACTED_WITH, AttributeSections.RELATED_TO_CONCEPT])
    COUNT_OF_APP_SPECIFIC_LOGINS = ".".join([Metrics.COUNT_OF, AttributeSections.LOGINS])
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = ".".join([Metrics.DURATION_OF, AttributeSections.LOGINS])
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = ".".join([Metrics.COUNT_OF, AttributeSections.DAILY_LOGINS])
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = ".".join([Metrics.DURATION_OF, AttributeSections.DAILY_LOGINS])
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = ".".join([Metrics.AVERAGE_COUNT_OF, AttributeSections.DAILY_LOGINS])
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = ".".join([Metrics.AVERAGE_DURATION_OF, AttributeSections.DAILY_LOGINS])
    STAT_SUMMARY_DAILY_APP_SPECIFIC_LOGINS = ".".join([Metrics.STAT_SUMMARY, AttributeSections.DAILY_LOGINS])
    STAT_SUMMARY_DAILY_APP_SPECIFIC_DURATIONS = ".".join([Metrics.STAT_SUMMARY, AttributeSections.DAILY_APP_DURATION])
    ENTITY_INTERACTION_INSTANCE = ".".join([Metrics.INSTANCE_OF, AttributeSections.INTERACTION])
    TOTAL_ENTITY_RELATIONSHIPS = ".".join([Metrics.COUNT_OF, AttributeSections.RELATIONSHIP, AttributeSections.RELATIONSHIP_TARGET])
    TALLY_ENTITY_RELATIONSHIPS = ".".join([Metrics.TALLY_OF, AttributeSections.RELATIONSHIP, AttributeSections.RELATIONSHIP_TARGET])
    TOTAL_DURATION_ON_ENTITY_INTERACTION = ".".join([Metrics.TOTAL_DURATION, AttributeSections.RELATIONSHIP, AttributeSections.RELATIONSHIP_TARGET])


class QuestionTemplates(AttrsAsDict):
    TYPE = "What are the different roles the profile adheres to?"
    COUNT_OF_INSIGHT_INTERACTIONS = attr_template("How many {{{insight_type}}} have been {{{interaction_type}}} the profile?")
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = attr_template("How many {{{insight_type}}} related to a specific {{{singular_concept_title}}} have been {{{interaction_type}}} the profile?")
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = attr_template("How much time did the profile spend on {{{insight_type}}} insights related to a specific {{{singular_concept_title}}}?")
    COUNT_OF_APP_SPECIFIC_LOGINS = attr_template("How many times did the profile log into the {{{app_title}}} app?")
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = attr_template("How much time did the profile spend logged into the {{{app_title}}} app?")
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("On a daily basis, how many times did the profile log into the {{{app_title}}} App?")
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("On a daily basis, how much time did the profile spend logged into the {{{app_title}}} app?")
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("On average, how many daily logins into the the {{{app_title}}} App did the profile initiate?")
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("On average, how much time did the profile spend daily logged into the {{{app_title}}} App?")
    STAT_SUMMARY_DAILY_APP_SPECIFIC_LOGINS = attr_template("How can we summarize the profile's count of daily logins into the the {{{app_title}}} App?")
    STAT_SUMMARY_DAILY_APP_SPECIFIC_DURATIONS = attr_template("How can we summarize the time the profile spent on the {{{app_title}}} App on a daily basis?")
    ENTITY_INTERACTION_INSTANCE = attr_template("What interactions with entities has the profile initiated?")
    TOTAL_ENTITY_RELATIONSHIPS = attr_template("How many times has the profile {{{relationship_desc}}} a {{{relationship_target_singular}}}?")
    TALLY_ENTITY_RELATIONSHIPS = attr_template("For the different {{{relationship_target_plural}}}, how many times has the profile {{{relationship_desc}}} each?")
    TOTAL_DURATION_ON_ENTITY_INTERACTION = attr_template("For each of the different {{{relationship_target_plural}}}, how much time has the profile spent {{{relationship_desc}}}?")


class DescriptionTemplates(AttrsAsDict):
    TYPE = "Different Types Profile Adheres to."
    COUNT_OF_INSIGHT_INTERACTIONS = attr_template("Total {{{insight_type}}} insights {{{interaction_type}}} profile.")
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = attr_template("Total {{{insight_type}}} insights related to {{{plural_concept_title}}} {{{interaction_type}}} profile.")
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = attr_template("Total time spent by profile on {{{insight_type}}} insights related to {{{plural_concept_title}}}.")
    COUNT_OF_APP_SPECIFIC_LOGINS = attr_template("Total times profile logged into {{{app_title}}} app.")
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = attr_template("Total time profile spent logged into {{{app_title}}} app")
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("Total times per day profile logged into {{{app_title}}} app")
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("Total time per day profile spent logged into {{{app_title}}} app")
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("Daily average of logins for profile on {{{app_title}}} app.")
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = attr_template("Daily average time profile spent logged into {{{app_title}}} app ")
    STAT_SUMMARY_DAILY_APP_SPECIFIC_LOGINS = attr_template("Summary of the profile's count of daily logins into the the {{{app_title}}} App?")
    STAT_SUMMARY_DAILY_APP_SPECIFIC_DURATIONS = attr_template("Summary of the time the profile spent on the {{{app_title}}} App on a daily basis?")
    ENTITY_INTERACTION_INSTANCE = attr_template("Instances of the profiles interactions with entities.")
    TOTAL_ENTITY_RELATIONSHIPS = attr_template("Total times has the profile has {{{relationship_desc}}} a {{{relationship_target_singular}}}")
    TALLY_ENTITY_RELATIONSHIPS = attr_template("Chart of the amount of times the profile has {{{relationship_desc}}} each different {{{relationship_target_singular}}}.")
    TOTAL_DURATION_ON_ENTITY_INTERACTION = attr_template("Chart of the total time the profile has spent {{{relationship_desc}}} each different {{{relationship_target_singular}}}.")


class TitleTemplates(AttrsAsDict):
    TYPE = "Profile Types"
    COUNT_OF_INSIGHT_INTERACTIONS = attr_template("Insights {{{Interaction_type}}}")
    COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS = attr_template("{{{Plural_concept_title}}} in Insights {{{Interaction_type}}}")
    TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT = attr_template("Duration on {{{Plural_concept_title}}}")
    COUNT_OF_APP_SPECIFIC_LOGINS = "Total Logins"
    TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS = "Duration of Logins"
    COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = "Daily Login Count"
    TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = "Daily Login Durations"
    AVERAGE_COUNT_OF_DAILY_APP_SPECIFIC_LOGINS = "Average Daily Logins"
    AVERAGE_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS = "Average Login Duration"
    STAT_SUMMARY_DAILY_APP_SPECIFIC_LOGINS = "Daily Login Summary"
    STAT_SUMMARY_DAILY_APP_SPECIFIC_DURATIONS = "Daily Duration Summary"
    ENTITY_INTERACTION_INSTANCE = "Entity Interactions"
    TOTAL_ENTITY_RELATIONSHIPS = attr_template("Total {{{relationship_target_Plural}}} {{{relationship_Past}}}")
    TALLY_ENTITY_RELATIONSHIPS = attr_template("Tally of {{{relationship_target_Plural}}} {{{relationship_Past}}}")
    TOTAL_DURATION_ON_ENTITY_INTERACTION = attr_template("Time Spent on {{{relationship_target_Plural}}} {{{relationship_Past}}}")

# So do I want the tags and groups to be driven by the ones that appear in attributes ...
# If a tag or group does not appear in an attribute then its not part of the schema ... dont think that is what we are going for!
# Should expand the potential tags!
# Should have validation code to validate that attributes are not tagged with tags that dont exist ...
# And that all tags belong to a group


def all_attribute_names_for_candidates(pattern: Patterns, candidates: list) -> List[str]:
    return [
        NameTemplates[pattern.name].format(**{k: v.id for k, v in cand.items()})
        for cand in candidates
    ]


def cast_to_profile_link(context:str, profile_link_contexts:Optional[List[str]]=None) -> Union[str, type]:
    plc = [] if profile_link_contexts is None else profile_link_contexts
    return context if context not in plc else ProfileLink


def expand_profile_attribute_schema(
            attribute_pattern: Patterns,
            attribute_filers:dict,
            valueType:ProfileValueTypeSummary,
            custom_subject:str=None,
            attributeContext:str=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
            include_tags:bool=True,
            additional_tags:Optional[List[str]]=None
        ) -> ProfileAttributeSchema:
    tags_to_add = additional_tags if additional_tags is not None else []
    return ProfileAttributeSchema(
        name=NameTemplates[attribute_pattern.name].format(**{k: v.id for k, v in attribute_filers.items()}),
        type=attributeContext,
        valueType=valueType,
        label=TitleTemplates[attribute_pattern.name].format(**attribute_filers),
        description=DescriptionTemplates[attribute_pattern.name].format(**attribute_filers),
        questions=[QuestionTemplates[attribute_pattern.name].format(**attribute_filers)],
        tags=list(sorted((expand_tags_for_profile_attribute(attribute_filers, attributeContext, custom_subject) + tags_to_add) if include_tags else []))
    )


def schema_for_interaction_instances(schema_config:SchemaConfig, include_tags:bool=True, profile_link_contexts:Optional[List[str]]=None) -> List[ProfileAttributeSchema]:
    return [
        expand_profile_attribute_schema(
            Patterns.ENTITY_INTERACTION_INSTANCE, {},
            EntityAttributeValue.detailed_schema_type(),
            custom_subject=None,
            attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
            include_tags=include_tags,
            additional_tags=[ImplicitTags.APP_INTERACTION.id]
        )
    ]


def schema_for_aggregated_relationships(schema_config:SchemaConfig, include_tags:bool=True, profile_link_contexts:Optional[List[str]]=None) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, APP_INTERACTION_FIELDS)
    return (
        [
            expand_profile_attribute_schema(
                Patterns.TOTAL_ENTITY_RELATIONSHIPS, cand,
                CounterAttributeValue.detailed_schema_type(),
                custom_subject=None,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
                include_tags=include_tags,
                additional_tags=[ImplicitTags.APP_SPECIFIC.id, ImplicitTags.APP_INTERACTION.id]
            )
            for cand in candidates
        ]
        +
        [
            expand_profile_attribute_schema(
                Patterns.TALLY_ENTITY_RELATIONSHIPS, cand,
                DimensionalAttributeValue.detailed_schema_type(
                    cast_to_profile_link(attr_template("{{{relationship_type}}}").format(**cand), profile_link_contexts),
                    CounterAttributeValue
                ),
                custom_subject=None,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
                include_tags=include_tags,
                additional_tags=[ImplicitTags.APP_SPECIFIC.id, ImplicitTags.APP_INTERACTION.id]
            )
            for cand in candidates
        ]
    )


def schema_for_aggregated_timed_relationships(schema_config:SchemaConfig, include_tags:bool=True, profile_link_contexts:Optional[List[str]]=None) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, TIMED_APP_INTERACTION_FIELDS)
    return (
        [
            expand_profile_attribute_schema(
                Patterns.TOTAL_DURATION_ON_ENTITY_INTERACTION, cand,
                DimensionalAttributeValue.detailed_schema_type(
                    cast_to_profile_link(attr_template("{{{relationship_type}}}").format(**cand), profile_link_contexts),
                    CounterAttributeValue
                ),
                custom_subject=None,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
                include_tags=include_tags,
                additional_tags=[ImplicitTags.APP_SPECIFIC.id, ImplicitTags.APP_INTERACTION.id]
            )
            for cand in candidates
        ]
        +
        schema_for_aggregated_relationships(
            attr.evolve(schema_config, timed_application_events=[], application_events=schema_config.timed_application_events),
            include_tags=include_tags, profile_link_contexts=profile_link_contexts
        )
    )


def schema_for_concept_specific_interaction_attributes(schema_config:SchemaConfig, include_tags:bool=True, profile_link_contexts:Optional[List[str]]=None) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, CONCEPT_SPECIFIC_INTERACTION_FIELDS)
    return [
        expand_profile_attribute_schema(
            Patterns.COUNT_OF_CONCEPT_SPECIFIC_INSIGHT_INTERACTIONS, cand,
            DimensionalAttributeValue.detailed_schema_type(
                cast_to_profile_link(cand[CONCEPT].id, profile_link_contexts),
                CounterAttributeValue
            ),
            custom_subject=None,
            attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
            include_tags=include_tags,
            additional_tags=[ImplicitTags.INSIGHT_INTERACTIONS.id]
        )
        for cand in candidates
    ]


def schema_for_concept_specific_duration_attributes(schema_config: SchemaConfig, include_tags:bool=True, profile_link_contexts:Optional[List[str]]=None) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, CONCEPT_SPECIFIC_DURATION_FIELDS)
    return [
        expand_profile_attribute_schema(
            Patterns.TOTAL_DURATION_ON_CONCEPT_SPECIFIC_INSIGHT, cand,
            DimensionalAttributeValue.detailed_schema_type(
                cast_to_profile_link(cand[CONCEPT].id, profile_link_contexts),
                TotalAttributeValue
            ),
            custom_subject=None,
            attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
            include_tags=include_tags,
            additional_tags=[ImplicitTags.INSIGHT_INTERACTIONS.id]
        )
        for cand in candidates
    ]


def schema_for_interaction_attributes(schema_config: SchemaConfig, include_tags:bool=True, profile_link_contexts:Optional[List[str]]=None) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, INTERACTION_FIELDS)
    return [
        expand_profile_attribute_schema(
            Patterns.COUNT_OF_INSIGHT_INTERACTIONS, cand,
            CounterAttributeValue.detailed_schema_type(),
            custom_subject=None,
            attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
            include_tags=include_tags,
            additional_tags=[ImplicitTags.INSIGHT_INTERACTIONS.id,]
        )
        for cand in candidates
    ]


def schema_for_app_specific_attributes(schema_config:SchemaConfig, include_tags:bool=True, profile_link_contexts:Optional[List[str]]=None) -> List[ProfileAttributeSchema]:
    candidates = prepare_template_candidates_from_schema_fields(schema_config, APP_SPECIFIC_FIELDS)
    return (
        [
            expand_profile_attribute_schema(
                attribute_pattern, cand,
                CounterAttributeValue.detailed_schema_type(),
                custom_subject=None,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
                include_tags=include_tags,
                additional_tags=[ImplicitTags.APP_USAGE.id, ImplicitTags.APP_SPECIFIC.id,]
            )
            for attribute_pattern in [Patterns.COUNT_OF_APP_SPECIFIC_LOGINS] for cand in candidates
        ]
        +
        [
            expand_profile_attribute_schema(
                attribute_pattern, cand,
                DimensionalAttributeValue.detailed_schema_type(
                    cast_to_profile_link("cortex/day", profile_link_contexts),
                    CounterAttributeValue
                ),
                custom_subject=None,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
                include_tags=include_tags,
                additional_tags=[ImplicitTags.APP_USAGE.id, ImplicitTags.APP_SPECIFIC.id,]
            )
            for attribute_pattern in [Patterns.COUNT_OF_DAILY_APP_SPECIFIC_LOGINS] for cand in candidates
        ]
        +
        [
            expand_profile_attribute_schema(
                attribute_pattern, cand,
                TotalAttributeValue.detailed_schema_type(),
                custom_subject=None,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
                include_tags=include_tags,
                additional_tags=[ImplicitTags.APP_USAGE.id, ImplicitTags.APP_SPECIFIC.id,]
            )
            for attribute_pattern in [Patterns.TOTAL_DURATION_OF_APP_SPECIFIC_LOGINS] for cand in candidates
        ]
        +
        [
            expand_profile_attribute_schema(
                attribute_pattern, cand,
                DimensionalAttributeValue.detailed_schema_type(
                    cast_to_profile_link("cortex/day", profile_link_contexts),
                    TotalAttributeValue
                ),
                custom_subject=None,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
                include_tags=include_tags,
                additional_tags=[ImplicitTags.APP_USAGE.id, ImplicitTags.APP_SPECIFIC.id,]
            )
            for attribute_pattern in [Patterns.TOTAL_DURATION_OF_DAILY_APP_SPECIFIC_LOGINS] for cand in candidates
        ]
        +
        [
            expand_profile_attribute_schema(
                attribute_pattern, cand,
                StatisticalSummaryAttributeValue.detailed_schema_type(),
                custom_subject=None,
                attributeContext=CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE,
                include_tags=include_tags,
                additional_tags=[ImplicitTags.APP_USAGE.id, ImplicitTags.APP_SPECIFIC.id,]
            )
            for attribute_pattern in [Patterns.STAT_SUMMARY_DAILY_APP_SPECIFIC_LOGINS, Patterns.STAT_SUMMARY_DAILY_APP_SPECIFIC_DURATIONS] for cand in candidates
        ]

    )


def schemas_for_universal_attributes(include_tags:bool=True, profile_link_contexts:Optional[List[str]]=None) -> List[ProfileAttributeSchema]:
    return [
        ProfileAttributeSchema(
            name=UNIVERSAL_ATTRIBUTES.TYPES,
            type=CONTEXTS.ASSIGNED_PROFILE_ATTRIBUTE,
            valueType=ListAttributeValue.detailed_schema_type("str"),
            label=TitleTemplates.TYPE,
            description=DescriptionTemplates.TYPE,
            questions=[QuestionTemplates.TYPE],
            tags=[ImplicitTags.ASSIGNED.id, ImplicitTags.GENERAL.id] if include_tags else []
        )
    ]