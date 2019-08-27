from pathlib import Path
from bbox import BBox3D
from collections import OrderedDict
from graph_articulations.config import *
from graph_articulations import line_br, obj_to_ply_to_shell_script
from torch import from_numpy, tensor
import argparse
import numpy as np
import simplejson as json
import torch


def aggregate_part_labels(list_of_all_models, display=False):
    """
    Given a list of strings model names, this function returns a sorted list of parts
    :param list_of_all_models: List of models to find part information for
    :return master_part_list: Sorted list of parts from Highest to lowest frequency of occurrence
    """
    part_count_dict = {}
    for model in list_of_all_models:
        parts_path = str(PART_ROOT / model / model) + '.parts.json'
        with open(parts_path, 'r') as part_info:
            part_json = json.load(part_info)

        part_instances = part_json['segmentation'][6]['labels']
        for clss in part_instances:
            part_count_dict[clss] = part_count_dict[clss] + 1 if clss in part_count_dict.keys() else 1

    # Sort parts by number of occurrence in the dataset (Highest to lowest)
    # Get only the part class name from the sorted results
    master_part_list = [part[0] for part in sorted(part_count_dict.items(), key=lambda kv: kv[1], reverse=True)]
    list_of_tuples = [(key, part_count_dict[key]) for key in master_part_list]
    part_count_dict = OrderedDict(list_of_tuples)

    if display: print(f'Found Part Classes by Occurrence (Highest to lowest)\n{line_br}\n{part_count_dict}')
    return master_part_list


def update_part_and_instance_labels(model: str, object_instances=None, display=False):
    """
    :param object_instances: list of comprehensive parts in the dataset
    :param model: (String) model id. (e.g "100", 's__669', etc). Does not expect 'p5d.' as prefix
    :return: Updated global part labels, local instance labels, updated pid to point labels
    """
    # Get path to the model and part information
    # Read the json into memory
    parts_path = str(PART_ROOT / model / model) + '.parts.json'
    with open(parts_path, 'r') as part_info: part_json = json.load(part_info)

    # Grab the part label names and indices
    json_face_labels = np.array(part_json['segmentation'][6]['index'])
    json_label_names = np.array(part_json['segmentation'][6]['labels'])

    # Out-of-place variables ... keep things simple you babo
    # Store the instance of the part as well (e.g drawer 1, drawer 2, etc)
    # Part Labels
    instance_labels = np.zeros(json_face_labels.shape, dtype=np.int64)
    part_labels = np.zeros(json_face_labels.shape, dtype=np.int64)

    if display: print(f'Updating {model}\'s part labels...\n{line_br}')


    # Changing current indices to match the comprehensive class list
    pid_to_points_dict = OrderedDict()
    for index in range(len(json_label_names)):
        new_label = object_instances.index(json_label_names[index])
        label_name = json_label_names[index]

        # Get the number of instances so far for the current part classes
        unique, instance_counts = np.unique(json_label_names[:index + 1], return_counts=True)
        cur_instance = instance_counts[np.where(unique == label_name)][0]

        # Get the current face indices of the current part
        # Update the part label and instance label accordingly
        indices = np.where(json_face_labels == index)

        # Update the Labels out-of-place
        part_labels[indices] = new_label
        instance_labels[indices] = cur_instance
        pid_to_points_dict[str(index)] = (new_label, cur_instance)

        # Display
        if display: print(f'{index}) {label_name}-{cur_instance} encoded from {index} ===> {new_label}')
        # print(f'Index {index} | Unique: {unique} | Instance #: {instance_counts} | cur_instance {cur_instance}')
        # print(f'{len(part_labels[indices])} changed from {index} to {new_label}')
    return from_numpy(part_labels), from_numpy(instance_labels), pid_to_points_dict


