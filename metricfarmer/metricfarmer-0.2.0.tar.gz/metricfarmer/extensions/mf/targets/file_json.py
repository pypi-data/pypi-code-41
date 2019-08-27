import json
import os

from metricfarmer.exceptions import ExtensionException


def target_file_json(metrics, **kwargs):
    if 'path' not in kwargs:
        raise ExtensionException('Path parameter must be specified for mf.file_json')

    path = kwargs['path']
    override = kwargs.get('override', False)
    if os.path.exists(path) and not override:
        raise ExtensionException('Given file already exists. Set override parameter to True tpo avoid this. '
                                 'Path: {}'.format(path))

    metrics_json = json.dumps(metrics, indent=4)
    with open(path, 'w') as result_file:
        result_file.writelines(metrics_json)
