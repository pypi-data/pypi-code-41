import click

from girder.models.collection import Collection
from girder.models.file import File
from girder.models.item import Item
from girder.models.user import User
from girder.utility.path import lookUpPath
from geometa.rest import create_geometa


@click.command(name="extract-geospatial",
               short_help='Manually extract geospatial data',
               help='Manually extract geospatial data on all '
                    'items under the provided paths')
@click.option('-p', '--path', multiple=True, default='/', show_default=True,
              help="Used to specify a path under which to extract data.")
def extract(path):
    resources = []

    if '/' in path:
        resources += list(Collection().find())
        resources += list(User().find())
    elif '/collection' in path:
        resources += list(Collection().find())
    elif '/user' in path:
        resources += list(User().find())
    else:
        resources += [lookUpPath(p)['document'] for p in path]

    for resource in resources:
        items = list(Item().find({
            'baseParentId': resource['_id']
        }))

        for item in items:
            files = list(File().find({
                'itemId': item['_id']
            }))

            for file in files:
                create_geometa(item, file)
