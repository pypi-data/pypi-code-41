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

# the compound_shapes module exists to collection together shapes from a
# multitude of parts or "members", that may themselves have members, etc.

import re
from math import *
from MAYA.VIA import repos, uuid, uform
from MAYA.utils import scalablecoll 
from MAYA.utils.shepherding import waitForPresence
from MAYA.utils.geometry import vectors, spherical, areas_centroids, geodetic, make_uforms, chainages, graph
from Numeric import *
from LinearAlgebra import inverse

xyz_path_role = uuid._('~01bc650844d3b011d99de5500e1b263dc5')
geo_trans_role = uuid._('~0182c18d8cd44c11d991834612785d73c0')

r = repos.Repository('localhost:6200')

ID_transform = vectors.transformer(vectors.BASEFRAME, vectors.BASEFRAME)

class TopologyError(RuntimeError):
    pass

def getName( uu ):
    return r.getAttr( uu, 'name' )

## this function takes a collection, all expressed w.r.t some
# transformation from a BASEFRAME.
# It produces a path that contains the other shapes as 'members', possibly recursively
def makeCompoundShape( collection ):
    pass

###
def makeHeadAnnotation( r, path_uu ):
    try:
        path_uf = r.getUForm( path_uu )
    except:
        print path_uu, "doesn't exist in this venue."
        return(-1)

    if not path_uf.has_key('members'):
        return

    head_shape = path_uf['members'][0]
    path_frame = make_uforms.getGeoFrame(r, head_shape)
    
    make_uforms.addGeoTransform(r, path_uf, path_frame)

    # work out transformations to each member shape
    #if not path_uf.has_key('child_properties'):
    path_uf['child_properties'] = [None]*len(path_uf['members'])
    for i in range(len(path_uf['members'])):
        member = path_uf['members'][i]
        member_frame = make_uforms.getGeoFrame(r, member)
        transformation = vectors.transformer(path_frame, member_frame)
        data = uform.EForm()
        data['origin_translation'] = transformation.origin.tolist()
        data['basis_vectors'] = transformation.axes.tolist()
        member_points = reconstruct(r, path_uu, member_index=i, recurse_depth=1)
        data['bounds'] = make_uforms.getBounds( member_points )
        
        path_uf['child_properties'][i] = ((member, data))
        
    r.setAttr(path_uf)
    return

###
# many shapes are composed of smaller shapes; this function allows the
# endpoints of the smaller shapes to appear as keypoints on the
# composed shape.
# This enables decimation to preserve the endpoints of member shapes
def addKeypointsFromMembers( r, path_uu ):
    members = r.getAttr( path_uu, 'members')
    if members == None:
        print path_uu, r.getAttr(path_uu, 'name'), "has no members."
        r.setAttr(path_uu, 'path_keypoints', r.getAttr(path_uu, 'endpoints'))
        return
    properties = r.getAttr( path_uu, 'child_properties' )
    keypoints = [] # this will hold a list of endpoints around the shape
        
    for i in range(len(members)-1):
        # check to see whether the member path needs to be reversed
        reverse = 0
        if properties[i][1].has_key('reverse'):
            if properties[i][1]['reverse'] == 1:
                reverse = 1
                
        endpoints = r.getAttr( members[i], 'endpoints' )
        if reverse == 1:
            endpoints.reverse()

        print getName(endpoints[0]), getName(endpoints[1])

        # if this is the fist member, put both endpoints onto keypoints
        if i==0:
            keypoints.extend(endpoints)
        else:
            # check that the chain is proceeding consistently
            if keypoints[-1] != endpoints[0]:
                if keypoints[-1] == endpoints[1]:
                    endpoints.reverse()
                    r.setAttr(member, 'endpoints', endpoints)
                    print "Swapped endpoints for", getName(member)
                else:
                    raise TopologyError("Inconsistent endpoint chain for %s at member %d." % (str(path_uu), i))
            # if we've got this far we know the keypoints are correct
            keypoints.append(endpoints[1])

    r.setAttr(path_uu, 'path_keypoints', keypoints)
    r.setAttr(path_uu, 'endpoints', [keypoints[0], keypoints[-1]])
    return(keypoints)
        

###
# this function takes a path with many members and breaks it into a
# 2-level decomposition. The number of members on the top u-form is given.
def makePathRecursive(r, path_uu, top_member_count):
    segments = lengths.evenPathDivide(r, path_uu, top_member_count)
    segment_uus = []
    for segment in segments:
        # if there is only one u-form in the segment, it doesn't need a new u-form
        if len(segment) == 1:
            endpoints = r.getAttr(segment[0], 'endpoints')
            segment_uus.append(segment[0])
        else:
            endpoints = (graph.getEndpoint(r, [segment[0],segment[1]]), graph.getEndpoint(r, [segment[-1],segment[-2]]))
            # use the frame of the (roughly) middle bit of the segment for now
            frame = getLocalBasis( r, segment[len(segment)/2] )
            segment_uf = uform.UForm()
            segment_uf['roles'] = [xyz_path_role]
            segment_uf['members'] = segment
            segment_uf['path_features'] = endpoints
            make_uforms.addGeoTransform(r, segment_uf, frame)
            r.setAttr(segment_uf)
            makeHeadAnnotation(r, segment_uf.uuid)
            segment_uus.append(segment_uf.uuid)
    r.setAttr(path_uu, 'members', segment_uus)
    r.setAttr(path_uu, 'child_properties', None)
    makeHeadAnnotation( r, path_uu )
    return

