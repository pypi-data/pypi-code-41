from PySimultan.base_classes import GeoBaseClass
import itertools

from PySimultan import settings


class Wall(GeoBaseClass):

    new_wall_id = itertools.count(0)
    visible_class_name = 'Wall'

    def __init__(self,
                 faces=None,
                 wall_id=None,
                 color=None,
                 name=None,
                 color_from_parent=True,
                 is_visible=True,
                 layers=None):

        super().__init__(id=wall_id,
                         pid=next(type(self).new_wall_id),
                         color=color,
                         name=name,
                         color_from_parent=color_from_parent,
                         is_visible=is_visible,
                         layers=layers
                         )

        self._Faces = None

        if faces is not None:
            self.Faces = faces
        else:
            self.Faces = list()

        settings.building_collection.Wall_collection.append(self)

    @property
    def Faces(self):
        return self._Faces

    @Faces.setter
    def Faces(self, value):
        if not (isinstance(value, list)):
            if value is None:
                value = []
            else:
                value = [value]

        self._default_set_handling('Faces', value)



