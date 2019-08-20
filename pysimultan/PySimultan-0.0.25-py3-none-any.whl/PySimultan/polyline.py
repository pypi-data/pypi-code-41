import numpy as np
import uuid
import itertools

from PySimultan.base_classes import GeoBaseClass


class Polyline(GeoBaseClass):

    def __init__(self,
                 poly_id=uuid.uuid4(),
                 name='polyline',
                 layers=None,
                 is_visible=True,
                 edge_ids=None,
                 color=np.append(np.random.rand(1, 3), 0)*255,
                 color_from_parent=False,
                 edges=None
                 ):

        super().__init__(id=poly_id,
                         pid=next(self.new_id),
                         color=color,
                         name=name,
                         color_from_parent=color_from_parent,
                         is_visible=is_visible,
                         layers=layers
                         )

        if edges is None:
            self._Edges = []
        elif type(edges) == list:
            self._Edges = edges
        else:
            self._Edges = [edges]

        if edge_ids is None:
            self._EdgeIDs = []
        elif type(edge_ids) == list:
            self._EdgeIDs = edge_ids
        else:
            self._EdgeIDs = [edge_ids]

        self._EdgeCount = self.Edges.__len__()
        self._EdgeIDs = (edge.ID for edge in self._Edges)

    # --------------------------------------------------------
    # Attributes
    # --------------------------------------------------------

    @property
    def EdgeCount(self):
        self._EdgeCount = self._Edges.__len__()
        return self._Edges.__len__()

    @property
    def EdgeIDs(self):
        return self._EdgeIDs

    @property
    def Edges(self):
        return self._Edges

    @Edges.setter
    def Edges(self, edges):
        self._Edges = edges
        self._EdgeIDs = (edge.ID for edge in self._Edges)
        for callback in self._observers:
            self.print_status('Edges_changed')
            callback(ChangedAttribute='Edges')

    # --------------------------------------------------------
    # observed object change callbacks
    # --------------------------------------------------------

    def edge_updated(self, **kwargs):
        self.print_status('edge has updated')
        for key, value in kwargs.items():
            self.print_status("{0} = {1}".format(key, value))
            if value == 'vertex_position_changed':
                for callback in self._observers:
                    callback(ChangedAttribute='vertex_position_changed')

    def reprJSON(self):
        return dict(ID=self._ID,
                    PID=self._PID,
                    Name=self._Name,
                    IsVisible=self._IsVisible,
                    Color=self._Color,
                    ColorFromParent=self.ColorFromParent,
                    Edges=self._Edges,
                    EdgeIDs=self._EdgeIDs,
                    EdgeCount=self._EdgeCount
                    )
