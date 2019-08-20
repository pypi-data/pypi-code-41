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

# this module implements functions to perform Douglas-Peucker
# decomposition on a line segment (expressed in 3-d vectors)

from MAYA.VIA import uuid, repos, uform
from MAYA.utils import signing
from MAYA.utils.geometry import vectors

r = repos.Repository('localhost:6200')
signing.enableSignatureReads(r)
path_role = uuid._('~01e704f9f081f3100a99cf28f420b07250')

class RoleError(RuntimeError):
    pass

##
def getFarPoint( points, start=0, end=-1 ):
    """find point in point list segment furthest from line between endpoints."""
    max_dist = 0
    max_index = None
    # go through and 
    for i in range(start+1,end):
        dist = vectors.pointToLine( points[i], points[start], points[end] )
        if dist > max_dist:
            max_dist = dist
            max_index = i
    return(max_index, max_dist)

## function simplify takes a polyline segment and performs DP simplification
def markBestPoints( points, tolerance, j=0, k=-1, marks={} ):
    # some initialization and checking
    if k == -1:
        k = len(points)-1  
    if j >= k:
        print "Endpoint is before or the same as startpoint."
        return marks

    if marks == {}:
        marks = {j:1, k:1}

    (max_index, max_dist) = getFarPoint( points, j, k )

    # if the biggest distance is greater than the tolerance, mark it accordingly and descend recursively
    if max_dist > tolerance:
        marks[max_index] = 1
        # descend for segment up to i
        marks = markBestPoints( points, tolerance, j, max_index, marks )
        # descend for segment after i
        marks = markBestPoints( points, tolerance, max_index, k, marks )

    return marks

##
def markNBestPoints( points, target ):

    class segment:
	def __init__(self, start, end):
	    self.start = start
	    self.end = end
	    (self.max_index, self.max_dist) = getFarPoint(points, start, end)
	    self.previous = None
	    self.next = None

	def addToLinkedList(self, top):
	    if self.max_dist > top.max_dist:
		self.next = top
		top = self
		return(top)

	    current = top
	    while self.max_dist < current.max_dist:
		if current.next == None:
		    current.next = self
		    self.previous = current
		    return(top)
		current = current.next
	    if current.next != None:
		self.next = current.next
		self.next.previous = self
	    current.next = self
	    self.previous = current
	    return(top)

	def removeFromLinkedList(self, top):
	    if self == top:
		top = self.next
		return(top)
	    self.previous.next = self.next or None
	    self.next.previous = self.previous or None
	    return(top)

    total_segments = 0
    marks = {0:1, len(points)-1:1}
    first_pass = segment(0, len(points)-1)
    top = first_pass
    while total_segments < target:
	marks[top.max_index] = 1
	first_segment = segment(top.start, top.max_index)
	second_segment = segment(top.max_index, top.end)
	top = top.next or top
	top = first_segment.addToLinkedList(top)
	top = second_segment.addToLinkedList(top)
	total_segments += 1
    return(marks)

## take a list of points and a dictionary of "marked" points
# return marked points
def getChosenPoints( points, marks ):
    chosen_list = []
    for i in range(len(points)):
        if marks.has_key(i):
            chosen_list.append(points[i])
    return chosen_list

## get points marked just with a 1
def getPointsMarkedN( points, marks, n ):
    chosen_list = []
    for i in range(len(points)):
        if marks.get(i) == 1:
            chosen_list.append(points[i])
    return chosen_list

##
def cylinderProjectionDecimate( points, tolerance ):
    marks = {0:1, len(points)-1:1} 
    current_anchor = 0 # index of current origin
    average_ray = [0]*len(points[0])  # average place of points so far from origin

    for i in range(len(points)-1):
	displaced_average = vectors.vecPlus(points[current_anchor], average_ray)

	if vectors.pointToLine( points[i], points[current_anchor], displaced_average) > tolerance:
	    marks[current_anchor] = 1
	    marks[i] = 1
	    average_ray = [0]*len(points[0])

	    # check for an escapee (this sometimes happens)
	    max_delta = 0
	    for j in range(current_anchor, i):
		this_delta = vectors.pointToLine( points[j], points[current_anchor], points[i])
		if this_delta > max_delta:
		    max_delta = this_delta 
		    max_offset_index = j
	    if max_delta > tolerance:
		marks[max_offset_index] = 1
		# check for missed escapees
		TEST = 1
		if TEST:
		    for j in range(current_anchor, max_offset_index):
			if vectors.pointToLine( points[j], points[current_anchor], points[max_offset_index]) > tolerance:
			    print "Found missed escapee."
			    marks[j] = 3
		    for j in range(max_offset_index, i):
			if vectors.pointToLine( points[j], points[i], points[max_offset_index]) > tolerance:
			    print "Found missed escapee."
			    marks[j] = 3
	    current_anchor = i


	# update average
	else:
	    displacement = vectors.vecMinus(points[i], points[current_anchor])
	    average_ray = vectors.vecPlus(average_ray, displacement) # effectively, points[current_anchor] is segment origin
    return marks


