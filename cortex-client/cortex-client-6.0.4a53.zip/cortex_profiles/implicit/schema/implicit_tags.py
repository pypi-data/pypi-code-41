from typing import List, Mapping, Any, Callable, Optional

import attr

from cortex_profiles.implicit.schema.implicit_groups import ImplicitGroups
from cortex_profiles.implicit.schema.implicit_templates import tag_template, APP_ID, INSIGHT_TYPE, CONCEPT, \
    INTERACTION_TYPE
from cortex_profiles.schemas.schemas import CONTEXTS
from cortex_profiles.types.schema import ProfileTagSchema, ProfileGroupSchema
from cortex_profiles.utils import AttrsAsDict
from cortex_profiles.utils import label_generator


def profile_tag_schema_in_group(tagId:str, group:ProfileGroupSchema, **kwargs:Mapping[str, Any]) -> ProfileTagSchema:
    return ProfileTagSchema(id="{}/{}".format(group.id, tagId.replace("/","-")), group=group.id, **kwargs)


class ImplicitAttributeSubjects(AttrsAsDict):
    """
    These are the different subjects expected to be used within the subject group ...
    """
    INTERACTIONS = "interactions"
    INSIGHT_INTERACTIONS = "insight-interactions"
    APP_USAGE = "application-usage"


class ImplicitAttributeUsage(AttrsAsDict):
    """
    These are the different uasges expected to be used within the usage group ...
    """
    GENERAL = "general"
    APP_SPECIFIC = "app-specific"

class ImplicitTagDescriptions(AttrsAsDict):
    DECLARED = "Which attributes are declared by the profile themself?"
    OBSERVED = "Which attributes are observed?"
    INFERRED = "Which attributes are inferred?"
    ASSIGNED = "Which attributes are assigned to the profile?"
    INTERACTION = "Which attributes capture a specific user interaction?"
    INSIGHT_INTERACTIONS = "Which attributes capture a part of the profile's interactions with insights?"
    APP_USAGE = "Which attributes capture a part of the profile's application usage behavior?"
    APP_SPECIFIC = "Which attributes are specific to an specific application?"
    CONCEPT_SPECIFIC = "Which attributes are related to external concepts?"
    CONCEPT_AGNOSTIC = "Which attributes are agnostic of external concepts?"
    APP_INTERACTION = "Which attributes related to significant interactions that occured within a specific application?"
    GENERAL = "Which attributes are expected to be used generally?"


class ImplicitTagLabels(AttrsAsDict):
    DECLARED = "ICD"
    OBSERVED = "ICO"
    INFERRED = "ICI"
    ASSIGNED = "ICA"
    INSIGHT_INTERACTIONS = "SII"
    APP_INTERACTION = "SAE"
    APP_USAGE = "SAU"
    APP_SPECIFIC = "CAS"
    CONCEPT_SPECIFIC = "CCS"
    CONCEPT_AGNOSTIC = "CCA"
    GENERAL = "GNR"


