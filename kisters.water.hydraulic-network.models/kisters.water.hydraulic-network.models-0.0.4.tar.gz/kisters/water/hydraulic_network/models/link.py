from .element import ABCElement


class _Link(ABCElement):
    schema = {
        **ABCElement.schema,
        "uid": {"type": "string", "required": True, "regex": "^[a-zA-Z]\\w*$"},
        "source_uid": {"type": "string", "required": True},
        "target_uid": {"type": "string", "required": True},
        "display_name": {
            "type": "string",
            "required": False,
            "default_setter": lambda doc: doc["uid"],
        },
        "vertices": {
            "type": "list",
            "required": False,
            "schema": {"type": "dict", "schema": ABCElement.location_schema(False)},
        },
        "schematic_vertices": {
            "type": "list",
            "required": False,
            "schema": {"type": "dict", "schema": ABCElement.location_schema(False)},
        },
    }


class Delay(_Link):
    schema = {
        **_Link.schema,
        "transit_time": {"type": "float", "required": True, "default": 0.0},
    }


class Pipe(_Link):
    schema = {
        **_Link.schema,
        "diameter": {"type": "float", "min": 0, "required": True},
        "length": {"type": "float", "required": True, "min": 0},
        "roughness": {"type": "float", "required": True, "min": 0},
        "model": {
            "type": "string",
            "required": True,
            "allowed": ["darcy-weisbach", "hazen-williams"],
        },
        "max_time_step": {"type": "float", "required": False, "min": 0.0},
        "check_valve": {"type": "boolean", "required": True, "default": False},
    }


class Channel(_Link):
    schema = {
        **_Link.schema,
        "stations": {
            "type": "list",
            "required": True,
            "minlength": 1,
            "schema": {
                "type": "dict",
                "schema": {
                    "distance": {"type": "float", "required": False, "min": 0.0},
                    "roughness": {"type": "float", "required": True, "min": 0.0},
                    "cross_section": {
                        "type": "list",
                        "minlength": 3,
                        "schema": {
                            "type": "dict",
                            "schema": {
                                "lr": {"type": "float", "required": True},
                                "z": {"type": "float", "required": True},
                            },
                        },
                    },
                },
            },
        },
        "length": {"type": "float", "required": True, "min": 0},
        "roughness_model": {
            "type": "string",
            "required": True,
            "allowed": ["chezy", "manning"],
            "default": "chezy",
        },
        "model": {
            "type": "string",
            "required": True,
            "allowed": ["saint-venant", "inertial-wave", "diffusive-wave"],
        },
        "max_time_step": {"type": "float", "required": False, "min": 0.0},
    }


class FlowControlledStructure(_Link):
    schema = {
        **_Link.schema,
        "min_flow": {"type": "float", "required": False},
        "max_flow": {"type": "float", "required": False},
    }


class _PumpTurbine(_Link):
    schema = {
        **_Link.schema,
        "speed": {
            "type": "list",
            "required": False,
            "minlength": 1,
            "schema": {
                "type": "dict",
                "schema": {
                    "flow": {"type": "float", "required": True, "min": 0.0},
                    "head": {"type": "float", "required": True, "min": 0.0},
                    "speed": {
                        "type": "float",
                        "required": True,
                        "min": 0.0,
                        "default": 1.0,
                    },
                },
            },
        },
        "efficiency": {
            "type": "list",
            "required": False,
            "minlength": 1,
            "schema": {
                "type": "dict",
                "schema": {
                    "flow": {"type": "float", "required": True, "min": 0.0},
                    "head": {"type": "float", "required": True, "min": 0.0},
                    "efficiency": {
                        "type": "float",
                        "required": True,
                        "min": 0.0,
                        "max": 1.0,
                    },
                },
            },
        },
        "length": {"type": "float", "required": False, "min": 0.0},
        "min_flow": {"type": "float", "required": False, "min": 0.0},
        "max_flow": {"type": "float", "required": False},
        "min_head": {"type": "float", "required": False, "min": 0.0},
        "max_head": {"type": "float", "required": False},
        "min_power": {"type": "float", "required": False, "min": 0.0},
        "max_power": {"type": "float", "required": False},
        "min_speed": {"type": "float", "required": False, "min": 0.0},
        "max_speed": {"type": "float", "required": False},
        "head_tailwater_correction": {
            "type": "list",
            "required": False,
            "minlength": 0,
            "schema": {
                "type": "dict",
                "schema": {
                    "link_uid": {
                        "type": "string",
                        "required": True,
                        "regex": "^[a-zA-Z]\\w*$",
                    },
                    "power": {"type": "integer", "required": True, "min": 0},
                    "value": {"type": "float", "required": True},
                },
            },  # By convention, this polynomial is added to the difference between up- and downstream levels
        },
        "other_constraints": {
            "type": "list",
            "required": False,
            "minlength": 0,
            "schema": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "flow_power": {"type": "integer", "required": True, "min": 0},
                        "head_power": {"type": "integer", "required": True, "min": 0},
                        "value": {"type": "float", "required": True},
                    },
                },  # By convention, every polynomial will be added a constraint less or equal than zero.
            },
        },
    }


class Pump(_PumpTurbine):
    pass


class Turbine(_PumpTurbine):
    pass


class Valve(_Link):
    schema = {
        **_Link.schema,
        "model": {
            "type": "string",
            "required": True,
            "allowed": ["prv", "psv", "pbv", "fcv", "tcv", "gpv"],
        },
        "coefficient": {"type": "float", "required": False, "min": 0},
        "diameter": {"type": "float", "required": True, "min": 0},
        "setting": {"type": "float", "required": True},
    }


class Weir(_Link):
    schema = {
        **_Link.schema,
        "model": {
            "type": "string",
            "required": True,
            "allowed": ["free", "submerged", "dynamic"],
        },
        "coefficient": {"type": "float", "required": True, "min": 0},
        "min_crest_level": {"type": "float", "required": True},
        "max_crest_level": {"type": "float", "required": True},
        "crest_width": {"type": "float", "required": True, "min": 0},
    }


class Orifice(_Link):
    schema = {
        **_Link.schema,
        "model": {
            "type": "string",
            "required": True,
            "allowed": ["free", "submerged", "dynamic"],
        },
        "coefficient": {"type": "float", "required": True, "min": 0},
        "aperture": {"type": "float", "required": True, "min": 0},
    }


def _get_all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        (s for c in cls.__subclasses__() for s in _get_all_subclasses(c))
    )


_all_links = {
    element_class.__name__: element_class
    for element_class in _get_all_subclasses(_Link)
    if not element_class.__name__.startswith("_")
}


def instantiate(attribute_mapping, validate_normalize=True):
    class_name = attribute_mapping.get("type", None)
    if not class_name:
        raise ValueError("Cannot instantiate: missing attribute 'type'")
    element_class = _all_links.get(class_name, None)
    if not element_class:
        raise ValueError("link type '{}' not found".format(class_name))
    return element_class(**attribute_mapping, validate_normalize=validate_normalize)
