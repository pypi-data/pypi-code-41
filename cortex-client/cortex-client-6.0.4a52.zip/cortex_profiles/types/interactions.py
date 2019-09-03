from typing import Optional

import attr
from attr import attrs

from cortex_profiles.schemas.schemas import CONTEXTS, VERSION
from cortex_profiles.types.utils import describableAttrib, CONTEXT_DESCRIPTION, VERSION_DESCRIPTION
from cortex_profiles.utils import unique_id

ID_DESCRIPTION = "What is the id of this piece of data?"


@attrs(frozen=True)
class UserActivity(object):
    """
    Base abstraction of a specific profile's in-app activity.
    """
    id = describableAttrib(type=str, description=ID_DESCRIPTION)
    profileId = describableAttrib(type=str, description="What profile initiated the activity?")
    appId = describableAttrib(type=str, description="Which app did this activity occur on?")
    isoUTCStartTime = describableAttrib(type=str, description="When did this activity start?")
    isoUTCEndTime = describableAttrib(type=Optional[str], description="When did this activity end?")
    context = describableAttrib(type=str, description=CONTEXT_DESCRIPTION, internal=True)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION, internal=True)


@attrs(frozen=True)
class Session(object):
    """
    A session initiated by the profile on a specific app.
    """
    id = describableAttrib(type=str, description=ID_DESCRIPTION)
    profileId = describableAttrib(type=str, description="What profile initiated the session?")
    appId = describableAttrib(type=str, description="Which app did this session occur on?")
    isoUTCStartTime = describableAttrib(type=str, description="When did this session start?")
    isoUTCEndTime = describableAttrib(type=str, description="When did this session end?")
    durationInSeconds = describableAttrib(type=float, description="How long did the session last?")
    context = describableAttrib(type=str, default=CONTEXTS.SESSION, description=CONTEXT_DESCRIPTION, internal=True)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION, internal=True)


@attrs(frozen=True)
class InteractionEvent(object):
    """
    Any interaction that the profile can initiate.
    """
    profileId = describableAttrib(type=str, description="Which profile was responsible for this interaction?")
    interactionType = describableAttrib(type=str, description="What type of interaction was performed by the profile?")
    interactionDateISOUTC = describableAttrib(type=str, description="When did the interaction occur?")

    id = describableAttrib(type=str, factory=unique_id, description=ID_DESCRIPTION)
    sessionId = describableAttrib(type=Optional[str], factory=lambda: None, description="What session did the interaction occur in?")
    properties = describableAttrib(type=dict, factory=dict, description="What additional information needs to be captured based on the type of interaction that occured??")
    custom = describableAttrib(type=Optional[dict], factory=dict, description="What custom, application specfic information do we seek to capture with respect to the interaction?")
    context = describableAttrib(type=str, default=CONTEXTS.INTERACTION, description=CONTEXT_DESCRIPTION, internal=True)
    version = describableAttrib(type=str, default=VERSION, description=VERSION_DESCRIPTION, internal=True)


@attrs(frozen=True)
class InsightInteractionEvent(InteractionEvent):
    """
    Any interaction that the profile can initiate on an insight.
    """
    # Setting a factory to get over the extension limitations ...
    # But insightId is actually required ... this the validator ...
    insightId = describableAttrib(type=str, factory=lambda:None, validator=attr.validators.instance_of(str), description="Which insight was interacted on?")


# - [ ] TODO ... what is the list of interaction types?
