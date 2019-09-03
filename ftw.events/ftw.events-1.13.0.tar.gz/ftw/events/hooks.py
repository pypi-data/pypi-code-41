from Products.CMFCore.utils import getToolByName


def default_profile_installed(portal):
    reindex_indexes(portal)


def reindex_indexes(portal):
    """
    `plone.app.events` replaces the start and end index by a
    RecurringDateIndex (before DateIndex) but it omits to reindex
    the new index. This causes the loss of the start and end index
    data of every content. So we need to take care of reindexing
    the indexes.
    """
    catalog = getToolByName(portal, 'portal_catalog')
    catalog.reindexIndex('start', None)
    catalog.reindexIndex('end', None)
