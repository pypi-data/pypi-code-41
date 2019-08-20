from argparse import ArgumentParser
from pathlib import Path
import importlib.util
import inspect
import os
import sys

from pagr.services import ServiceLoader


def run_folder(argv=None):
    parser = ArgumentParser(description='pagr - the Python Aggregator')
    parser.add_argument('folder', metavar='myfolder', type=str,
                        help='a base folder in which all services/metrics should be executed')
    parser.add_argument('-m', '--metric', metavar='metric class name', type=str, nargs='*', action='append',
                        help='The Class name of a metric to be executed')

    args = parser.parse_args(argv)
    path = args.folder
    desired_metrics = []
    if args.metric is not None:
        for m in args.metric:
            if m not in desired_metrics:
                desired_metrics.append(m[0])
    if os.environ.get('PAGR_METRICS', None) is not None:
        for m in os.environ['PAGR_METRICS'].split(','):
            desired_metrics.append(m)

    module_name = os.path.basename(os.path.normpath(path))
    abspath = os.path.abspath(path)

    services = ServiceLoader(path)
    metrics = dict()

    if not os.path.isdir(abspath):
        raise Exception(f'Given folder {abspath} could not be found')

    # import metrics
    for pyfile in Path(os.path.join(abspath, 'metrics')).glob('**/*.py'):
        service_name = module_name + '.metrics.' + os.path.split(pyfile)[1].rsplit('.py')[0]

        spec = importlib.util.spec_from_file_location(service_name, pyfile)
        service = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(service)

        for name, obj in inspect.getmembers(service):
            if not inspect.isclass(obj):
                continue
            if not name.endswith('Metric'):
                continue
            if len(desired_metrics) > 0 and name not in desired_metrics:
                continue

            if name in metrics:
                raise Exception(f'Metric {name} already exists')

            metrics[name] = m = {
                'name': name,
                'instance': obj(services)
            }
            print('running metric', m['name'])
            m['instance'].run()

    return abspath, services, metrics


if __name__ == '__main__':
    run_folder(sys.argv[1:])
