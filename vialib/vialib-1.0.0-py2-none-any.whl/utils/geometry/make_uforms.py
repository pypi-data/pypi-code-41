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

from MAYA.VIA import repos, uuid, uform
from MAYA.utils.geometry import vectors, utils, spherical, areas_centroids, geodetic, lengths, simplify, graph, parallel_cuboid, tree
from MAYA.utils.shepherding import waitForPresence
from MAYA.utils import scalablecoll, signing

r = repos.Repository('localhost:6200')
signing.enableSignatureReads(r)

path_role = uuid._('~01e704f9f081f3100a99cf28f420b07250')
geo_trans_role = uuid._('~0182c18d8cd44c11d991834612785d73c0')

seen_uus = {}

class LengthError( RuntimeError ):
    pass
class RoleError( RuntimeError ):
    pass

###
def addRole(r, uu, role):
    current_roles = r.getAttr(uu, 'roles') 
    if current_roles == None:
        r.setAttr(uu, 'roles', [role])
    elif uu not in current_roles:
        current_roles.append(role)
        r.setAttr(uu, 'roles', current_roles)

###
def addLoopsOrLines(r, path_uu, loop_or_line):
    loops_or_lines = [loop_or_line] * len(r.getAttr(path_uu, 'point_lists'))
    r.setAttr(path_uu, 'loops_or_lines', loops_or_lines) 
    cp = r.getAttr(path_uu, 'child_properties') or []
    for (member, data) in cp:
	if data['type'] == 'addition':
	    addLoopsOrLines(r, member, loop_or_line)

##
def removeChildPath( r, parent_uu, child_uu ):
    """Removes a child path from a parent path: from members and child properties.""" 
    mem = r.getAttr( parent_uu, 'members' )
    try:
        mem.remove( child_uu )
    except:
        print "Child path wasn't in parent path."

    cp = r.getAttr( parent_uu, 'child_properties' ) or []
    for child_pair in cp:
        if child_pair[0] == child_uu:
            cp.remove( child_pair )

    if len(mem) != len(cp):
        print "Members and Child Properties don't correspond for", child_uu

    r.setAttr(parent_uu, 'members', mem)
    r.setAttr(parent_uu, 'child_properties', cp)
    
##
def simplifyPathFromMembers(r, path_uu, tolerance=None ):
    """Takes a path and gets its members and puts a simplified shape on the top node.
    Assumes that important things such as reverses have been taken care of"""

    if path_role not in r.getAttr(path_uu, 'roles'):
        raise RoleError("%s doesn't play path role." % (path_uu) )

    try:
        top_frame = utils.getGeoFrame( r, path_uu )
    except:
        top_frame = utils.getGeoFrame( r, r.getAttr(path_uu, 'members')[0] )
    top_points = []
    strand_offset = 0
    subshape_spans = []
    subshape_bounds = []

    properties = r.getAttr( path_uu, 'child_properties' )

    # first pass to work out how many points you have
    point_count = 0
    total_length = 0
    for (member, data) in properties:
        if data['type'] == 'detail':
            points = r.getAttr(member, 'path_points')
            point_count += len(points)
            total_length += lengths.getLength( points )
        
    if tolerance == None:
        tolerance = r.getAttr(path_uu, 'path_epsilon') or (1.5*total_length/point_count) # this is a guess at appropriate tolerance - just the average point density

    # second pass to do the decimation
    for i in range(len(properties)):
        (member, data) = properties[i]
        # get only those members that add detail to the shape
        if data['type'] == 'addition':
            continue
        if r.getAttr(member, 'path_points') == [] or None:
            continue

        new_points = utils.getVectorsFromPath( r, member )
        transformation = vectors.transformer(new_points[0].frame, top_frame)
        mapped_points = map(transformation.transform, new_points)

        # reverse this list if it needs to be included in opposite direction
        if data.has_key('reverse'):
            if( data['reverse'] == 1 ):
                print "Reversing points from", r.getName(member)
                mapped_points.reverse()
        
        if point_count > 100: # this avoids decimating shapes that are too small
            marks = simplify.markBestPoints( mapped_points, tolerance )
            extension = simplify.getChosenPoints(mapped_points, marks)
        else:
            extension = mapped_points
            
        top_points.extend(extension)
     
        strand_offset = strand_offset + len(extension)
        subshape_spans.append( [strand_offset-len(extension), strand_offset] )

        subshape_bounds.append( utils.getBounds(extension) )

    #print top_points
    makePathUForm( r, top_points, path_uu, path_epsilon=tolerance )
    makeHeadAnnotation(r,  path_uu, subshape_spans, subshape_bounds )
    return top_points

