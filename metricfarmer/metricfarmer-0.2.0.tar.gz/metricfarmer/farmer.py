import os
from pathlib import Path
import sys
import datetime

import click
from colorama import Fore, Style
import json
import pkg_resources
import re

from metricfarmer.exceptions import ConfigException, InvalidTargetException
from metricfarmer.helpers import walker

version = "0.1"
help = "http//metric-farmer.readthedocs.org"

greetings = """
*********************
*   Metric-Farmer   *
*********************
version: {version} 
help:    {help}""".format(version=version, help=help)

mf_replace_re = re.compile(r':MF_REPLACE:([\w]*)$', re.VERBOSE)


class MetricFarmerApp:
    def __init__(self):

        self.farm_folders = []
        self.metrics = {}
        self.sources = {}
        self.targets = {}
        self.settings = {}

        self.tags = []

        self.extensions = {}

    def load_config(self, farmer):
        if farmer is not None and farmer != "":
            if not os.path.exists(farmer):
                raise ConfigException('Farmer folder not found: {config}'.format(config=farmer))
            self.farm_folders.append(farmer)
        else:
            self.farm_folders = [
                os.path.join(os.path.dirname(__file__), "basics"),
            ]
            cwd = os.getcwd()
            farm_user = os.path.join(os.path.expanduser("~"), ".farmer")
            os.chdir(cwd)
            if os.path.exists(farm_user):
                self.farm_folders.append(farm_user)

            farm_cwd = os.path.join(os.getcwd(), ".farmer")
            if os.path.exists(farm_cwd):
                self.farm_folders.append(farm_cwd)

        for farm_path in self.farm_folders:
            if not os.path.isdir(farm_path):
                raise ConfigException("Given config is not a folder: {config}".format(config=farm_path))
            farm_files = Path(farm_path).glob('**/*.farm')
            for farm_file in farm_files:
                click.echo('Reading {farm_file}: '.format(farm_file=farm_file), nl=False)
                with open(farm_file) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError as error:
                        click.echo(Fore.RED + 'INVALID' + Style.RESET_ALL)
                        # raise ConfigException("Farm file doesn't contain valid json data: {farm_file}."
                        #                       "\nError: {error}".format(farm_file=farm_file, error=error))
                        continue
                    # Store metrics
                    if 'metrics' in data.keys():
                        self.metrics = {**self.metrics, **data['metrics']}

                    if 'sources' in data.keys():
                        self.sources = {**self.sources, **data['sources']}

                    if 'targets' in data.keys():
                        self.targets = {**self.targets, **data['targets']}

                    if 'settings' in data.keys():
                        self.settings = {**self.settings, **data['settings']}

                    click.echo(Fore.GREEN + 'DONE' + Style.RESET_ALL)

        # Clean metrics and store/count tags
        for metric in self.metrics.values():
            if "description" not in metric.keys():
                metric['description'] = []
            if "tags" not in metric.keys():
                metric['tags'] = []
            else:
                for tag in metric['tags']:
                    if tag not in self.tags:
                        self.tags.append(tag)

    def load_extensions(self):
        for extension in pkg_resources.iter_entry_points('metricfarmer'):
            click.echo('Loading {name}: '.format(name=extension.name), nl=False)
            try:
                ext_class = extension.load()
                ext_instance = ext_class(self)  # Give extension access to overall metricfarmer app
                self.extensions[ext_instance.namespace] = ext_instance
            except Exception as error:
                click.echo(Fore.RED + 'FAILED' + Style.RESET_ALL + ' Error: {error}'.format(error=error))
                continue
            click.echo(Fore.GREEN + 'DONE' + Style.RESET_ALL + ' (namespace: {ns})'.format(ns=ext_instance.namespace))

    def filter_metrics(self, metrics=None, tags=None, exclude_tags=None):
        if metrics is None or not isinstance(metrics, list):
            metrics = []
        if tags is None or not isinstance(tags, list):
            tags = []
        if exclude_tags is None or not isinstance(exclude_tags, list):
            if 'mf_examples' not in tags:
                exclude_tags = ['mf_examples']
            else:
                exclude_tags = []

        click.echo("Filter rules:")
        click.echo("  metric names: {}".format(','.join(metrics)))
        click.echo("  metric tags: {}".format(','.join(tags)))
        click.echo("  metric exclude tags: {}".format(','.join(exclude_tags)))

        click.echo('Filtering all defined metrics: ', nl=False)

        filtered_metrics = {}

        for name, metric in self.metrics.items():
            # Check if metric name is given or metric has a common tag with given tag-list
            # and tag is not in exclude taq
            if ((not metrics and not tags) and len(list(set(metric['tags']) & set(exclude_tags))) == 0) or \
                    (name in metrics or len(list(set(metric['tags']) & set(tags))) >= 1):
                filtered_metrics[name] = metric

        click.echo(Fore.GREEN + 'DONE' + Style.RESET_ALL)
        click.echo('Accepted metrics for measurement: ' + Fore.GREEN +
                   '{}/{}'.format(len(filtered_metrics), len(self.metrics)) + Style.RESET_ALL)

        return filtered_metrics

    def measure(self, filtered_metrics):
        if not filtered_metrics:
            click.echo(Fore.RED + 'Empty metric list\nChange filters or define more metrics'
                       '\nE.g. run "metricfarmer -t mf_examples" to use examples metrics.' + Style.RESET_ALL)
        for name, metric in filtered_metrics.items():
            click.echo('Measuring {name}: '.format(name=name), nl=False)
            try:
                source_type = metric['source']['type']
                source_class = self.sources[source_type]['class']

                # Combine the parameters from metric definition and source definition
                # metric definition must win, if a parameter is defined twice
                parameters = {**self.sources[source_type], **metric['source']}

                result = self._call_source_handler(source_class, parameters, name)
                metric['result'] = result
                metric['result_timestamp'] = datetime.datetime.now().isoformat()

            except KeyError as error:
                click.echo(Fore.RED + 'INVALID' + 'Configuration errors detected: {error}'.format(error=error)
                           + Style.RESET_ALL)
                continue

            click.echo(Fore.GREEN + 'DONE' + Style.RESET_ALL)

    def store(self, targets, filtered_metrics):

        # Lets check, if there are default targets to run, if no special targets are given by user.
        if not targets:
            targets = self.settings.get('targets_default', [])

        # There may be also targets, which must always run.
        targets = list(targets)  # we got a tuple from click for targets
        for always_target in self.settings.get('targets_always', []):
            if always_target not in targets:
                targets.insert(0, always_target)

        if not targets:
            click.echo(Fore.RED + 'No targets defined. Use e.g. "metricfarmer print".' + Style.RESET_ALL)
        for target in targets:
            click.echo('Running {target}: '.format(target=target), nl=False)
            if target not in self.targets.keys():
                click.echo(Fore.RED + 'ERROR ' + Style.RESET_ALL + '(Unknown target)')
                continue
            try:
                target_config = self.targets[target]
                self._call_target_handler(target_config['class'], filtered_metrics, target_config)
            except Exception as error:
                click.echo(Fore.RED + 'ERROR' + Style.RESET_ALL + ' {}'.format(error))
                continue
            click.echo(Fore.GREEN + 'DONE' + Style.RESET_ALL)

    def _call_source_handler(self, source_class, parameters, metric_name):
        source_namespace = source_class.split('.')[0]
        source_func = source_class.split('.')[1]
        handler = self.extensions[source_namespace].source_classes[source_func]

        checked_parameters = walker(parameters)
        result = handler(**checked_parameters, metric_name=metric_name)
        return result

    def _call_target_handler(self, target_class, filtered_metrics, parameters):
        target_namespace = target_class.split('.')[0]
        target_func = target_class.split('.')[1]

        if target_namespace not in self.extensions.keys():
            raise InvalidTargetException('Unknown target namespace: {}'.format(target_namespace))
        if target_func not in self.extensions[target_namespace].target_classes.keys():
            raise InvalidTargetException('Unknown target function: {}'.format(target_func))
        handler = self.extensions[target_namespace].target_classes[target_func]

        checked_parameters = walker(parameters)
        result = handler(metrics=filtered_metrics, **checked_parameters)
        return result