class ImplicitTags(AttrsAsDict):

    DECLARED = profile_tag_schema_in_group("declared", ImplicitGroups.ATTRIBUTE_TYPE,
        label=ImplicitTagLabels.DECLARED, description=ImplicitTagDescriptions.DECLARED)
    OBSERVED = profile_tag_schema_in_group("observed", ImplicitGroups.ATTRIBUTE_TYPE,
        label=ImplicitTagLabels.OBSERVED, description=ImplicitTagDescriptions.OBSERVED)
    INFERRED = profile_tag_schema_in_group("inferred", ImplicitGroups.ATTRIBUTE_TYPE,
        label=ImplicitTagLabels.INFERRED, description=ImplicitTagDescriptions.INFERRED)
    ASSIGNED = profile_tag_schema_in_group("assigned", ImplicitGroups.ATTRIBUTE_TYPE,
        label=ImplicitTagLabels.ASSIGNED, description=ImplicitTagDescriptions.ASSIGNED)

    CONCEPT_SPECIFIC = profile_tag_schema_in_group("concept-specific", ImplicitGroups.CLASSIFICATIONS,
        label=ImplicitTagLabels.CONCEPT_SPECIFIC, description=ImplicitTagDescriptions.CONCEPT_SPECIFIC)
    CONCEPT_AGNOSTIC = profile_tag_schema_in_group("concept-agnostic", ImplicitGroups.CLASSIFICATIONS,
        label=ImplicitTagLabels.CONCEPT_AGNOSTIC, description=ImplicitTagDescriptions.CONCEPT_AGNOSTIC)

    INSIGHT_INTERACTIONS = profile_tag_schema_in_group(ImplicitAttributeSubjects.INSIGHT_INTERACTIONS, ImplicitGroups.SUBJECTS,
        label=ImplicitTagLabels.INSIGHT_INTERACTIONS, description=ImplicitTagDescriptions.INSIGHT_INTERACTIONS)
    APP_USAGE = profile_tag_schema_in_group(ImplicitAttributeSubjects.APP_USAGE, ImplicitGroups.SUBJECTS,
        label=ImplicitTagLabels.APP_USAGE, description=ImplicitTagDescriptions.APP_USAGE)
    APP_INTERACTION = profile_tag_schema_in_group(ImplicitAttributeSubjects.INTERACTIONS, ImplicitGroups.SUBJECTS,
        label=ImplicitTagLabels.APP_INTERACTION, description=ImplicitTagDescriptions.APP_INTERACTION)

    APP_SPECIFIC = profile_tag_schema_in_group(ImplicitAttributeUsage.APP_SPECIFIC, ImplicitGroups.USAGE,
        label=ImplicitTagLabels.APP_SPECIFIC, description=ImplicitTagDescriptions.APP_SPECIFIC)
    GENERAL = profile_tag_schema_in_group(ImplicitAttributeUsage.GENERAL, ImplicitGroups.USAGE,
        label=ImplicitTagLabels.GENERAL, description=ImplicitTagDescriptions.GENERAL)


class ImplicitTagTemplate(AttrsAsDict):
    INTERACTION = tag_template("{{{interaction_type}}}")
    APP_ASSOCIATED = tag_template("{{{app_id}}}")
    ALGO_ASSOCIATED = tag_template("{{{insight_type_id}}}")
    CONCEPT_ASSOCIATED = tag_template("{{{concept_id}}}")


class ImplicitTagTemplateName(AttrsAsDict):
    """
    This includesthe group name in the template ...
    The tag here ... is generated the same way the tag id in profile_tag_schema_in_group is generated ...
    """
    INTERACTION = profile_tag_schema_in_group(tag_template("{{{interaction_type}}}"), ImplicitGroups["INTERACTION"], label=None, description=None).id
    APP_ASSOCIATED = profile_tag_schema_in_group(tag_template("{{{app_id}}}"), ImplicitGroups["APP_ASSOCIATED"], label=None, description=None).id
    ALGO_ASSOCIATED = profile_tag_schema_in_group(tag_template("{{{insight_type_id}}}"), ImplicitGroups["ALGO_ASSOCIATED"], label=None, description=None).id
    CONCEPT_ASSOCIATED = profile_tag_schema_in_group(tag_template("{{{concept_id}}}"), ImplicitGroups["CONCEPT_ASSOCIATED"], label=None, description=None).id


def expand_template_for_tag(tag_template_name:str) -> Callable:
    """
    There needs to be a ImplicitGroup with the same name as the tag tempalte ...
    :param tag_template_name:
    :return:
    """
    def callable(candidate, used_tags:Optional[List[str]]=None) -> ProfileTagSchema:
        """
        :param candidate:
        :param used_tags: Used for automatic label generation ... dont want to reuse tag labels ...
        :return:
        """
        tag_name = ImplicitTagTemplate[tag_template_name].format(**candidate)
        tag = profile_tag_schema_in_group(
            tag_name,
            ImplicitGroups[tag_template_name],
            label=None,
            description=DescriptionTemplates[tag_template_name].format(**candidate)
        )
        if used_tags is not None:
            tag = attr.evolve(tag, label=label_generator(tag.id, used_tags))
        return tag
    return callable


