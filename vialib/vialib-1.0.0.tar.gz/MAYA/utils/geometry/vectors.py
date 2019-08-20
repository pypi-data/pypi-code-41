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

## this library allows you to transform shapes from one Cartesian
## coordinate frame for to another.

import math
#from MAYA.utils.geometry import areas_centroids
import numpy 
import numpy.oldnumeric.linear_algebra as LinearAlgebra 
import pprint 

# scalar multiplication
def rescale(vector, scale):
    for i in range(len(vector)):
	vector[i] = scale*vector[i]
    return vector

def vecPlus(first, second):
    result = first[:]
    for i in range(len(first)):
	result[i] = first[i]+second[i]
    return result
def vecMinus(first, second):
    result = first[:]
    for i in range(len(first)):
	result[i] = first[i]-second[i]
    return result

def scalarProduct(first, second):
    sum = 0
    for i in range(len(first)):
	sum += first[i]*second[i]
    return sum

def euclideanDistance( first, second ):
    distance = 0
    for i in range(len(first)):
        distance += (first[i] - second[i])**2
    return math.sqrt(distance)

def vectorProduct( first, second ):
    if not len(first) == len(second) == 3:
	raise "Can only compute vector product in 3-space."
    product = [0,0,0]
    product[0] = first[1]*second[2] - first[2]*second[1]
    product[1] = first[2]*second[0] - first[0]*second[2]
    product[2] = first[0]*second[1] - first[1]*second[0]
    return(product)
        
def norm(vector):
    return math.sqrt(scalarProduct(vector, vector))

def normalize(vector):
    length = norm(vector)
    for i in range(len(vector)):
	vector[i] = vector[i]/length
    return None

## a basis will be defined by the new matrix of axes and an "origin shift"
# and a global frame in which all these vectors are defined
class basis:
    def __init__(self, axes, origin=None, frame=None):
        self.dimension = len(axes)
	self.axes = numpy.matrix(axes).astype(numpy.float)
	if origin == None:
	    origin = [0]*self.dimension
        #self.origin = numpy.array(origin).astype(numpy.float)
	self.origin = origin
	
	# if BASEFRAME has been defined, use as default
	if frame==None:
	    try:
		frame=BASEFRAME
	    except:
		pass

        # check that this is a square matrix
        if( (len(self.axes.shape)!=2) or (self.axes.shape[0] != self.axes.shape[1])):
            raise "Can't use this array as basis vectors " + str(axes)
        if( len(axes) != len(origin) ):
	    raise "Can't use the origin " + str(origin) + " with axes " + str(axes)
	self.frame = frame
        self.checkOrthogonal()

	# create affine transformation matrix from this frame to its parent
	pull_matrix = []
	for i in range(self.dimension):
	    row = axes[i]
	    row.append(0)
	    pull_matrix.append(row)
	end_row = origin + [1] 
	pull_matrix.append(end_row)
	self.pull_matrix = numpy.matrix(pull_matrix)
	self.push_matrix = LinearAlgebra.inverse(self.pull_matrix)

    def __getitem__(self, i):
        return self.axes[i]

    def __len__(self):
        return len(self.axes)

    # default "print" behaviour for bases
    def __repr__(self):
        print "Axes:" 
	print self.axes
        print "Origin:", self.origin
        return ""

    def checkOrthogonal(self):
        EPS = 0.001 #small number / margin for error with scalar product test for orthoogonality
	vecs = self.axes.tolist()
        for i in range(len(self.axes)):
            for j in range(i-1):
                if not ( -1*EPS < scalarProduct(vecs[i], vecs[j]) < EPS ):
		    print "Basis is not orthogonal."
		    return(-1)
        return(0)

    def pullTransform(self, vec):
	return affineTransform( vec, self.pull_matrix )
    def pushTransform(self, vec):
	return affineTransform( vec, self.push_matrix )

###
def affineTransform( row_vec, matrix ):
    if type(matrix) != type(numpy.matrix([])):
	raise "Matrix isn't of correct type."
    if len(matrix) != len(row_vec)+1:
	print row_vec
	print matrix
	raise "Vector must be one smaller than matrix for affineTransform."
    row_vec = row_vec + [1] # -higgins eliminated side-effect
    result = numpy.matrix(row_vec)*matrix
    result = result.tolist()[0] # new numpy returns double bracketed list
    result.pop()
    return(result)

