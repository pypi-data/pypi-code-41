import numpy as np

from collada import *
from PySimultan.layer import *
from PySimultan.vertice import *
from PySimultan.edge import *
from PySimultan.edge_loop import *
from PySimultan.face import *
from PySimultan.building import *


def read_dae(file_path):
    layers = list()
    vertices = list()
    edges = list()
    edge_loops = list()
    faces = list()

    # create a layer:
    layers.append(Layer())

    # read the .dae file:
    mesh = Collada(file_path, ignore=[DaeUnsupportedError, DaeBrokenRefError])

    for geometry in mesh.geometries:

        for primitive in geometry.primitives:

            if primitive.npolygons == 0:
                continue

            if vertices.__len__() == 0:
                first_new_vertex = 0
            else:
                first_new_vertex = vertices.__len__()
            # create vertices:
            for i in range(primitive.vertex.shape[0]):
                vertices.append(Vertex(layers=layers[0],
                                       position=primitive.vertex[i, :],
                                       color_from_parent=True)
                                )

            for i in range(primitive.npolygons):

                # create edges:
                if edges.__len__() == 0:
                    first_new_edge = 0
                else:
                    first_new_edge = edges.__len__()
                first_node = primitive.polystarts[i]
                last_node = primitive.polyends[i]
                for j in range(primitive.polystarts[i], primitive.polyends[i]):
                    edges.append(Edge(vertex_1=vertices[primitive.vertex_index[j] + first_new_vertex],
                                      vertex_2=vertices[primitive.vertex_index[j+1 if (j+1) < last_node else first_node] + first_new_vertex],
                                      layers=layers[0]
                                      )
                                 )
                last_new_edge = edges.__len__()

                # create edge_loop:
                edge_loops.append(EdgeLoop(layers=layers[0],
                                           edges=edges[first_new_edge:last_new_edge]))

                # create face:
                faces.append(
                             Face(layers=layers[0],
                                  boundary=edge_loops[-1],
                                  orientation=0
                                  )
                            )

    # -----------------------------------------------------------------------------------
    # create building
    # -----------------------------------------------------------------------------------

    my_building = Building(vertices=vertices,
                           faces=faces,
                           layers=layers,
                           edges=edges,
                           edge_loops=edge_loops
                           )

    return my_building




