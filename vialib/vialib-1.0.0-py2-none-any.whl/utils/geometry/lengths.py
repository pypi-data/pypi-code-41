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

## routines to calculate the length (path integral distance) along a path,
# and to split up a path into segments of roughly equal length

from MAYA.VIA import repos, uform, uuid
from MAYA.utils import scalablecoll
from MAYA.utils.geometry import vectors, graph
import math

r = repos.Repository('localhost:6200')
path_role = uuid._('~01ae8e098408ec11dabfc5248a4bb32356')

###
def getLength(points):
    length = 0

    for i in range(len(points)-1):
        current = points[i]
        next = points[i+1]
        length += vectors.euclideanDistance( current, next )

    return length


### naive (n-squared) algorithm to get the diameter of a collection of points,
# i.e. largest pairwise distance between any 2 points
def getDiameter( points ):
    if len(points) > 200:
        new_points = []
        mod = len(points)/200
        for i in range(0, len(points), mod):
            new_points.append(points[i])
        points = new_points

    diameter = 0
    for i in range(len(points)):
	for j in range(i, len(points)):
	    dist = vectors.euclideanDistance(points[i], points[j])
	    if dist > diameter:
		diameter = dist
    return diameter

##
def orderByDiameter( path_uu ):
    members = r.getAttr(path_uu, 'members')
    print members
    members.sort( diameterSort )
    return(members)

##
def diameterSort( uu1, uu2 ):
    return( cmp( r.getAttr(uu2, 'diameter'), r.getAttr(uu1, 'diameter') ) )

###
def getAveDeviation( points, wrap=0 ):
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
def getMaxDeviation( points, wrap=0 ):
    """Gets the average curvature over a list of point. If wrap == 1,
presume that the list is meant to represent a polygon."""
    i = 1-wrap
    precision = 0
    while i < len(points)-1:
        offset = vectors.pointToLine(points[i], points[i-1], points[i+1])
	if offset > precision:
	    precision = offset
	i+=1
    return precision

###
def addLengthFromMembers(r, path_uu):
    subshapes = r.getAttr(path_uu, 'child_properties')
    if subshapes == None:
        print "Couldn't get members to find length of", path_uu
        return
    total_length = 0
    for (subshape, data) in subshapes:
        if data['type'] == 'detail':
            length = r.getAttr(subshape, 'length')
            total_length += length
    r.setAttr(path_uu, 'length', total_length)
    return total_length

###
# this function takes a (recursively created) path and decomposes
# it into a fixed number of segments, each of roughly equal length,
# each made up of a discrete number of members
def evenPathDivideFromMembers(r, path_uu, segment_count):
    total_length = r.getAttr(path_uu, 'length')
    if not total_length:
        total_length = addLengthFromMembers(r, path_uu)

    subshapes = []
    for (member, data) in r.getAttr(path_uu, 'child_properties'):
        if data['type'] == 'detail':
            subshapes.append(member)

    segment_length = total_length / float(segment_count)

    final_segments = []
    current_length = 0
    segment_members = []

    for subshape in subshapes:
        new_length = r.getAttr(subshape, 'length')
        next_length = current_length + new_length
        # if this new border puts our length beyond the threshold 
        if (next_length > segment_length):
            # check if length is nearer to optimal with and without new segment
            if( segment_length - current_length > next_length - segment_length ):
                segment_members.append(subshape)
                final_segments.append( segment_members )
                segment_members = []
                current_length = 0
            else:
                final_segments.append( segment_members )
                segment_members = [subshape]
                current_length = new_length
        # otherwise, just add the new segment and increment the current length
        else:
            segment_members.append(subshape)
            current_length = next_length

    # if we've run out of members, stick the last one on (whatever it is)
    final_segments.append(segment_members)

    while [] in final_segments:
        final_segments.remove([])
        
    return(final_segments)

###
# this function takes a single path and decomposes
# it into a fixed number of segments, each of roughly equal length
# it is based purely on the points in the path, not members or keypoints 
def evenPathDivide(strand, segment_count, total_length=None):
    if total_length==None:
        total_length = getLength( strand )
    
    segment_length = total_length / float(segment_count)

    break_indices = [0] # array indices of points at which the path is split
    current_length = 0
    next_length = 0

    for i in range(len(strand)-1):
        current_point = strand[i]
        new_point = strand[i+1]
        new_length = vectors.euclideanDistance(current_point, new_point)
        next_length = current_length + new_length
        # if this new border puts our length beyond the threshold 
        if (next_length > segment_length):
            # check if length is nearer to optimal with or without new point
            if( segment_length - current_length > next_length - segment_length ):
                break_indices.append(i+1)
                current_length = 0
            else:
                break_indices.append(i)
                current_length = new_length
        # otherwise, just increment the current length and move on
        else:
            current_length = next_length

    # if we've run out of members, stick the last one on (whatever it is)
    break_indices.append(len(strand)-1)
        
    return(break_indices)

##
def thingDiameterSort(th1, th2):
    uu1 = r.getAttr(th1, 'shape')
    uu2 = r.getAttr(th2, 'shape')
    return( cmp( r.getAttr(uu2, 'diameter'), r.getAttr(uu1, 'diameter') ) )

###
def addContinentChainages():
    country_graph = uuid._ ( '~016350a250d46d11d9956d40d900543a33' )
    continents = r.getAttr(country_graph, 'components')
    for continent in continents:
        shape = r.getAttr(continent, 'shape')
        chainage = 0
        for y in r.getAttr(shape, 'members'):
            length = r.getAttr(y, 'length')
            print length, r.getAttr(y, 'name')
            chainage += length
            r.getAttr(y, 'length')
        r.setAttr(shape, 'length', chainage)

###
def test2():
    shapes = scalablecoll.new(r, uuid._('~012f2f83fafefd11d9afd50e3536c971a6'))
    for shape in shapes:
        print getName( shape ), shape
        if r.getAttr(shape, 'diameter') != None:
            continue
        strands = r.getAttr(shape, 'path_points')
        points = flatten( strands )
        diameter = getDiameter( points )
        print diameter
        r.setAttr( shape, 'diameter', diameter )

###
def test():
    #rcoast = uuid._('~019b54be54d92a11d98e191d94345035d6')
    #print evenStrandDivide( r.getAttr( rcoast, 'path_points' )[0], 10 )
    america = uuid._('~018c013cce09b411da990c05db490555b6')
    evenPathDivideFromMembers(r, america, 4)
    
###
if __name__ == '__main__':
    test()
