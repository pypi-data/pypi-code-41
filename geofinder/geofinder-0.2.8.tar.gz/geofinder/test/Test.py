import os
from pathlib import Path
from xml.etree.ElementTree import iterparse
import xml.etree.ElementTree as ET


from geofinder import GeoKeys

dtd = '{http://gramps-project.org/xml/1.7.1/}'

path = os.path.join(str(Path.home()), GeoKeys.get_directory_name(), 'cache', 'gramps.xml')

with open(path) as f:
    while True:
        line = f.readline()
        if line == '':
            break
        try:
            ky = ET.fromstring(line).tag
            txt = ET.fromstring(line).text
            att = ET.fromstring(line).attrib

            if txt is not None:
                print(f'<{ky}>{txt}</{ky}>')
            else:
                if ky == 'pname':
                    nm = att.get('value')
                    print(f'<{ky} VALUE="{nm}"/>')
                elif ky == 'coord':
                    lon = att.get('long')
                    lat = att.get('lat')
                    print(f'<{ky} LONG="{lon}" LAT="{lat}"/>')
                else:
                    print(f'<{ky} {att}>')

        except ET.ParseError:
            print(f'@{line}',end ="")


""" 
for event, elem in iterparse(path):
    if "ptitle" in elem.tag:
        print('PLACE title ' + str(elem.attrib))
    else:
        print(elem)
"""
