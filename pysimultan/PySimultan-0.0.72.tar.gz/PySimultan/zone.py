import numpy as np
import uuid
import itertools
import trimesh
import pyrender

from PySimultan.geo_functions import create_volume_mesh_from_faces, vector_angle, on_same_plane, connected, angle_between_faces
from PySimultan.base_classes import GeoBaseClass
from PySimultan import settings
from PySimultan.wall import Wall


class Zone(GeoBaseClass):

    visible_class_name = 'Zone'
    new_zone_id = itertools.count(0)

    def __init__(self,
                 zone_id=None,
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
        self._Walls = None
        self._FaceIDs = face_ids
        self._Faces = faces
        self._Volume = None
        self._Mesh = None

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

        # add to the collection
        settings.building_collection.Zone_collection.append(self)

        self.create_walls()

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
        if self.Faces is None:
            self.Faces = value
        else:
            for face in self.Faces:
                try:
                    face.Zones = face.Zones.remove(self)
                except Exception as e:
                    print('zone was not in face.Zones')
            self.Faces = value

        for face in self.Faces:
            face.Zones = face.Zones.append(self)

        # delete walls:
        for wall in self._Walls:
            settings.building_collection.Wall_collection.remove(wall)
        self._Walls = None
        for callback in self._observers:
            callback(ChangedAttribute='Faces')

    # Walls
    @property
    def Walls(self):
        if self._Walls is None:
            self.create_walls()
        return self._Walls

    @Walls.setter
    def Walls(self, value):
        self._Walls = value
        for callback in self._observers:
            callback(ChangedAttribute='Walls')

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

    def create_walls(self):

        zone_faces = self.Faces

        # check which faces lie on the same face:
        distances = on_same_plane(zone_faces)

        # check which faces are connected:
        faces_to_build_wall = zone_faces
        con_mat = connected(zone_faces)

        # check angles between faces:
        angles = angle_between_faces(zone_faces)
        angles[angles > 180] = angles[angles > 180] - 180
        angles[abs((180 - angles)) < 90] = np.abs(angles[abs((180 - angles)) < 90] - 180)
        low_angle = angles < 1

        on_wall_mat = np.bitwise_and(np.bitwise_or(distances, low_angle), con_mat)

        walls = list()
        walls_faces = list()
        for i in range(zone_faces.__len__()):
            wall_faces = np.unique(np.append(np.where(on_wall_mat[i, :])[0], i))
            if i == 0:
                walls.append(wall_faces)
            else:
                intersected = False
                for i, wall in enumerate(walls):
                    if np.intersect1d(wall_faces, wall).size != 0:
                        walls[i] = np.unique(np.append(wall, wall_faces))
                        intersected = True
                if not intersected:
                    walls.append(wall_faces)

        # create walls:
        for wall in walls:
            new_wall = Wall(faces=np.asarray(zone_faces)[wall].tolist())
            if self._Walls is None:
                self.Walls = list()
            self.Walls.append(new_wall)

        print('Walls created')




