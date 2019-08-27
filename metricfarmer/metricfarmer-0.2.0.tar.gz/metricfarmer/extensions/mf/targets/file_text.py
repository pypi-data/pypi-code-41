import os

from metricfarmer.exceptions import ExtensionException


def target_file_text(metrics, **kwargs):
    if 'path' not in kwargs:
        raise ExtensionException('Path parameter must be specified for mf.file_text')

    path = kwargs['path']
    override = kwargs.get('override', False)
    if os.path.exists(path) and not override:
        raise ExtensionException('Given file already exists. Set override parameter to True tpo avoid this. '
                                 'Path: {}'.format(path))

    with open(path, 'w') as result_file:
        for name, metric in metrics.items():
            result_file.write('{metric}: {result}\n'.format(
                metric=name, result=metric['result']
            ))
