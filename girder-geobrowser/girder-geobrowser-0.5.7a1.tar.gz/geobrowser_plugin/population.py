import click
import json
from bson.objectid import ObjectId

from girder.models.collection import Collection
from girder.utility.path import lookUpPath, split
from girder.exceptions import ResourcePathNotFound


@click.command(name='populate-collection-meta',
               short_help='Populates a collection with the provided metadata',
               help='Populates a collection\'s meta field with '
                    'the provided JSON data')
@click.option('-i', '--id', 'ids', multiple=True,
              help="Used to specify a collection ID to extract metadata to.")
@click.option('-p', '--path', 'paths', multiple=True,
              help="Used to specify a girder path to extract metadata to. "
              "Default behavior is to create this path if it doesn't exist")
@click.option('-d', '--data', required=True,
              help="The metadata to populate the desired collection(s) with.")
def populate(ids, paths, data):
    if not (ids or paths):
        click.echo('Error: No destination specified')
        return

    data = json.load(open(data, 'r'))
    totalTargets = len(ids) + len(paths)
    success = 0

    for collectionId in ids:
        collection = Collection().findOne({
            '_id': ObjectId(collectionId)
        })

        if (collection):
            Collection().setMetadata(collection=collection, metadata=data)
            success += 1
        else:
            click.echo('Warning: No collection found with ID: ' + collectionId)

    for path in paths:
        # Truncates anything past the collection level
        path = '/'.join(split(path.lstrip('/'))[0:2])

        try:
            doc = lookUpPath(path, force=True)
            if doc['model'] != 'collection':
                click.echo('Warning: Ignoring non-collection path: ' + path)
                continue
            doc = doc['document']
        except(ResourcePathNotFound):
            name = split(path)[1]
            doc = Collection().createCollection(name, reuseExisting=True)

        Collection().setMetadata(collection=doc, metadata=data)
        success += 1

    click.echo('Successfully set metadata on '
               + str(success) + '/' + str(totalTargets) + ' targets')
