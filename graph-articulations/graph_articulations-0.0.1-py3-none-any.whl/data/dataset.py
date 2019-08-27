import open3d as o3d
from torch_geometric.data import Dataset
from pathlib import Path
from graph_articulations import obj_to_ply_to_shell_script, list_of_models_with_issues, line_br
from graph_articulations.data import get_con_graph_and_bounding_boxes, aggregate_part_labels, SamplePointsWithLabels
from graph_articulations.config import MODEL_ROOT, DATA_ROOT
from graph_articulations.visualization import bounding_boxes_lines, tensor_to_point_cloud
import torch
import torch_geometric.read as read
import torch_geometric.transforms as T
import tqdm
import time

class Articulations(Dataset):
    """
    .. note::
        Data objects hold mesh faces instead of edge indices.
        To convert the mesh to a graph, use the
        :obj:`torch_geometric.transforms.FaceToEdge` as :obj:`pre_transform`.
        To convert the mesh to a point cloud, use the
        :obj:`torch_geometric.transforms.SamplePoints` as :obj:`transform` to
        sample a fixed number of points on the mesh faces according to their
        face area.
    """

    def __init__(self, root, categorical_instances, transform=None, pre_transform=None, visualize=False):
        super(Articulations, self).__init__(root, transform, pre_transform)
        self.root = root
        self.visualize = visualize
        self.known_parts = aggregate_part_labels(categorical_instances)
        self.categorical_instances = categorical_instances
        self.num_classes = len(self.known_parts)
        self.model_names = []
        self.process()


    def _process(self):
        pass

    @property
    def names(self):
        return self.model_names

    @property
    def raw_file_names(self):
        return [model + '.ply' for model in self.categorical_instances]

    # @property
    # def processed_file_names(self):
    #     return self.processed_file_names()

    def __len__(self):
        return len(self.processed_file_names()) - len(list_of_models_with_issues())

    def _download(self):
        pass
        # Download to `self.raw_dir`.

    def process(self):
        i = 0
        bad_models = list_of_models_with_issues()


        if not Path((self.raw_paths[-1])).exists():
            print(f'Found {MODEL_ROOT}! Moving models to {DATA_ROOT}')
            obj_to_ply_to_shell_script(self.categorical_instances)

        print(f'Loading Dataset \n{line_br}')
        for raw_path in tqdm.tqdm(self.raw_paths):
            # Read data from `raw_path`.
            time.sleep(0.01)
            model_name = Path(raw_path).name.split('.')[0]
            data = read.read_ply(raw_path)
            data.__setitem__('name', i)

            # TODO Let Angel know of this issue
            if model_name in bad_models:
                continue

            self.model_names.append(self.categorical_instances[i])
            con_graph, bboxs, origin = get_con_graph_and_bounding_boxes(model_name, self.known_parts)
            data.__setitem__('connectivity_graph', con_graph)
            data.__setitem__('bounding_boxes', bboxs)
            data.__setitem__('origin', origin)

            if self.pre_filter is not None and not self.pre_filter(data):
                continue

            if self.pre_transform is not None:
                data = self.pre_transform(data)

            # GUI Display of each model in the dataset
            if self.visualize:
                print(data.name)
                pcd = tensor_to_point_cloud(data, object_instances=self.known_parts)
                bboxes = bounding_boxes_lines(bboxs)
                o3d.draw_geometries([bboxes, pcd])

            if not Path(self.processed_dir).exists():
                Path.mkdir(Path(self.processed_dir))
            torch.save(data, Path(self.processed_dir, f'data_{i}.pt'))
            i += 1

    def __getitem__(self, item):
        data = self.get(item)
        data = data if self.transform is None else self.transform(data)
        return data

    def get(self, idx):
        data = torch.load(Path(self.processed_dir, f'data_{idx}.pt'))
        print(f'Loaded {self.names[idx]}')
        return data
        # cur_count = 0
        # for path in Path(self.processed_dir).iterdir():
        #     if cur_count == idx:
        #         data = torch.load(path)
        #         return data
        #     cur_count += 1

    def processed_file_names(self):
        return [model + '.pt' for model in self.categorical_instances]