def get_con_graph_and_bounding_boxes(model: str, part_labels: list, display: bool = False):
    """
    :param model: name of the model
    :param part_labels: list of all known part labels in the dataset
    :param display: if True prints progress out to the console
    :return: A model's Connectivity Graphs, Bounding Boxes and Name of Parts
    """
    parts_path = str(PART_ROOT / model / model) + '.parts.json'
    conn_path = str(CONNECTIVITY_ROOT) + f'/{model}.artpre.json'

    with open(parts_path, 'r') as part_info:
        part_json = json.load(part_info)
    with open(conn_path, 'r') as json_file:
        precom_dict = json.load(json_file)

    # Grab the part label names and indices
    label_names = np.array(part_json['segmentation'][6]['labels'])
    con_graph = precom_dict['connectivityGraph']
    distance_matrix = np.array(precom_dict['distanceMatrix'])
    updated_graph = np.zeros((len(label_names), len(label_names)))
    updated_dis = np.zeros((updated_graph.shape))
    updated_graph[:][:] = np.nan
    updated_dis[:][:] = np.nan

    # Update Connectivity Graph
    for cur_part in range(len(con_graph)):
        orig_idx = []
        dis = []
        not_none_indices = []
        cur_dis = np.array(distance_matrix[cur_part])

        # Todo confirm distance the provide part distances... not very clear to me at the moment
        if cur_dis.size != 0:
                not_none_indices = np.where(cur_dis != None)
                dis = cur_dis[not_none_indices]
                if not_none_indices[0].size != 0:
                    updated_dis[cur_part][not_none_indices] = np.around((dis * 10).astype(float), decimals=6)
                    not_none_indices = not_none_indices[0]
        if display:
            print(f'\n{cur_part}) {label_names[cur_part]} - {con_graph[cur_part]} \n{line_br}'
                          # f'\n Original Distances: {distance_matrix[cur_part]}\nUpdated Distances: {updated_dis[cur_part]}'
                          # f'\nLength check: {len(not_none_indices)} - {len(con_graph[cur_part])}'
                          )

        for node in con_graph[cur_part]:
            index = node
            orig_idx.append(orig_idx)
            new_label = part_labels.index(label_names[index])
            updated_graph[cur_part][index] = new_label
            if display:
                print(f'{index}) {label_names[node]} encoded from {index} ===> {new_label}'
                      f'\nUpdated graph: {updated_graph[cur_part]}')

    if display:
        print(updated_graph)

    # Store the JSON into placeholder variables
    part_obb_dict = precom_dict['parts']
    names = np.array([])
    centroids = np.array([])
    axes_lengths = np.array([])
    normalized_axes = np.array([])
    pids = np.array([])

    # Populate arrays with json information
    for obb in part_obb_dict:
        if obb is not None:
            if pids.size == 0:
                names = np.array(obb['name'])
                centroids = np.array(obb['obb']['centroid'])
                axes_lengths = np.array(obb['obb']['axesLengths'])
                normalized_axes = np.array(obb['obb']['normalizedAxes'])
                pids = np.array(obb['pid'], dtype=int)
                if 'side' in obb["name"]:
                    if display: print(f'Swapped axes on pid {obb["pid"]}: {obb["name"]}')
                    axes_lengths = np.array([axes_lengths[-1], axes_lengths[1], axes_lengths[0]])
            else:
                names = np.vstack((names, obb['name']))
                pids = np.vstack((pids, np.array(obb['pid'])))
                centroids = np.vstack((centroids, np.array(obb['obb']['centroid'])))
                axes_lengths = np.vstack((axes_lengths, np.array(obb['obb']['axesLengths'])))
                normalized_axes = np.vstack((normalized_axes, np.array(obb['obb']['normalizedAxes'])))

                if 'side' in obb["name"]:
                    if display: print(f'Swapped axes on pid {obb["pid"]}: {obb["name"]}')
                    axes_lengths[-1] = np.array([axes_lengths[-1][-1], axes_lengths[-1][1], axes_lengths[-1][0]])

    # Compute Bounding Boxes
    b_boxes = np.array([])
    for part in range(len(pids)):
        x, y, z = centroids[part][0], centroids[part][1], centroids[part][2]
        l, w, h = axes_lengths[part][0], axes_lengths[part][1], axes_lengths[part][2]
        bbox = BBox3D(x, y, z, length=l, width=w, height=h)
        b_boxes = bbox.p if b_boxes.size == 0 else np.vstack((b_boxes, bbox.p))
    b_boxes = np.reshape(b_boxes, (len(pids), 8, 3))

    return from_numpy(updated_graph), from_numpy(b_boxes), centroids #, from_numpy(updated_dis)