###
def addGeoTransform(r, path_uu, frame):
    roles = r.getAttr(path_uu, 'roles')
    if geo_trans_role not in roles:
        roles.append(geo_trans_role)
        r.setAttr(path_uu, 'roles', roles)
    r.setAttr(path_uu, 'origin_translation', frame.origin.tolist())
    r.setAttr(path_uu, 'basis_vectors', frame.axes.tolist())
    return(path_uu)
###
def makeCountryBorderUForm(r, xyz_uu ):
    lat_lon_shape = r.getAttr(xyz_uu, 'source')
    path_vectors = geodetic.latLongPathToVectors(lat_lon_shape)
    r.setAttr(xyz_uu, 'members', None)
    r.setAttr(xyz_uu, 'child_properties', None)
    makePathUForm(r, path_vectors, xyz_uu )
    centralizePath(r, xyz_uu)
    print r.getAttr(xyz_uu, 'name')

###
def test2():
    
    gbcoast = uuid._('~01f579743ed46311d9bf8110a4088a50d6')
    rcoast = uuid._('~019b54be54d92a11d98e191d94345035d6')
    ethborder = uuid._('~01cbf7fa76d92a11d98e19367641642bfa')
    icoast = uuid._('~01870bc6c2d92a11d98e19140669b80273')

    borders = scalablecoll.new(r, uuid._('~012f2f83fafefd11d9afd50e3536c971a6'))
    for border in borders:
        print r.getName(border)
        try:
            makeCountryBorderUform( border )
            r.setAttr(border, 'fused_ends', None)
        except:
            pass
#        makeEvenSubpaths(border, 16, head_epsilon=50000, leaf_length=100)

###
def test():
    country_graph = uuid._('~016350a250d46d11d9956d40d900543a33')

    islands = scalablecoll.new(r, r.getAttr(country_graph, 'singletons'))
    
    alg_shape = uuid._('~01d9e044d6d92a11d98e19529d4f423cc1')
    SC = r.getAttr(r.getAttr(country_graph, 'components')[0], 'shape')
    america = uuid._('~018c013cce09b411da990c05db490555b6')
    australia = uuid._('~018470715ce1b211d9a0750f906a934feb')
    argentina = uuid._('~0183429404e1b211d9a0753fd87d594453')
    canada = uuid._('~018f1a22ece1b211d9a075211c1ffb6813')
    usa = uuid._('~01ae8a7294e1b211d9a0755c9d33271ff6')
    usa48node = uuid._('~016bfd3cdad47011d988b63f803e6f7a48')
    canada_mainland = uuid._('~016c6007f2d47011d988b606081bbf2c86')
    namerica = uuid._('~01c89b1b76295011daa80456387511565d')
    america_shape = uuid._('~01bc12a7b240ec11da86cc50ee169563b5')
                            
    #makeInterveningNodes(r, uuid._('~018573ddc240ec11da86cc33960b97324d'))

    #for island in islands:
    #    makeCountryBorderUForm(r, r.getAttr(island, 'shape'))

    loucopy=uuid._('~01c2d419c083cf100aa5d23592181c2607')
    centralizePath(r, loucopy)

###
if __name__ == '__main__':
    test()

