import numpy as np
import itertools
import uuid

from PySimultan.base_classes import GeoBaseClass


class ProxyGeometry(GeoBaseClass):

    new_proxy_id = itertools.count().__next__()

    def __init__(self,
                 prox_geo_id=uuid.uuid4(),
                 name='ProxyGeometry',
                 layers=None,
                 is_visible=True,
                 VertexID=0,
                 SizeX=0,
                 SizeY=0,
                 SizeZ=0,
                 PositionCount=0,
                 NormalCount=0,
                 IndicesCount=0,
                 Index=0,
                 color=np.append(np.random.rand(1, 3), 0) * 255,
                 color_from_parent=False
                 ):
        super().__init__(id=prox_geo_id,
                         pid=next(type(self).new_proxy_id),
                         color=color,
                         name=name,
                         color_from_parent=color_from_parent,
                         is_visible=is_visible,
                         layers=layers
                         )

        # name
        if name is None:
            self._Name = 'ProxyGeometry{}'.format(self._PID)
        else:
            self._Name = name

