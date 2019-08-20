#######################################################################
#
#       COPYRIGHT 2006 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY MAYA DESIGN.
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY MAYA
# DESIGN AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR CONSENT
# OF MAYA DESIGN.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH THE TERMS
# OF THE APPLICABLE LICENSE AGREEMENT FROM MAYA DESIGN. THIS LEGEND MAY NOT BE
# REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY MAYA DESIGN LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################

"""This module contains functions for parsing an esri-format shape
into a shape list. Each member of the shape list is an object
containing a bounding box (shape.bb) and a list of polylines.
Each polyline is a list of points - normally long, lat pairs for esri.
Beware of point order!"""

import struct
import StringIO
import dbf

NULL = 0
POINT = 1
MULTIPOINT = 8
POLYLINE = 3
POLYGON = 5
POINTZ = 11
MULTIPOINTZ = 18
POLYLINEZ = 13
POLYGONZ = 15
POINTM = 21
POLYLINEM = 23
POLYGONM = 25
MULTIPOINTM = 28

# leave off the .shp or .dbf extension
# returns ESRI shape objects with an extra member field called dbf_record,
# which is a dictionary
def make_esri_dbf_records(filename_stem, debug=0):

    fd = open(filename_stem + '.shp')
    data = fd.read()
    fd.close()
    
    shapes = esri_to_shapes(data, 1, debug=debug)
    
    reader = dbf.DBF(filename_stem + '.dbf')
    records = reader.open()

    n = min(len(records), len(shapes))

    i = 0
    while i < n:
        shapes[i].dbf_record = records[i]
        i += 1

    shapes = [ shp for shp in shapes if not (shp.type in (POLYLINE, POLYGON) 
                                             and not shp.parts) ]

    return shapes

def get_geo_extents(filename_stem):
    fd = open(filename_stem + '.shp')
    header = fd.read(100)
    fd.close()

    (xmin, ymin, xmax, ymax) = struct.unpack('<dddd', header[36:68])

    return ( (ymin, xmin), (ymax, xmax) )

# This function is taken from Mike's esri parsing code
# If you're getting data from a .shp file, pass read_header=1
# If you're getting data from a previous import, someone may have
# stripped the header
def esri_to_shapes(esri_data, read_header=0, debug=0):
    shapes = []

    fd = StringIO.StringIO(esri_data)
    if read_header:
	fd.read(100) 

    buf = fd.read(8)
    while len(buf) > 0:
        recno, l = struct.unpack('>ii', buf)

        data = fd.read(l*2)
        try:
            shape = create_shape(data, debug)
        except AttributeError:
            print "No such shape type"

        shapes.append(shape)

        buf = fd.read(8)

    return shapes

# The rest of this module is from the Greenmap utils
def create_shape(data, debug=0):
    shape_type = struct.unpack('<i', data[:4])[0]

    if shape_type == NULL:
        if debug: print "create_shape: found type", shape_type
        return ESRI_Null()
    elif shape_type in (POINT, POINTZ, POINTM):
        if debug: print "create_shape: found type", shape_type
        return ESRI_Point(data)
    elif shape_type in (MULTIPOINT, MULTIPOINTZ, MULTIPOINTM):
        if debug: print "create_shape: found type", shape_type
        return ESRI_MultiPoint(data)
    elif shape_type in (POLYLINE, POLYLINEZ, POLYLINEM):
        if debug: print "create_shape: found type", shape_type
        return ESRI_PolyLine(data)
    elif shape_type in (POLYGON, POLYGONZ, POLYGONM):
        if debug: print "create_shape: found type", shape_type
        return ESRI_Polygon(data)
    else:
        if debug: print "create_shape: found unknown type", shape_type
        return None

def nested_from_flat(xs):
    pts = []
    pt = []
    i = 0
    for x in xs:
        pt.append(x)
        if i % 2 == 1:
            pts.append(pt)
            pt = []
        i = i + 1
    return pts
    
