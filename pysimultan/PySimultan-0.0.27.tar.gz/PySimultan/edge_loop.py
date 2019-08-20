import numpy as np
import uuid
import itertools

from PySimultan.layer import Layer
from PySimultan.base_classes import GeoBaseClass


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

        # name
        if name is None:
            self._Name = 'EdgeLoop{}'.format(self._PID)
        else:
            self._Name = name

        if edges is None:
            self._Edges = []
        elif type(edges) == list:
            self._Edges = edges
        else:
            self._Edges = [edges]

        if edge_id is None:
            if self._Edges.__len__() > 0:
                self._EdgeID = list(x.ID for x in self._Edges)
            else:
                self._EdgeID = []
        elif type(edge_id) == list:
            self._EdgeID = edge_id
        else:
            self._EdgeID = [edge_id]

        self._Length = None

        # --------------------------------------------------------
        # bind observed objects
        # --------------------------------------------------------

        for edge in self._Edges:
            edge.bind_to(self.edge_updated)

    # --------------------------------------------------------
    # Attributes
    # --------------------------------------------------------

    @property
    def EdgeCount(self):
        return self._Edges.__len__()

    @property
    def EdgeID(self):
        return list(x.ID for x in self._Edges)

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
        self._Length = sum([x.Length for x in self.Edges])

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
