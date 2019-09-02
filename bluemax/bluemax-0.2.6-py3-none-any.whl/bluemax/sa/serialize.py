"""
    Introspective helpers for serializing SqlAlchemy Objects
"""
import logging
from sqlalchemy.orm import class_mapper, ColumnProperty

LOGGER = logging.getLogger(__name__)


def dumps(item):
    """ returns a dictionary of item properties """
    result = {"_type_": item.__class__.__name__}
    for prop in class_mapper(item.__class__).iterate_properties:
        if prop.key[0] == "_":
            continue
        if isinstance(prop, ColumnProperty):
            result[prop.key] = getattr(item, prop.key)
    return result


def loads(values, item):
    """ sets properties from values"""
    for prop in class_mapper(item.__class__).iterate_properties:
        if prop.key[0] == "_":
            continue
        if isinstance(prop, ColumnProperty) and prop.key in values.keys():
            setattr(item, prop.key, values.get(prop.key))
