from pkg_resources import DistributionNotFound, get_distribution

import girder.api.v1.item
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import filtermodel
from girder.constants import AccessType, TokenScope
from girder.exceptions import RestException
from girder.models.folder import Folder
from girder.models.item import Item as ItemModel
from girder.plugin import GirderPlugin, getPlugin


try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass


class ItemResource(girder.api.v1.item.Item):
    def __init__(self, apiRoot):
        super(ItemResource, self).__init__()
        apiRoot.item.route('GET', ('find', 'geometa', ), self.findWithGeometa)

    @access.public(scope=TokenScope.DATA_READ)
    @filtermodel(model=ItemModel, addFields=['geometa'])
    @autoDescribeRoute(
        Description('List or search for items; include geometa in the returned data.')
        .notes('You must pass either a "itemId" or "text" field '
               'to specify how you are searching for items.  '
               'If you omit one of these parameters the request will fail and respond : '
               '"Invalid search mode."')
        .responseClass('Item', array=True)
        .param('folderId', 'Pass this to list all items in a folder.',
               required=False)
        .param('text', 'Pass this to perform a full text search for items.',
               required=False)
        .param('name', 'Pass to lookup an item by exact name match. Must '
               'pass folderId as well when using this.', required=False)
        .pagingParams(defaultSort='lowerName')
        .errorResponse()
        .errorResponse('Read access was denied on the parent folder.', 403)
    )
    def findWithGeometa(self, folderId, text, name, limit, offset, sort):
        """
        Get a list of items with given search parameters. Currently accepted
        search modes are:

        1. Searching by folderId, with optional additional filtering by the name
           field (exact match) or using full text search within a single parent
           folder. Pass a "name" parameter or "text" parameter to invoke these
           additional filters.
        2. Searching with full text search across all items in the system.
           Simply pass a "text" parameter for this mode.
        """
        user = self.getCurrentUser()

        if folderId:
            folder = Folder().load(
                id=folderId, user=user, level=AccessType.READ, exc=True)
            filters = {}
            if text:
                filters['$text'] = {
                    '$search': text
                }
            if name:
                filters['name'] = name
            return Folder().childItems(
                folder=folder, limit=limit, offset=offset, sort=sort, filters=filters)
        elif text is not None:
            return self._model.textSearch(
                text, user=user, limit=limit, offset=offset, sort=sort)
        else:
            raise RestException('Invalid search mode.')


class GirderPlugin(GirderPlugin):
    DISPLAY_NAME = 'Geo Heatmap'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        getPlugin('geometa').load(info)

        ItemResource(info['apiRoot'])
