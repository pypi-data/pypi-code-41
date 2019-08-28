"""Utility classes and functions"""
from plone import api
from Products.CMFCore.utils import getToolByName

_marker = object()


class PrefixedFieldProperty(object):

    def __init__(self, field, prefix=''):
        self.field = field
        self.__name__ = field.__name__
        self.attribute_name = prefix + self.__name__

    def __get__(self, inst, klass):
        attribute = getattr(inst.context, self.attribute_name, _marker)
        if attribute is _marker:
            field = self.field.bind(inst)
            attribute = getattr(field, 'default', _marker)
            if attribute is _marker:
                raise AttributeError(self.__name__)
        return attribute

    def __set__(self, inst, value):
        field = self.field.bind(inst)
        field.validate(value)
        if field.readonly:
            raise ValueError(self.__name__, 'field is readonly')

        setattr(inst.context, self.attribute_name, value)


def uuidToCatalogBrainUnrestricted(uuid):
    """Given a UUID, attempt to return a catalog brain even when the object is
    not visible for the logged in user (e.g. during anonymous traversal)
    """

    site = api.portal.get()
    if site is None:
        return None

    catalog = getToolByName(site, 'portal_catalog', None)
    if catalog is None:
        return None

    result = catalog.unrestrictedSearchResults(UID=uuid)
    if len(result) != 1:
        return None

    return result[0]


def uuidToObject(uuid):
    """Given a UUID, attempt to return a content object. Will return
    None if the UUID can't be found. Raises Unauthorized if the current
    user is not allowed to access the object.
    """

    brain = uuidToCatalogBrainUnrestricted(uuid)
    if brain is None:
        return None

    return brain.getObject()
