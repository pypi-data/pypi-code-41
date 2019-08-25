import exifread
import piexif
import datetime
from PIL import Image

from deepgeo.util.to_float import to_float
from deepgeo.util.from_datetime import from_datetime as datatime_to_timestamp
from deepgeo.util.to_date import toYYYYMMDDHHMMSS as check_format_date

def __17__(ratio):
    return to_float(ratio)

def __6__(ratio):
    return to_float(ratio.values[0])

def __2__4__(ratio, ref):
    item = ratio.values
    _min = to_float(item[0])
    _sec = to_float(item[1])
    _deg = to_float(item[2])
    data = (_min + (_sec + _deg / 60.0) / 60.0)
    if data == 0.0:
        data = None
    else:
        if ref is not None:
            if str(ref) == 'S' or str(ref) == 'W':
                data *= -1
    return data

def exif_to_data(ratio, ref=None):
    if ratio.tag == 17:
        return __17__(ratio)
    if ratio.tag == 4 or ratio.tag == 2:
        return __2__4__(ratio, ref)
    if ratio.tag == 6:
        return __6__(ratio)
    return None

class EXIF:
    def __init__(self, pImage, file_path):
        self._file_path_ = file_path
        self._image_ = pImage
        self._bEXIF_ = None
        self._EXIF_ = None
        self.__load_image__()

    def __load_image__(self):
        try:
            with open(self._file_path_, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            self._EXIF_ = tags 
            exif_dict = piexif.load(self._image_.info["exif"])
            self._bEXIF_ = piexif.dump(exif_dict)
        except Exception:
            self._EXIF_ = {}
            self._bEXIF_ = None
    
    def setOrientation(self, ori):
        exif_dict = piexif.load(self._image_.info["exif"])
        exif_dict["0th"][piexif.ImageIFD.Orientation] = ori
        self._bEXIF_ = piexif.dump(exif_dict)

    def getBinaryEXIF(self):
        return self._bEXIF_

    def getEXIF(self, key):
        if key in self._EXIF_:
            return self._EXIF_[key]
        return None

    def get_location(self, type=""):
        """
            # get_location : 이미지의 위치정보를 가져옵니다.
            type : 반환되는 형태를 말합니다.
            type is "" : (Longitude, Latitude) 형태로 반환됩니다.
            type is None : (Longitude, Latitude) 형태로 반환됩니다.
            type is "dictionary" :  {"Longitude": Longitude, "Latitude": Latitude} 형태로 반환됩니다.
            type is "point" : POINT(Longitude Latitude) 형태로 반환됩니다.
        """
        exif = self._EXIF_
        lon=None
        lat=None
        if "GPS GPSLongitude" in exif.keys():
            ref = None
            if "GPS GPSLongitudeRef" in exif.keys():
                ref = exif["GPS GPSLongitudeRef"]
            lon = exif_to_data(exif["GPS GPSLongitude"], ref)
        if "GPS GPSLatitude" in exif.keys():
            ref = None
            if "GPS GPSLatitudeRef" in exif.keys():
                ref = exif["GPS GPSLatitudeRef"]
            lat = exif_to_data(exif["GPS GPSLatitude"], ref)
        
        if lon is not None and lat is not None:
            if type == "dictionary":
                return {"Longitude": lon, "Latitude": lat}
            elif type=="point": 
                return "POINT(" + str(lon) + " " + str(lat) + ")"
            else:
                return (lon, lat)
        return None

    def get_altitude(self, type=""):
        """
            # get_altitude : 이미지의 altitude정보를 가져옵니다.
            type : 반환되는 형태를 말합니다.
            type is "" : altitude 형태로 반환됩니다.
            type is None : altitude 형태로 반환됩니다.
            type is "dictionary" :  {"altitude": altitude} 형태로 반환됩니다.
        """
        exif = self._EXIF_
        if "GPS GPSAltitude" in exif.keys():
            ref = None
            if "GPS GPSAltitudeRef" in exif.keys():
                ref = exif["GPS GPSAltitudeRef"]
            altitude = exif_to_data(exif["GPS GPSAltitude"], ref)
            if type=="dictionary":
                return {"Altitude": altitude}
            else:
                return altitude
        return None

    def get_datetime(self, type=""):
        """
            # get_datetime : 이미지에 있는 시간 데이터를 가져옵니다.
            
            type : 반환되는 형태를 말합니다.
            type is "timestamp_with_dictionary" : timestamp으로 Dictionary 형태로 반환됩니다.
            type is "timestamp" : timestamp으로 반환됩니다.
            type is "date_with_dictionary" : date으로 Dictionary 형태로 반환됩니다.
            type is "date" : date으로 반환됩니다.
            type is None or type is "" : date으로 반환됩니다.
        """
        exif = self._EXIF_
        if "Image DateTime" in exif.keys():
            datetime_ = str(exif["Image DateTime"]).split(" ")
            date_ = datetime_[0].replace(":", '-') + " " + datetime_[1]
            date_ = check_format_date(date_)
        else:
            date_ = "2000-01-01 00:00:00"
        timestamp_ = datatime_to_timestamp(date_)
        
        if type=="timestamp_with_dictionary":
            return {"Timestamp" : timestamp_}
        elif type == "timestamp":
            return timestamp_
        elif type == "date_with_dictionary":
            return {"Date": date_}
        else:
            return date_

    def get_direction(self, type=""):
        """
            # get_direction : 이미지에 있는 방향 데이터를 가져옵니다.
            
            type : 반환되는 형태를 말합니다.
            type is "dictionary" : {"Direction": Direction} 형태로 반환됩니다.
            type is "" or type is None : Direction 형태로 반환됩니다.
        """
        exif = self._EXIF_
        if "GPS GPSImgDirection" in exif.keys():
            ref = None
            if "GPS GPSImgDirectionRef" in exif.keys():
                ref = exif["GPS GPSImgDirectionRef"]
            data = exif_to_data(exif["GPS GPSImgDirection"], ref)
            if type=="dictionary":
                return {"Direction": data}
            else:
                return data
        return None

    def get_distance(self, type=""):
        """
            # get_distance : 이미지에 있는 방향 데이터를 가져옵니다.
            
            type : 반환되는 형태를 말합니다.
            type is "dictionary" : {"Distance": Distance} 형태로 반환됩니다.
            type is "" or type is None : Distance 형태로 반환됩니다.
        """
        exif = self._EXIF_
        if "GPS GPSDestDistance" in exif.keys():
            distance = exif_to_data(exif["GPS GPSDestDistance"], exif["GPS GPSDestDistance"])
            if type=="dictionary":
                return {"Distance": distance}
            else:
                return distance
        else:
            return None