## take a list of points and do a linear time simplification
# this function currently only works in 2 dimensions, for 3d expt see
# cylinderProjectionDecimate
def cylinderDecimate( points, tolerance, marks={} ):

    # y intercept tells whether, in plane of first 2 coords, line between
    # point 1 and 2 is above y coord of point 0
    def y_int(pt0, pt01, pt02):
	pt01 = [pt01[0]-pt0[0], pt01[1]-pt0[1]] 
	pt02 = [pt02[0]-pt0[0], pt02[1]-pt0[1]] 
	try:
	    slope = (pt02[1]-pt01[1]) / (pt02[0]-pt01[0])
	except:
	    return 0
	y_int = pt01[1] - slope*pt01[0]
	return(y_int) 

    # if marks are passed in, it implies that some points should always be added
    if marks == {}:
	# use 1 for anchor points, 2 for edge-cutting points
	marks = {0:1, len(points)-1:1} 
    current_anchor = 0
    hi_bound = lo_bound = None
    
    for i in range(len(points)-1):
	if marks.has_key(i):
	    current_anchor = i
	    hi_bound = None
	    lo_bound = None
	    continue
	    
	# check to see if we're far enough away to bother
	if vectors.euclideanDistance(points[current_anchor], points[i]) < tolerance:
	    continue
	else:
	    if hi_bound == None: hi_bound = i
	    if lo_bound == None: lo_bound = i 

	# check to see if we've broken the bounds
	if vectors.pointToLine( points[lo_bound], points[current_anchor], points[i]) > tolerance:
	    marks[lo_bound] = 2
	    marks[current_anchor] = 1
	    current_anchor = i
	    hi_bound = None
	    lo_bound = None
	    continue

	if vectors.pointToLine( points[hi_bound], points[current_anchor], points[i]) > tolerance:
	    marks[hi_bound] = 2
	    marks[current_anchor] = 1
	    current_anchor = i
	    lo_bound = None
	    hi_bound = None
	    continue

	# check to see if this point should be a new lo_bound or hi_bound
	intercept_point = y_int( points[current_anchor], points[lo_bound], points[i] )
	if lo_bound and intercept_point<0:
	    if vectors.pointToLine( points[current_anchor], points[lo_bound], points[i]) < tolerance: 
		lo_bound = i
	if hi_bound and intercept_point>0:
	    if vectors.pointToLine( points[current_anchor], points[hi_bound], points[i]) < tolerance: 
		hi_bound = i

    return marks

##
def test2(): 
    import time
    rcoast = uuid._('~019b54be54d92a11d98e191d94345035d6')
    points = r.getAttr(rcoast, 'path_points')    
    t = time.time()
    #marks = markBestPoints( points, 150000 )
    marks = cylinderDecimate( points, tolerance=150000 )
    #marks = cylinderProjectionDecimate( points, tolerance=150000 )
    print "Time:", time.time() - t
    chosen_points = getChosenPoints(points, marks)
    control_points = getPointsMarkedN(points, marks, 1)
    escaped_points = getPointsMarkedN(points, marks, 3)
    print escaped_points
    print "Before:", len(points), "After:", len(chosen_points)
    return(([points, chosen_points]), escaped_points)

##
def test():
    rcoast = uuid._('~019b54be54d92a11d98e191d94345035d6')
    cgraph=uuid._('~016350a250d46d11d9956d40d900543a33')
    SuperCShape = r.getAttr(r.getAttr(cgraph, 'components')[0], 'shape')
    for member in r.getAttr(SuperCShape, 'members'):
       simplifyPath(member, tolerance=50000)
    simplifyPath(SuperCShape, tolerance=300000)
    
##
if __name__ == '__main__':
    test2()
