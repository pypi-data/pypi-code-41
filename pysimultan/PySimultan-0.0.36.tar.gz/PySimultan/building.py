# class and methods holding building informations
import os
# import itertools
# import uuid
# import itertools
# import numpy as np
# import weakref
# from stl import mesh
import scipy.io
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename
# from json_import_config_creator import Resource, Parameter
# import xlrd
from sxl import Workbook
import pandas as pd
# import re
from tkinter.filedialog import asksaveasfile
import json


from PySimultan.geo_functions import *
from PySimultan.layer import *
from PySimultan.update_handler import UpdateHandler
from PySimultan.material import Part, MatLayer, Material, Window
from PySimultan.geo_functions import print_status as print_status


class Building(SelfTrackingClass):

    visible_class_name = 'Building'
    new_building_id = itertools.count()

    def __init__(self,
                 building_id=uuid.uuid4(),
                 is_visible=True,
                 vertices=None,
                 faces=None,
                 zones=None,
                 name=None,
                 layer_permissions=1,
                 geometry_permissions=1535,
                 model_permissions=3,
                 layers=None,
                 edges=None,
                 edge_loops=None,
                 polylines=None,
                 proxy_geometries=None,
                 geo_ref_count=0,
                 linked_model_count=0
                 ):

        self._UpdateHandler = UpdateHandler()

        self._observers = []

        self._ID = building_id
        self._PID = next(type(self).new_building_id)
        self._IsVisible = is_visible

        # layers
        if layers is None:
            self._Layers = Layer()
        elif type(layers) == list:
            self._Layers = layers
        else:
            self._Layers = [layers]
        self._LayersCount = self.Layers.__len__()

        # vertices
        if vertices is None:
            self._Vertices = []
        elif type(vertices) == list:
            self._Vertices = vertices
        else:
            self._Vertices = [vertices]
        self._VertexCount = self.Vertices.__len__()

        # edges
        if edges is None:
            self._Edges = []
        elif type(edges) == list:
            self._Edges = edges
        else:
            self._Edges = [edges]
        self._EdgeCount = self._Edges.__len__()

        # edge_loops
        if edge_loops is None:
            self._EdgeLoops = []
        elif type(edge_loops) == list:
            self._EdgeLoops = edge_loops
        else:
            self._EdgeLoops = [edge_loops]
        self._EdgeLoopCount = self._EdgeLoops.__len__()

        # polylines
        if polylines is None:
            self._Polylines = []
        elif type(polylines) == list:
            self._Polylines = polylines
        else:
            self._Polylines = [polylines]
        self._PolylineCount = self._Polylines.__len__()

        # faces
        if faces is None:
            self._Faces = []
        elif type(faces) == list:
            self._Faces = faces
        else:
            self._Faces = [faces]
        self._FaceCount = self._Faces.__len__()

        # proxy_geometries
        if proxy_geometries is None:
            self._ProxyGeometries = []
        elif type(proxy_geometries) == list:
            self._ProxyGeometries = proxy_geometries
        else:
            self._ProxyGeometries = [proxy_geometries]
        self._ProxyGeometryCount = self._ProxyGeometries.__len__()

        # zones
        if zones is None:
            self._Zones = []
        elif type(zones) == list:
            self._Zones = zones
        else:
            self._Zones = [zones]
        self._ZoneCount = self._Zones.__len__()

        # name
        if name is None:
            self._Name = 'Building{}'.format(self.PID)
        else:
            self._Name = name

        self._LayerPermissions = layer_permissions
        self._ModelPermissions = model_permissions
        self._GeometryPermissions = geometry_permissions
        self._Mesh = None

        self._Parts = list()
        self._MatLayers = list()
        self._Materials = list()

        self.GeoRefCount = geo_ref_count
        self.LinkedModelCount = linked_model_count

    # -----------------------------------------------
    # ID
    @property
    def ID(self):
        return self._ID

    # -----------------------------------------------
    # PID
    @property
    def PID(self):
        return self._PID

    # -----------------------------------------------
    # IsVisible
    @property
    def IsVisible(self):
        return self._IsVisible

    @IsVisible.setter
    def IsVisible(self, value):
        self._IsVisible = value
        for callback in self._observers:
            callback(ChangedAttribute='IsVisible')

    # -----------------------------------------------
    # Layers

    @property
    def Layers(self):
        return self._Layers

    @Layers.setter
    def Layers(self, value):
        self._Layers = value
        for callback in self._observers:
            callback(ChangedAttribute='Layers')

    # -----------------------------------------------
    # LayersCount

    @property
    def LayersCount(self):
        return self._Layers.__len__()

    # -----------------------------------------------
    # vertices

    @property
    def Vertices(self):
        return self._Vertices

    @Vertices.setter
    def Vertices(self, value):
        self._Vertices = value
        for callback in self._observers:
            callback(ChangedAttribute='Vertices')

    # -----------------------------------------------
    # VertexCount

    @property
    def VertexCount(self):
        return self._Vertices.__len__()

    # -----------------------------------------------
    # Edges

    @property
    def Edges(self):
        return self._Edges

    @Edges.setter
    def Edges(self, value):
        self._Edges = value
        for callback in self._observers:
            callback(ChangedAttribute='Edges')

    # -----------------------------------------------
    # EdgeCount

    @property
    def EdgeCount(self):
        return self._EdgeCount

    # -----------------------------------------------
    # EdgeLoops

    @property
    def EdgeLoops(self):
        return self._EdgeLoops

    @EdgeLoops.setter
    def EdgeLoops(self, value):
        self._EdgeLoops = value
        for callback in self._observers:
            callback(ChangedAttribute='EdgeLoops')

    # -----------------------------------------------
    # EdgeLoopCount

    @property
    def EdgeLoopCount(self):
        return self._EdgeLoops.__len__()

    # -----------------------------------------------
    # Polylines

    @property
    def Polylines(self):
        return self._Polylines

    @Polylines.setter
    def Polylines(self, value):
        self._Polylines = value
        for callback in self._observers:
            callback(ChangedAttribute='Polylines')

    # -----------------------------------------------
    # PolylineCount

    @property
    def PolylineCount(self):
        return self._Polylines.__len__()

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
    # FaceCount

    @property
    def FaceCount(self):
        return self._Faces.__len__()

    # -----------------------------------------------
    # ProxyGeometries

    @property
    def ProxyGeometries(self):
        return self._ProxyGeometries

    @ProxyGeometries.setter
    def ProxyGeometries(self, value):
        self._ProxyGeometries = value
        for callback in self._observers:
            callback(ChangedAttribute='ProxyGeometries')

    # -----------------------------------------------
    # ProxyGeometryCount

    @property
    def ProxyGeometryCount(self):
        return self._ProxyGeometries.__len__()

    # -----------------------------------------------
    # Zones

    @property
    def Zones(self):
        return self._Zones

    @Zones.setter
    def Zones(self, value):
        self._Zones = value
        for callback in self._observers:
            callback(ChangedAttribute='Zones')

    # -----------------------------------------------
    # ZoneCount

    @property
    def ZoneCount(self):
        return self._Zones.__len__()

    # -----------------------------------------------
    # Name

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, value):
        self._Name = value
        for callback in self._observers:
            callback(ChangedAttribute='Name')

    # -----------------------------------------------
    # LayerPermissions

    @property
    def LayerPermissions(self):
        return self._LayerPermissions

    @LayerPermissions.setter
    def LayerPermissions(self, value):
        self._LayerPermissions = value
        for callback in self._observers:
            callback(ChangedAttribute='LayerPermissions')

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
    # ModelPermissions

    @property
    def ModelPermissions(self):
        return self._ModelPermissions

    @ModelPermissions.setter
    def ModelPermissions(self, value):
        self._ModelPermissions = value
        for callback in self._observers:
            callback(ChangedAttribute='ModelPermissions')

    # -----------------------------------------------
    # GeometryPermissions

    @property
    def GeometryPermissions(self):
        return self._GeometryPermissions

    @GeometryPermissions.setter
    def GeometryPermissions(self, value):
        self._GeometryPermissions = value
        for callback in self._observers:
            callback(ChangedAttribute='GeometryPermissions')

    #------------------------------------------------
    #  Materials / parts

    @property
    def Parts(self):
        return self._Parts

    @Parts.setter
    def Parts(self, value):
        self._Parts = value
        for callback in self._observers:
            callback(ChangedAttribute='Parts')

    @property
    def MatLayers(self):
        return self._MatLayers

    @MatLayers.setter
    def MatLayers(self, value):
        self._MatLayers = value
        for callback in self._observers:
            callback(ChangedAttribute='MatLayers')

    @property
    def Materials(self):
        return self._Materials

    @Materials.setter
    def Materials(self, value):
        self._Materials = value
        for callback in self._observers:
            callback(ChangedAttribute='Materials')

    # -----------------------------------------------
    # bind
    def bind_to(self, callback):
        if callback not in self._observers:
            self._observers.append(callback)

    # -----------------------------------------------
    # unbind
    def unbind(self, callback):
        if callback in self._observers:
            self._observers.remove(callback)

    def start_bulk_update(self):
        self._UpdateHandler.BulkUpdate = True

    def end_bulk_update(self):
        self._UpdateHandler.BulkUpdate = False

    def add_layer(self, layer):
        self.Layers.append(layer)

    def add_vertices(self, vertices):
        self.Vertices.append(vertices)

    def add_edge(self, edge):
        self.Edges.append(edge)

    def add_edge_loop(self, edge_loop):
        self.EdgeLoops.append(edge_loop)

    def add_polyline(self, polyline):
        self.Polylines.append(polyline)

    def add_faces(self, faces):
        self.Faces.append(faces)

    def add_zone(self, zone):
        self.Zones.append(zone)

    def add_mat_layer(self, mat_layer):
        self._MatLayers.append(mat_layer)
        
    def add_material(self, material):
        self._Materials.append(material)
        
    def add_part(self, part):
        self._Parts.append(part)

    def print_status(self, *args, **kwargs):
        print_status(*args, **kwargs)

    def write_simgeo(self, file='testfile.simgeo'):

        file = open(file, 'w')

        # ----------------------------------------------------------------
        # write header:
        # ----------------------------------------------------------------

        file.write(("{FormatType}"
                    "{Version};"
                    "{ModelID};"
                    "{ModelPermissions};"
                    "{GeometryPermissions};"
                    "{LayerPermissions};"
                    "{LayerCount};"
                    "{VertexCount};"
                    "{EdgeCount};"
                    "{EdgeLoopCount};"
                    "{PolylineCount};"
                    "{FaceCount};"
                    "{VolumeCount};"
                    "{LinkedModelCount};"
                    "{ProxyCount};"
                    "{GeoRefCount};"
                    "\n"
                    ).format(FormatType='T',
                             Version=7,
                             ModelID=self.ID,
                             ModelPermissions=self.ModelPermissions,
                             GeometryPermissions=self.GeometryPermissions,
                             LayerPermissions=self.LayerPermissions,
                             LayerCount=self.Layers.__len__(),
                             VertexCount=self.Vertices.__len__(),
                             EdgeCount=self.Edges.__len__(),
                             EdgeLoopCount=self.EdgeLoops.__len__(),
                             PolylineCount=self.Polylines.__len__(),
                             FaceCount=self.Faces.__len__(),
                             VolumeCount=self.Zones.__len__(),
                             LinkedModelCount=self.LinkedModelCount,
                             ProxyCount=self.ProxyCount,
                             GeoRefCount=self.GeoRefCount
                             )
                   )

        # ----------------------------------------------------------------
        # write content:
        # ----------------------------------------------------------------

        file.write(("{NameLength};"
                    "{ModelName}"
                    "{IsVisible};"
                    "\n"
                    ).format(NameLength=self.Name.__len__(),
                             ModelName=self.Name,
                             IsVisible=self.IsVisible)
                   )

        # ----------------------------------------------------------------
        # write layers:
        # ----------------------------------------------------------------

        for layer in self.Layers:

            file.write(("{ID};"
                        "{ParentID};"
                        "{NameStrLength};"
                        "{Name}"
                        "{IsVisible}"
                        "{ColorR};"
                        "{ColorG};"
                        "{ColorB};"
                        "{ColorA};"
                        "{ColorFromParent};"
                        "\n").format(ID=layer.Layer_Id,
                                     ParentID=layer.ParentID,
                                     NameStrLength=layer.Name.__len__(),
                                     Name=layer.Name,
                                     IsVisible=layer.IsVisible,
                                     ColorR=layer.Color[0],
                                     ColorG=layer.Color[1],
                                     ColorB=layer.Color[2],
                                     ColorA=layer.Color[3],
                                     ColorFromParent=layer.ColorFromParent
                                     )
                       )

        # ----------------------------------------------------------------
        # write vertices:
        # ----------------------------------------------------------------

        for vertex in self.Vertices:

            file.write(("{ID};"
                        "{NameStrLength};"
                        "{Name}"
                        "{LayerID};"
                        "{IsVisible}"
                        "{PositionX};"
                        "{PositionY};"
                        "{PositionZ};"
                        "{ColorR};"
                        "{ColorG};"
                        "{ColorB};"
                        "{ColorA};"
                        "{ColorFromParent};"
                        "\n").format(ID=vertex.ID,
                                     NameStrLength=vertex.Name.__len__(),
                                     Name=vertex.Name,
                                     LayerID=vertex.LayerID,
                                     IsVisible=vertex.IsVisible,
                                     PositionX=vertex.Position[0],
                                     PositionY=vertex.Position[1],
                                     PositionZ=vertex.Position[2],
                                     ColorR=vertex.Color[0],
                                     ColorG=vertex.Color[1],
                                     ColorB=vertex.Color[2],
                                     ColorA=vertex.Color[3],
                                     ColorFromParent=vertex.ColorFromParent
                                     )
                       )

        # ----------------------------------------------------------------
        # write edges:
        # ----------------------------------------------------------------

        for edge in self.Edges:
            file.write(("{ID};"
                        "{NameStrLength};"
                        "{Name}"
                        "{LayerID};"
                        "{IsVisible}"
                        "{Vertex1};"
                        "{Vertex2};"
                        "{ColorR};"
                        "{ColorG};"
                        "{ColorB};"
                        "{ColorA};"
                        "{ColorFromParent};"
                        "\n").format(ID=edge.ID,
                                     NameStrLength=edge.Name.__len__(),
                                     Name=edge.Name,
                                     LayerID=edge.LayerID,
                                     IsVisible=edge.IsVisible,
                                     Vertex1=edge.Vertex1.ID,
                                     Vertex2=edge.Vertex2.ID,
                                     ColorR=edge.Color[0],
                                     ColorG=edge.Color[1],
                                     ColorB=edge.Color[2],
                                     ColorA=edge.Color[3],
                                     ColorFromParent=edge.ColorFromParent
                                     )
                       )

        # ----------------------------------------------------------------
        # write edge loops:
        # ----------------------------------------------------------------

        for edge_loop in self.EdgeLoops:
            file.write(("{ID};"
                        "{NameStrLength};"
                        "{Name}"
                        "{LayerID};"
                        "{IsVisible}"
                        "{EdgeCount};"
                        "{EdgeIDs};"
                        "{ColorR};"
                        "{ColorG};"
                        "{ColorB};"
                        "{ColorA};"
                        "{ColorFromParent};"
                        "\n").format(ID=edge_loop.ID,
                                     NameStrLength=edge_loop.Name.__len__(),
                                     Name=edge_loop.Name,
                                     LayerID=edge_loop.LayerID,
                                     IsVisible=edge_loop.IsVisible,
                                     EdgeCount=edge_loop.EdgeCount,
                                     EdgeIDs=";".join(edge_loop.EdgeID),
                                     ColorR=edge_loop.Color[0],
                                     ColorG=edge_loop.Color[1],
                                     ColorB=edge_loop.Color[2],
                                     ColorA=edge_loop.Color[3],
                                     ColorFromParent=edge_loop.ColorFromParent
                                     )
                       )

        # ----------------------------------------------------------------
        # write Polylines:
        # ----------------------------------------------------------------

        for polyline in self.Polylines:

            file.write(("{ID};"
                        "{NameStrLength};"
                        "{Name}"
                        "{LayerID};"
                        "{IsVisible}"
                        "{EdgeCount};"
                        "{EdgeIDs};"
                        "{ColorR};"
                        "{ColorG};"
                        "{ColorB};"
                        "{ColorA};"
                        "{ColorFromParent};"
                        "\n").format(ID=polyline.ID,
                                     NameStrLength=polyline.Name.__len__(),
                                     Name=polyline.Name,
                                     LayerID=polyline.LayerID,
                                     IsVisible=polyline.IsVisible,
                                     EdgeCount=polyline.EdgeCount,
                                     EdgeIDs=";".join(polyline.EdgeID),
                                     ColorR=polyline.Color[0],
                                     ColorG=polyline.Color[1],
                                     ColorB=polyline.Color[2],
                                     ColorA=polyline.Color[3],
                                     ColorFromParent=polyline.ColorFromParent
                                     )
                       )

        # ----------------------------------------------------------------
        # write Faces:
        # ----------------------------------------------------------------

        for face in self.Faces:

            file.write(("{ID};"
                        "{NameStrLength};"
                        "{Name}"
                        "{LayerID};"
                        "{IsVisible}"
                        "{HoleCount};"
                        "{HoleIDs};"
                        "{ColorR};"
                        "{ColorG};"
                        "{ColorB};"
                        "{ColorA};"
                        "{ColorFromParent};"
                        "\n").format(ID=face.ID,
                                     NameStrLength=face.Name.__len__(),
                                     Name=face.Name,
                                     LayerID=face.LayerID,
                                     IsVisible=face.IsVisible,
                                     HoleCount=face.HoleCount,
                                     HoleIDs=";".join(face.HoleIDs),
                                     ColorR=face.Color[0],
                                     ColorG=face.Color[1],
                                     ColorB=face.Color[2],
                                     ColorA=face.Color[3],
                                     ColorFromParent=face.ColorFromParent
                                     )
                       )

        # ----------------------------------------------------------------
        # write volumes:
        # ----------------------------------------------------------------

        for zone in self.Zones:

            file.write(("{ID};"
                        "{NameStrLength};"
                        "{Name}"
                        "{LayerID};"
                        "{IsVisible}"
                        "{FaceCount};"
                        "{FaceIDs};"
                        "{ColorR};"
                        "{ColorG};"
                        "{ColorB};"
                        "{ColorA};"
                        "{ColorFromParent};"
                        "\n").format(ID=zone.ID,
                                     NameStrLength=zone.Name.__len__(),
                                     Name=zone.Name,
                                     LayerID=zone.LayerID,
                                     IsVisible=zone.IsVisible,
                                     HoleCount=zone.FaceCount,
                                     HoleIDs=";".join(zone.FaceIDs),
                                     ColorR=zone.Color[0],
                                     ColorG=zone.Color[1],
                                     ColorB=zone.Color[2],
                                     ColorA=zone.Color[3],
                                     ColorFromParent=zone.ColorFromParent
                                     )
                       )

        # ----------------------------------------------------------------
        # write ProxyGeometry:
        # ----------------------------------------------------------------




        file.close()

    def scale(self, scale_factor):
        """
        Scales the geometry by factor
        :param scale_factor:
        :return:
        """

        for edge in self.Edges:
            edge.start_bulk_update()

        for vertex in self.Vertices:
            vertex.Position = (vertex.Position * scale_factor)
        self.print_status('Vertices updated')

        self.print_status('Setting EdgeLoops to bulk update')
        for edge_loop in self.EdgeLoops:
            edge_loop.start_bulk_update()

        self.print_status('Update Edges')
        for edge in self.Edges:
            edge.end_bulk_update()

        self.print_status('Setting Faces to bulk update')
        for face in self.Faces:
            face.start_bulk_update()

        self.print_status('update EdgeLoops ')
        for edge_loop in self.EdgeLoops:
            edge_loop.end_bulk_update()

        self.print_status('Setting Zones to bulk update')
        for zone in self.Zones:
            zone.start_bulk_update()

        self.print_status('update faces ')
        for face in self.Faces:
            face.end_bulk_update()

        self.print_status('update zones ')
        for zone in self.Zones:
            zone.end_bulk_update()

    def move_to_origin(self, origin=np.array((0, 0, 0))):
        """ Moves the geometry to origin (closest point)

        :param origin: 1x3 np.array with x,y,z-koordinates
        :return:
        """

        # minimal Distance to origin:

        min_distance = np.inf
        translation = np.array((0, 0, 0))

        for vertex in self.Vertices:
            if magnitude(vertex.Position) < min_distance:
                translation = vertex.Position - origin
                min_distance = magnitude(vertex.Position)

        if not(magnitude(translation == 0)):
            for edge in self.Edges:
                edge.start_bulk_update()

            for vertex in self.Vertices:
                vertex.Position = (vertex.Position - translation)
            self.print_status('Vertices updated')

            self.print_status('Setting EdgeLoops to bulk update')
            for edge_loop in self.EdgeLoops:
                edge_loop.start_bulk_update()

            self.print_status('Update Edges')
            for edge in self.Edges:
                edge.end_bulk_update()

            self.print_status('Setting Faces to bulk update')
            for face in self.Faces:
                face.start_bulk_update()

            self.print_status('update EdgeLoops ')
            for edge_loop in self.EdgeLoops:
                edge_loop.end_bulk_update()

            self.print_status('Setting Zones to bulk update')
            for zone in self.Zones:
                zone.start_bulk_update()

            self.print_status('update faces ')
            for face in self.Faces:
                face.end_bulk_update()

            self.print_status('update zones ')
            for zone in self.Zones:
                zone.end_bulk_update()

    def create_mesh(self):
        coords = np.zeros((self.Vertices.__len__(), 3))

        for vertex in self.Vertices:
            coords[vertex.PID, :] = vertex.Position

        a = (coords[:, 0] == coords[:, 1]) | (coords[:, 1] == coords[:, 2]) | (coords[:, 0] == coords[:, 2])
        coords = numpy.delete(coords, numpy.where(a), axis=0)

        face_list = np.empty((1, 3), dtype=int)
        n = 0
        for face in self.Faces:
            print(n)
            face_coords = face.Triangulation['vertices3D']
            for triangle in face.Triangulation['triangles']:
                point_list = []
                for vertex in face_coords[triangle, :]:
                    index = np.where(np.all((np.abs(coords - vertex)) < 0.00001, axis=1))[0]
                    if not (index.size == 0):
                        point_list.append(index[0])
                    else:  # create a new point:
                        np.vstack((coords, vertex))
                        point_list.append(coords.shape[0])
                face_list = numpy.insert(face_list, -1, axis=0, values=np.array(point_list).transpose())
            n = n+1
        # remove last triangle (from initialization)
        face_list = np.delete(face_list, -1, axis=0)

        self.Mesh = trimesh.Trimesh(vertices=coords,
                                    faces=face_list
                                    )

    def write_stl(self, file=None):
        if file is None:
            Tk().withdraw()
            file = asksaveasfilename(filetypes=(("geometry files", "*.stl *.off *.ply *.dae  *.json *.dict *.glb *.dict64 *.msgpack"),("All Files", "*.*")))

            filename, file_extension = os.path.splitext(file)
        else:
            file_extension = None

        if self.Mesh is None:
            self.create_mesh()

        # trimesh.Trimesh.export(self.Mesh, file_obj=file, file_type=file_extension[1:])

        trimesh.base.export_mesh(self.Mesh, file_obj=file, file_type=file_extension[1:])

    def export_to_matlab(self, file=None):

        # file picker for debugging surposes
        if file is None:
            Tk().withdraw()
            file = asksaveasfilename()

        scipy.io.savemat(file, self)

    def write_json(self):

        class ComplexEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, trimesh.Trimesh):
                    print('converting trimesh')
                    return dict(vertices=obj.vertices,
                                volume=obj.volume,
                                triangles=obj.triangles,
                                mass_properties=obj.mass_properties,
                                faces=obj.faces,
                                area=obj.area
                                )

                if isinstance(obj, uuid.UUID):
                    return str(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                if hasattr(obj, 'reprJSON'):
                    return obj.reprJSON()
                else:
                    return json.JSONEncoder.default(self, obj)

        fout = asksaveasfile(mode='a', defaultextension='.txt')
        json_string = json.dumps(self.reprJSON(), cls=ComplexEncoder)
        with open(fout.name, "w") as text_file:
            text_file.write(json_string)

        self.print_status('json sucessfully written to {}'.format(fout.name))

    def reprJSON(self):
        return dict(ID=self._ID,
                    PID=self._PID,
                    Name=self._Name,
                    IsVisible=self._IsVisible,
                    Layers=self.Layers,
                    LayersCount=self.LayersCount,
                    Vertices=self.Vertices,
                    VertexCount=self.VertexCount,
                    Edges=self.Edges,
                    EdgeCount=self.EdgeCount,
                    EdgeLoops=self.EdgeLoops,
                    EdgeLoopCount=self.EdgeLoopCount,
                    Polylines=self.Polylines,
                    PolylineCount=self.PolylineCount,
                    Faces=self.Faces,
                    FaceCount=self.FaceCount,
                    Zones=self.Zones,
                    ZoneCount=self.ZoneCount,
                    Mesh=self.Mesh
                    )

    def import_data_from_excel(self, filename, import_config):

        self.print_status('importing data from file: {}'.format(filename))

        data_frame = self.create_data_frames(filename, import_config)
        self.create_material_layers(data_frame)
        self.create_parts(data_frame)
        self.assign_imported_materials(data_frame)
        # self.create_window_parts(data_frame)

    def create_data_frames(self, filename, import_config):

        wb = Workbook(filename)

        data = dict()
        for resource in import_config:
            self.print_status('\n Importing {}:'.format(resource['name']))
            number_of_parameters = list(resource['parameters'][0].keys()).__len__()
            parameters = dict()
            parameter_sheets = list()
            parameter_sheets_num_rows = list()
            parameter_sheets_num_cols = list()
            start_rows = list()
            start_columns = list()
            end_rows = list()
            end_columns = list()
            directions = list()
            end_indx1 = list()
            end_indx2 = list()

            for parameter in resource['parameters']:
                parameters[parameter['name']] = list()
                parameter_sheets.append(wb.sheets[parameter['sheet']])
                parameter_sheets_num_rows.append(wb.sheets[parameter['sheet']].num_rows)
                parameter_sheets_num_cols.append(wb.sheets[parameter['sheet']].num_cols)
                directions.append(parameter['direction'])
                start_rows.append(parameter['start_row'])

                start_columns.append(parameter['start_column'] - 1)
                end_rows.append(parameter['end_row'])
                end_columns.append(parameter['end_column'])

                if parameter['end_row'] is None:
                    end_indx1.append(wb.sheets[parameter['sheet']].num_rows)
                else:
                    end_indx1.append(parameter['end_row'])

                if parameter['end_column'] is None:
                    end_indx2.append(wb.sheets[parameter['sheet']].num_cols)
                else:
                    end_indx2.append(parameter['end_column'])

            parameter_sheets_num_rows = np.array(parameter_sheets_num_rows)
            parameter_sheets_num_cols = np.array(parameter_sheets_num_cols)
            start_rows = np.array(start_rows)
            end_rows = np.array(end_rows)
            start_columns = np.array(start_columns)
            end_columns = np.array(end_columns)
            Ndirections = numpy.multiply(np.array(np.logical_not(directions), dtype=bool), 1)
            directions = numpy.multiply(np.array(directions, dtype=bool), 1)
            end_indx1 = np.array(end_indx1)
            end_indx2 = np.array(end_indx2)

            row = 0
            df = pd.DataFrame(columns=parameters.keys())

            end_indx = end_indx1 * Ndirections + end_indx1 * directions
            start_indx = start_rows * Ndirections + start_columns * directions
            self.print_status('reading row: ', end='')
            while any((row + start_indx) <= end_indx):
                self.print_status(' {} '.format(row), end='')
                parameter_values = [None] * parameters.__len__()

                for i in range(parameters.__len__()):
                    row_indx = int(start_rows[i] + row * Ndirections[i])
                    col_indx = int(start_columns[i] + row * directions[i])
                    if (row_indx * Ndirections[i] + col_indx * directions[i]) > end_indx[i]:
                        parameter_values[i] = None
                    else:
                        parameter_values[i] = parameter_sheets[i].rows(row_indx)[0][col_indx]
                if any(parameter_values):
                    df = df.append(pd.Series(parameter_values, index=df.columns), ignore_index=True)
                else:
                    self.print_status('\n Empty dataset which means last row or empty row.\n Finishing reading {}'.format(resource['name']))
                    break
                row = row + 1
            self.print_status('\n {} import finished'.format(resource['name']))

            data[resource['name']] = df

        self.print_status('Successfully created dataframe from excel data input \n')

        self.print_status('------------------------------------------------------')

        return data

    def create_material_layers(self, data):
        # ---------------------------------------------------------------------------------------------
        #   Create Materials and dependencies from th excel data
        # ----------------------------------------------------------------------------------------------

        # create materials, layers and parts
        self.print_status('Start creating materials, material layers and parts:  \n')
        material_df = data['Layer']
        # convert to numeric values if possible
        material_df = material_df.apply(pd.to_numeric, errors='ignore')
        for index, row in material_df.iterrows():
            self.print_status('Creating Material and Layer for: {} {}'.format(row['Name'], row['ID']))
            new_mat = (Material(name=row['Name'],
                                density=row['Density'],
                                heat_capacity=row['SpecificHeatCapacity'],
                                thermal_conductivity=row['HeatConductivity'],
                                transparent=False,
                                solar_absorption_coefficient=row['AbsorptionCoefficient'],
                                wvdrf=row['Mu'],
                                w20=row['w20'],
                                w80=row['w80'],
                                color=np.append(np.random.rand(1, 3), 0) * 255)
                       )
            self.add_material(new_mat)

            new_mat_layer = MatLayer(material=new_mat, thickness=row['Thickness'], mat_layer_id=row['ID'])
            self.add_mat_layer(new_mat_layer)
        self.print_status('Material and layer creation finished')

    def create_parts(self, data):
        # create parts
        self.print_status('\nStart creating parts:')
        material_df = data['Layer']
        # convert to numeric values if possible
        material_df = material_df.apply(pd.to_numeric, errors='ignore')
        new_part_ids = np.unique(np.array(material_df['PartId'],))
        for new_id in new_part_ids.__iter__():
            self.print_status('Creating part {}'.format(str(new_id)))
            layer_ids = material_df.index[material_df['PartId'] == new_id].tolist()
            new_part = Part(name=str(new_id), layers=[self.MatLayers[i] for i in layer_ids], part_id=new_id)
            self.add_part(new_part)
        self.print_status('Part creation finished')

    def create_window_parts(self, data):

        self.print_status('Start Window creation:  \n')
        window_construction_df = data['WindowConstruction']
        window_construction_df = window_construction_df.apply(pd.to_numeric, errors='ignore')
        new_part_ids = np.unique(np.array(window_construction_df['ID'], ))

        window_df = data['Windows']
        window_df = window_df.apply(pd.to_numeric, errors='ignore')

        def extract_id(str):
            return str.split()[1]

        window_df.ID = window_df.ID.apply(extract_id)
        window_df = window_df.apply(pd.to_numeric, errors='ignore')

        new_window_ids = np.array(window_df['ID'], )

        window_parts = list()

        for new_window_id in new_window_ids:
            window_face = [face for face in self.Faces if (face.ID == new_window_id)]
            window_df_indx = window_df.index[window_df['ID'] == new_window_id].tolist()
            window_series = window_df.iloc[[window_df_indx[0]]]
            window_construction_df_indx = window_construction_df.index[window_construction_df['ID'] == window_series['PartID']].tolist()
            window_construction_series = window_construction_df.iloc[[window_construction_df_indx[0]]]

            self.print_status('Creating Window part {}'.format(str(window_construction_series['ID'])))

            window_part = Window(name=str(window_construction_series['ID']),
                                 face=window_face[0],
                                 part_id=window_construction_series['ID'],
                                 color=np.append(np.random.rand(1, 3), 0) * 255,
                                 color_from_parent=False,
                                 is_visible=True,
                                 openable=bool(window_construction_series['Openable'][0]),
                                 u_g=window_construction_series['Ug'][0],
                                 u_f=window_construction_series['Uf'][0],
                                 psi=window_construction_series['Psi'][0],
                                 frame_width=window_construction_series['FrameWidth'][0],
                                 eps=window_construction_series['Eps'][0],
                                 tau=window_construction_series['Tau'][0],
                                 rho=window_construction_series['Rho'][0],
                                 alpha=window_construction_series['Alpha'][0],
                                 number_of_glazings=2,
                                 glazing_thickness=0.01
                                 )
            window_parts.append(window_part)

            window_face.Part = window_part


        for new_id in new_part_ids.__iter__():
            self.print_status('Creating Window part {}'.format(str(new_id)))

    def assign_imported_materials(self, data):
        for index, row in data['Surfaces'].iterrows():
            part_id = int(row.PartID)
            surface_id = [int(s) for s in row.ID.split() if s.isdigit()][0]

            # find surface with id:
            surface = next((x for x in self.Faces if x.ID == surface_id), None)
            part = next((x for x in self.Parts if x.ID == part_id), None)

            if (surface is None) and (part is None):
                self.print_status('Surface with ID {} not found'.format(surface_id))
                self.print_status('Part with ID {} not found'.format(part_id))
                continue
            elif surface is None:
                self.print_status('Surface with ID {} not found'.format(surface_id))
                continue
            elif part is None:
                self.print_status('Part with ID {} not found'.format(part_id))
                continue
            else:
                # assign part to surface
                surface.Part = part

        self.print_status('Part successfully assigned')

















