from typing import List

import attr

from cortex_profiles.implicit.schema.implicit_groups import ImplicitGroups
from cortex_profiles.implicit.schema.implicit_tags import ImplicitTags, ImplicitTagTemplates, ImplicitAttributeSubjects
from cortex_profiles.implicit.schema.implicit_templates import tag_template, attr_template
from cortex_profiles.implicit.schema.utils import prepare_template_candidates_from_schema_fields
from cortex_profiles.types.schema import ProfileHierarchySchema, ProfileAttributeSchemaQuery, ProfileSchema
from cortex_profiles.types.schema_config import SchemaConfig
from cortex_profiles.types.utils import describableAttrib
from cortex_profiles.utils import unique_id
from cortex_profiles.implicit.schema.attribute_queries import query_attributes


class HierarchyDescriptionTemplates(object):
    GENERAL = "Group of general attributes that are applicable across use cases."
    INSIGHT_INTERACTION = "Group of attributes related to the profile's interactions on insights."
    APPLICATION_USAGE = "Group of attributes related to information on the profile's application usage."
    MEANINGFUL_INTERACTIONS = "Group of attributes related to a profile's meaingful interactions with the system."
    APP_SPECIFIC = attr_template("Group of attributes related to the {{{app_title}}} app.")
    ALGO_SPECIFIC = attr_template("Group of attributes related to the {{{insight_type}}} algo.")
    CONCEPT_SPECIFIC = "Group of attributes related to different concepts in the system."
    CONCEPT_AGNOSTIC = "Group of attributes that are independent of the different concepts in the system."


class HierarchyNameTemplates(object):
    GENERAL = "general"
    INSIGHT_INTERACTION = ImplicitAttributeSubjects.INSIGHT_INTERACTIONS
    APPLICATION_USAGE = ImplicitAttributeSubjects.APP_USAGE
    MEANINGFUL_INTERACTIONS = ImplicitAttributeSubjects.INTERACTIONS
    APP_SPECIFIC = tag_template("app::{{{app_id}}}")
    ALGO_SPECIFIC = tag_template("algo::{{{insight_type_id}}}")
    CONCEPT_SPECIFIC = "concept-specific"
    CONCEPT_AGNOSTIC = "concept-agnostic"


def prepare_to_be_flattened(parentNode:'RecursiveProfileHierarchyGroup', childNode:'RecursiveProfileHierarchyGroup') -> 'RecursiveProfileHierarchyGroup':
    oldChildName = childNode.name
    # Update the name of the child to have the parents name ...
    e1 = attr.evolve(childNode, name="{}/{}".format(parentNode.name, childNode.name))
    # Update all the children of the child node to point to the child nodes new name
    e2 = attr.evolve(e1, children=[
        attr.evolve(
            child_of_e1,
            parents=[attr.evolve(p, name=e1.name) if p.name == oldChildName else p for p in child_of_e1.parents]
        )
        for child_of_e1 in e1.children
    ])
    # Repeat process for all the children of the node ..
    e3 = attr.evolve(e2, children=[prepare_to_be_flattened(e2, child_of_e2) for child_of_e2 in e2.children])
    return e3


@attr.attrs(frozen=True)
class RecursiveProfileHierarchyGroup(object):
    name = describableAttrib(type=str, description="What is the name of the profile hierarchy node?")
    label = describableAttrib(type=str, description="What is the label of the profile hierarchy node?")
    description = describableAttrib(type=str, description="What is the essential meaning of this group?")
    includedAttributes = describableAttrib(type=ProfileAttributeSchemaQuery, description="What attributes are included in this group?")
    tags = describableAttrib(type=List[str], factory=list, description="What list of tags is applied to this group?")
    parents = describableAttrib(type=List['RecursiveProfileHierarchyGroup'], factory=list, description="What are the parents of this group of attributes ...?")
    children = describableAttrib(type=List['RecursiveProfileHierarchyGroup'], factory=list, description="What are the children of this group of attributes ...?")
    id = describableAttrib(type=str, factory=unique_id, description="What is the unique identifier for this group ...?")

    # Traversal method to help construct a recusive data structure
    def append_children(self, nodes:List['RecursiveProfileHierarchyGroup']) -> 'RecursiveProfileHierarchyGroup':
        """
        Children are to be associated later ...
        :param node:
        :return:
        """
        # The children are all siblings of the parent ...
        if not nodes:
            return self
        head, tail = nodes[0], nodes[1:]
        return self.append_child(head).append_children(tail)

    def append_child(self, node:'RecursiveProfileHierarchyGroup') -> 'RecursiveProfileHierarchyGroup':
        """
        Children are to be associated later ...
        :param node:
        :return:
        """
        return attr.evolve(self, children=self.children+[attr.evolve(node, tags=self.tags+node.tags, parents=node.parents+[self])])

    def to_profile_hierarchy_schema(self, schema:ProfileSchema) -> ProfileHierarchySchema:
        return ProfileHierarchySchema(
            name=self.name,
            label=self.label,
            description=self.description,
            tags=self.tags,
            attributes=query_attributes(self.includedAttributes, schema),
            parents=[x.name for x in self.parents],
            children=[x.name for x in self.children],
            id=self.id
        )

    def flatten(self, schema:ProfileSchema) -> List[ProfileHierarchySchema]:
        schema_to_flatten = attr.evolve(self, children=[prepare_to_be_flattened(self, c) for c in self.children])
        return schema_to_flatten._flatten(schema)

    def _flatten(self, schema:ProfileSchema) -> List[ProfileHierarchySchema]:
        hierarchical_schema = self.to_profile_hierarchy_schema(schema)
        return [hierarchical_schema] + [x for child in self.children for x in child._flatten(schema)]


