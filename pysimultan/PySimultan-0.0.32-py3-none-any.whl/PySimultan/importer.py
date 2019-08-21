# from shapely.geometry import Polygon
import pkg_resources

from tkinter import Tk
from tkinter.filedialog import askopenfilename
import numpy as np

from PySimultan.layer import Layer
from PySimultan.vertice import Vertex
from PySimultan.edge import Edge
from PySimultan.edge_loop import EdgeLoop
from PySimultan.polyline import Polyline
from PySimultan.face import Face
from PySimultan.material import Material, MatLayer, Window
from PySimultan.zone import Zone
from PySimultan.building import Building
from PySimultan.proxy_geometry import ProxyGeometry

from PySimultan.import_dae import read_dae
from PySimultan.import_obj import read_obj
from PySimultan.import_stl import import_stl
from PySimultan.geo_functions import print_status


class Importer(object):
    def __init__(self):
        self.data = None
        self.status = None
        self.content = None
        self.header = None
        self.model = None
        self.layers = None
        self.layers_data = None
        self.vertices = None
        self.vertices_data = None
        self.edges = None
        self.edges_data = None
        self.edge_loops = None
        self.edge_loops_data = None
        self.polylines = None
        self.polylines_data = None
        self.faces = None
        self.faces_data = None
        self.volumes = None
        self.volumes_data = None
        self.proxy_geometries = None
        self.proxy_geometries_data = None
        self.building = None

    def import_geometry(self, filename, encoding_format='utf16'):
        # file picker for debugging surposes
        # Tk().withdraw()
        # file = askopenfilename()
        try:
            self.read_content(filename=filename, encoding_format=encoding_format)
            print_status('reading content successful')
        except Exception as e:
            print_status('error while reading content: {} '.format(e))
            raise e

        try:
            self.parse_content()
            print_status('parsing content successful')
        except Exception as e:
            print_status('error while parsing content: {} '.format(e))
            raise e

        try:
            self.parse_layers()
            print_status('layer creation successful')
        except Exception as e:
            print_status('error while parsing layers: {} '.format(e))
            raise e

        try:
            self.parse_vertices()
            print_status('vertex creation successful')
        except Exception as e:
            print_status('error while parsing vertices: {} '.format(e))
            raise e

        try:
            self.parse_edges()
            print_status('edge creation successful')
        except Exception as e:
            print_status('error while parsing edges: {} '.format(e))
            raise e

        try:
            self.parse_edge_loops()
            print_status('edge loop creation successful')
        except Exception as e:
            print_status('error while parsing edge loops: {} '.format(e))
            raise e

        try:
            self.parse_polylines()
            print_status('polyline creation successful')
        except Exception as e:
            print_status('error while parsing polylines: {} '.format(e))
            raise e

        try:
            self.parse_faces()
            print_status('face creation successful')
        except Exception as e:
            print_status('error while parsing faces: {} '.format(e))
            raise e

        try:
            self.parse_volumes()
            print_status('volume creation successful')
        except Exception as e:
            print_status('error while parsing volumes: {} '.format(e))
            raise e

        try:
            self.parse_building()
            print_status('building creation successful')
        except Exception as e:
            print_status('error while parsing building: {} '.format(e))
            raise e

        print_status('geometry sucessfully imported \n \n --------------------------------------')

    def read_content(self, filename, encoding_format='utf16'):

        with open(filename, 'r', encoding=encoding_format) as f:
            print_status('reading file')
            content = f.read()

        self.content = content.rstrip('\r\n').replace('\n', ';')
        # self.content = content
        self.data = self.content.split(';')

    def parse_content(self):
        """

        :return:
        """
        # file format description:
        # https://github.com/bph-tuwien/SIMULTAN/wiki/FORMAT_geosim
        print_status('processing header')

        self.parse_header()

        # remove all newline characters
        # content = content.rstrip('\r\n').replace('\n', ';')
        # # split string:
        # data = content.split(';')
        #
        # # ------------------------------------------------------------------
        # # read Header
        # # ------------------------------------------------------------------
        #
        # header_fields = ['FormatType',                   # 0        str
        #                  'Version',                      # 1        int
        #                  'ModelID',                      # 2        ulong
        #                  'ModelPermissions',             # 3        ulong
        #                  'GeometryPermissions',          # 4
        #                  'LayerPermissions',             # 5
        #                  'LayerCount',                   # 6
        #                  'VertexCount',                  # 7
        #                  'EdgeCount',                    # 8
        #                  'EdgeLoopCount',                # 9
        #                  'PolylineCount',                # 10
        #                  'FaceCount',                    # 11
        #                  'VolumeCount',                  # 12
        #                  'LinkedModelCount',             # 13
        #                  'ProxyCount',                   # 14
        #                  'GeoRefCount'                   # 15
        #                  ]
        #
        # header_formats = []
        #
        # data[1:15] = map(int, data[1:15])
        #
        # # header
        # header = dict(zip(header_fields[2:], data[1:15]))
        # header['FormatType'] = data[0][0]
        # header['Version'] = data[0][1]
        # data = data[16:]
        #
        # self.header = header

        # Model

        self.model = {'Name': self.data[1][0:int(self.data[0])], 'IsVisible': bool(self.data[1][int(self.data[0])])}
        # remove model entry:
        self.data = self.data[2:]

        # -----------------------------------------------------------------------------------
        # read layers
        # -----------------------------------------------------------------------------------

        layer_header = ['ID',		        # ulong
                        'ParentID',	        # ulong (or empty when no parent exists)
                        'Name',		        # string
                        'IsVisible',	    # bool
                        'ColorR',		    # byte
                        'ColorG',		    # byte
                        'ColorB',		    # byte
                        'ColorA',		    # byte
                        'ColorFromParent'   # bool
                        ]

        print_status('reading layers')

        layers_data = list()

        for i in range(self.header['LayerCount']):
            layers_data.append(self.data[0:8])
            self.data = self.data[8:]

        self.layers_data = layers_data

        # -----------------------------------------------------------------------------------
        # read vertices
        # -----------------------------------------------------------------------------------

        vertices_data = list()

        print_status('reading vertices')
        for i in range(self.header['VertexCount']):
            vertices_data.append(self.data[0:11])
            self.data = self.data[11:]

        self.vertices_data = vertices_data

        # -----------------------------------------------------------------------------------
        # read edges
        # -----------------------------------------------------------------------------------

        edges_data = list()

        print_status('reading edges')
        for i in range(self.header['EdgeCount']):
            edges_data.append(self.data[0:10])
            self.data = self.data[10:]

        self.edges_data = edges_data

        # -----------------------------------------------------------------------------------
        # read edge-loops
        # -----------------------------------------------------------------------------------

        edge_loops_data = list()

        print_status('reading edge loops')
        for i in range(self.header['EdgeLoopCount']):
            edge_count = int(self.data[3][1:])
            edge_loops_data.append(self.data[0:edge_count+9])
            self.data = self.data[edge_count + 9:]

        self.edge_loops_data = edge_loops_data

        # -----------------------------------------------------------------------------------
        # read polylines
        # -----------------------------------------------------------------------------------

        polylines_data = list()

        print_status('reading polylines')
        for i in range(self.header['PolylineCount']):
            edge_count = int(self.data[3][1:])
            polylines_data.append(self.data[0:edge_count + 9])
            self.data = self.data[edge_count + 9:]

        self.polylines_data = polylines_data

        # -----------------------------------------------------------------------------------
        # read faces
        # -----------------------------------------------------------------------------------

        faces_data = list()

        print_status('reading faces')
        for i in range(self.header['FaceCount']):
            hole_count = int(self.data[4])
            faces_data.append(self.data[0:hole_count + 11])
            self.data = self.data[hole_count + 11:]

        self.faces_data = faces_data

        # -----------------------------------------------------------------------------------
        # read volumes
        # -----------------------------------------------------------------------------------

        volumes_data = list()

        print_status('reading volumes')
        for i in range(self.header['VolumeCount']):
            face_count = int(self.data[3][1:])
            volumes_data.append(self.data[0:9+face_count])
            self.data = self.data[9+face_count:]

        self.volumes_data = volumes_data

        # -----------------------------------------------------------------------------------
        # read ProxyGeometry
        # -----------------------------------------------------------------------------------

        proxy_geometries_data = list()
        proxy_geometries = list()

        print_status('reading proxy geometries')
        for i in range(self.header['ProxyCount']):
            proxy_geometries_data.append(self.data[0:16])
            self.data = self.data[16:]

        self.proxy_geometries_data = proxy_geometries_data

        # -----------------------------------------------------------------------------------
        # process ProxyGeometry
        # -----------------------------------------------------------------------------------

    def parse_header(self):
        content = self.content
        # split string:


        # ------------------------------------------------------------------
        # read Header
        # ------------------------------------------------------------------

        header_fields = ['FormatType',  # 0        str
                         'Version',  # 1        int
                         'ModelID',  # 2        ulong
                         'ModelPermissions',  # 3        ulong
                         'GeometryPermissions',  # 4
                         'LayerPermissions',  # 5
                         'LayerCount',  # 6
                         'VertexCount',  # 7
                         'EdgeCount',  # 8
                         'EdgeLoopCount',  # 9
                         'PolylineCount',  # 10
                         'FaceCount',  # 11
                         'VolumeCount',  # 12
                         'LinkedModelCount',  # 13
                         'ProxyCount',  # 14
                         'GeoRefCount'  # 15
                         ]

        header_formats = []

        self.data[1:15] = map(int, self.data[1:15])

        # header
        header = dict(zip(header_fields[2:], self.data[1:15]))
        header['FormatType'] = self.data[0][0]
        header['Version'] = self.data[0][1]
        self.data = self.data[16:]

        self.header = header

    def parse_layers(self):

        print_status('processing layers')

        layers = list()

        for layer_data in self.layers_data:
            # convert data:
            if layer_data[1]:
                parent_id = int(layer_data[1])
            else:
                parent_id = []

            is_visible = layer_data[3][int(layer_data[2])]
            color = np.array(int(layer_data[3][int(layer_data[2]) + 1:]))
            color = np.append(color, (list(map(int, layer_data[4:7]))))

            layers.append(Layer(layer_id=int(layer_data[0]),
                                parent_id=parent_id,
                                name=layer_data[3][0:int(layer_data[2])],
                                is_visible=is_visible,
                                color=color,
                                color_from_parent=bool(layer_data[7])
                                )
                          )

        self.layers = layers
        # return layers

    def parse_vertices(self):

        print_status('processing vertices')

        vertices = list()
        for vertex_data in self.vertices_data:

            position = float(vertex_data[3][1:])
            position = np.append(position, (list(map(float, vertex_data[4:6]))))
            color = np.array(list(map(int, vertex_data[6:10])))
            layer_id = int(vertex_data[2][int(vertex_data[1]):])
            layer = next((x for x in self.layers if x.ID == layer_id), None)

            vertices.append(Vertex(vertex_id=int(vertex_data[0]),
                                   layers=layer,
                                   name=vertex_data[2][0:int(vertex_data[1])],
                                   is_visible=bool(vertex_data[3][0]),
                                   position=position,
                                   color=color,
                                   color_from_parent=bool(vertex_data[10])))
        self.vertices = vertices

        # return vertices

    def parse_edges(self):

        print_status('processing edges')

        edges = list()

        for edge_data in self.edges_data:
            color = np.array(list(map(int, edge_data[5:8])))

            vertex_1 = next((x for x in self.vertices if x.ID == int(edge_data[3][1:])), None)
            vertex_2 = next((x for x in self.vertices if x.ID == int(edge_data[4])), None)

            layer_id = int(edge_data[2][int(edge_data[1]):])
            layer = next((x for x in self.layers if x.ID == layer_id), None)

            edges.append(Edge(vertex_1=vertex_1,
                              vertex_2=vertex_2,
                              edge_id=int(edge_data[0]),
                              name=edge_data[2][0:int(edge_data[1])],
                              layers=layer,
                              is_visible=bool(edge_data[3][0]),
                              color=color,
                              color_from_parent=bool(edge_data[9]))
                         )
        self.edges = edges
        # return edges

    def parse_edge_loops(self):

        print_status('processing edge loops')

        edge_loops = list()

        for edge_loop_data in self.edge_loops_data:
            edge_count = int(edge_loop_data[3][1:])
            edge_ids = list(map(int, edge_loop_data[4:4 + int(edge_loop_data[3][1:])]))

            edge_loop_edges = []
            for edge_id in edge_ids:
                edge_loop_edges.append(next((x for x in self.edges if x.ID == edge_id), None))

            color = np.array(list(map(
                int, edge_loop_data[4 + int(edge_loop_data[3][1:]):4 + int(edge_loop_data[3][1:]) + 4]
            )))
            color_from_parent = bool(edge_loop_data[4 + edge_count + 4])

            layer_id = int(edge_loop_data[2][int(edge_loop_data[1]):])
            layer = next((x for x in self.layers if x.ID == layer_id), None)

            edge_loops.append(EdgeLoop(
                edge_loop_id=int(edge_loop_data[0]),
                name=edge_loop_data[2][0:int(edge_loop_data[1])],
                layers=layer,
                is_visible=bool(edge_loop_data[3][0]),
                edge_id=edge_ids,
                color=color,
                color_from_parent=color_from_parent,
                edges=edge_loop_edges
            )
            )
        self.edge_loops = edge_loops
        # return edge_loops

    def parse_polylines(self):

        print_status('processing polylines')

        polylines = list()

        for data in self.polylines_data:
            edge_count = int(data[3][1:])
            self.polylines_data.append(data[0:edge_count + 9])
            data = data[edge_count + 9:]

            edge_count = int(data[3][1:])
            edge_ids = list(map(int, data[4:4 + int(data[3][1:])]))

            polyline_edges = []
            for edge_id in edge_ids:
                polyline_edges.append(next((x for x in self.edges if x.ID == edge_id), None))

            layer_id = int(data[2][int(data[1]):])
            layer = next((x for x in self.layers if x.ID == layer_id), None)

            polylines.append(Polyline(
                poly_id=int(data[0]),
                name=data[2][0:int(data[1])],
                layers=layer,
                is_visible=bool(data[3][0]),
                edge_ids=edge_ids,
                color=np.append(np.random.rand(1, 3), 0) * 255,
                color_from_parent=False,
                edges=polyline_edges
            )
            )
        self.polylines = polylines
        # return polylines

    def parse_faces(self):

        print_status('processing faces')

        faces = list()

        # create default material:
        from PySimultan.material import Part as NewPart

        default_part = NewPart(name='Default part')

        for data in self.faces_data:

            # check if face already exists:
            face_exists = next((x for x in self.edge_loops if x.ID == int(data[0])), None)
            if face_exists:
                continue

            hole_count = int(data[4])
            boundary_id = int(data[3][1:])
            color = np.array(list(map(int, data[5 + hole_count + 1:9 + hole_count + 1])))
            color_from_parent = bool(data[9 + hole_count + 1])
            boundary = next((x for x in self.edge_loops if x.ID == boundary_id), None)

            if not(hole_count == 0):
                hole_ids = list(map(int, data[5:5+hole_count]))
                holes = list()
                # if there is a hole in the face:
                for hole_id in hole_ids:
                    # check if the hole - face already exists
                    hole = next((x for x in faces if x.Boundary[0].ID == hole_id), None)

                    # check if hole-face is going to be created:
                    if not hole:
                        hole_face_indx = []
                        for hole_data in enumerate(self.faces_data):
                            if int(hole_data[1][3][1:]) == hole_id:
                                hole_face_indx = hole_data[0]
                                break
                        # if a face to be created was found, create the face:
                        if hole_face_indx:
                            hole_data = self.faces_data[hole_face_indx]
                            hole_count = 0
                            hole_boundary = next((x for x in self.edge_loops if x.ID == hole_id), None)

                            layer_id = int(hole_data[2][int(hole_data[1]):])
                            layer = next((x for x in self.layers if x.ID == layer_id), None)

                            hole = Face(name=hole_data[2][0:int(hole_data[1])],
                                        layers=layer,
                                        is_visible=bool(hole_data[3][0]),
                                        boundary=hole_boundary,
                                        orientation=int(data[5 + hole_count]),
                                        color=color,
                                        color_from_parent=color_from_parent,
                                        part=default_part)
                        # create new face
                        else:   # if hole_face_indx:
                            hole_boundary = next((x for x in self.edge_loops if x.ID == hole_id), None)

                            layer_id = int(data[2][int(data[1]):])
                            layer = next((x for x in self.layers if x.ID == layer_id), None)

                            hole = Face(name='Hole{}'.format(hole_id),
                                        layers=layer,
                                        is_visible=bool(data[3][0]),
                                        boundary=hole_boundary,
                                        orientation=int(data[5 + hole_count]),
                                        color=color,
                                        color_from_parent=color_from_parent,
                                        overwrite_calcable=True,
                                        part=default_part)

                    holes.append(hole)
                    faces.append(hole)
            else:   # if not(hole_count == 0):
                hole_ids = list()
                holes = list()

            layer_id = int(data[2][int(data[1]):])
            layer = next((x for x in self.layers if x.ID == layer_id), None)

            faces.append(
                Face(face_id=int(data[0]),
                     name=data[2][0:int(data[1])],
                     layers=layer,
                     is_visible=bool(data[3][0]),
                     boundary=boundary,
                     holes=holes,
                     orientation=int(data[5+hole_count]),
                     color=color,
                     color_from_parent=color_from_parent,
                     overwrite_calcable=True,
                     part=default_part)
            )
        self.faces = faces
        # return faces

    def parse_volumes(self):

        print_status('processing volumes')

        volumes = list()

        for data in self.volumes_data:

            try:
                face_count = int(data[3][1:])
                face_ids = list(map(int, data[4:4+face_count]))
            except Exception as e:
                print_status('error: {error} \n data-str: {data_str}'.format(error=e, data_str=data))
                face_ids = list()
                face_count = 0

            zone_faces = list()
            for face_id in face_ids:
                zone_faces.append(next((x for x in self.faces if x.ID == face_id), None))

            color = np.array(list(map(int, data[4 + face_count + 1:9 + face_count])))
            try:
                color_from_parent = bool(data[7 + face_count + 1])
            except Exception as e:
                color_from_parent = False

            volumes.append(Zone(
                                zone_id=int(data[0]),
                                name=data[2][0:int(data[1])],
                                is_visible=bool(data[3][0]),
                                face_ids=face_ids,
                                faces=zone_faces,
                                color=color,
                                color_from_parent=color_from_parent
                                )
                           )
        self.volumes = volumes
        # return volumes

    def parse_proxy_geometries(self):

        print_status('processing proxy_geometries')

        proxy_geometries = list()

        for data in self.proxy_geometries_data:
            proxy_geometries.append(ProxyGeometry())

        self.proxy_geometries = proxy_geometries
        #return proxy_geometries

    def parse_building(self):
        my_building = Building(is_visible=self.model['IsVisible'],
                               vertices=self.vertices,
                               faces=self.faces,
                               zones=self.volumes,
                               name=self.model['Name'],
                               layers=self.layers,
                               edges=self.edges,
                               geometry_permissions=self.header["GeometryPermissions"],
                               layer_permissions=self.header['LayerPermissions'],
                               model_permissions=self.header["ModelPermissions"],
                               edge_loops=self.edge_loops,
                               polylines=self.polylines,
                               geo_ref_count=self.header["GeoRefCount"],
                               linked_model_count=self.header["LinkedModelCount"],
                               building_id=self.header["ModelID"])
        self.building = my_building


if __name__ == '__main__':

    import json

    # file picker for debugging surposes
    # Tk().withdraw()
    # file = askopenfilename()

    # read default simgeo file:
    file = pkg_resources.resource_filename('resources', 'two_rooms_linked.simgeo')

    # file picker for debugging surposes
    Tk().withdraw()
    file = askopenfilename()

    if file.endswith('.dae'):
        building = read_dae(file)
    elif file.endswith('.obj'):
        building = read_obj(file)
    elif file.endswith('.stl'):
        building = import_stl(file)
    elif file.endswith('.simgeo'):
        importer = Importer()
        importer.import_geometry(file)
        building = importer.building
    else:
        building = Building()

    print_status('Geometry successful imported')

    file_name = askopenfilename()
    with open(file_name, "r", encoding='utf8') as text_file:
        data = text_file.read()
        import_config = json.loads(data)
        # scale the building

    file_name = askopenfilename()
    building.import_data_from_excel(filename=file_name, import_config=import_config)


    # building.plot_faces()

    # building.write_stl()

    # write .simgeo file:
    # building.write_simgeo()
