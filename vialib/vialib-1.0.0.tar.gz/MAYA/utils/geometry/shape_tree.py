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

# This module creates a tree of shapes in memory that can later be output to u-forms
from MAYA.utils.geometry import vectors, utils, lengths, simplify, make_uforms
from MAYA.VIA import repos, uuid, uform
from MAYA.utils import signing

import sys

r = repos.Repository('localhost:6200')
signing.enableSignatureReads(r)

path_role = uuid._('~01e704f9f081f3100a99cf28f420b07250')
geo_trans_role = uuid._('~0182c18d8cd44c11d991834612785d73c0')

my_uus = {}

class shapeNode:

    def __init__(self, point_lists, child_properties=None, parents=None, max_children=50, max_points=2000, frame=vectors.BASEFRAME, frequency=None, precision=None, path_uu=None, refactor=1):
	"""As far as possible, these arguments correspond to attributes in the Compound Path Role. Consult this role for data definitions. Note that the members in child_properties are other shape nodes, not u-forms."""
	self.point_lists = point_lists
	if child_properties:
	    self.child_properties = child_properties
	else:
	    self.child_properties = []
	self.max_children = max_children
	self.max_points = max_points
	self.frame = frame
	if parents:
	    self.parents = parents
	else:
	    self.parents = []

	flat_list = utils.flatten(self.point_lists)
	if frequency == None:
	    frequency = 1 / ( lengths.getDiameter(flat_list) + 1 ) # hack to avoid zero division
	self.frequency = frequency

	if precision == None:
	    max_deviation = 0
	    for point_list in point_lists:
		deviation = lengths.getMaxDeviation(point_list)
		if deviation > max_deviation:
		    max_deviation = deviation 
	    precision = 1 / ( max_deviation + 1 ) # hack to avoid zero division

	self.precision = precision
	self.bounds = utils.getBounds(flat_list)
	self.path_uu = path_uu or uuid.UUID()

	if frame.frame != vectors.BASEFRAME:
	    raise "No known ECEF back transform for this shape."
	else:
	    ecef_points = map(frame.pullTransform, flat_list)
	    self.ecef_bounds = utils.getBounds(ecef_points)
	    self.ecef_anchor = []
	    for interval in self.ecef_bounds:
		self.ecef_anchor.append( (interval[0]+interval[1])/2 )
	    self.ecef_anchor = self.ecef_anchor[:3]

	#print "New node with", len(flat_list), "points." 
	#print "Frequency", self.frequency, "\tPrecision", self.precision

	if refactor == 1:
	    #self.centralize()
	    if len(flat_list) > self.max_points:
		try:
		    self.decimate()
		    print "Node with", len(flat_list), "points", 
		    flat_list = utils.flatten(self.point_lists)
		    print "now has", len(flat_list), "points."
		except:
		    pass

    def addChildNode(self, new_child, detail=0, span=None):
	if self is new_child or new_child in map(lambda x: x[0], self.child_properties):
	    print "WARNING: add same child"
	    return

	def frequencySort( second, first ):
	    return cmp( first[1]['fundamental_frequency'], second[1]['fundamental_frequency'] ) 

	anchor = self.frame.pushTransform(new_child.frame.pullTransform(new_child.ecef_anchor))
	# deal with cases where the node is already full
	if len(self.child_properties) >= self.max_children and detail == 0:
	    # if this shape is less significant than those we already have
	    if self.child_properties[-1][1]['fundamental_frequency'] < new_child.frequency or self.child_properties[-1][1]['type'] == 'detail':
		next_attempt = self.getNearestChild(anchor)
		next_attempt.addChildNode(new_child)
		return
	    # otherwise push down the last shape on the list
	    else:
		little_one = self.child_properties.pop()
		little_one = little_one[0]
		self.addChildNode(new_child)
		self.addChildNode(little_one) # this will now be pushed down

	# if the node has room or the addition is forced, add the child
	else:
	    data = {}
	    data['fundamental_frequency'] = new_child.frequency
	    data['precision'] = new_child.precision
	    data['anchor'] = anchor
	    if detail == 1: 
		data['type'] = 'detail'
		data['span'] = span
	    else: 
		data['type'] = 'addition'

	    trans = vectors.composeBases(new_child.frame, self.frame)
	    data['origin_translation'] = trans.origin.tolist()
	    data['basis_vectors'] = trans.axes.tolist()
	    child_list = utils.flatten(new_child.point_lists)
	    data['bounds'] = utils.getBounds(map(trans.pushTransform, child_list)) 
	    self.child_properties.append([new_child, data])
	    self.child_properties.sort(frequencySort) # could be optimized to avoid new sort
	    new_child.parents.append(self)

    def centralize(self):
	"""Puts a node into a coordinate frame that is "central" to it. Currently this means a frame whose origin is the shape's anchor, whose z-axis is radial, and whose x-y plane is normal to the radial direction."""
	if len(self.child_properties) > 0 or len(self.parents) > 0:
	    print "It's dangerous to change the basis of a node that has children or parents..."
	new_frame = vectors.radialFrame( self.ecef_anchor )
	trans = vectors.composeBases(self.frame, new_frame)
	self.point_lists = utils.recursive_map( trans.pushTransform, self.point_lists, target_level=2 )
	self.frame = new_frame

    def decimate(self, subpath_count=16, leaf_length=200, tolerance=None):
	"""Makes top level paths simpler."""
	num_points = len(utils.flatten(self.point_lists))
	# don't decimate paths with fewer than 2*leaf_length points
	if num_points < 2*leaf_length:
	    return
	if tolerance == None:
	    tolerance = (1/self.precision) * (num_points/500.0) # this is a heuristic, try experimenting
	print "Decimating", num_points, "points, with tolerance", tolerance
	self.precision = 1/tolerance
	if num_points < leaf_length*subpath_count:
	    subpath_count = num_points/leaf_length

	# decimate original shape, put simplified version on top u-form
	for path_no in range(len(self.point_lists)):
	    points = self.point_lists[path_no]
	    marks = simplify.markNBestPoints(points, self.max_points)
	    chosen_indices = marks.keys()
	    chosen_indices.sort()
	    chosen_points = map( lambda x: points[x], chosen_indices )
	    self.point_lists[path_no] = chosen_points

	    # divide the path and make the subshapes
	    # break_indices is an array of indices to breakpoints in chosen_points
	    # this is so that each subshape is in between two points on the chosen simplification
	    break_indices = lengths.evenPathDivide(chosen_points, subpath_count)

	    for i in range(len(break_indices)-1):
		data = {}
		subpath = points[chosen_indices[break_indices[i]]:
				 chosen_indices[break_indices[i+1]]+1]
		if len(subpath) > 1:
		    subnode = shapeNode([subpath], frame=self.frame)
		    self.addChildNode(subnode, detail=1, span=[path_no, [break_indices[i], break_indices[i+1]]])
	

    def mergeNodes(self, other):
	"""The job of this function is to add the points and children from "other" to the self node."""
	if len(other.parents)>0 and other.parents!=[self]:
	    print "Warning - trying to merge in a node that has a separate parent."
	trans = vectors.composeBases(other.frame, self.frame)
	head_offset = len(self.point_lists)
	self.point_lists.extend(utils.recursive_map(trans.pushTransform, other.point_lists, target_level=2))
	for child in other.child_properties:
	    child[0].parents.remove(other)
	    child[0].parents.append(self)
	    if child[1]['type'] == 'detail':
		span = child[1]['span']
		span[0] = span[0] + head_offset
		self.addChildPath(child[0], detail=1, span=span)
	    else:
		self.addChildPath(child[0], detail=0)
	
	# the following code just find outs if "other" is a child, and if so removes it 
	# and fixes child_properties.
	# it looks nasty because we don't want to alter the list while iterating it,
	# and because the list is one of tuples (child, properties), not just of children
	other_index = -1
	for i in range(len(self.child_properties)):
	    if self.child_properties[i][0] == other:
		other_index = i
		
	if other_index != -1:
	    for j in range(other_index, len(self.child_properties)):
		if self.child_properties[j][1].has_key('span'):
		    [a, [b,c]] = self.child_properties[j][1]['span']
		    self.child_properties[j][1]['span'] = [a-1, [b,c]]
	
    def compressTree(self):
	"""Try to find childless children and merge them with their parent nodes."""
	for child in self.child_properties:
	    child[0].compressTree()
	merged = []
	for child in self.child_properties:
	    if child[1]['type'] == 'addition' and \
		    len(utils.flatten(self.point_lists)) + len(utils.flatten(child[0].point_lists)) < self.max_points \
		    and len(self.child_properties) + len(child[0].child_properties) < self.max_children: 
		self.mergeNodes(child[0])
		merged.append(child)
	for child in merged:
	    self.child_properties.remove(child)

    def getNearestChild(self, point):
	near_child = self.child_properties[0][0]
	near_dist = vectors.euclideanDistance(point, self.child_properties[0][1]['anchor'])
	for child in self.child_properties:
	    if vectors.euclideanDistance(point, child[1]['anchor']) < near_dist:
		near_child = child[0]
		near_dist = vectors.euclideanDistance(point, child[1]['anchor'])
	return near_child

    def getChildPointsIndex(self, i, write_bounds=0):
	child = self.child_properties[i][0]
	child_points = child.getAllPoints()
	trans = vectors.composeBases(child.frame, self.frame)
	point_lists = utils.recursive_map(trans.pushTransform, child_points, target_level=2)
	if write_bounds == 1:
	    self.child_properties[i][1]['bounds'] = utils.getBounds(utils.flatten(point_lists))
	return(point_lists)

    def getAllPoints(self, write_bounds=0):
	point_lists = list(self.point_lists)
	for i in range(len(self.child_properties)):
	    point_lists.extend(self.getChildPointsIndex(i, write_bounds))
	if write_bounds == 1:
	    self.bounds = utils.getBounds(utils.flatten(point_lists))
	    self.ecef_bounds = utils.getBounds(map(self.frame.pullTransform, utils.flatten(point_lists))) 
	return(point_lists)

    def writeToUForms(self, r):
	uf = r.getUForm(self.path_uu)
	uf['point_lists'] = self.point_lists
	uf['precision'] = self.precision
	uf['fundamental_frequency'] = self.frequency
	uf['path_bounds'] = self.bounds
	uf['ecef_bbox'] = self.ecef_bounds
	uf['members'] = []
	cp = []
	for child in self.child_properties:
	    cp.append([child[0].path_uu, child[1]])
	    uf['members'].append(child[0].path_uu)
	uf['child_properties'] = cp
	r.setAttr(uf)
	make_uforms.addRole(r, self.path_uu, path_role)
	make_uforms.addGeoTransform(r, self.path_uu, self.frame)
	for child in self.child_properties:
	    child[0].writeToUForms(r)
	return(self.path_uu)

    def printShapeSummary(shape, level=0):
	total_points = len(utils.flatten(shape.point_lists)) # how many points there are in this shape and descendents
	total_polylines = len(shape.point_lists)
	splinched_points = total_points # total points once decimation overlaps have been removed
	indent = '   '*level
	print indent, shape.path_uu.toString(),
	print indent, str(len(shape.child_properties)), 'children', total_polylines, 'head polylines', total_points, 'head points.'
	print map(lambda x: x[1]['type'], shape.child_properties)
	for (shp, data) in shape.child_properties:
	    (child_polylines, child_total, child_splinched) = shp.printShapeSummary(level+1)
	    total_points += child_total
	    splinched_points += child_splinched
	    total_polylines += child_polylines
	    if data['type'] == 'detail':
		splinched_points = splinched_points - data['span'][1][1] + data['span'][1][0] - 1
		total_polylines -= 1

	print indent, total_polylines, "total polylines", total_points, 'descendant points', splinched_points, 'after splinching.'
	return(total_polylines, total_points, splinched_points)

