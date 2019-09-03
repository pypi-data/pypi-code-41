from typing import List
import pydash

from cortex_profiles.builders.schema import ProfileSchemaBuilder
from cortex_profiles.implicit.schema.utils import custom_attributes
from cortex_profiles.types.schema import ProfileTagSchema, ProfileValueTypeSummary, ProfileSchema
from cortex_profiles.types.schema_config import SchemaConfig
from cortex_profiles.utils import converter_for_classes, flatten_list_recursively

from cortex_profiles.tools.schema_adaptor import upgrade_old_profile_schema


def schema_config_dict_to_schema(schema_config_dict:dict) -> ProfileSchema:
    schema_config_template = SchemaConfig(**schema_config_dict["fill_implicit_schema_template_with"])
    additional_attributes = flatten_list_recursively([
        custom_attributes(
            attr_group["attributes"],
            schema_config_template,
            converter_for_classes(attr_group["valueType"], ProfileValueTypeSummary),
            tags=attr_group.get("tags", [])
        )
        for attr_group in schema_config_dict.get("additional_groups_of_attributes", [])
    ])
    additional_tags = [
        converter_for_classes(x, ProfileTagSchema)
        for x in schema_config_dict.get("additional_attribute_tags", [])
    ]
    disabled_attributes = schema_config_dict.get("disabled_attributes", [])
    old_sdk_schema = (
        ProfileSchemaBuilder()
            .append_tag_oriented_schema_from_config(schema_config_template, disabledAttributes=disabled_attributes, additional_tags=additional_tags, profile_link_contexts=schema_config_dict.get("profile_link_contexts"))
            .append_hierarchical_schema_from_config(schema_config_template, disabledAttributes=disabled_attributes)
            .append_attributes(additional_attributes)
            .append_tags(additional_tags)
            .get_schema()
    )
    return old_sdk_schema


def build_custom_schema(schema_config_dict:dict) -> dict:
    """
    Helps build a profile schema ...

    :param schema_config_dict:
    :return:
    """
    from functools import reduce
    schemas = list(map(schema_config_dict_to_schema, schema_config_dict.get("schema_configs", [])))
    old_sdk_schema = reduce(lambda x, y: x + y, schemas).dict()
    return pydash.merge(
        upgrade_old_profile_schema(old_sdk_schema),
        schema_config_dict.get("additional_fields", {})
    )

def main():
    import os
    import sys
    import json

    schema_config_file = os.path.expanduser(pydash.get(sys.argv, 1, "~/Workspace/git/bridgeweave-bwii-profile-builder/old-data/company-profile-schema-config-v8.json"))
    # schema_config_file = pydash.get(sys.argv, 1, os.path.expanduser("~/Workspace/git/bridgeweave-bwii-profile-builder/old-data/profile-schema-config-v8.json"))
    schema_file = os.path.expanduser(pydash.get(sys.argv, 2, "~/Desktop/profile-schema-v8.json"))
    with open(schema_file, "w") as fhw:
        with open(schema_config_file, "r") as fh:
            new_schema = build_custom_schema(json.load(fh))
        json.dump(new_schema, fhw, indent=4)


if __name__ == '__main__':
    main()