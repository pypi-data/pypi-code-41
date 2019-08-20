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

# basic utilities that involve dealing with lists of points

from MAYA.VIA import repos, uuid, uform
from MAYA.utils.geometry import vectors, geodetic, spherical
from Numeric import *
from LinearAlgebra import inverse
import types

r = repos.Repository('localhost:6200')
from MAYA.utils import signing
signing.enableSignatureReads(r)

path_role = uuid._('~01e704f9f081f3100a99cf28f420b07250')
geo_trans_role = uuid._('~0182c18d8cd44c11d991834612785d73c0')

###
def removeDuplicates(r, uu, attr):
    members = r.getAttr(uu, attr)
    new_members = []
    for member in members:
        if member not in new_members:
            new_members.append(member)
    r.setAttr(uu, attr, new_members)

### naive function to take two (small) lists
# and return 1 if they're the same set and 0 if not
def testSetEquality( list1, list2 ):
    if not type(list1) == type(list2) == type([]):
        return(-1)
    try:
        for x in list1:
            list2.remove(x)
    except:
        return 0
    if len(list2) > 0:
        return 0
    return 1

###
def simpleSetIntersect( list1, list2 ):
    """Returns a list of elements common to both lists. Ignores order of inputs lists and removes multiplicity."""
    list1dict = {}
    for item in list1:
        list1dict[item] = 1

    intersection = {}
    for item in list2:
        if list1dict.has_key(item):
            intersection[item] = 1
    return intersection.keys()

###
def flatten( lists ):
    flat_list = []
    for list in lists:
        flat_list.extend(list)
    return flat_list

###
def recursive_map(f, ys, target_level=-1, level=0):
    t = type(ys)
    if target_level == level:
	return f(ys)
    elif t is types.ListType or t is types.TupleType:
	return map(lambda x: recursive_map(f, x, target_level, level+1), ys)
    else:
	return f(ys)

##
def getVectorsFromPath( r, path_uu ):
    if path_role not in r.getAttr(path_uu, 'roles'):
        print path_uu, "doesn't play the correct path role."
    point_lists = r.getAttr( path_uu, 'point_lists' )
    frame = getGeoFrame( r, path_uu )
    return(recursive_map(lambda x: vectors.vector(x, frame), point_lists, target_level=2))


## strip the coordinates out of a list of vector objects (normally to serialize them)
def getCoords( vector_list ):
    return map( lambda x: x.coords.tolist(), vector_list )

### get the min and max for each coordinate in a collection of strands
def getBounds(strand):
    bounds = []
    dim = len(strand[0])
    
    # initialize bounds array to coords of first point
    for coord in strand[0]:
        bounds.append([coord, coord])

    # iterate through each point in each polyline finding min and max
    for point in strand:
        for i in range(dim):
            # if smaller than min, found new min
            if point[i] < bounds[i][0]:
                bounds[i][0] = point[i]
                #print "New min:", point[i]
            # if bigger than max, found new max                    
            if point[i] > bounds[i][1]:
                #print "\t\tNew max:", point[i]
                bounds[i][1] = point[i]            
    return(bounds)

###
def estimatePrecision( points, wrap=0 ):
    """Gets the average curvature over a list of point. If wrap == 1,
presume that the list is meant to represent a polygon."""
    i = 1-wrap
    precision = 0
    while i < len(points)-1:
        precision += vectors.pointToLine(points[i], points[i-1], points[i+1])
        i+=1
    precision = precision / len(points)+wrap
    return precision

###
def reconstructPolygon( r, path_uu ):
    path_uf = r.getUForm(path_uu)
    parent_frame = getGeoFrame(path_uu)

    child_points = []

    for (member, data) in path_uf['child_properties']:
        # get only those members that add detail to the shape
        if data['type'] == 'addition':
            continue

        new_points = getVectorsFromPath( r, member )
        transformation = vectors.transformer(new_points[0].frame, parent_frame)
        mapped_points = map(transformation.transform, new_points)

        # reverse this list if it needs to be included in opposite direction
        if data.has_key('reverse'):
            if( data['reverse'] == 1 ):
                print "Reversing points from", r.getName(member)
                mapped_points.reverse()

        child_points.extend(mapped_points)

    return(child_points)

###
def mapBoundsToLatLong( r, path_uu ):
    bounds = r.getAttr(path_uu, 'path_bounds')
    frame = getGeoFrame( r, path_uu )

    llpoints = []
    midbounds = []
    for bound in bounds:
        midbounds.append([bound[0], (bound[0]+bound[1])/2.0, bound[1]])

    for x in midbounds[0]:
        for y in midbounds[1]:
            for z in midbounds[2]:
                ecef_point = frame.pullTransform(local_vector)
                llpoints.append(geodetic.cartesianToGeodetic(ecef_point))

    bounds = getBounds(llpoints)
    R2D = spherical.radiansToDegrees
    llbounds = [[R2D(bounds[0][1]), R2D(bounds[1][0])], [R2D(bounds[0][0]), R2D(bounds[1][1])]]
    print llbounds

##
def getGeoFrame( r, trans_uu ):
    #print "Getting geo_frame from:", trans_uu
    if geo_trans_role not in (r.getAttr(trans_uu, 'roles') or []):
	print "roles are:", r.getAttr(trans_uu, 'roles')
	print r.listAttr(trans_uu)
        raise RuntimeError( trans_uu, "doesn't play the role for geo-transformation." )
    axes = r.getAttr(trans_uu, 'basis_vectors')
    origin = r.getAttr(trans_uu,'origin_translation')
    frame = vectors.basis(axes, origin, vectors.BASEFRAME)
    return(frame)

##
def test():
    hawaii_bit = uuid._('~012daf84b0216e11dab0166dc164576fda')
    la_bit = uuid._('~0141e533a6214811daa2811eb1011c24b8')

    usa = uuid._('~01bdfdee5a786311d79a4651bb76677012')
    la = uuid._('~017b120da0f9b011d79d27538a0ca65c9f')
    mi = uuid._('~017bd73260f9b011d79d2701bf359d291e')
    al = uuid._('~01774c5310f9b011d79d2629ce41161138')
    tx = uuid._('~017e0053f0f9b011d79d2718b70fc351bd')

##
if __name__ == "__main__":
    test()
