from .element import ABCElement


class _Node(ABCElement):
    schema = {
        **ABCElement.schema,
        "uid": {"type": "string", "required": True, "regex": "^[a-zA-Z]\\w*$"},
        "display_name": {
            "type": "string",
            "required": False,
            "default_setter": lambda doc: doc["uid"],
        },
        "location": {
            "type": "dict",
            "required": True,
            "schema": ABCElement.location_schema(True),
        },
        "schematic_location": {
            "type": "dict",
            "required": False,
            "schema": ABCElement.location_schema(False),
            "default_setter": lambda doc: doc["location"],
        },
        "tags": {"type": "list", "required": False, "schema": {"type": "string"}},
    }


class Junction(_Node):
    pass


class LevelBoundary(_Node):
    pass


class FlowBoundary(_Node):
    pass


class Storage(_Node):
    schema = {
        **_Node.schema,
        "level_volume": {
            "type": "list",
            "required": True,
            "minlength": 2,
            "schema": {
                "type": "dict",
                "schema": {
                    "level": {"type": "float", "required": True},
                    "volume": {"type": "float", "required": True, "min": 0},
                },
            },
        },
    }


def _get_all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        (s for c in cls.__subclasses__() for s in _get_all_subclasses(c))
    )


_all_nodes = {
    element_class.__name__: element_class
    for element_class in _get_all_subclasses(_Node)
    if not element_class.__name__.startswith("_")
}


def instantiate(attribute_mapping, validate_normalize=True):
    class_name = attribute_mapping.get("type", None)
    if not class_name:
        raise ValueError("Cannot instantiate: missing attribute 'type'")
    element_class = _all_nodes.get(class_name, None)
    if not element_class:
        raise ValueError("link type '{}' not found".format(class_name))
    return element_class(**attribute_mapping, validate_normalize=validate_normalize)
