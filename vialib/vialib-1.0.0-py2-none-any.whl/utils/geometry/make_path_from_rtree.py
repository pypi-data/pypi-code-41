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

"""This module is designed to create a recursuve shape from an r-tree
index. The motivation is that the explicit shape representation needs
a good way of organizing drill-down, and an r-tree does preciely this anyway."""

from MAYA.VIA import repos, uuid, uform
from MAYA.utils.geometry import utils, make_uforms
from MAYA.utils import scalablecoll, signing
from MAYA.utils.indexing.spatial.rtree_builder import *


r = repos.Repository('localhost:6200')
signing.enableSignatureReads(r)

###
class RTreeNodeShape:
    def __init__(self, uu, parent, shape=None):
        self.uu = uu
        self.parent = parent
        self.type = r.getAttr( uu, 'type' )

        # if internal node, recurse down
        if self.type == 'internal node':
            self.children = []
            for child_data in r.getAttr(uu, 'children'):
                self.children.append( RTreeNodeShape( child_data[0], self ) ) 

        # create shape from index entries
        self.shape = makeShapeFromNode( r, self )

###
def makeRTreeFromThings( r, dataset_uu ):
    mem=scalablecoll.new(r, dataset_uu)

    name = "Index of " + r.getAttr(dataset_uu, 'name')

    # the following line instantiates Rtreebuilder object with dimensions=2
    myRt=Rtreebuilder(r,2,add_priority=1)
    print 'index builder initialized'
    count=0
    print 'starting to insert into local file'
    print 'This might take a while ...'
    for item in mem:
        waitForPresence(r,item,TIMEOUTSECS)
        shape = r.getAttr(item, 'shape')
	waitForPresence(r,shape,TIMEOUTSECS)
	frequency = r.getAttr(shape, 'fundamental_frequency')
	key = r.getAttr(shape, 'ecef_bbox')
	min = []
	max = []
	for pair in key:
	    min.append(pair[0])
	    max.append(pair[1])
	key = [min, max]

        #The next line inserts the tuple containing the uuid,bbox and the priority value( the mean value of 0.5)
        myRt.insert([item,key,frequency]) 
        count+=1 #keep track of the number of inserts needed later for makeIndex
    root=myRt.makeIndex(count,25,25) #creates index uforms and returns the root

    header=myRt.genHeader(root, dataset_uu, ['shape.fundamental_frequency', 'shape.ecef_bbox'], name=name) # creates the Header UUID
    myRt.delDbFile() # deletes the default 'tempbtree.btdb' file
    return header

###
def readRTree( r, root_uu ):
    #root_uu = r.getAttr( head, 'rtree_root' )
    root_node = RTreeNodeShape( root_uu, None )
    return(root_node)

##
def makePathFromDataset( r, dataset_head ):
    index_uu = makeRTreeFromThings( r, dataset_head )
    r.setAttr( dataset_head, 'other_indexes', index_uu )
    root_node = readRTree(r, index_uu)
    path_uu = makeShapeFromNode(r, root_node)
    return(path_uu)

###
def makeShapeFromNode(r, node):
    member_shapes = []
    shape = uuid.UUID()

    if node.type == 'internal node':
        for child in node.children:
            if not child.shape:
                # if child of internal node has no shape, descend recursively
                child.shape = makeShapeFromNode(r, child)
            member_shapes.append(child.shape)

    elif node.type == 'leaf':
        # go through child nodes and gather their shape uuids
        for index_entry in r.getAttr( node.uu, 'children'):
            child = index_entry[0]
            child_shape = r.getAttr(child, 'shape')
            if child_shape == None:
                print "This leaf node doesn't have a shape attached:", child
            else:
                print "Gathering shape", child_shape
                member_shapes.append(child_shape)
    
    r.setAttr(shape, 'members', member_shapes)
    print "Making new internal node shape ..."
    make_uforms.makePathFromIslands(r, shape)
    node.shape = shape
    return shape

def setPolygons(r, shape):
    r.setAttr(shape, 'is_line', 0)
    for (member, data) in r.getAttr(shape, 'child_properties') or []:
        if data['type'] == 'addition':
            setPolygons(r, member)

###
def test():
    node = uuid._('~012caf8d66249c11da8e2a3f9119dd6ea3')
    #world_islands = uuid._('~016371e942d46d11d9956d30bf2c3f7449')
    #world_land_shapes = uuid._ ('~01fe2dd5a6584611da8dab5a41301935a8')
    #print makePathFromDataset(r, world_land_shapes)
    #island_index = uuid._('~01a4dc2bb4530b11da8ffb565e2c350bc8')
    #land_shapes_index = uuid._('~0114b4d7ea584a11daad7d703379652902')
    #print "Reading r-tree."
    #root_node = readRTree(r, land_shapes_index)
    #path_uu = makeShapeFromNode(r, root_node)
    #print path_uu

    #shape = uuid._('~0144658328587611dabf8719386a8b7821')
    #setPolygons(r, shape)
    
    la = uuid._('~017b120da0f9b011d79d27538a0ca65c9f')    
    print makeRTreeFromThings(r, la)

if __name__ == '__main__':
    test()
