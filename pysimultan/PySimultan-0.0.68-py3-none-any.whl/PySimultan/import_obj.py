import os

from tkinter import Tk
from tkinter.filedialog import askopenfilename

from PySimultan.vertice import *
from PySimultan.edge import *
from PySimultan.edge_loop import *
from PySimultan.face import *
from PySimultan.building import *
from PySimultan.material import *


def read_obj(file_path):

    obj = Obj(file_path)

    return obj.Building


class Obj:
    def __init__(self, filename, file=None, path=None):

        self.layers = list()
        self.vertices = list()
        self.edges = list()
        self.edge_loops = list()
        self.faces = list()
        self.parts = list()

        # create a layer:
        self.layers.append(Layer())

        used_mat = []

        if file is None:
            file = open(filename, 'r')

        if path is None:
            path = os.path.dirname(filename)
        self.path = path

        for line in file:
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'v':
                vertex = Vertex(layers=self.layers[0],
                                position=np.float_(values[1:4]))
                self.vertices.append(vertex)

            elif values[0] == 'mtllib':
                print(values[1])

            elif values[0] in ('usemtl', 'usemat'):
                part_list = []
                [part_list.append(i.Name) for i in self.parts]
                if not(values[1] in part_list):
                    mat = Part(name=values[1])
                    self.parts.append(mat)
                    part_list.append(values[1])

                used_part = self.parts[-1]

            elif values[0] == 'o':

                pass

            elif values[0] == 'f':
                # points = []

                points_list = []
                for i, v in enumerate(values[1:]):
                    v_index, t_index, n_index = map(int, [j or 0 for j in v.split('/')])
                    if v_index < 0:
                        v_index += len(self.vertices) - 1
                    if n_index < 0:
                        n_index += len(self.normals) - 1
                    # vertex = tex_coords[t_index] + \
                    #         normals[n_index] + \
                    #         vertices[v_index]
                    points_list.append(self.vertices[v_index-1])

                    # create edges:
                if self.edges.__len__() == 0:
                    first_new_edge = 0
                else:
                    first_new_edge = self.edges.__len__()

                for j in range(points_list.__len__()):
                    self.edges.append(Edge(vertex_1=points_list[j],
                                           vertex_2=points_list[j + 1 if (j + 1) < points_list.__len__() else 0],
                                           layers=self.layers[0]
                                           )
                                      )
                last_new_edge = self.edges.__len__()

                # create edge_loop:
                self.edge_loops.append(EdgeLoop(layers=self.layers[0],
                                                edges=self.edges[first_new_edge:last_new_edge]))

                # create face:
                self.faces.append(
                    Face(layers=self.layers[0],
                         boundary=self.edge_loops[-1],
                         orientation=0,
                         part=used_part
                         )
                )
        self.Building = Building(vertices=self.vertices,
                                 faces=self.faces,
                                 layers=self.layers,
                                 edges=self.edges,
                                 edge_loops=self.edge_loops)


if __name__ == '__main__':

    # file picker for debugging surposes
    Tk().withdraw()
    file = askopenfilename()

    MyBuilding = read_obj(file)

    MyBuilding.move_to_origin()

    MyBuilding.write_stl()

    print('done')






