from geopy.geocoders import Nominatim
import json
import urllib3
from transliterate import translit
from langdetect import detect

#############################
#   GET NOMINATIM DATA
#############################


def getCity(name=None, address=None, lat=None, lon=None, countryCode='RU'):

    userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    nominatim = Nominatim(user_agent=userAgent)

    if name is not None:
        if detect(str(name)) is "RU":
            name = translit(str(name), reversed=True)
        location = nominatim.geocode(str(name), country_codes=countryCode)
        return location.raw

    if address is not None:
        if detect(str(name)) is "RU":
            name = translit(str(name), reversed=True)
        location = nominatim.geocode(str(address))
        return location.raw

    if lat is not None and lon is not None:
        lat = str(lat)
        lon = str(lon)
        location = nominatim.reverse("{lat}, {lon}")
        return location.raw


#############################
#   GET POLYGONS GEOJSON
#############################


def getPolygons(osm_id=None):
    if osm_id is not None:
        url = "http://polygons.openstreetmap.fr/get_geojson.py?id=%a&params=0" % osm_id

        http = urllib3.PoolManager()
        response = http.request('GET', url)
        code = response.status
        message = response.msg
        data = response.data.decode('utf-8')

        if code != 200:
            data = {
                "code": code,
                "message": message,
                "data": data
            }
        else:
            data = json.loads(data)
            return data['geometries'][0]['coordinates'][0][0]

    else:
        data = {
            "code": "404",
            "message": "please enter osm_id"
        }
    return data


