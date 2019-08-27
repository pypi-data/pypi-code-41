import numpy as np
import uuid
import itertools

from PySimultan.layer import Layer
from PySimultan.base_classes import GeoBaseClass
from PySimultan import settings
from PySimultan.geo_functions import polygon_area_3d, convert_to_global, convert_to_local
import triangle
import trimesh
import pyclipper


class EdgeLoop(GeoBaseClass):

    visible_class_name = 'EdgeLoop'
    new_edge_loop_id = itertools.count(0)

    def __init__(self,
                 edge_loop_id=uuid.uuid4(),
                 name=None,
                 layers=None,
                 is_visible=True,
                 edge_id=None,
                 color=np.append(np.random.rand(1, 3), 0)*255,
                 color_from_parent=False,
                 edges=None):

        super().__init__(id=edge_loop_id,
                         pid=next(type(self).new_edge_loop_id),
                         color=color,
                         name=name,
                         color_from_parent=color_from_parent,
                         is_visible=is_visible,
                         layers=layers
                         )

        self._Points = None
        self._Coords = None
        self._Edges = None
        self._Area = None
        self._Closed = None
        self._Triangulation = None
        self._LocalCoord = None
        self._G2L_TransMat = None


        # name
        if name is None:
            self.Name = 'EdgeLoop{}'.format(self._PID)
        else:
            self.Name = name

        if edges is None:
            self.Edges = []
        elif type(edges) == list:
            self.Edges = edges
        else:
            self.Edges = [edges]

        if edge_id is None:
            if self.Edges.__len__() > 0:
                self.EdgeID = list(x.ID for x in self.Edges)
            else:
                self.EdgeID = []
        elif type(edge_id) == list:
            self.EdgeID = edge_id
        else:
            self.EdgeID = [edge_id]

        self._Length = None

        # --------------------------------------------------------
        # bind observed objects
        # --------------------------------------------------------

        for edge in self.Edges:
            edge.bind_to(self.edge_updated)

        # add to the collection
        settings.building_collection.Edge_loop_collection.append(self)

    # --------------------------------------------------------
    # Attributes
    # --------------------------------------------------------

    @property
    def EdgeCount(self):
        return self.Edges.__len__()

    @property
    def EdgeID(self):
        return list(x.ID for x in self.Edges)

    @EdgeID.setter
    def EdgeID(self, value):
        self._default_set_handling('EdgeID', value)

    @property
    def Edges(self):
        return self._Edges

    @Edges.setter
    def Edges(self, value):
        self._default_set_handling('Edges', value)

    @property
    def Length(self):
        if self._Length is None:
            self.calc_length()
        return self._Length

    @Length.setter
    def Length(self, value):
        self._default_set_handling('Length', value)

    @property
    def Area(self):
        if self._Area is None:
            self.calc_area()
        return self._Area

    @Area.setter
    def Area(self, value):
        self._default_set_handling('Area', value)

    @property
    def Coords(self):
        if self._Coords is None:
            self.create_poly_coordinates()
        return self._Coords

    @Coords.setter
    def Coords(self, value):
        self._default_set_handling('Coords', value)

    @property
    def Points(self):
        if self._Points is None:
            self.create_poly_points()
        return self._Points

    @Points.setter
    def Points(self, value):
        self._default_set_handling('Points', value)

    @property
    def Closed(self):
        if self._Closed is None:
            self.check_closed()
        return self._Closed

    @Closed.setter
    def Closed(self, value):
        self._default_set_handling('Closed', value)

    @property
    def LocalCoord(self):
        if self._LocalCoord is None:
            self.convert_to_local_coord()
        return self._LocalCoord

    @LocalCoord.setter
    def LocalCoord(self, value):
        self._default_set_handling('LocalCoord', value)

    @property
    def Triangulation(self):
        if self._Triangulation is None:
            self.triangulate()
        return self._Triangulation

    @Triangulation.setter
    def Triangulation(self, value):
        self._default_set_handling('Triangulation', value)

    # --------------------------------------------------------
    # observed object change callbacks
    # --------------------------------------------------------

    def edge_updated(self, **kwargs):
        self.print_status('edge has updated')
        for key, value in kwargs.items():
            self.print_status("{0} = {1}".format(key, value))
            if value == 'vertex_position_changed':
                for callback in self._observers:
                    instance = callback.__self__
                    instance._UpdateHandler.add_notification(callback, 'vertex_position_changed')

    def reprJSON(self):
        return dict(ID=self._ID,
                    PID=self._PID,
                    Name=self._Name,
                    IsVisible=self._IsVisible,
                    Color=self._Color,
                    ColorFromParent=self.ColorFromParent,
                    EdgeCount=self.EdgeCount,
                    Edges=self._Edges,
                    EdgeID=self._EdgeID)

    def calc_length(self):
        self.Length = sum([x.Length for x in self.Edges])

    def get_edges(self):
        return self.Edges

    def get_vertices(self):
        vertices = list()
        vertices.append(self.Edges[0].Vertex1)
        vertices.append(self.Edges[0].Vertex2)
        for edge in self.Edges[1:]:
            vert1 = edge.Vertex1
            vert2 = edge.Vertex2
            if any((x == vert1) for x in vertices):
                vertices.append(vert2)
            else:
                vertices.append(vert1)

        return vertices
    
    def get_ccordinates(self):
        vertices = self.get_vertices()
        
        coordinates = np.empty([vertices.__len__(), 3])

        for i, vertex in enumerate(vertices):
            coordinates[i, :] = vertex.Position

        return coordinates

    def calc_area(self):
        self.Area = polygon_area_3d(self.Coords)

    def create_poly_coordinates(self):
        Coords = np.zeros((self.Points.__len__()-1, 3))
        for i in range(self.Points.__len__() - 1):
            Coords[i, :] = self.Points[i].Position

        self.Coords = Coords

    def create_poly_points(self):

        points = list()

        points.append(self.Edges[0].Vertex1)
        points.append(self.Edges[0].Vertex2)

        for i in range(1, self.EdgeCount):
            if points[-1] == self.Edges[i].Vertex1:
                points.append(self.Edges[i].Vertex2)
            elif points[-1] == self.Edges[i].Vertex2:
                points.append(self.Edges[i].Vertex1)
            else:
                self.print_status('start of the edge is not the end of the previous edge')

        # check if polygon is closed
        if points[-1] == points[0]:
            self._Closed = True
        else:
            self._Closed = False

        self.Points = points

    def check_closed(self):
        if (self.Edges[0].Vertex1 == self.Edges[-1].Vertex1) or \
           (self.Edges[0].Vertex1 == self.Edges[-1].Vertex2) or \
           (self.Edges[0].Vertex2 == self.Edges[-1].Vertex1) or \
           (self.Edges[0].Vertex2 == self.Edges[-1].Vertex2):
            self.Closed = True
        else:
            self.Closed = False

    def triangulate(self):

        segments = []
        for i in range(len(self.Points) - 2):
            segments.append([int(i), int(i + 1)])
        segments.append([int(i + 1), int(0)])

        a = {'vertices': self.LocalCoord, 'segments': segments}

        triangulation = triangle.triangulate(a, 'p')
        # triangle.compare(plt, dict(vertices=self._LocalCoord), triangulation)
        triangulation['vertices3D'] = convert_to_global(self.G2L_TransMat.transformation_mat, triangulation['vertices'])

        # plt.show()
        self.Triangulation = triangulation

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

