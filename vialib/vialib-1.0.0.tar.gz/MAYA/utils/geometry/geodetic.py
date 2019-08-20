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

# this library contains general algorithms for spheroidal / geodetic geometry

from math import sin, cos, tan, asin, acos, atan, atan2, pi, sqrt
import numpy
from MAYA.utils.geometry import spherical, areas_centroids
from MAYA.utils.geometry import vectors

#r=repos.Repository('localhost:6200')

#geo_coord_role = uuid._('~0182c18d8cd44c11d991834612785d73c0')
#geo_ref_role = uuid._('~fd000a02510bfd7b6cab54')

# this is the specification of the GPS ellipsoid
WGS84 = (6378137.0, 1.0/298.2572235630)
DEGREE_RADIAN_CHECK = 0

### takes a lat, lon, elevation and a reference ellipsoid

# spheroid : This defines the reference shperoid and its a tuple of
# two parameters, the first being the length of the semi-major axis of
# the spheroid in meters(usually denoted by a) and the second is the
# flattening factor (usually denoted by f)

# point is a tuple of three of the form (lat, lon, elvn)) where lat is
# in radians, lon is in radians and height is in meters
# height measured from the surface of the reference ellipsoid

# from http://www.colorado.edu/geography/gcraft/notes/datum/gif/llhxyz.gif
def geodeticToCartesian(lat, lon, elvn=0, spheroid=WGS84):
    if DEGREE_RADIAN_CHECK == 1:
	if fabs(lat) > 4.0 or fabs(lon) > 8.0:
	    print "Geodetic to Cartesian: Your angles look too big to be radians!"
	    print "Doing automatic translation to radians. This may not be smart."
	    (lat, lon) = map(spherical.degreesToRadians, (lat, lon))
    (a,f) = spheroid # this definition is major axis, flattening
    esq = f*(2-f) # the square of the eccentricity
    latsin = sin(lat)
    nu = a / sqrt(1 - esq*latsin**2) # prime radius of curvature at lat
    x = (nu+elvn)*cos(lat)*cos(lon)
    y = (nu+elvn)*cos(lat)*sin(lon)
    z = (nu*(1-esq)+elvn)*latsin
    return [x,y,z] 

### http://www.colorado.edu/geography/gcraft/notes/datum/gif/xyzllh.gif
def cartesianToGeodetic(xyz_vector, spheroid=WGS84): 
    x = xyz_vector[0]
    y = xyz_vector[1]
    z = xyz_vector[2]
    (a,f) = spheroid # this definition is major axis, flattening
    b = a - a*f # this gives the minor axis
    rsq = x*x + y*y # this is the radius outwards in the x-y plane    
    r = sqrt(rsq)
    esq = f*(2-f) # the square of the eccentricity
    #Esq = a*a - b*b
    eprimesq = (a*a)/(b*b) - 1

    theta = atan((z*a)/(r*b))
    lat = atan((z + eprimesq*b*(sin(theta)**3))/(r - esq*a*(cos(theta)**3)))
    lon = atan2(y, x)

    sinlat = sin(lat)
    if sinlat == 0:
        elvn = r - a
    else:
        nu = a / sqrt(1 - esq*sinlat*sinlat) # prime radius of curvature at lat
        #elvn = z/sinlat - nu*(1-esq)
        elvn = r/cos(lat) - nu
                
    return(lat, lon, elvn)

### take a point P (on the surface) and return local canonical frame
# this is the frame whose local east and north are tangent to P
def getSpheroidTangentFrame( lat, lon, elvn=0, spheroid=WGS84 ):
    (a,f) = spheroid # this definition is major axis, flattening
    esq = f*(2-f) # now the square of the eccentricity
    latsin = sin(lat)
    nu = a / sqrt(1 - esq*latsin**2) # prime radius of curvature at lat
    x = (nu+elvn)*cos(lat)*cos(lon)
    y = (nu+elvn)*cos(lat)*sin(lon)
    z = (nu*(1-esq)+elvn)*latsin

    # start with rotation around earth's axis (from longitude)
    twist_matrix = [[cos(lon),sin(lon),0],[-sin(lon),cos(lon),0],[0,0,1]]

    # now handle tilt from latitude
    if lat == 0:
	slope_axes = [[0,1,0],[0,0,1],[1,0,0]]
    else:	    
	b = (1-f)*a
	rad = sqrt(x*x + y+y)
	slope = (b*b)/(a*a)*(rad/z) # this is the gradient of a 2-d ellipse
	tan_len = sqrt(1 + slope*slope)
	dz = slope/tan_len
	dx = 1/tan_len
	# frame at this latitude on greenwich meridian
	if z < 0:
	    slope_axes = [[0,1,0],[dx,0,-dz],[dz,0,-dx]]
	if z > 0:
	    slope_axes = [[0,1,0],[-dx,0,dz],[dz,0,dx]]

    # compose rotation about axis with change of slope
    local_axes = map(lambda x: twist_matrix * numpy.matrix(x).transpose(), slope_axes)
    local_frame = vectors.basis(local_axes, origin=[x,y,z])
    return local_frame

### takes a geo-reference u-form and returns vector in ECEF coords
def getECEFfromGeoRef(r, geo_uu ):
    if geo_ref_role not in r.getAttr(geo_uu, 'roles'):
        print "Can't get global position from u-form not playing geo-reference role."
        return(-1)
    lat = spherical.degreesToRadians(r.getAttr(geo_uu, 'latitude'))
    long = spherical.degreesToRadians(r.getAttr(geo_uu, 'longitude'))
    elev = r.sphereTangentgetAttr(geo_uu, 'elevation') or 0
    return geodeticToCartesian( lat, long, elev )


def degreesToRadians(deg):
    return (deg / 360.0) * 2.0 * pi

"""
###
def test2():
    #r = repos.Repository('localhost:6200')
    GBcoast = uuid._ ('~01b37c2d9ed3af11d98f7123eb3f312ba0')
    gbcoords = zip(r.getAttr(GBcoast, 'path_data_lat'), r.getAttr(GBcoast, 'path_data_long'))
    for point in gbcoords:
        point = map(spherical.degreesToRadians, point)
        point1 = geodeticToCartesian(point[0], point[1])
        point2 = cartesianToGeodetic(point1)
        print point, "**",  point2
"""
###
def office_test():
    officelat = degreesToRadians(40.42733)
    officelon = degreesToRadians(-79.96550)
    office_xyz = geodeticToCartesian(officelat, officelon, elvn=350)
    print office_xyz

###
def test():
    for x in range(-9,10,3):
	(lat, lon) = (x*pi/18, 0)
	print "Lat:", lat, "Lon:", lon
	frame = getSpheroidTangentFrame( lat, lon )
	#print frame
	print vectors.radialFrame( geodeticToCartesian(lat,lon))

    """
    for lon in range(-10, 10, 1):
        xyz = geodeticToCartesian(lat, lon/10.0, elvn)
        (nlat, nlon, nelvn) = cartesianToGeodetic(xyz)
        print("%1.6f\t%1.6f\t%1.6f\t%1.6f" % (elvn, nelvn, lon/10.0, nlon))
"""



###
if __name__ == '__main__':
    test()