def create_shape_from_plain(data, debug=0):
    shape_type = data[0]

    if shape_type == NULL:
        if debug: print "create_shape_from_plain: found type", shape_type
        e = ESRI_Null()
    elif shape_type == POINT:
        if debug: print "create_shape_from_plain: found type", shape_type
        e = ESRI_Point()
        data = data[1]
        e.x = data[0]
        e.y = data[1]
    elif shape_type == MULTIPOINT:
        if debug: print "create_shape_from_plain: found type", shape_type
        e = ESRI_MultiPoint()
        data = data[1]        
        e.bb = data[0]
        e.points = nested_from_flat(data[1])
    elif shape_type == POLYLINE:
        if debug: print "create_shape_from_plain: found type", shape_type
        e = ESRI_PolyLine()
        data = data[1]
        e.bb = data[0]
        parts = []
        for part in data[1]:
            part = nested_from_flat(part)
            parts.append(part)
        e.parts = parts
    elif shape_type == POLYGON:
        if debug: print "create_shape_from_plain: found type", shape_type
        e = ESRI_Polygon()
        data = data[1]
        e.bb = data[0]
        parts = []
        for part in data[1]:
            part = nested_from_flat(part)
            parts.append(part)        
        e.parts = parts
    else:
        if debug: print "create_shape_from_plain: found unknown type", shape_type
        e = None

    return e

class ESRI_Null:

    def __init__(self):
        self.type = NULL

    def toESRI(self):
        return struct.pack('<i', self.type)

    def toPlain(self):
        return tuple(self.type)

    def __repr__(self):
        return 'ESRI NULL'


class ESRI_Point:

    def __init__(self, data = None):
        self.type = POINT

        if data == None:
            x = None
            y = None
            return
        
        x, y = struct.unpack('<dd', data[4:20])
        self.x = x
        self.y = y

    def toESRI(self):
        return struct.pack('<i', self.type) + struct.pack('<dd', self.x, self.y)

    def toPlain(self):
        return (self.type, (self.x, self.y))

    def __repr__(self):
        return "ESRI POINT " + `self.x` + " " + `self.y`

    
class ESRI_MultiPoint:

    def __init__(self, data = None):
        self.type = MULTIPOINT

        if data == None:
            points = None

        self.bb = struct.unpack('<dddd', data[4:36])
        num_points = struct.unpack('<i', data[36:40])[0]

        points = []
        data_index = 40
        for i in range(num_points):
            pt = struct.unpack('<dd', data[data_index:data_index + 16])
            points.append(pt)
            data_index = data_index + 16

        self.points = points

    def toPlain(self):
        pts = []
        for pt in self.points:
            pts.extend(pt)
        return (self.type, (self.bb, pts))

    def __repr__(self):
        return "ESRI MULTIPOINT " + `self.bb` + " " + `self.points`


class ESRI_PolyLine:

    def __init__(self, data = None):
        self.type = POLYLINE
        
        if data == None:
            self.bb = None
            self.parts = None
            return
        
        self.bb = struct.unpack('<dddd', data[4:36])
        num_parts, num_points = struct.unpack('<ii', data[36:44])

        parts_indices= []
        data_index = 44
        for i in range(num_parts):
            part_index = struct.unpack('<i',
                                       data[data_index:data_index + 4])[0]
            data_index = data_index + 4
            parts_indices.append(part_index)
        parts_indices.append(num_points)

        self.parts = []
        for i in range(len(parts_indices) - 1):
            cur_part = []
            for j in range(parts_indices[i + 1] - parts_indices[i]):
                point = struct.unpack('<dd', data[data_index:data_index + 16])
                data_index = data_index + 16
                cur_part.append(point)
            self.parts.append(cur_part)

    def toESRI(self):
        buf = struct.pack('<iddddi',
                          self.type,
                          self.bb[0],
                          self.bb[1],
                          self.bb[2],
                          self.bb[3],
                          len(self.parts))
        num_points = 0
        for p in self.parts:
            num_points = num_points + len(p)
        buf = buf + struct.pack('<i', num_points)

        parts_buf = ''
        index = 0
        for p in self.parts:
            parts_buf = parts_buf + struct.pack('<i', index)
            index = index + len(p)

        points_buf = ''
        for p in self.parts:
            for pt in p:
                points_buf = points_buf + struct.pack('<dd', pt[0], pt[1])

        return buf + parts_buf + points_buf

    def toPlain(self):
        parts = []
        for part in self.parts:
            new_part = []
            for pt in part:
                new_part.extend(pt)
            parts.append(pt)
        return (self.type, (self.bb, parts))

    def __repr__(self):
        return "ESRI POLYLINE " + `self.bb` + " " + `self.parts`


