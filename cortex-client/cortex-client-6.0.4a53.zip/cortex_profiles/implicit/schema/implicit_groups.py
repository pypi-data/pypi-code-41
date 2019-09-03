from cortex_profiles.types.schema import ProfileGroupSchema
from cortex_profiles.utils import AttrsAsDict


class ImplicitGroupDescriptions(AttrsAsDict):
    ATTRIBUTE_TYPE = "What tags capture of the different classifications of the attributes?"
    CLASSIFICATIONS = "What tags help classify attributes?"
    SUBJECTS = "What tags represent the conceptual essences of attributes?"
    INTERACTION = "What tags capture the different interactions attributes can be optionally related to?"
    APP_ASSOCIATED = "What tags capture the different apps attributes can be optionally related to?"
    ALGO_ASSOCIATED = "What tags capture the different algos attributes can be optionally related to?"
    CONCEPT_ASSOCIATED = "What tags capture the different concepts attributes can be optionally related to?"
    USAGE = "What tags capture how an attribute is intended to be used?"


class ImplicitGroups(AttrsAsDict):
    ATTRIBUTE_TYPE = ProfileGroupSchema(
        id="attr", label="ATTR-TYPE", description=ImplicitGroupDescriptions.ATTRIBUTE_TYPE)
    CLASSIFICATIONS = ProfileGroupSchema(
        id="info", label="INFO-TYPE", description=ImplicitGroupDescriptions.CLASSIFICATIONS)
    SUBJECTS = ProfileGroupSchema(
        id="subject", label="SUBJECTS", description=ImplicitGroupDescriptions.SUBJECTS)
    INTERACTION = ProfileGroupSchema(
        id="interaction", label="INTERACTIONS", description=ImplicitGroupDescriptions.INTERACTION)
    APP_ASSOCIATED = ProfileGroupSchema(
        id="app", label="APPS", description=ImplicitGroupDescriptions.APP_ASSOCIATED)
    ALGO_ASSOCIATED = ProfileGroupSchema(
        id="algo", label="INSIGHTS", description=ImplicitGroupDescriptions.ALGO_ASSOCIATED)
    CONCEPT_ASSOCIATED = ProfileGroupSchema(
        id="concept", label="CONCEPTS", description=ImplicitGroupDescriptions.CONCEPT_ASSOCIATED)
    USAGE = ProfileGroupSchema(
        id="usage", label="USAGE", description=ImplicitGroupDescriptions.USAGE)