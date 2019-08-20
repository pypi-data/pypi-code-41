import numpy as np
import uuid
import itertools

from PySimultan.geo_functions import create_volume_mesh_from_faces
from PySimultan.base_classes import GeoBaseClass


class Zone(GeoBaseClass):

    visible_class_name = 'Zone'
    new_zone_id = itertools.count(0)

    def __init__(self,
                 zone_id=uuid.uuid4(),
                 name=None,
                 layers=None,
                 is_visible=True,
                 face_ids=None,
                 faces=None,
                 color=np.append(np.random.rand(1, 3), 0) * 255,
                 color_from_parent=False):

        super().__init__(id=zone_id,
                         pid=next(type(self).new_zone_id),
                         color=color,
                         name=name,
                         color_from_parent=color_from_parent,
                         is_visible=is_visible,
                         layers=layers
                         )
        self._FaceIDs = face_ids
        self._Faces = faces
        self._Volume = []
        self._Mesh = []

        self.get_updated_volume()

        # name
        if name is None:
            self._Name = 'Zone{}'.format(self.PID)
        else:
            self._Name = name

        # faces
        if faces is None:
            self._Faces = []
        elif type(faces) == list:
            self._Faces = faces
        else:
            self._Faces = [faces]
        self._FaceCount = self.Faces.__len__()

        if face_ids is None:
            if self._Faces.__len__() > 0:
                self.FaceIDs = list(x.ID for x in self._Faces)
            else:
                self.FaceIDs = []
        elif type(face_ids) == list:
            self.FaceIDs = face_ids
        else:
            self.FaceIDs = [face_ids]

        # --------------------------------------------------------
        # bind observed objects
        # --------------------------------------------------------

        for face in self._Faces:
            face.bind_to(self.face_updated)

    # --------------------------------------------------------
    # Attributes
    # --------------------------------------------------------

    # -----------------------------------------------
    # Faces
    @property
    def Faces(self):
        return self._Faces

    @Faces.setter
    def Faces(self, value):
        self._Faces = value
        for callback in self._observers:
            callback(ChangedAttribute='Faces')

    # -----------------------------------------------
    # Volume
    @property
    def Volume(self):
        return self._Volume

    @Volume.setter
    def Volume(self, value):
        self._Volume = value
        for callback in self._observers:
            callback(ChangedAttribute='Volume')

    # -----------------------------------------------
    # Mesh
    @property
    def Mesh(self):
        return self._Mesh

    @Mesh.setter
    def Mesh(self, value):
        self._Mesh = value
        for callback in self._observers:
            callback(ChangedAttribute='Mesh')

    # -----------------------------------------------
    # LayersCount

    @property
    def LayersCount(self):
        return self._Layers.__len__()

    # --------------------------------------------------------
    # observed object change callbacks
    # --------------------------------------------------------

    def face_updated(self, **kwargs):
        self.print_status('face has updated')
        for key, value in kwargs.items():
            self.print_status("{0} = {1}".format(key, value))
            if value == 'vertex_position_changed':
                self.get_updated_volume()
                for callback in self._observers:
                    instance = callback.__self__
                    instance._UpdateHandler.add_notification(callback, 'vertex_position_changed')

    def get_updated_volume(self):

        if not self.Volume:
            # calculate volume:
            self.Mesh = create_volume_mesh_from_faces(self)
            self.Volume = self.Mesh.volume
        else:
            return self.Volume

    def create_mesh(self):
        self.Mesh = create_volume_mesh_from_faces(self)
        return self.Mesh

    def reprJSON(self):
        return dict(ID=self._ID,
                    PID=self._PID,
                    Name=self._Name,
                    IsVisible=self._IsVisible,
                    Color=self._Color,
                    ColorFromParent=self.ColorFromParent,
                    Faces=self.Faces,
                    FaceIDs=self.FaceIDs,
                    Volume=self.Volume,
                    Mesh=self.Mesh,
                    LayersCount=self.LayersCount,
                    )



