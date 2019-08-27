from graph_articulations.data import update_part_and_instance_labels
from torch_geometric.data import Data
import torch
import numpy as np


class SamplePointsWithLabels(object):
    r"""Uniformly samples :obj:`num` points on the mesh faces according to
    their face area.

    Args:
        num (int): The number of points to sample.
        remove_faces (bool, optional): If set to :obj:`False`, the face tensor
            will not be removed. (default: :obj:`True`)
        include_normals (bool, optional): If set to :obj:`True`, then compute
            normals for each sampled point. (default: :obj:`False`)
    """

    def __init__(self, num, remove_faces=True, include_normals=False, object_instances=None,
                 categorical_instances=None, display=False):
        self.num = num
        self.remove_faces = remove_faces
        self.include_normals = include_normals
        self.object_instances = object_instances
        self.categorical_instances = categorical_instances
        self.display = display

    def __call__(self, data):
        pos, face, model_name = data.pos, data.face, data.name
        assert pos.size(1) == 3 and face.size(0) == 3

        # Get face part and instance labels
        face_part_labels, face_instance_labels, pid_points_indices = \
            update_part_and_instance_labels(self.categorical_instances[model_name], self.object_instances)

        # Construct sub graph of pid and corresponding point indices
        # Add the subgraph to the current model's data object
        pid_graph = Data.from_dict(pid_points_indices)
        data.__setitem__('pids', pid_graph)

        # Movable parts of interest before sample
        if self.display:
            print(f'Part labels shape: {face_part_labels.shape}')
            drawer_count = np.where(face_part_labels == 0)[0]
            cabinet_count = np.where(face_part_labels == 7)[0]
            print(f'Drawer count: {drawer_count.shape}')
            print(f'Cabinet count: {cabinet_count.shape}')

        # Normalize vertices
        pos_max = pos.max()
        pos = pos / pos_max

        #  The cross product between to the two edges to get the area in between
        #  Normalize the surface area
        area = (pos[face[1]] - pos[face[0]]).cross(pos[face[2]] - pos[face[0]])
        area = area.norm(p=2, dim=1).abs() / 2

        # Get of sampling probability for each face
        prob = area / area.sum()
        sample = torch.multinomial(prob, self.num, replacement=True)

        # Sample from faces, face part labels and face instance labels
        face = face[:, sample]
        face_part_labels = face_part_labels[sample]
        face_instance_labels = face_instance_labels[sample]

        # Movable parts of interest after sample
        if self.display:
            drawer_count = np.where(face_part_labels == 0)[0]
            cabinet_count = np.where(face_part_labels == 7)[0]
            print(f'Part labels shape: {face_part_labels.shape}')
            print(f'Drawer count: {drawer_count.shape}')
            print(f'Cabinet count: {cabinet_count.shape}')

        frac = torch.rand(self.num, 2, device=pos.device)
        mask = frac.sum(dim=-1) > 1
        frac[mask] = 1 - frac[mask]

        vec1 = pos[face[1]] - pos[face[0]]
        vec2 = pos[face[2]] - pos[face[0]]

        if self.include_normals:
            data.norm = torch.nn.functional.normalize(vec1.cross(vec2), p=2)

        pos_sampled = pos[face[0]]
        pos_sampled += frac[:, :1] * vec1
        pos_sampled += frac[:, 1:] * vec2

        pos_sampled = pos_sampled * pos_max

        # Add samples as attributes to the data object
        data.pos = pos_sampled
        data.__setitem__('y', face_part_labels)
        data.__setitem__('instance_label', face_instance_labels)

        from collections import OrderedDict
        part_points = OrderedDict()
        # Get individual point parts
        for pid in range(len(data.pids)):
            part_label, inst_label = data.pids[str(pid)][0], data.pids[str(pid)][1]
            label_indices = np.where(data.y == part_label)
            inst_indices = np.where(data.instance_label[label_indices] == inst_label)
            points = pos_sampled[label_indices]
            points = points[inst_indices]
            part_points[str(pid)] = points

        part_graph = Data.from_dict(part_points)
        data.__setitem__('parts', part_graph)

        if self.remove_faces:
            data.face = None

        return data
