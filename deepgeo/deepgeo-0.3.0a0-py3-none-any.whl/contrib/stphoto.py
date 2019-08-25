# Defalut Info
__deepgeo_category__ = "type"
__id__="STPhoto"

import json

from deepgeo.util import error, to_json, create
from deepgeo.image import obj as Image

class obj(Image):
    @staticmethod
    def fromDictionary(data):
        if isinstance(data, dict):
            uri = data['uri']
            name = uri
            path = "tmp"
            if not("http" in uri or "file" in uri):
                name = uri.replace("\\","/").split("/")[-1]
                path = uri.replace(name,"")
            return STPhoto((name, path), data['annotations'])
        raise error.SupportFormatError(type(data))
        
    @staticmethod
    def fromJSON(data):
        if isinstance(data, str):
            return STPhoto.fromDictionary(json.loads(data))
        raise error.SupportFormatError(type(data))

    def to_stphoto(self):
        info = self.get_info()
        return {
            "uri":self._uri_,
            "width":info['Width'],
            "height":info['Height'],
            "t":info['Time'],
            "annotations":self.get_annotation(),
            "geo":{
                "pointx":info['Latitude'],
                "pointy":info['Longitude']
            },
            "altitude":info['Altitude'],
            "afov":{
                "horizontalAngle":info['HorizontalAngle'],
                "verticalAngle":None,
                "direction2d":info['Direction2d'],
                "direction3d":None,
                "distance":info['Distance']
            }
        }

    def to_stphoto_tuple(self):
        s = self.to_stphoto()
        return (s['uri'],s['width'],s['height'],s['t'],s['annotations'],
        (s['geo']['pointx'],s['geo']['pointy']),s['altitude'],
        (s['afov']['horizontalAngle'],s['afov']['verticalAngle'],
        s['afov']['direction2d'],s['afov']['direction3d'],s['afov']['distance']))
    
    def to_stphoto_as_json(self):
        return json.dumps(self.to_stphoto(), indent='\t', sort_keys=True, default=tojson.default_DICT_TO_JSON)
    
    def to_stphoto_as_json_file(self, path, file_name):
        path = create.folder(path)
        file_name = file_name.replace("."+file_name.split(".")[-1],"")
        path = path + file_name + ".json"
        data = self.to_stphoto()
        
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent='\t', sort_keys=True, default=tojson.default_DICT_TO_JSON)
        return path