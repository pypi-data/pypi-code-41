from typing import List

import attr
import pydash

from cortex_profiles.utils import list_converter, attr_fields_except, converter_for_classes


@attr.s(frozen=True)
class OptionalDescriber(object):
    id = attr.ib(type=str)
    adjective = attr.ib(type=str)
    adverb = attr.ib(type=str)
    include = attr.ib(type=bool)
    optionalAdjective = attr.ib(type=str)
    optionalAdverb = attr.ib(type=str)

    @optionalAdjective.default
    def defaultOptionalAdjective(self):
        if self.include:
            return self.adjective
        return ""

    @optionalAdverb.default
    def defaultOptionalAdverb(self):
        if self.include:
            return self.adverb
        return ""


@attr.s(frozen=True)
class Subject(object):
    id = attr.ib(type=str, default="")
    singular = attr.ib(type=str, default="")
    Singular = attr.ib(type=str)
    plural = attr.ib(type=str, default="")
    Plural = attr.ib(type=str)
    acronym = attr.ib(type=str, default="")

    @Singular.default
    def defaultSingular(self):
        return pydash.title_case(self.singular)

    @Plural.default
    def defaultPlural(self):
        return pydash.title_case(self.plural)


@attr.s(frozen=True)
class Verb(object):
    id = attr.ib(type=str)
    verb = attr.ib(type=str)
    past = attr.ib(type=str, default="")
    verbInitiatedBySubject = attr.ib(type=bool, default=True)
    Verb = attr.ib(type=str)
    verbStatement = attr.ib(type=str)
    Past = attr.ib(type=str)

    @Verb.default
    def defaultVerb(self):
        return pydash.title_case(self.verb)

    @Past.default
    def defaultPast(self):
        return pydash.title_case(self.past)

    @verbStatement.default
    def defaultVerbStatement(self):
        return "{} to".format(self.verb) if not self.verbInitiatedBySubject else "{} by".format(self.verb)


@attr.s(frozen=True)
class RelationshipConfig(object):
    relationship = attr.ib(type=Verb, converter=lambda x: converter_for_classes(x, Verb))
    relatedType = attr.ib(type=Subject, converter=lambda x: converter_for_classes(x, Subject))


@attr.s(frozen=True)
class SchemaConfig(object):
    apps = attr.ib(type=List[Subject], converter=lambda l: list_converter(l, Subject))
    insight_types = attr.ib(type=List[Subject], converter=lambda l: list_converter(l, Subject))
    concepts = attr.ib(type=List[Subject], converter=lambda l: list_converter(l, Subject))
    interaction_types = attr.ib(type=List[Verb], converter=lambda l: list_converter(l, Verb))
    timed_interaction_types = attr.ib(type=List[Verb], converter=lambda l: list_converter(l, Verb))
    application_events = attr.ib(type=List[RelationshipConfig], converter=lambda l: list_converter(l, RelationshipConfig), factory=list)
    timed_application_events = attr.ib(type=List[RelationshipConfig], converter=lambda l: list_converter(l, RelationshipConfig), factory=list)


CONCEPT_SPECIFIC_INTERACTION_FIELDS = [attr.fields(SchemaConfig).insight_types, attr.fields(SchemaConfig).concepts, attr.fields(SchemaConfig).interaction_types]
CONCEPT_SPECIFIC_DURATION_FIELDS = [attr.fields(SchemaConfig).insight_types, attr.fields(SchemaConfig).concepts, attr.fields(SchemaConfig).timed_interaction_types]
INTERACTION_FIELDS = [attr.fields(SchemaConfig).insight_types, attr.fields(SchemaConfig).interaction_types, attr.fields(SchemaConfig).apps]
# Should interactions be app specific???
APP_SPECIFIC_FIELDS = [attr.fields(SchemaConfig).apps]
APP_INTERACTION_FIELDS = [attr.fields(SchemaConfig).apps, attr.fields(SchemaConfig).application_events]
TIMED_APP_INTERACTION_FIELDS = [attr.fields(SchemaConfig).apps, attr.fields(SchemaConfig).timed_application_events]