## this takes a collection of shapes and works out their combined
## areas and centroids
## it was never finished
def getCentroidOfCollection( path_uus ):
    for path_uu in path_uus:
        waitForPresence( path_uu )
        path_uf = r.getUForm( path_uu )
        if not path_uf.has_key('roles'):
            print path_uu, "has no 'roles' attribute."
            return(-1)
    else:
            lat_lon_points = get_geodetic_coords( path_uf )

## given a top level shape, find its members and paste them together
## in the frame of the top-level shape
# this needs to be made more architectural for detail shapes, new shapes, recursion, etc.
def reconstruct( r, path_uu, head_uu=None, parent_frame=vectors.BASEFRAME, recurse_depth=0, member_index=None ):
    if recurse_depth < 0:
        return
    
    path_uf = r.getUForm( path_uu )

    path_coords=[]

    if xyz_path_role not in path_uf['roles']:
        print path_uu, "doesn't play the role for xyz-path."
        #return

    if head_uu == None:
        head_uu = path_uu
        # for the purpose of this shape, the head-uform frame is the BASEFRAME
        parent_frame = vectors.BASEFRAME

    parent_transformer = vectors.transformer(parent_frame, vectors.BASEFRAME)
        
    if path_uf.has_key('child_properties'):
        # this little interjection allows you to get individual children
        if member_index:
            path_uf['child_properties'] = [path_uf['child_properties'][member_index]]
        # if there are member shapes, iterate through them
        for member in path_uf['child_properties']:
            (child_uu, properties) = member
            # try to get basis information and create transformation
            axes = array(properties['basis_vectors'])
            axes = matrixmultiply(axes, parent_frame.axes)
            origin = vectors.vector(properties['origin_translation'], parent_frame)
            origin = parent_transformer.transform(origin).coords
            child_frame = vectors.basis(axes, origin, vectors.BASEFRAME)
            # call recursively with new transformation to get child points
            if recurse_depth > 0:
                path_coords.extend(reconstruct(r, child_uu, head_uu, child_frame, recurse_depth-1))
        # if we wanted a specific member, we don't want the top shape
        if member_index:
            return(path_coords)

    # try to get points off this u-form, tranform to head frame, and add to list
    if path_uf.has_key('path_points'):
        points = path_uf['path_points']
        parent_transform = vectors.transformer(parent_frame, vectors.BASEFRAME)
        new_points = []
        for strand in points:
            new_strand = []
            for point in strand:
                new_strand.append(parent_transform.transform( vectors.vector(point, parent_frame)) )
            new_points.append(new_strand)
        path_coords.extend(new_points)
    else:
        print "Couldn't get any points directly from", path_uu
        pass

    return(path_coords)
 
##
def test2():
    antarctica = uuid._('~01830890eee1b211d9a07512535e3a7417')
    canada = uuid._('~018f1a22ece1b211d9a075211c1ffb6813')
    india = uuid._('~0187d0b6c6d92a11d98e194035023e437c')
    spain = uuid._('~01ba571680d92a11d98e195c532b6663a2')
    russia = uuid._('~019da54926d92a11d98e1937a233ac18c1')

    cgraph=uuid._('~016350a250d46d11d9956d40d900543a33')
    country_names_uuid = uuid._ ( '~01cf89e05edde011d9b97830db15e369e0' )
    country_name = "New Zealand"
    country_parts = r.getAttr( country_names_uuid, country_name )

    for component in r.getAttr(cgraph, 'components'):
        for country in r.getAttr(component, 'members'):
            shape = r.getAttr(country, 'shape')
            makeHeadAnnotation( r, shape )
            print r.getAttr(country, 'name')

    # this is a little hack from Dom's PIL interface
    #from geographic import drawShape
    #my_picture = drawShape.makePicture( compound_vectors, y_invert=1 )
    #filename = "Canada.gif"
    #my_picture.save(filename)

###  
def test():
    r = repos.Repository('localhost:6200')
    cgraph=uuid._('~016350a250d46d11d9956d40d900543a33')
    SuperCShape = r.getAttr(r.getAttr(cgraph, 'components')[0], 'shape')
    #makePathRecursive(r, SuperCShape, 10)
    #for member in r.getAttr(SuperCShape, 'members'):
        #addKeypointsFromMembers( r, member )
    makeHeadAnnotation(r, SuperCShape)
        
if __name__ == '__main__':
    test()

    
