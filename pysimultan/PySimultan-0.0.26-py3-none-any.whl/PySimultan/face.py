
import numpy as np
# from geo_functions import *
# from material import *

import uuid
import itertools
# from polygon_triangulation import polygon_triangulate
import triangle
# import matplotlib.pyplot as plt
# import gmsh
import trimesh
import pyclipper

from PySimultan.geo_functions import unit_normal, convert_to_global, convert_to_local, polygon_area_3d
from PySimultan.material import Part as NewPart
from PySimultan.base_classes import GeoBaseClass
from PySimultan.vertice import Vertex
from PySimultan.edge import Edge
from PySimultan.edge_loop import EdgeLoop


class Face(GeoBaseClass):

    new_face_id = itertools.count(0)
    visible_class_name = 'Face'

    def __init__(self,
                 face_id=uuid.uuid4(),
                 name=None,
                 layers=None,
                 is_visible=True,
                 boundary=None,
                 holes=None,
                 orientation=0,
                 color=np.append(np.random.rand(1, 3), 0)*255,
                 color_from_parent=False,
                 overwrite_calcable=True,
                 area=0,
                 triangulation=None,
                 part=None
                 ):

        super().__init__(id=face_id,
                         pid=next(type(self).new_face_id),
                         color=color,
                         name=name,
                         color_from_parent=color_from_parent,
                         is_visible=is_visible,
                         layers=layers
                         )

        self._Normal = []
        self._Coords = None
        self._Holes = list()
        self._Part = None
        self._Boundary = list()
        self._BoundaryID = None

        if boundary is None:
            self.Boundary = []
        elif type(boundary) == list:
            self.Boundary = boundary
        else:
            self.Boundary = [boundary]

        self.BoundaryID = self.Boundary[0].ID

        if holes is None:
            self.Holes = list()
        elif type(holes) == list:
            self.Holes = holes
        else:
            self.Holes = [holes]

        if self.Holes.__len__() > 0:
            self.HoleIDs = list(x.ID for x in self._Holes)
        else:
            self.HoleIDs = []

        self.HoleCount = self.Holes.__len__()

        if name is None:
            self._Name = 'face{}'.format(self._PID)
        else:
            self._Name = name

        if part is None:
            if not NewPart.get_instances():
                self.Part = NewPart()
            else:
                self.Part = NewPart.get_instances()[0]
        else:
            self.Part = part

        self._IsVisible = is_visible
        self._Orientation = orientation
        self._Color = color
        self._ColorFromParent = color_from_parent
        self._OverwriteCalcable = overwrite_calcable        # the attributes which can be calculated for this face are overwritten
        self._Points = list()

        self._Area = area
        self._Closed = []
        self._LocalCoord = []
        self._G2L_TransMat = []
        self._Triangulation = triangulation
        self._Mesh = []
        self._Circumference = None

        self._observers = []

        # -----------------------------------------------
        # bindings
        # -----------------------------------------------

        for hole in self._Holes:
            hole.bind_to(self.hole_updated)

        for boundary in self._Boundary:
            boundary.bind_to(self.boundary_updated)

        self.Part.bind_to(self.part_updated)

        # -----------------------------------------------
        # initial face calculations
        # -----------------------------------------------

        if self._OverwriteCalcable:
            self.calc_normal()
            self.create_poly_points()
            self.create_poly_coordinates()
            self.calculate_area()
            self.convert_to_local_coord()
            self.triangulate()
            self.create_mesh()

    # --------------------------------------------------------
    # specific attributes
    # --------------------------------------------------------

    @property
    def Boundary(self):
        return self._Boundary

    @Boundary.setter
    def Boundary(self, value):
        if not(isinstance(value, list)):
            if value is None:
                value = []
            else:
                value = [value]

        self._default_set_handling('Boundary', value)

    @property
    def Mesh(self):
        return self._Mesh

    @Mesh.setter
    def Mesh(self, value):
        self._default_set_handling('Mesh', value)

    @property
    def OverwriteCalcable(self):
        return self._OverwriteCalcable

    @OverwriteCalcable.setter
    def OverwriteCalcable(self, value):
        self._default_set_handling('OverwriteCalcable', value)

    @property
    def BoundaryID(self):
        return self._Boundary[0].ID

    @BoundaryID.setter
    def BoundaryID(self, value):
        self._default_set_handling('BoundaryID', value)

    @property
    def Holes(self):
        return self._Holes

    @Holes.setter
    def Holes(self, value):
        if isinstance(value, list):
            if value:
                if not(type(value) == list):
                    value = [value]
            else:
                value = []
        else:
            value = [value]

        self._default_set_handling('Holes', value)

        self.HoleCount = self.Holes.__len__()

        if self.Holes.__len__() > 0:
            self.HoleIDs = list(x.ID for x in self.Holes)
        else:
            self.HoleIDs = []

    @property
    def HoleCount(self):
        return self._HoleCount

    @HoleCount.setter
    def HoleCount(self, value):
        self._default_set_handling('HoleCount', value)

    @property
    def HoleIDs(self):
        return self._HoleIDs

    @HoleIDs.setter
    def HoleIDs(self, value):
        self._default_set_handling('HoleIDs', value)

    @property
    def Orientation(self):
        return self._Orientation

    @Orientation.setter
    def Orientation(self, value):
        self._default_set_handling('Orientation', value)

    @property
    def Points(self):
        return self._Points

    @Points.setter
    def Points(self, value):
        self._default_set_handling('Points', value)

    @property
    def Area(self):
        return self._Area

    @Area.setter
    def Area(self, value):
        self._default_set_handling('Area', value)

    @property
    def Normal(self):
        return self._Normal

    @Normal.setter
    def Normal(self, value):
        self._default_set_handling('Normal', value)

    @property
    def Coords(self):
        if self._Coords is None:
            self.create_poly_coordinates()
        return self._Coords

    @Coords.setter
    def Coords(self, value):
        self._default_set_handling('Coords', value)

    @property
    def Closed(self):
        return self._Closed

    @Closed.setter
    def Closed(self, value):
        self._default_set_handling('Closed', value)

    @property
    def LocalCoord(self):
        return self._LocalCoord

    @LocalCoord.setter
    def LocalCoord(self, value):
        self._default_set_handling('LocalCoord', value)

    @property
    def G2L_TransMat(self):
        return self._G2L_TransMat

    @G2L_TransMat.setter
    def G2L_TransMat(self, value):
        self._default_set_handling('G2L_TransMat', value)

    @property
    def Triangulation(self):
        return self._Triangulation

    @Triangulation.setter
    def Triangulation(self, value):
        self._default_set_handling('Triangulation', value)

    @property
    def Part(self):
        if self._Part is None:
            if not NewPart.get_instances():
                self.Part = NewPart()
            else:
                self.Part = NewPart.get_instances()[0]
        return self._Part

    @Part.setter
    def Part(self, value):
        self._default_set_handling('Part', value)
        if not(value is None):
            self._Part.bind_to(self.part_updated)

    @property
    def Circumference(self):
        if self._Circumference is None:
            self.calc_circumference()
        return self._Circumference

    @Circumference.setter
    def Circumference(self, value):
        self._default_set_handling('Circumference', value)

    # --------------------------------------------------------
    # observed object change callbacks
    # --------------------------------------------------------

    def hole_updated(self, **kwargs):
        for key, value in kwargs.items():
            self.print_status("{0} = {1}".format(key, value))
            if value == 'vertex_position_changed':
                if self._OverwriteCalcable:
                    self.calc_normal()
                    self.create_poly_points()
                    self.create_poly_coordinates()
                    self.calculate_area()
                    self.convert_to_local_coord()
                    self.triangulate()
                    self.create_mesh()
                for callback in self._observers:
                    instance = callback.__self__
                    instance._UpdateHandler.add_notification(callback, 'vertex_position_changed')

    def boundary_updated(self, **kwargs):
        for key, value in kwargs.items():
            self.print_status("{0} = {1}".format(key, value))
            if value == 'vertex_position_changed':
                if self._OverwriteCalcable:
                    self.calc_normal()
                    self.create_poly_points()
                    self.create_poly_coordinates()
                    self.calculate_area()
                    self.convert_to_local_coord()
                    self.triangulate()
                    self.create_mesh()
                for callback in self._observers:
                    instance = callback.__self__
                    instance._UpdateHandler.add_notification(callback, 'vertex_position_changed')

    def part_updated(self):
        print('Part updated')

    # --------------------------------------------------------
    # class methods
    # --------------------------------------------------------

    def create_poly_points(self):

        self._Points = list()

        self._Points.append(self.Boundary[0].Edges[0].Vertex1)
        self._Points.append(self.Boundary[0].Edges[0].Vertex2)

        for i in range(1, self._Boundary[0].EdgeCount):
            if self._Points[-1] == self.Boundary[0].Edges[i].Vertex1:
                self._Points.append(self.Boundary[0].Edges[i].Vertex2)
            elif self._Points[-1] == self.Boundary[0].Edges[i].Vertex2:
                self._Points.append(self.Boundary[0].Edges[i].Vertex1)
            else:
                self.print_status('start of the edge is not the end of the previous edge')

        # check if polygon is closed
        if self._Points[-1] == self._Points[0]:
            self._Closed = True
        else:
            self._Closed = False

        self.Points = self._Points

    def calc_normal(self):

        if self._Points.__len__() > 2:
            # other method
            a = np.array(self._Points[0].Position)
            b = np.array(self._Points[1].Position)
            c = np.array(self._Points[2].Position)

            self.Normal = unit_normal(a, b, c)
        else:
            self.Normal = []

    def create_poly_coordinates(self):
        self._Coords = np.zeros((self.Points.__len__()-1, 3))
        for i in range(self.Points.__len__() - 1):
            self._Coords[i, :] = self.Points[i].Position

        self.Coords = self._Coords

    def convert_to_local_coord(self, *args):

        self.LocalCoord, self.G2L_TransMat = convert_to_local(self.Coords)

        if args:
            points = args
            local_coords = np.zeros((len(points), 2))
            local_coords[:, 0] = np.dot((points - self.G2L_TransMat.loc0), self.G2L_TransMat.locx)
            local_coords[:, 1] = np.dot((points - self.G2L_TransMat.loc0), self.G2L_TransMat.locy)
            return local_coords
        else:
            return self.LocalCoord, self.G2L_TransMat

    def convert_to_global_coord(self, *args):
        if args:
            points = args[0]
            return convert_to_global(self.G2L_TransMat.transformation_mat, points)
        else:
            return convert_to_global(self.G2L_TransMat.transformation_mat, self.LocalCoord)

    def calculate_area(self):

        area = polygon_area_3d(self.Coords)

        # subtract holes area:
        hole_area = 0
        if any(self.Holes):
            for hole in self.Holes:
                hole_area += hole.Area
            self.Area = area - hole_area
        else:
            self.Area = area

    def triangulate(self):

        segments = []
        for i in range(len(self.Points) - 2):
            segments.append([int(i), int(i + 1)])
        segments.append([int(i + 1), int(0)])

        # handle holes
        if self.HoleCount > 0:
            local_coord = self._LocalCoord
            holes_point = np.empty(0)
            for hole in self.Holes:
                initial_number_of_nodes = local_coord.shape[0]
                hole_local_ccord = self._G2L_TransMat.transform(hole.Coords)
                local_coord = np.vstack((local_coord, hole_local_ccord))
                for i in range(len(hole.Points) - 2):
                    segments.append([int(i+initial_number_of_nodes), int(i + 1 + initial_number_of_nodes)])
                segments.append([int(i + 1 + initial_number_of_nodes), int(0 + initial_number_of_nodes)])

                # create points inside the hole; these points are the centre of gravity of the triangulated hole:
                # https://de.wikipedia.org/wiki/Geometrischer_Schwerpunkt#Dreieck

                for j in range(hole.Triangulation['triangles'].shape[0]):
                    s = np.array(
                        (1/3 * np.sum(hole_local_ccord[hole.Triangulation['triangles'][j, :], 0]),
                         1/3 * np.sum(hole_local_ccord[hole.Triangulation['triangles'][j, :], 1])
                         )
                    )
                    if holes_point.shape[0] == 0:
                        holes_point = s
                    else:
                        holes_point = np.vstack((holes_point, s))

            a = {'vertices': local_coord, 'segments': segments, 'holes': holes_point}

            # add a vertex, which lies inside the hole:

        else:
            a = {'vertices': self.LocalCoord, 'segments': segments}

        triangulation = triangle.triangulate(a, 'p')
        # triangle.compare(plt, dict(vertices=self._LocalCoord), triangulation)
        triangulation['vertices3D'] = convert_to_global(self.G2L_TransMat.transformation_mat, triangulation['vertices'])

        # plt.show()
        self.Triangulation = triangulation

    def calc_circumference(self):
        if type(self.Boundary) == list:
            self._Circumference = self.Boundary[0].Length
        else:
            self._Circumference = self.Boundary.Length

    def create_mesh(self):
        self.Mesh = trimesh.Trimesh(vertices=self.Triangulation['vertices3D'],
                                    faces=self.Triangulation['triangles']
                                    )

    def create_offset_face(self, offset):

        # from face import Face

        # https://github.com/fonttools/pyclipper
        if self.HoleCount > 0:
            raise ValueError('Polygon offsetting for polygons with hole not possible')



        # 1 take local coordinates:
        local_coord = tuple(map(tuple, self.LocalCoord))

        # 2 create pyclipper object:
        pco = pyclipper.PyclipperOffset()
        pco.AddPath(local_coord, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)

        # 3 create offset:
        solution = pco.Execute(offset)

        # 4 convert coordinates back to global coordinates
        offset_coords = self.convert_to_global_coord(np.asarray(solution).squeeze())
        self.print_status(offset_coords)

        # create vertices
        vertices = list()
        for position in offset_coords:
            vertices.append(Vertex(layers=self.Layers,
                                   is_visible=True,
                                   position=position,
                                   color_from_parent=False))

        # create edges
        edges = list()
        for index in range(vertices.__len__() - 1):
            edges.append(Edge(vertex_1=vertices[index],
                              vertex_2=vertices[index+1])
                         )
        edges.append(Edge(vertex_1=vertices[-1],
                          vertex_2=vertices[0])
                     )

        # create edge loop:
        edge_loop = EdgeLoop(edges=edges)

        # create face:
        face = Face(boundary=edge_loop,
                    orientation=self.Orientation)

        return face

    def reprJSON(self):
        return dict(ID=self._ID,
                    PID=self._PID,
                    Name=self._Name,
                    IsVisible=self._IsVisible,
                    Color=self._Color,
                    ColorFromParent=self.ColorFromParent,
                    Boundary=self._Boundary,
                    BoundaryID=self._BoundaryID,
                    Holes=self._Holes,
                    HoleIDs=self._HoleIDs,
                    HoleCount=self._HoleCount,
                    Orientation=self._Orientation,
                    Points=self._Points,
                    Area=self._Area,
                    Normal=self._Normal,
                    Coords=self._Coords,
                    Closed=self._Closed,
                    LocalCoord=self._LocalCoord,
                    Triangulation=self.Triangulation)