def readShapeFromUForm(r, path_uu):
    print "Reading", path_uu
    path_uf = r.getUForm(path_uu)
    if path_uf.has_key('child_properties'):
	cp = path_uf['child_properties']
    frame = utils.getGeoFrame(r, path_uu)
    path_node = shapeNode(path_uf['point_lists'], child_properties=cp, frequency=path_uf['fundamental_frequency'], precision=path_uf['precision'], path_uu=path_uu, frame=frame, refactor=0)
    for i in range(len(cp)):
	cp[i][0] = readShapeFromUForm(r, cp[i][0]) # replace member UUID with member node
    return(path_node)

def testImport():
    lshuu = uuid._('~019b8095fc831f11daba8769a83e850075')
    loupts = r.getAttr(lshuu, 'point_lists')
    head_frame = utils.getGeoFrame(r, lshuu)
    head_points = [loupts[0]]
    head_node = shapeNode(head_points, frame=head_frame)
    for new_points in loupts[1:]:
	new_node = shapeNode([new_points], frame=head_frame)
	head_node.addChildNode(new_node)
    head_node.compressTree()
    print head_node.writeToUForms(r)

if __name__ == '__main__':
    la_shape = uuid._('~011593a7c2214711da8cc10350131644d9')
    la_node = readShapeFromUForm(r, la_shape)
    walkShape(la_node)
    #la_node.getAllPoints()
    #la_node.writeToUForms(r)
