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

from MAYA.VIA import uuid, uform, repos
from MAYA.utils.geometry import vectors, utils, make_uforms, geodetic, spherical, make_path_from_rtree, esri_parser, dbf, shape_tree
from MAYA.utils.shepherding import waitForPresence
from MAYA.utils import scalablecoll, signing
from MAYA.utils.indexing.spatial.rtree_builder import *

TIMEOUTSECS=10

r = repos.Repository('localhost:6200')
signing.enableSignatureReads(r) 

collection_role = uuid._('~fd000a02510bfd17204424')
geophysical_role = uuid._('~fd000a02510bfd8a0d250b')

###
def makeGeoRef( thing_uu, latLongPoints ):
    """Add the geo-extents attributes to something with a shape so that the thing can be indexed."""
    shape = r.getAttr( thing_uu, 'shape' )
    if shape == None:
        return
    print "makeGeoRef: Adding georeference to", r.getAttr(thing_uu, 'name') or thing_uu
    bounds = utils.getBounds(latLongPoints)
    bbox = [[bounds[0][0],bounds[1][0]], [bounds[0][1],bounds[1][1]]]
    r.setAttr( thing_uu, 'geo_extents', bbox )
    r.setAttr( thing_uu, 'latitude', bound[0][0]+bounds[0][1]/2)
    r.setAttr( thing_uu, 'longitude', bound[1][0]+bounds[1][1]/2)

###
def llmap(point):
    (lon, lat) = map(spherical.degreesToRadians, point)
    vec = geodetic.geodeticToCartesian(lat, lon)
    return(vec)

###
def makeCompoundPathFromESRI(r, esri_objects, path_uu=None, baseline=0):

    point_count = 0
    point_lists = []
    for esri_object in esri_objects:
	for part in esri_object.parts:
	    points = map(llmap, part) 
	    point_lists.append(points)
	    point_count += len(points)

    point_lists.sort(lengthSort)

    # a baseline import will put all of the path points into a single compound u-form
    if baseline==1:
	head_node = shape_tree.shapeNode(point_lists, path_uu=path_uu, refactor=0)
    else:
	head_points = [point_lists[0]]
	# don't centralize for now
	head_node = shape_tree.shapeNode(head_points, path_uu=path_uu)
	for new_points in point_lists[1:]:
	    new_node = shape_tree.shapeNode([new_points])
	    head_node.addChildNode(new_node)
	print "Now compressing tree and merging nodes ..."
	head_node.compressTree()
	head_node.getAllPoints(write_bounds=1)

    #print len(esri_objects), "ESRI objects.", len(point_lists), "polylines", point_count, "points." 
    print "Writing out", head_node.path_uu, "and descendents."
    return head_node.writeToUForms(r)

###
def makeDatasetFromESRI( r, esri_shp, esri_dbf=None, read_header=1 ):

    def correlate_dbf_data(shapes, dbf_fn):
	dbf_reader = dbf.DBF(dbf_fn)
	records = dbf_reader.open()

	i = 0
	for shp in shapes:
	    shp.dbf_record = records[i]
	    i += 1
	return

    #print "Raw ESRI data:", esri_shp 
    shapes = esri_parser.esri_to_shapes(esri_shp, read_header)

    if esri_dbf:
	correlate_dbf_data(shapes, esri_dbf)

    for shape in shapes:
	if shape.parts == []:
	    shapes.remove(shape)

    phenomena = scalablecoll.new(r)
    print phenomena.head

    for shape in shapes:
	## remember to add the right roles and class information to these u-forms
	thing = uform.UForm()
	if esri_dbf:
	    for key in shape.dbf_record.keys():
		value = shape.dbf_record[key]
		#if key[-1] == '\xf8': # this was for gnonkw
		#    key = key[:-1]
		#    attr = 'gnonkw_' + key.lower()
		thing[attr] = value
	thing['geo_extents'] = [[shape.bb[1],shape.bb[3]], [shape.bb[0], shape.bb[2]]]
	thing['latitude'] = (shape.bb[1]+shape.bb[3])/2
	thing['longitude'] = (shape.bb[0]+shape.bb[2])/2
	shape_uu = makeCompoundPathFromESRI(r, [shape])
	thing['shape'] = shape_uu
	#if thing.has_key('gnonkw_name'):
	#    thing['name'] = thing['gnonkw_name']
	r.setAttr(thing)
	phenomena.append(thing.uuid)

    return phenomena.head
##
def lengthSort(list1, list2):
    return cmp(len(list2), len(list1))

def Test():
    """
    orleans = uuid._('~0112667d70f9c111d7a00f7d3f12126806')
    oshuu = uuid._('~0119e27b00838311daba87173e78c2750d')
    osh = r.getAttr(orleans, 'shape_data')
    louisiana = uuid._('~017b120da0f9b011d79d27538a0ca65c9f')
    lou = r.getAttr(louisiana, 'shape_data')
    lshuu = uuid._('~019b8095fc831f11daba8769a83e850075')
    loucopy=uuid._('~01c2d419c083cf100aa5d23592181c2607')
    #makeCompoundPathFromESRI(r, lou, lshuu)
    #makeCompoundPathFromESRI(r, osh, oshuu)    
    #make_uforms.removeChildPath(r, lshuu, oshuu)
    #make_uforms.addChildPath(r, lshuu, oshuu)
    """
    #world_shapes = scalablecoll.new(r, uuid._('~016350a250d46d11d9956d40d900543a33'))
    #usa = uuid._('~01bdfdee5a786311d79a4651bb76677012')
    #la = uuid._('~017b120da0f9b011d79d27538a0ca65c9f')

    #esri_objects = []

    #for node in world_shapes:
	#source = r.getAttr(node, 'source')
	#esri_data = r.getAttr(source, 'shape_data')
	#esri_objects.extend(esri_parser.esri_to_shapes(esri_data))
    #print "Making shape:", makeCompoundPathFromESRI(r, esri_objects)#, shape)

    flpanther = uuid._('~01c1ff6d302b5011d88b98408a64196f76')
    esri_data = r.getAttr(flpanther, 'data')
    esri_objects = esri_parser.esri_to_shapes(esri_data)
    print makeDatasetFromESRI(r, esri_data)

    """	
    for part in r.getAttr(usa, 'members'):
	print r.getAttr(part, 'name')
	if r.getAttr(part, 'name') == 'Alaska':
	    continue
	if part == la:
	    continue
	shape = r.getAttr(part, 'shape')
	r.setAttr(shape, 'name', 'Shape of ' + r.getAttr(part, 'name'))
	print r.getAttr(part, 'name')
	esri_data = r.getAttr(part, 'shape_data')
	esri_objects = esri_parser.esri_to_shapes(esri_data)
	print "Making shape:", makeCompoundPathFromESRI(r, esri_objects, shape)
"""
##
if __name__ == '__main__':
    Test()