@click.command()
@click.argument("targets", nargs=-1)
@click.option('-f', '--farmer', help="Only uses the given farm folder")
@click.option('-m', '--metrics', default='', help="Filter metrics for specific name")
@click.option('-t', '--tags', default='', help="Filter metrics for tags")
@click.option('--list', is_flag=True, help="Show configuration information only")
def mf_cli(targets, farmer, metrics, tags, list):
    """Measure metrics and execute TARGETS"""

    mf_app = mf_startup(farmer)

    if list:
        mf_list(mf_app)
        sys.exit(0)

    click.echo('\nFiltering metrics')
    click.echo('*******************')
    metrics = [entry for entry in metrics.split(',') if entry != '']
    tags = [entry for entry in tags.split(',') if entry != '']
    filtered_metrics = mf_app.filter_metrics(metrics=metrics, tags=tags)

    click.echo('\nExecuting measurements')
    click.echo('**********************')
    mf_app.measure(filtered_metrics)

    click.echo('\nRunning targets')
    click.echo('***************')
    mf_app.store(targets, filtered_metrics)


def mf_list(mf_app):
    click.echo("\nConfiguration information")
    click.echo("*************************")
    click.echo('Metrics found: {}\n{}\n'.format(len(mf_app.metrics), ', '.join(mf_app.metrics)))
    click.echo('Metric tags found: {}\n{}\n'.format(len(mf_app.tags), ', '.join(mf_app.tags)))
    click.echo('Sources found: {}\n{}\n'.format(len(mf_app.sources), ', '.join(mf_app.sources)))
    click.echo('Targets found: {}\n{}\n'.format(len(mf_app.targets), ', '.join(mf_app.targets)))
    click.echo('Settings found: {}\n{}\n'.format(len(mf_app.settings), ', '.join(mf_app.settings)))

    click.echo("Extension information")
    click.echo("**********************")
    click.echo('Extensions loaded: {}\n{}\n'.format(len(mf_app.extensions), ', '.join(mf_app.extensions)))

    for name, extension in mf_app.extensions.items():
        name_string = '{} ({})'.format(extension.name, name)
        click.echo(name_string)
        click.echo('-' * len(name_string))
        click.echo('Author: {}'.format(extension.author))
        click.echo('Description: {}'.format(extension.description))
        click.echo('Source classes: {} ({})'.format(len(extension.source_classes), ', '.join(extension.source_classes)))
        click.echo('Target classes: {} ({})'.format(len(extension.target_classes), ', '.join(extension.target_classes)))


def mf_startup(farmer):
    click.echo(greetings)
    mf = MetricFarmerApp()

    click.echo('\nLoading extensions')
    click.echo('******************')
    mf.load_extensions()

    click.echo('\nReading configurations')
    click.echo('**********************')
    mf.load_config(farmer)
    return mf


if "__main__" in __name__:
    mf_cli()
