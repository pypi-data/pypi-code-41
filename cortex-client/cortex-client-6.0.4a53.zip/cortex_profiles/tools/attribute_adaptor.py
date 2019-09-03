import json
import pydash


def upgrade_old_attributes_into_new_ones(attributes, schema="cortex/end-user:1"):
    keysToRemove = ["tenantId", "environmentId", "onLatestProfile", "commits", "attributeValue.summary"]
    upgraded_attributes = list(map(
        lambda x: pydash.set_(
            pydash.set_(
                pydash.omit(x, *keysToRemove),
                "profileSchema",
                schema
            ),
            "profileId",
            "{}".format(x["profileId"])
        ),
        attributes if isinstance(attributes, list) else [attributes]
    ))
    return upgraded_attributes if isinstance(attributes, list) else upgraded_attributes[0]


if __name__ == '__main__':
    import sys
    import os

    old_attrs = os.path.expanduser(pydash.get(sys.argv, 1, "~/Desktop/old-attributes.json"))
    new_attrs = os.path.expanduser(pydash.get(sys.argv, 2, "~/Desktop/new-attributes.json"))
    profile_schema = pydash.get(sys.argv, 3, "cortex/end-user:1")
    with open(new_attrs, "w") as fhw:
        with open(old_attrs, "r") as fhr:
            attributes = json.load(fhr)
        json.dump(upgrade_old_attributes_into_new_ones(attributes, schema=profile_schema), fhw, indent=4)