def categorical_list_of_models(path_to_category_list=None):
    """
    :param path_to_category_list: path to the json file that details models for each category
    :return: Dictionary from the loaded category json file
    """
    if path_to_category_list is None:
        path_to_category_list = GRAPH_ART_ROOT / 'category_to_models.json'
    with open(path_to_category_list, 'r') as file:
        categorical_instances = json.load(file)
    return categorical_instances


def find_part_instances(data, object_instances:list=None, display=False):
    """
    :param data: Graph data object with model information
    :param object_instances: list of all
    :return: Consolidated Tensor of Encode Part Labels and Instances
    """
    unique_parts = torch.unique(data.y)
    part_instances = torch.zeros(unique_parts.shape, dtype=torch.int8)
    part_names = [object_instances[part] for part in unique_parts]
    part_indices = [torch.where(data.y == part) for part in unique_parts]
    if display: print(f'\nModel part-instance stats\n{line_br}')
    for cur_part in range(len(part_indices)):
        num_of_instances = torch.unique(data.instance_label[part_indices[cur_part]])
        if display: print(f'{part_names[cur_part]} has {len(num_of_instances)} instances')
        part_instances[cur_part] = len(num_of_instances)
    return unique_parts, part_instances


def list_of_separated_parts(data: object, object_instance: list, display=False):
    """
    :param data: Data object containing the current model's information
    :param object_instance: List of all parts within the dataset
    :return: Two lists of tensors representing each part's points position and labels for the current model
    """
    collective_part_points = []
    collective_point_labels = []
    part_labels, instance_labels = find_part_instances(data, object_instance)

    # Iterate through each part within the current model
    for idx in range(len(part_labels)):
        current_part = part_labels[idx]
        part_indices = np.where(data.y == current_part)

        # Iterate through each instance
        current_inst = 1
        for inst_idx in range(instance_labels[idx]):
            # Find the associated indices for the current part-instance
            points = data.pos[part_indices]
            labels = data.y[part_indices]
            instances = data.instance_label[part_indices]
            instant_indices = np.where(instances == current_inst)

            if display:
                print(f'Looking at {object_instance[part_labels[idx]]}-{current_inst}')
                print(f'{object_instance[part_labels[idx]]}-{current_inst} has {points.shape} points')


            # Select the current part-instance and add it to the list
            points = points[instant_indices]
            labels = labels[instant_indices]
            collective_part_points.append(points)
            collective_point_labels.append(labels)
            current_inst += 1
    return collective_part_points, collective_point_labels


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_root', default=None, help='path to model meshes')
    parser.add_argument('--part_root', default=None, help='path to parts')
    parser.add_argument('--conn_root', default=None, help='path to connectivity graphs')
    args = parser.parse_args()

    PART_ROOT = PART_ROOT if args.part_root is None else args.part_root
    CONNECTIVITY_ROOT = CONNECTIVITY_ROOT if args.conn_root is None else args.conn_root
    MODEL_ROOT = MODEL_ROOT if args.model_root is None else args.model_root

    categorical_instances = categorical_list_of_models()
    list_of_dressers = categorical_instances['dresser']
    known_part_labels = aggregate_part_labels(list_of_dressers)

    get_con_graph_and_bounding_boxes(list_of_dressers[-1], known_part_labels)
    # obj_to_ply_to_shell_script(list_of_dressers)
