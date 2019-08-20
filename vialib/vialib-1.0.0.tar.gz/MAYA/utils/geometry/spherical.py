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

# this library contains general algorithms for *abstract* spherical geometry 
# in other words, everything is worked out on a sphere of radius 1, so that a
# geodesic angle of 1 radian corresponds to a great circle distance of 1

# spherical coordinates are represented in latitude and longitude, in radians
# sorry if this seems like a mixture of conventions, it seems to work ...

# bearings are measured from north, being the angle east of north

# if you want to use this library for planet Earth geometry (no mixed
# language pun intended), remember to multiply by the radius of the
# planet Earth.

from math import sin, cos, asin, atan2, pi, sqrt
from MAYA.utils.geometry.vectors import *

def degreesToRadians(deg):
    return (deg / 360.0) * 2.0 * pi
def radiansToDegrees(rad):
    return (rad * 360.0) / ( 2.0 * pi )

###
def spherical_to_cartesian( lat, lon, rad=radius_earth ):
    return vector((rad*cos(lon)*cos(lat),rad*sin(lon)*cos(lat),rad*sin(lat)), BASEFRAME)

# calculates the angle between A and B, represented in latitude and longitude
def geodesicSegment(A, B):
    (lat1, lon1) = A
    (lat2, lon2) = B
    x1 = cos(lat1) * cos(lon1)
    y1 = cos(lat1) * sin(lon1)
    z1 = sin(lat1)
    x2 = cos(lat2) * cos(lon2)
    y2 = cos(lat2) * sin(lon2)
    z2 = sin(lat2)
    C = sqrt( ((x1-x2) * (x1-x2)) +
              ((y1-y2) * (y1-y2)) +
              ((z1-z2) * (z1-z2)) )
    alpha = asin(C/2.0)
    return (2.0 * alpha)

###
def geodesicDirection(A, B):
    (lat1, lon1) = A
    (lat2, lon2) = B
    bearing = atan2(-sin(lon1-lon2)*cos(lat2),
                    cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(lon1-lon2) )

    # make sure bearing is within bounds [0, 2pi)
    while bearing < 0:
        bearing = bearing + 2.0*pi
    while bearing >= 2.0*pi:
        bearing = bearing - 2.0*pi
    
    return bearing

### this is an inverse function to compute the latitude and longitude
### of the point where you end up if you start at point (lat1, lon1)
### and go certain distance beginning along a certain bearing
def endLatLon( (start_lat, start_lon), distance, bearing ):

    end_lat = asin( sin(start_lat)*cos(distance) + cos(start_lat)*sin(distance)*cos(bearing) )
    dlon = atan2( sin(bearing)*sin(distance)*cos(start_lat),
                cos(distance) - sin(start_lat)*sin(end_lat) )
    print dlon
    end_lon = start_lon + dlon

    while end_lon < -1.0*pi:
        end_lon = end_lon + 2.0*pi
    while end_lon >= pi:
        end_lon = end_lon - 2.0*pi

    return(end_lat, end_lon)

###
def test():
    # randomish test
    A = (1.2, 0.5)
    B = (0.6, 1.3)

    (dist, arg) = (geodesicSegment(A, B), geodesicDirection(A, B))

    print A
    print B
    print dist, arg
    print endLatLon( A, dist, arg)

if __name__ == '__main__':
    test()