def derive_hierarchy_from_attribute_tags(schema_config:SchemaConfig, schema:ProfileSchema) -> List[ProfileHierarchySchema]:
    """
    general
    application-usage
        {app}
    insight-interactions
        concept-specific-interactions
            apps-{app}
            algos-{algo}
        concept-agnostic-interactions
            apps-{app}
            algos-{algo}

    # TODO ... implement folders above ...
    # Todo ... implement the following as declared preferences ...

    app-preferences
        {app}
    trading-preferences

    :param attributes:
    :return:
    """

    apps = prepare_template_candidates_from_schema_fields(schema_config, [attr.fields(SchemaConfig).apps])
    algos = prepare_template_candidates_from_schema_fields(schema_config, [attr.fields(SchemaConfig).insight_types])

    hierarchy = (
        RecursiveProfileHierarchyGroup(
            name=HierarchyNameTemplates.GENERAL,
            label=HierarchyNameTemplates.GENERAL,
            description=HierarchyDescriptionTemplates.GENERAL,
            includedAttributes=ProfileAttributeSchemaQuery(attributesWithAnyTags=[ImplicitTags.ASSIGNED.id]),
            tags=[ImplicitTags.ASSIGNED.id]
        ).flatten(schema)
        +
        RecursiveProfileHierarchyGroup(
            name=HierarchyNameTemplates.INSIGHT_INTERACTION,
            label=HierarchyNameTemplates.INSIGHT_INTERACTION,
            description=HierarchyDescriptionTemplates.INSIGHT_INTERACTION,
            includedAttributes=ProfileAttributeSchemaQuery(none=True),
            tags=[ImplicitTags.INSIGHT_INTERACTIONS.id]
        ).append_child(
            RecursiveProfileHierarchyGroup(
                name=HierarchyNameTemplates.CONCEPT_SPECIFIC,
                label=HierarchyNameTemplates.CONCEPT_SPECIFIC,
                description=HierarchyDescriptionTemplates.CONCEPT_SPECIFIC,
                includedAttributes=ProfileAttributeSchemaQuery(none=True),
                tags=[ImplicitTags.CONCEPT_SPECIFIC.id]
            )
            .append_children(
                [
                    RecursiveProfileHierarchyGroup(
                        name=HierarchyNameTemplates.ALGO_SPECIFIC.format(**algo),
                        label=HierarchyNameTemplates.ALGO_SPECIFIC.format(**algo),
                        description=HierarchyDescriptionTemplates.ALGO_SPECIFIC.format(**algo),
                        includedAttributes=ProfileAttributeSchemaQuery(
                            attributesWithAllTags=[ImplicitTags.INSIGHT_INTERACTIONS.id, ImplicitTagTemplates.ALGO_ASSOCIATED(algo).id],
                            attributesInAllGroups=[ImplicitGroups.CONCEPT_ASSOCIATED.id]
                        ),
                        tags=[ImplicitTagTemplates.ALGO_ASSOCIATED(algo).id]
                    )
                    for algo in algos
                ]
            )
        ).append_child(
            RecursiveProfileHierarchyGroup(
                name=HierarchyNameTemplates.CONCEPT_AGNOSTIC,
                label=HierarchyNameTemplates.CONCEPT_AGNOSTIC,
                description=HierarchyDescriptionTemplates.CONCEPT_AGNOSTIC,
                includedAttributes=ProfileAttributeSchemaQuery(none=True),
                tags=[ImplicitTags.CONCEPT_AGNOSTIC.id]
            )
            .append_children(
                [
                    RecursiveProfileHierarchyGroup(
                        name=HierarchyNameTemplates.ALGO_SPECIFIC.format(**algo),
                        label=HierarchyNameTemplates.ALGO_SPECIFIC.format(**algo),
                        description=HierarchyDescriptionTemplates.ALGO_SPECIFIC.format(**algo),
                        includedAttributes=ProfileAttributeSchemaQuery(
                            attributesWithAllTags=[ImplicitTags.INSIGHT_INTERACTIONS.id, ImplicitTagTemplates.ALGO_ASSOCIATED(algo).id],
                            inverse=ProfileAttributeSchemaQuery(attributesInAllGroups=[ImplicitGroups.CONCEPT_ASSOCIATED.id])
                        ),
                        tags=[ImplicitTagTemplates.ALGO_ASSOCIATED(algo).id]
                    )
                    for algo in algos
                ]
            )
        ).flatten(schema)
        +
        RecursiveProfileHierarchyGroup(
            name=HierarchyNameTemplates.APPLICATION_USAGE,
            label=HierarchyNameTemplates.APPLICATION_USAGE,
            description=HierarchyDescriptionTemplates.APPLICATION_USAGE,
            includedAttributes=ProfileAttributeSchemaQuery(none=True),
            tags=[ImplicitTags.APP_USAGE.id]
        ).append_children([
            RecursiveProfileHierarchyGroup(
                name=HierarchyNameTemplates.APP_SPECIFIC.format(**app),
                label=HierarchyNameTemplates.APP_SPECIFIC.format(**app),
                description=HierarchyDescriptionTemplates.APP_SPECIFIC.format(**app),
                includedAttributes=ProfileAttributeSchemaQuery(
                    attributesWithAllTags=[ImplicitTags.APP_USAGE.id, ImplicitTagTemplates.APP_ASSOCIATED(app).id]
                ),
                tags=[ImplicitTags.APP_SPECIFIC.id, ImplicitTagTemplates.APP_ASSOCIATED(app).id]
            )
            for app in apps
        ]).flatten(schema)
        +
        RecursiveProfileHierarchyGroup(
            name=HierarchyNameTemplates.MEANINGFUL_INTERACTIONS,
            label=HierarchyNameTemplates.MEANINGFUL_INTERACTIONS,
            description=HierarchyDescriptionTemplates.MEANINGFUL_INTERACTIONS,
            includedAttributes=ProfileAttributeSchemaQuery(none=True),
            tags=[ImplicitTags.APP_INTERACTION.id]
        ).flatten(schema)
    )
    return hierarchy