class ESRI_Polygon:

    def __init__(self, data = None):
        self.type = POLYGON

        if data == None:
            self.bb = None
            self.parts = None
            return
        
        self.bb = struct.unpack('<dddd', data[4:36])
        num_parts, num_points = struct.unpack('<ii', data[36:44])

        parts_indices= []
        data_index = 44
        for i in range(num_parts):
            part_index = struct.unpack('<i',
                                       data[data_index:data_index + 4])[0]
            data_index = data_index + 4
            parts_indices.append(part_index)
        parts_indices.append(num_points)

        self.parts = []
        for i in range(len(parts_indices) - 1):
            cur_part = []
            for j in range(parts_indices[i + 1] - parts_indices[i]):
                point = struct.unpack('<dd', data[data_index:data_index + 16])
                data_index = data_index + 16
                cur_part.append(point)
            self.parts.append(cur_part)

    def toESRI(self):
        buf = struct.pack('<iddddi',
                          self.type,
                          self.bb[0],
                          self.bb[1],
                          self.bb[2],
                          self.bb[3],
                          len(self.parts))
        num_points = 0
        for p in self.parts:
            num_points = num_points + len(p)
        buf = buf + struct.pack('<i', num_points)

        parts_buf = ''
        index = 0
        for p in self.parts:
            parts_buf = parts_buf + struct.pack('<i', index)
            index = index + len(p)

        points_buf = ''
        for p in self.parts:
            for pt in p:
                points_buf = points_buf + struct.pack('<dd', pt[0], pt[1])

        return buf + parts_buf + points_buf

    def toPlain(self):
        parts = []
        for part in self.parts:
            new_part = []
            for pt in part:
                new_part.extend(pt)
            parts.append(pt)        
        return (self.type, (self.bb, parts))

    def __repr__(self):
        return "ESRI POLYGON " + `self.bb` + " " + `self.parts`

def isPolygonCW(ring):
    """ Return if the vertices in the polygon ring are clockwise or 
    anti-clockwise.  """
    # Based on http://debian.fmi.uni-sofia.bg/~sergei/cgsr/docs/clockwise.htm

    p = 0
    n = 0

    N = len(ring)
    i = 0
    while i < N:
        x0 = ring[i]
        y0 = ring[i+1]
        x1 = ring[(i+2) % N]
        y1 = ring[(i+3) % N]
        x2 = ring[(i+4) % N]
        y2 = ring[(i+5) % N]

        cp = ((x1-x0)*(y2-y1)) - ((y1-y0)*(x2-x1))
        if cp > 0:
            p += 1
        elif cp < 0:
            n += 1

        i += 2

    return n >= p

def isGeodetic(records):
    """ Check to see if the ESRI records are in lon/lat format.  Can't
    tell *which* geodetic coordinate system, though! """

    i = 1
    for r in records:
        if r.type == NULL: continue
        if hasattr(r, 'parts'):
            for p in r.parts:
                for (lon, lat) in p:
                    if not (-180.0 <= lon and lon <= 180.0 and 
                             -90.0 <= lat and lat <= 90.0):
                        return "Shapefile not in geodetic coordinate system. It contains at least one coordinate outside the valid WGS84 range: (%f, %f) found in record %d" % (lon, lat, i)
        else:
            (lon, lat) = (r.x, r.y)
            if not (-180.0 <= lon and lon <= 180.0 and 
                     -90.0 <= lat and lat <= 90.0):
                return "Shapefile not in geodetic coordinate system. It contains at least one coordinate outside the valid WGS84 range: (%f, %f) found in record %d" % (lon, lat, i)
        i += 1
    return None
