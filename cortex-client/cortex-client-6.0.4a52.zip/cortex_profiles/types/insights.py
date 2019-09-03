from typing import List, Optional

from attr import attrs

from cortex_profiles.schemas.schemas import CONTEXTS, VERSION
from cortex_profiles.types.utils import describableAttrib, CONTEXT_DESCRIPTION, VERSION_DESCRIPTION
from cortex_profiles.utils import unique_id, utc_timestamp


ID_DESCRIPTION = "What is the id of this piece of data?"


@attrs(frozen=True)
class Link(object):

    """
    Linking to a specific concept by id.
    """
    id = describableAttrib(type=str, description=ID_DESCRIPTION)
    title = describableAttrib(type=Optional[str], default=None, description="What is the human friendly name of this link?")
    context = describableAttrib(type=str, default=CONTEXTS.LINK, description=CONTEXT_DESCRIPTION, internal=True)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION, internal=True)


@attrs(frozen=True)
class InsightTag(object):
    """
    Tags that can occur on insights.
    """
    id = describableAttrib(type=str, description=ID_DESCRIPTION)
    insight = describableAttrib(type=Link, description="What insight is this tag about?")
    tagged = describableAttrib(type=str, description="When was the insight tagged with this tag?")
    concept = describableAttrib(type=Link, description="What concept is being tagged by the insight?")
    relationship = describableAttrib(type=Link, description="What relationship does the tagged concept have with regards to the insight?")
    context = describableAttrib(type=str, default=CONTEXTS.INSIGHT_CONCEPT_TAG, description=CONTEXT_DESCRIPTION, internal=True)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION, internal=True)


@attrs(frozen=True)
class Insight(object):
    """
    A piece of information generated for a specific profile.
    """
    id = describableAttrib(type=str, description=ID_DESCRIPTION)
    insightType = describableAttrib(type=str, description="What kind of insight is this?")
    profileId = describableAttrib(type=str, description="What profile was this insight generated for?")
    dateGeneratedUTCISO = describableAttrib(type=str, description="When was this insight generated?")
    appId = describableAttrib(type=str, description="Which app was this insight generated for?")
    tags = describableAttrib(type=List[InsightTag], factory=list, description="What concepts were tagged in this insight?")
    body = describableAttrib(type=Optional[dict], factory=dict, description="What is the main content captured within the insight?")
    context = describableAttrib(type=str, default=CONTEXTS.INSIGHT, description=CONTEXT_DESCRIPTION, internal=True)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION, internal=True)


@attrs(frozen=True)
class InsightRelatedToConceptTag(InsightTag):
    """
    Tag relating an insight to another concept.
    """
    insightId = describableAttrib(type=str, factory=unique_id, description="What insight is this tag related to?")
    insight = describableAttrib(type=str, description="What insight is this tag related to?")
    id = describableAttrib(type=str, factory=unique_id, description=ID_DESCRIPTION)
    tagged = describableAttrib(type=str, factory=utc_timestamp, description="When was the insight tagged with this tag?")
    relationship = describableAttrib(
        type=Link,
        default=Link(id=CONTEXTS.INSIGHT_TAG_RELATED_TO_RELATIONSHIP, context=CONTEXTS.INSIGHT_TAG_RELATIONSHIP),
        description="What relationship does the tagged concept have with regards to the insight?"
    )
    @insight.default
    def from_insight_id(self):
        return Link(
            id=self.insightId,
            context=CONTEXTS.INSIGHT,
            version=VERSION
        )