## the BASEFRAME is the original xyz-basis
# it is currently a bit fuzzily defined
BASEFRAME = basis([[1,0,0],[0,1,0],[0,0,1]])
BASEFRAME.frame = BASEFRAME

radius_earth = 6378150.0
## coincidentally very nice frame for New Orleans work
LA_FRAME = basis([[1,0,0],[0,0.5,math.sqrt(3)/2],[0,-1*math.sqrt(3)/2,0.5]], origin=[0,-math.sqrt(3)*radius_earth/2, 0.5*radius_earth], frame=BASEFRAME)

###
def radialFrame( anchor_point, frame=BASEFRAME ):
    z_axis = anchor_point[:]
    normalize(z_axis)
    x_axis = vectorProduct([0,0,1], z_axis)
    normalize(x_axis)
    y_axis = vectorProduct(z_axis, x_axis)
    if y_axis[2] < 0:
	y_axis = rescale(y_axis, -1)
    normalize(y_axis)
    return( basis([x_axis, y_axis, z_axis], anchor_point, frame) )

###
def composeBases( source, target ):
    """ Returns a basis object representing the target frame w.r.t. the source frame."""
    if source.frame != target.frame:
	print source, target
	raise "Trying to compose without common parent basis." 
    pull_matrix = target.pull_matrix*source.push_matrix
    return matrix2basis(pull_matrix, source)

###
def chainBases( parent, child ):
    """ Returns the child frame w.r.t. the frame of the parent. """
    if child.frame != parent:
	print child.frame, parent
	raise "Trying to chain without compatible parent basis." 
    pull_matrix = child.pull_matrix*parent.pull_matrix
    return matrix2basis(pull_matrix, parent.frame)

###
def matrix2basis( pull_matrix, source=BASEFRAME ):
    vecs = pull_matrix.tolist()
    axes = []
    for i in range(source.dimension):
	axes.append(vecs[i][:-1])
    origin = vecs[-1][:-1]
    return( basis(axes, origin, frame=source) )

# calculates the distance from a point to a line given by the vectors
# start and end
def pointToLine( point, start, end ):
    if euclideanDistance(start, end) == 0:
        return euclideanDistance( point, start )

    start2point = vecMinus(point, start)
    start2end = vecMinus(end, start)
    normalize(start2end)

    # resolve start2point along the line
    parallel_dist = scalarProduct(start2point, start2end)
    # use pythagoras theorem to work out the perpendicular distance
    perp_dist = scalarProduct(start2point,start2point) - parallel_dist*parallel_dist
    if perp_dist < 0: # no negative distances
        return(0)
    return math.sqrt(perp_dist)

##
def test3():
    office_north_frame = radialFrame([847165.42192783975, -4787698.2247510059, 4114220.4446791997])
    print "Office frame, oriented north."
    print office_north_frame
    angle = degreesToRadians(-45)
    twist_frame = basis([[math.cos(angle), math.sin(angle),0],[-math.sin(angle),math.cos(angle),0],[0,0,1]], frame=office_north_frame)
    global_twist_frame = chainBases(office_north_frame, twist_frame)
    print "Office frame, rotated."
    print global_twist_frame


def degreesToRadians(deg):
    return (deg / 360.0) * 2.0 * math.pi

##
def test2():
    start = [0, 0, 0]
    end = [2*math.pi, 0, 0]
    for x in range(0, 20*math.pi):
        x = x / 10.0
        myvec = [0, math.sin(x), 0]
        print myvec, "Height:", pointToLine( myvec, start, end )

##
def test():
    stretch_basis = basis([[2,0,0],[0,1,0],[0,0,1]], [-10,-10,0], BASEFRAME)
    for i in range(10):
	myvec = [i,3,0]
	print "Vector ", myvec,
	trvec = stretch_basis.pushTransform(myvec)
	print "\tTransforms to", trvec,
	print "\tAnd back to", stretch_basis.pullTransform(trvec)
##
if __name__ == '__main__':
    test()
