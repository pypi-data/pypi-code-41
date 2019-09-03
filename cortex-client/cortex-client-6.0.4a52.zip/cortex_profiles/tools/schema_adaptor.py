import pydash

from cortex_profiles.utils import head


def upgrade_old_profile_schema(old_schema:dict) -> dict:
    """
    Transforms an old profile schema into a new one ...
    :param old_schema:
    :return:
    """


    keysToRemove = ["tenantId", "environmentId", "id", "createdAt", "version", ]
    remapped_schema = pydash.rename_keys(
        pydash.omit(
            # Remap tags ...
            pydash.set_(
                # Remap taxonomy ... and add label ...
                pydash.set_(
                    # Remap groups ...set group id as name ...
                    pydash.set_(
                        old_schema,
                        "groups",
                        list(map(
                            lambda group: pydash.omit(pydash.rename_keys(group, {"id": "name"}), "version"),
                            old_schema["groups"]
                        ))
                    ),
                    "taxonomy",
                    list(map(
                        lambda tax: pydash.omit(
                            pydash.set_(tax, "parent", head(tax["parents"])) if head(tax["parents"]) else tax,
                            "parents", "children", "attributes"
                        )
                        ,
                        old_schema["taxonomy"]
                    ))
                ),
                "tags",
                list(map(
                    lambda tag: pydash.rename_keys(pydash.omit(tag, "group", "version"), {"id": "name"}),
                    old_schema["tags"]
                ))
            ),
            *keysToRemove
        ),
        {
            "groups": "facets",
            "tags": "attributeTags",
        }
    )
    return remapped_schema


if __name__ == '__main__':
    import os
    import json
    import sys

    old_schema_file = pydash.get(sys.argv, 1, os.path.expanduser("~/Desktop/old-schema.json"))
    new_schema_file = pydash.get(sys.argv, 2, os.path.expanduser("~/Desktop/new-schema.json"))

    with open(new_schema_file, "w") as fhw:
        with open(old_schema_file, "r") as fhr:
            old_schema = json.load(fhr)
        json.dump(
            upgrade_old_profile_schema(old_schema),
            fhw,
            indent=4
        )

