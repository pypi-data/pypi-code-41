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
###
# takes the UUID of a u-form and sets the centroid

import math
from MAYA.VIA import repos
from MAYA.VIA import uuid
from MAYA.utils.geometry import areas_centroids, spherical
from MAYA.utils.shepherding import waitForPresence

r = repos.Repository('localhost:6200')
radius_earth = 6378150 # radius of the Earth in meters
#polar_uu = uuid._('~01474e873cb75a11d99f8d70f214a11ca3') # u-form representing polar coordinate system
polar_path_role = uuid._('~01c020c67cc6df11d99bb35a4c36df1d95')

####
## xyShapetoPolar takes a path in x/y style coordinates and returns a polar version
def xyShapeToPolar( path, centroid=None, manifold='sphere', radius=radius_earth, REVERSE=1 ):
    # if it's a u-form get the path data
    if uuid.isa(path ):
        path_data = r.getAttr( path , 'path_data' )
        if not path_data:
            print "Couldn't get point data from", path
            return(-1)
    # if it's a list of points, make a dictionary to look like they came from a path u-form
    # this assumes that your points are [x,y] pairs, if not beware
    # this is a bit ugly since it zips up the points to send them to tne centroid function; they get unzipped later to iterate through them
    elif type(path)==type([]):
        try:
            path_data = {'x':[], 'y':[]}
            for (x, y) in path:
                path_data['x'].append(x)
                path_data['y'].append(y)
        except:
            return(-1)
    else:
        print "Couldn't get point data from", path
        return(-1)

    if not centroid:
        centroid = areas_centroids.centroid( path_data )
        
    print "Centroid: ", centroid

    # zip together lists as latitude then longitude
    points = zip( path_data['x'], path_data['y'] )
    mod = []
    arg = []

    # if necessary, reverse the list
    if REVERSE==1:
        points.reverse()

    # if working on a sphere, use the spherical library
    if manifold == 'sphere':
        centroid = map(spherical.degreesToRadians, centroid)
        centroid = (centroid[1], centroid[0])
        
        for point in points:
            point = map(spherical.degreesToRadians, point)
            point = (point[1], point[0])
            modulus = spherical.geodesicSegment(centroid, point)
            modulus = modulus * radius
            argument = math.pi/2.0 - spherical.geodesicDirection(centroid, point)
            mod.append(modulus)
            arg.append(argument)

    # if working on a plane, use the planar library
    if manifold == 'plane':
        for point in points:
            (distance, bearing) = planar.distanceBearing(centroid, point)
            mod.append(modulus)
            arg.append(argument)

    return [mod, arg]

###
def xyTreeToPolar( curruu, centroid=None, depth=0):
    print "Now at depth", depth
    
    waitForPresence( r, curruu )
    # if this is the very top of the tree, we don't have a centroid yet
    if not centroid:
        xy_path_data = r.getAttr( curruu , 'path_data' )
        centroid = areas_centroids.centroid( xy_path_data )

    child_properties = r.getAttr( curruu, 'child_properties' )
    subshapes = r.getAttr( curruu, 'members' ) or []
    
    if len(subshapes)>0:
        for subshape in subshapes:
            xyTreeToPolar( subshape, centroid, depth+1 )
            
    [mod, arg] = xyShapeToPolar( curruu, centroid, manifold='sphere' )
    # need to change child_properties as well!!!!
    print curruu

#    r.setAttr( curruu, 'path_data', new_path_data )
    r.setAttr(curruu, 'path_data_mod', mod)
    r.setAttr(curruu, 'path_data_arg', arg)
    these_roles = r.getAttr(curruu, 'roles')
    roles.append(polar_path_role)
    r.setAttr(curruu, 'roles', these_roles)
                
#    r.setAttr( curruu, 'coordinate_system', polar_uu )
    return

###
def Test():
    braddock_county_uuid = uuid._('~01e39f0762fc4b11d896317637081a3e36')
#    path_uu = braddock_county_uuid
#    xyShapeToPolar( path_uu )

    greenland_shape = uuid._ ( '~012b9a5e3cb82011d982fb7706759d794c' )
    deer_park_shape = uuid._('~01a7183b28b80b11d982fb2299593f5954')
    xyTreeToPolar( greenland_shape )

if __name__ == "__main__":
    Test()
