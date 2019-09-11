import os
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

from geofinder import GeoKeys

dtd = '{http://gramps-project.org/xml/1.7.1/}'


def process_places():
    print(f'PROCESS len={len(lines)}')
    try:
        tr = ET.parse(BytesIO(lines))
    except TypeError:
        print(f'@{line}', end="")

    for child in tr.iter:
        if child.text is not None:
            print(f'AA <{child.tag}>{child.text}</{child.tag}>')
        else:
            if child.tag == 'pname':
                nm = child.attrib.get('value')
                print(f'BB <{child.tag} VALUE="{nm}"/>')
            elif child.tag == 'coord':
                lon = child.attrib.get('long')
                lat = child.attrib.get('lat')
                print(f'CC <{child.tag} LONG="{lon}" LAT="{lat}"/>')
            else:
                print(f'DD <{child.tag} {child.attrib}>')


    print('PROCESS DONE')


path = os.path.join(str(Path.home()), GeoKeys.get_directory_name(), 'cache', 'gramps.xml')
places_start = False
lines = b''

with open(path) as f:
    while True:
        line = f.readline()
        if line == '':
            break
        if '<places>' in line:
            places_start = True
        elif '</places>' in line:
            places_start = False
            lines += bytes(line, "utf8")
            # print(line)
            process_places()

        if places_start:
            # Collect lines
            lines += bytes(line, "utf8")
            # print(line)
        else:
            # print(line)
            pass