# https://stackoverflow.com/questions/31907060/python-3-enums-with-function-values
class ImplicitTagTemplates(AttrsAsDict):
    INTERACTION = expand_template_for_tag("INTERACTION")
    APP_ASSOCIATED = expand_template_for_tag("APP_ASSOCIATED")
    ALGO_ASSOCIATED = expand_template_for_tag("ALGO_ASSOCIATED")
    CONCEPT_ASSOCIATED = expand_template_for_tag("CONCEPT_ASSOCIATED")
    # TODO ... CUSTOM SUBJECT TAG ...


class DescriptionTemplates(AttrsAsDict):
    INTERACTION = tag_template("Which attributes are associated with insights {{{interaction_statement}}} the profile?")
    APP_ASSOCIATED = tag_template("Which attributes are associated with the {{{app_name}}} ({{{app_symbol}}})?")
    ALGO_ASSOCIATED = tag_template("Which attributes are associated with the {{{insight_type}}} ({{{insight_type_symbol}}}) Algorithm?")
    CONCEPT_ASSOCIATED = tag_template("Which attributes are associated with {{{concepts}}}?")


def expand_tags_for_profile_attribute(cand:Mapping[str, str], attribute_context:str, subject:str) -> List[str]:
    """
    Determines which tags are applicable to a specific attribute ... based on the candidate being expanded ...
    Subjects lead to additional tags ...

    :param cand:
    :param attribute_context:
    :param subject:
    :return:
    """
    interaction_tag = None if INTERACTION_TYPE not in cand else ImplicitTagTemplates.INTERACTION(cand).id
    insight_interaction_tag = None if interaction_tag is None else ImplicitTags.INSIGHT_INTERACTIONS.id

    app_association_tag = None if APP_ID not in cand else ImplicitTagTemplates.APP_ASSOCIATED(cand).id
    app_specific_tag = None if app_association_tag is None else ImplicitTags.APP_SPECIFIC.id

    algo_association_tag = None if INSIGHT_TYPE not in cand else ImplicitTagTemplates.ALGO_ASSOCIATED(cand).id
    concept_association_tag = None if CONCEPT not in cand else ImplicitTagTemplates.CONCEPT_ASSOCIATED(cand).id

    concept_specific_tag = ImplicitTags.CONCEPT_SPECIFIC.id if concept_association_tag is not None else None
    concept_agnostic_tag = None if concept_association_tag is not None else ImplicitTags.CONCEPT_AGNOSTIC.id
    concept_association_tag = None if CONCEPT not in cand else ImplicitTagTemplates.CONCEPT_ASSOCIATED(cand).id

    classification_tag = {
        CONTEXTS.DECLARED_PROFILE_ATTRIBUTE: ImplicitTags.DECLARED.id,
        CONTEXTS.OBSERVED_PROFILE_ATTRIBUTE: ImplicitTags.OBSERVED.id,
        CONTEXTS.INFERRED_PROFILE_ATTRIBUTE: ImplicitTags.INFERRED.id,
        CONTEXTS.ASSIGNED_PROFILE_ATTRIBUTE: ImplicitTags.ASSIGNED.id,
    }.get(attribute_context, None)
    subject_tag = None if not subject else "{}/{}".format(ImplicitGroups.SUBJECTS.id, subject)
    return list(filter(
        lambda x: x,
        [
            interaction_tag, app_association_tag, algo_association_tag, concept_association_tag, classification_tag, subject_tag,
            concept_specific_tag, concept_agnostic_tag, app_specific_tag, insight_interaction_tag
        ]
    ))


if __name__ == '__main__':
    print(dict(ImplicitTagTemplates))