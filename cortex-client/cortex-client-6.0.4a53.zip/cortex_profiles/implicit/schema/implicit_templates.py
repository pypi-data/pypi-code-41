import attr

from cortex_profiles.schemas.dataframes import TAGGED_CONCEPT
from cortex_profiles.types.attribute_values import EntityEvent
from cortex_profiles.types.insights import Insight
from cortex_profiles.types.interactions import InsightInteractionEvent
from cortex_profiles.types.interactions import Session

INSIGHT_TYPE = attr.fields(Insight).insightType.name
INTERACTION_TYPE = attr.fields(InsightInteractionEvent).interactionType.name
APP_ID = attr.fields(Session).appId.name
CONCEPT = TAGGED_CONCEPT.TYPE
EVENTS = attr.fields(EntityEvent).event.name
EVENT_TARGET_TYPE = attr.fields(EntityEvent).targetEntityType.name


# How are these keys such as INSIGHT_TYPE, ... used?
# Candidates that will fill in the schema ... will be set as these ... this serves as a vocabulary to reference specific candidates ...
# To use this ... still need to properly expand candidates / create tihemm

# These are populated at run time ... where we dont have the proper schema config!
# These also come from the id column names from dataframes! ... so they are based on the data!
attr_name_config_pattern = {
    "insight_type": INSIGHT_TYPE,
    "interaction_type": INTERACTION_TYPE,
    "concept_title": CONCEPT,
    "app_id": APP_ID,
    "app_event": EVENTS,
    "app_event_target_type": EVENT_TARGET_TYPE,
}

attr_schema_config_patterns = {
    "insight_type": "{}.plural".format(INSIGHT_TYPE),
    "interaction_type": "{}.verbStatement".format(INTERACTION_TYPE),
    "plural_concept_title": "{}.plural".format(CONCEPT),
    "Interaction_type": "{}.Verb".format(INTERACTION_TYPE),
    "Plural_concept_title": "{}.Plural".format(CONCEPT),
    "singular_concept_title": "{}.singular".format(CONCEPT),
    "app_title": "{}.acronym".format(APP_ID),
    "relationship_title": "{}.Verb".format(EVENTS),
    "relationship_desc": "{}.verb".format(EVENTS),
    "relationship_Past":  "{}.Past".format(EVENTS),
    "relationship_target_plural":  "{}.plural".format(EVENT_TARGET_TYPE),
    "relationship_target_singular":  "{}.singular".format(EVENT_TARGET_TYPE),
    "relationship_target_Singular":  "{}.Singular".format(EVENT_TARGET_TYPE),
    "relationship_target_Plural":  "{}.Plural".format(EVENT_TARGET_TYPE),
    "relationship_type":  "{}.id".format(EVENT_TARGET_TYPE),
}

tag_schema_config_patterns = {
    "app_id": "{}.id".format(APP_ID),
    "app_name": "{}.singular".format(APP_ID),
    "app_symbol": "{}.acronym".format(APP_ID),

    "insight_type_id": "{}.id".format(INSIGHT_TYPE),
    "insight_type": "{}.singular".format(INSIGHT_TYPE),
    "insight_type_symbol": "{}.acronym".format(INSIGHT_TYPE),

    "concept_id": "{}.id".format(CONCEPT),
    "concepts": "{}.plural".format(CONCEPT),

    "interaction_type": "{}.id".format(INTERACTION_TYPE),
    "interaction_statement": "{}.verbStatement".format(INTERACTION_TYPE),
}


def attr_name_template(s:str) -> str:
    return s.format(**attr_name_config_pattern)


def attr_template(s:str) -> str:
    return s.format(**attr_schema_config_patterns)


def tag_template(s:str) -> str:
    return s.format(**tag_schema_config_patterns)