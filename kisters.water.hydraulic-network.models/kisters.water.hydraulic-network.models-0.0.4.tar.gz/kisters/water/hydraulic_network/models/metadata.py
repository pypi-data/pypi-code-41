from .element import ABCElement


class Metadata(ABCElement):
    static_properties = "projection", "datum", "created"

    def get_static_properties(self) -> dict:
        return {prop: self[prop] for prop in self.static_properties}

    schema = {
        "created": ABCElement.schema["created"],
        "projection": {"type": "string", "required": True, "default": "EPSG:3857"},
        "datum": {"type": "string", "required": True, "default": "unknown"},
        "num_hierarchy_levels": {"type": "integer", "required": False, "default": 1},
        "extent": {
            "type": "dict",
            "required": False,
            "schema": {
                "x": {
                    "type": "list",
                    "required": True,
                    "schema": {"type": "float"},
                    "minlength": 2,
                    "maxlength": 2,
                },
                "y": {
                    "type": "list",
                    "required": True,
                    "schema": {"type": "float"},
                    "minlength": 2,
                    "maxlength": 2,
                },
                "z": {
                    "type": "list",
                    "required": True,
                    "schema": {"type": "float"},
                    "minlength": 2,
                    "maxlength": 2,
                },
            },
        },
        "schematic_extent": {
            "type": "dict",
            "required": False,
            "schema": {
                "x": {
                    "type": "list",
                    "required": True,
                    "schema": {"type": "float"},
                    "minlength": 2,
                    "maxlength": 2,
                },
                "y": {
                    "type": "list",
                    "required": True,
                    "schema": {"type": "float"},
                    "minlength": 2,
                    "maxlength": 2,
                },
                "z": {
                    "type": "list",
                    "required": False,
                    "schema": {"type": "float"},
                    "minlength": 2,
                    "maxlength": 2,
                },
            },
        },
    }
