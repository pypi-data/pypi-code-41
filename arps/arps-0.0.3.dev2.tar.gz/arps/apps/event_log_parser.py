import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict, namedtuple
import itertools
import csv

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import simplejson as json

from arps.core.simulator.resource_event import ResourceEvent
from arps.core.resource_category import ValueType

from arps.apps.configuration_file_loader import load_attribute, InvalidConfigurationError

def simulation_results_parser(simulation_result_file, resource_category_class, output_dir, index_file):
    '''
    Parse simulation result file accordingly with configuration file

    Args:
    - simulation_result_file: path to the location of the simulation result file
    - resource category class: class with resource category and its functions
    - output_dir: dir where the figures is saved
    - index_file: index containing all generated figures
    '''

    resources_event_per_env = group_resources_event_by_environment(simulation_result_file)

    NAME_TEMPLATE = 'env_{}_resource_{}_{}.png'

    saved_figures = list()

    largest_epoch = search_for_largest_epoch(resources_event_per_env)

    figure_index = 0
    for env, resources_event in resources_event_per_env.items():
        for category, resources in resources_event.items():
            resources = resources_axis(resources)
            normalize(resources, largest_epoch)
            for resource_id, axis_values in resources.items():
                _ = plt.figure(figure_index)
                figure_index += 1
                x_axis = axis_values[0]
                axis_range = [x_axis[0], x_axis[-1]]
                y_axis = resource_category_class[category].valid_range
                resource_category = resource_category_class[category]
                if resource_category.value_type is ValueType.numerical:
                    axis_range.extend(y_axis)
                    numerical_values = [resource_category.parse(value) for value in axis_values[1]]
                    plt.plot(axis_values[0], numerical_values, 'k')
                    plt.axis(axis_range)
                    plt.ylim(y_axis[0] * -1.01, y_axis[1] * 1.01)
                elif resource_category.value_type is ValueType.descriptive:
                    mapped_values = [y_axis.index(v) for v in axis_values[1]]
                    plt.step(axis_values[0], mapped_values, 'k')
                    plt.yticks(range(len(y_axis)), y_axis)
                    plt.xticks(x_axis)
                elif resource_category.value_type is ValueType.complex:
                    axis_range.extend(y_axis)
                    complex_values = [resource_category.parse(value) for value in axis_values[1]]
                    values_by_label = defaultdict(list)
                    for values in complex_values:
                        for k, v in values.items():
                            values_by_label[k].append(v)

                    markevery = len(axis_values[0]) // 20

                    for (label, values), marker in zip(values_by_label.items(), itertools.cycle('+o*x^.d|')):
                        plt.plot(axis_values[0], values, label=label, marker=marker, markevery=markevery)
                        plt.axis(axis_range)
                        plt.ylim(y_axis[0] * -1.01, y_axis[1] * 1.01)
                        plt.legend()
                else:
                    raise NotImplementedError('Resource category value_type {} not implemented', resource_category.value_type)


                plt.title('Environment: {} | Resource: {} | ID: {}'.format(env, category, resource_id))
                plt.xlabel('time')
                plt.ylabel(category)
                plt.tight_layout()

                png_file = output_dir / NAME_TEMPLATE.format(env, resource_id, simulation_result_file.stem)
                saved_figures.append(str(png_file))
                plt.savefig(png_file)

    with open(index_file, 'w') as index_file:
        json.dump({'results': saved_figures}, index_file)

def resources_axis(resources_event_by_category):
    '''
    For each resource event, create x and y axis, where x represent
    the time series and y the state of the resource

    Args:
    - resources_event: resources event grouped by their category
    '''
    resources = {}
    for resource, events in resources_event_by_category.items():
        events_x, events_y = create_axis(events)
        #if len(events_x) == 1:
        #    continue
        resources[resource] = (events_x, events_y)
    return resources


def create_axis(events):
    '''
    Return two sequences for x and y axis, where x is the
    timeseries and y is the resource state

    Args:
    - events: list containing tuples with the state of the
    resource given a specific epoch
    '''
    x = list()
    y = list()
    for event in events:
        epoch = event.epoch
        value = event.state
        if epoch in x:
            index = x.index(epoch)
            y[index] = value
        else:
            x.append(epoch)
            y.append(value)

    start = x[0]
    end = x[-1]
    complete_x = list(range(start, end+1))
    complete_y = list()
    y_it = iter(y)
    current_y = next(y_it)
    for i in complete_x:
        if i not in x:
            complete_y.append(complete_y[-1])
        else:
            complete_y.append(current_y)
            try:
                current_y = next(y_it)
            except StopIteration:
                pass

    return complete_x, complete_y


def normalize(resources_by_categories, largest_epoch):
    '''
    Organize all timeseries by the serie with the longest duration
    '''

    for resource_axis in resources_by_categories.values():
        number_of_missing_values = largest_epoch - len(resource_axis[0])
        if not number_of_missing_values:
            continue
        resource_axis[0].extend(list(range(largest_epoch - number_of_missing_values, largest_epoch)))
        resource_axis[1].extend([resource_axis[1][-1]] * number_of_missing_values)


def search_for_largest_epoch(resources_event_per_env):
    '''
    Search for the largest epoch to show all resources using the same scale

    Args:
    - resources_event_per_env:
    '''
    largest_epoch = 9
    for resources_event in resources_event_per_env.values():
        for resources in resources_event.values():
            for resource in resources.values():
                largest_epoch = max(resource[-1].epoch, largest_epoch)
    return largest_epoch

def group_resources_event_by_environment(simulator_result_file):
    '''
    Create a structure, for each category, containing a resource and
    its time series related to when it was modified

    Args:
    - simulator_result_file: path to the location of the log file
    '''

    EpochState = namedtuple('EpochState', 'epoch state')

    with open(simulator_result_file, 'r') as result:
        resources_event = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        events = csv.reader(result, delimiter=';')
        next(events) #skip header
        for event in events:
            resource_event = ResourceEvent(*event)
            resources_event[resource_event.env][resource_event.category][resource_event.identifier].append(EpochState(int(resource_event.epoch),
                                                                                                                      resource_event.value))
        return resources_event

def main():
    parser = argparse.ArgumentParser(description='Generate graph of the simulation')
    parser.add_argument('--result_file', help='simulation result file path')
    parser.add_argument('--rc_module', help='resource category module (format: package.module')
    parser.add_argument('--rc_class', help='resource category class')
    parser.add_argument('--index_file', help='output index file containing the path to all figures created')
    parser.add_argument('--out_dir', help='output directory where the charts will be created', default=None)

    parsed_args = parser.parse_args(sys.argv[1:])
    simulation_result_file = Path(parsed_args.result_file)

    output_dir = Path(parsed_args.out_dir) if parsed_args.out_dir and Path(parsed_args.out_dir).is_dir() else simulation_result_file.parent

    try:
        resource_category_class = load_attribute(module_path=parsed_args.rc_module, attribute_name=parsed_args.rc_class)
    except InvalidConfigurationError as err:
        sys.exit(err)
    else:
        simulation_results_parser(simulation_result_file, resource_category_class,
                                  output_dir, parsed_args.index_file)

if __name__ == '__main__':
    main()
