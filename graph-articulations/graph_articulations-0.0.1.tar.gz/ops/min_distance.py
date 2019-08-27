from graph_articulations.data import list_of_separated_parts
from torch import tensor
import torch
from scipy.spatial.distance import directed_hausdorff
from graph_articulations.data import get_con_graph_and_bounding_boxes
import numpy as np

def min_distances(data: object, object_instances: list):
    """
    :param data: Data object containing the current model's information
    :param object_instances: List of all parts within the dataset
    :return:
    """

    from graph_articulations.config import CONNECTIVITY_ROOT
    from graph_articulations import line_br
    import simplejson as json

    conn_path = str(CONNECTIVITY_ROOT) + f'/{129}.artpre.json'
    with open(conn_path, 'r') as json_file:
        precom_dict = json.load(json_file)

    # Grab the part label names and indices
    angels_graph = precom_dict['connectivityGraph']
    conn_graph = torch.zeros(len(data.pids.keys), len(data.pids.keys))
    conn_graph[:][:] = np.nan

    connected_threshold = precom_dict['metadata']['minDist']
    neighboring_parts = precom_dict['metadata']['maxDist']
    ground_truth = precom_dict['parts']

    for idx in range(len(data.pids.keys)):
        cur_conn = conn_graph[idx]
        part = data.parts[f'{idx}']
        label = data.pids[f'{idx}'][0]
        inst = data.pids[f'{idx}'][1]


        # todo construct new list and remove the current key from consideration
        adjacent_parts = {key:val for key, val in data.parts if key != f'{idx}'}
        adjacent_labels = {key:val[0] for key, val in data.pids if key != f'{idx}'}


        if object_instances[label] != 'unknown':
            print(f'{ground_truth[idx]["name"]}')
            print(f'{idx}) {object_instances[label]}-{inst}\n{line_br}')
            for adj_idx in range(len(data.pids.keys)):
                adj_part = data.parts[f'{adj_idx}']
                adj_label = data.pids[f'{adj_idx}'][0]
                adj_inst = data.pids[f'{adj_idx}'][1]

                if adj_idx == idx or object_instances[adj_label] == 'unknown':
                    continue

                dist = max(directed_hausdorff(part.numpy(), adj_part.numpy())[0],
                           directed_hausdorff(adj_part.numpy(), part.numpy())[0])

                print(f'{adj_idx}) {object_instances[adj_label]}-{adj_inst} dist: {dist} ', end="")

                if dist <= connected_threshold:
                    cur_conn[adj_idx] = adj_label
                    conn_graph[adj_idx][idx] = label
                    print(' \tCONNECTED')
                elif dist <= neighboring_parts:
                    cur_conn[adj_idx] = adj_label
                    conn_graph[adj_idx][idx] = label
                    print(' \t HIT')
                else:
                    print()

        conn_graph[idx] = cur_conn
        print(f'Estimated: {conn_graph[idx]}')
        print(f'Converted: {data.connectivity_graph[idx]}')
        print(f'Provided : {angels_graph[idx]}\n')
    #
    # for part, label in zip(part_list, label_list):
    #     cur_conn = conn_graph[idx]
    #
    #     print(f'{idx}) {object_instances[label[0]]}\n{line_br}')
    #     adjacent_part_list, adjacent_label_list = part_list, label_list
    #
    #     adj_idx = 0
    #     for adjacent_part, adjacent_label in zip(adjacent_part_list, label_list):
    #         if torch.equal(part, adjacent_part):
    #             continue
    #
    #         dist = min(directed_hausdorff(part.numpy(), adjacent_part.numpy())[0],
    #                    directed_hausdorff(adjacent_part.numpy(), part.numpy())[0])
    #         if adjacent_label.size == 0 or label.size == 0:
    #             continue
    #
    #         print(f'{adj_idx}) {object_instances[adjacent_label[0]]}', end="")
    #         print(f' dist: {dist} ', end="")
    #
    #         if dist <= threshold and label[0] != adjacent_label[0]:
    #             cur_conn[adj_idx] = adjacent_label[0]
    #             conn_graph[adj_idx][idx] = label[0]
    #             print(' \tCONNECTED')
    #         else:
    #             print()
    #
    #         adj_idx += 1
    #     conn_graph[idx] = cur_conn
    #     print(f'Estimated: {conn_graph[idx]}')
    #     print(f'Converted: {data.connectivity_graph[idx]}')
    #     print(f'Provided : {angels_graph[idx]}\n')
    #     idx += 1

