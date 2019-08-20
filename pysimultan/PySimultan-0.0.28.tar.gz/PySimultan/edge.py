import numpy as np
import uuid
import itertools

from PySimultan.base_classes import GeoBaseClass


class Edge(GeoBaseClass):

    visible_class_name = 'Edge'
    new_edge_id = itertools.count(0)

    def __init__(self,
                 vertex_1,
                 vertex_2,
                 edge_id=uuid.uuid4(),
                 name=None,
                 layers=None,
                 is_visible=True,
                 color=np.append(np.random.rand(1, 3), 0)*255,
                 color_from_parent=False
                 ):

        super().__init__(id=edge_id,
                         pid=next(type(self).new_edge_id),
                         color=color,
                         name=name,
                         color_from_parent=color_from_parent,
                         is_visible=is_visible,
                         layers=layers
                         )

        # name
        if name is None:
            self._Name = 'Edge{}'.format(self._PID)
        else:
            self._Name = name

        self._Vertex1 = vertex_1
        self._Vertex2 = vertex_2

        self._Length = None

        # -----------------------------------------------
        # bindings

        self._Vertex1.bind_to(self.vertex_updated)
        self._Vertex2.bind_to(self.vertex_updated)

    @property
    def Vertex1(self):
        return self._Vertex1

    @Vertex1.setter
    def Vertex1(self, value):
        self._Vertex1.bind_to(self.vertex_updated)
        self._Vertex2.bind_to(self.vertex_updated)

    @property
    def Vertex2(self):
        return self._Vertex2

    @Vertex2.setter
    def Vertex2(self, value):
        self._default_set_handling('Vertex2', value)

    @property
    def Length(self):
        if self._Length is None:
            self.calculate_length()
        return self._Length

    @Length.setter
    def Length(self, value):
        self._default_set_handling('Length', value)

    def vertex_updated(self, **kwargs):
        self.print_status('vertex has updated')
        self.calculate_length()
        for key, value in kwargs.items():
            if value == 'Position':
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
                    Vertex1=self._Vertex1,
                    Vertex2=self._Vertex2)

    def calculate_length(self):
        self._Length = np.linalg.norm(self.Vertex1.Position - self.Vertex2.Position)

    def get_ccordinates(self):
        vertices = [self.Vertex1, self.Vertex2]

        coordinates = np.empty([vertices.__len__(), 3])

        for i, vertex in enumerate(vertices):
            coordinates[i, :] = vertex.Position

        return coordinates