if __name__ == '__main__':
    from cortex_profiles.builders.schema import ProfileSchemaBuilder

    schema_config = SchemaConfig(**{
        "apps": [
            {"id": "insights-app-1", "singular": "IA1", "acronym": "IA1"}
        ],
        "insight_types": [
            {"id": "type-1-insight", "singular": "Type 1 Insight", "plural": "Type 1 Insights", "acronym": "T1I"},
            {"id": "type-2-insight", "singular": "Type 2 Insight", "plural": "Type 2 Insights", "acronym": "T2I"}
        ],
        "concepts": [
            {"id": "cortex/company", "singular": "company", "plural": "companies"},
            {"id": "cortex/sector", "singular": "sector", "plural": "sectors"},
            {"id": "cortex/market_index", "singular": "market index", "plural": "market indices"},
            {"id": "cortex/country", "singular": "country", "plural": "countries"},
            {"id": "cortex/market_cap_buckets", "singular": "market cap", "plural": "market caps"}
        ],
        "interaction_types": [
            {"id": "presented", "verb": "presented", "verbInitiatedBySubject": False},
            {"id": "viewed", "verb": "viewed"},
            {"id": "ignored", "verb": "ignored"},
            {"id": "liked", "verb": "liked"},
            {"id": "disliked", "verb": "disliked"}
        ],
        "timed_interaction_types": [
            {"id": "viewed", "verb": "viewed"}
        ],
        "application_events": [
            {
                "relationship": {
                    "id": "searched", "verb": "searched", "past": "searched"
                },
                "relatedType": {
                    "id": "cortex/company", "singular": "company", "plural": "companies"
                }
            }
        ]
    })

    schema = ProfileSchemaBuilder().append_tag_oriented_schema_from_config(schema_config).append_hierarchical_schema_from_config(schema_config).get_schema()
    import os, json
    with open(os.path.expanduser("~/Desktop/test-schema.json"), "w") as fh:
        print(schema)
        json.dump(attr.asdict(schema), fh, indent=4)

