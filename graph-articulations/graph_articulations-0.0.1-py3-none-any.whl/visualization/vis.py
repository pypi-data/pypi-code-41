import open3d as o3d
import numpy as np
import torch
from graph_articulations.data.process_models import find_part_instances

# Colors
# Refer to http://doc.instantreality.org/tools/color_calculator/
red = np.array([1, 0, 0])
orange = np.array([1, 0.5, 0])
yellow = np.array([1, 1, 0])
green = np.array([0.337, 0.890, 0.329])
blue = np.array([0, 1, 0])
indigo = np.array([0.294, 0, .51])
violet = np.array([.541, .169, .886])
black = np.array([0.027, 0.031, 0.027])
pink = np.array([0.988, 0.352, 0.984])


def bounding_boxes_lines(bboxes):
    """
    :param bboxes: Nd array with shape (# of Pid's, 8, 3)
    :return: LineSet Geometry of All bounding boxes for the current model
    """

    # Placeholder Lineset
    bounding_boxes = o3d.geometry.LineSet()

    # Iterate through the bounding boxes and construct lines
    for bb in range(bboxes.shape[0]):
        cur_box = bboxes[bb][:]

        # Connect the vertices
        # Color the lines Red
        lines = [[0, 1], [2, 3], [4, 5], [6, 7], [0, 4], [2, 6], [1, 5], [3, 7], [0, 3], [1, 2], [4, 7], [5, 6]]
        colors = [[1, 0, 0] for line in range(len(lines))]

        # Construct the current lineSet
        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(cur_box)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)

        # Add the current bound box to the collective set
        bounding_boxes = bounding_boxes + line_set
    return bounding_boxes


def part_points(points, labels, object_instances, colors=None, scale=None, part_instances:[]=None):
    """
    :param data: graph in the dataset
    :param colors: colors to set
    :return: Colored Point Cloud Object to Render
    """

    if colors is None:
        colors = np.ones(points.shape) * orange

    cabinet_index = np.where(labels == object_instances.index("cabinet"))
    cabinet_door_index = np.where(labels == object_instances.index("cabinet door"))
    door_index = np.where(labels == object_instances.index("door"))
    drawer_index = np.where(labels == object_instances.index("drawer"))
    side_panel_index = np.where(labels == object_instances.index("side panel"))
    top_panel_index = np.where(labels == object_instances.index("top panel"))
    unknown_index = np.where(labels == object_instances.index("unknown"))

    colors[drawer_index] = indigo
    colors[cabinet_index] = black
    colors[cabinet_door_index] = green
    colors[door_index] = green
    colors[side_panel_index] = red
    colors[top_panel_index] = yellow
    colors[unknown_index] = pink

    if scale is not None:
        points *= scale


    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points.numpy())
    pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd


def tensor_to_point_cloud(data, object_instances, colors=None, scale=None, part_instances:[]=None):
    """
    :param data: graph in the dataset
    :param colors: colors to set
    :return: Colored Point Cloud Object to Render
    """
    points = data.pos
    labels = data.y

    if colors is None:
        colors = np.ones(points.shape) * orange

    cabinet_index = np.where(labels == object_instances.index("cabinet"))
    cabinet_door_index = np.where(labels == object_instances.index("cabinet door"))
    door_index = np.where(labels == object_instances.index("door"))
    drawer_index = np.where(labels == object_instances.index("drawer"))
    side_panel_index = np.where(labels == object_instances.index("side panel"))
    top_panel_index = np.where(labels == object_instances.index("top panel"))
    unknown_index = np.where(labels == object_instances.index("unknown"))

    colors[drawer_index] = indigo
    colors[cabinet_index] = black
    colors[cabinet_door_index] = green
    colors[door_index] = green
    colors[side_panel_index] = red
    colors[top_panel_index] = yellow
    colors[unknown_index] = pink

    if scale is not None:
        points *= scale



    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points.numpy())
    pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd


def show_each_part_separately(data: object, object_instance: list):
    """
    :param data: Graph containing model information
    :param object_instance: list of all parts in the dataset
    :return: Renders each part-instance separately
    """

    for idx in range(len(data.pids.keys)):
        points = data.parts[f'{idx}']
        label, inst = data.pids[f'{idx}'][0], data.pids[f'{idx}'][1]
        labels = np.ones(points.shape[0]) * label

        print(f'{object_instance[label]}-{inst} has {points.shape} points')

        pcd = part_points(points, labels, object_instances=object_instance)
        bbox = bounding_boxes_lines(data.bounding_boxes)
        o3d.draw_geometries([bbox, pcd])


if __name__ == '__main__':
    from torch_geometric.data import Data
    from models import PointNetSegEncoder, PointNetEncoder
    from graph_articulations.config import GRAPH_ART_ROOT

    import torch.optim as optim


                # with torch.no_grad():
                #     # TODO get feature embedding here
                #
                #
                # # TODO compute distances and construct connectivity graph here
                # threshold = 0.5
                #
                # for
                #
                # else:
                # points = points[part_indices]
                # labels = labels[part_indices]
                #
                # pcd = part_points(points, labels, object_instances=object_instance)
                # bbox = bounding_boxes_lines(bboxes)
                # o3d.draw_geometries([bbox, pcd])

    model = PointNetSegEncoder(num_classes=4)
    optim = torch.optim.Adam(model.parameters(), lr=0.001)
    checkpoint = torch.load(GRAPH_ART_ROOT / 'PointNetSeg')
    model.load_state_dict(checkpoint['state_dict'], strict=False)
    optim.load_state_dict(checkpoint['optimizer'])
    criterion = checkpoint['loss']
    print(f'{checkpoint.keys()}')
    keys = list(checkpoint.keys())
    print(f'{"epoch" in checkpoint.keys()}')

    # print(model)

    # part_data = [Data(pos=points)]
    #
    # model.eval()
    #
    # with torch.no_grad():
    #     for part in part_data:
    #         points = part.pos
    #         output = model(points)

        # TODO how to iterate through by part dataset

