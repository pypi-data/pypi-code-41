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

# uses functions from graph.py and make_uforms.py to create shapes for nodes
# in graphs, etc.

from MAYA.VIA import repos, uuid
from MAYA.utils import scalablecoll, signing
from MAYA.utils.geometry import utils, lengths, graph, make_uforms

graph_role = uuid._('~011c5fbf78506211d9b0e92179616d6480')
graph_node_role = uuid._('~01c9a8fc08506211d995200aa670f75d99')
graph_component_role = uuid._('~0134db12c2506311d98492343127a95000')
graph_edge_role = uuid._('~017194bc9ce4d611d9b31b3efa58dd0d21')

r = repos.Repository('localhost:6200')
signing.enableSignatureReads(r)

###
def getReversesAlongChain( r, chain ):
    if len(chain) == 1:
        return([0])
    
    reverses = []

    # initialize first link
    endpoints0 = r.getAttr( chain[0], 'endpoints' )
    endpoints1 = r.getAttr( chain[1], 'endpoints' )
    if endpoints0[0] in endpoints1:
        current_point = endpoints0[0]
        reverses.append(1)
    elif endpoints0[1] in endpoints1:
        current_point = endpoints0[1]
        reverses.append(0)
    else:
        print "Couldn't initialize."
        print endpoints0, '\n', endpoints1

    # carry on
    for edge in chain[1:]:
        endpoints = r.getAttr(edge, 'endpoints')
        if endpoints[0] == current_point:
            reverses.append(0)
            current_point = endpoints[1]
            continue
        
        if endpoints[1] == current_point:
            reverses.append(1)
            current_point = endpoints[0]
            continue
        
        else:
            print "No endpoints found at", edge

    return (reverses)   

###
def addBoundaryWithSense(r, faces, path_uu=None):
    if path_uu == None:
        #path_uu = r.getAttr(faces[0], 'shape')
        path_uu = uuid.UUID()
        make_uforms.addPathRole(r, path_uu)
    (members, reverses) = graph.getExternalBoundary(r, faces)

    print len(members), ':', map(r.getName, members)
    print len(reverses), ':', reverses

    cp = r.getAttr(path_uu, 'child_properties')
    if cp == None:
        cp = [] 
        for i in range(len(members)):
            cp.append( [members[i], uform.EForm()] )
    if len(cp) != len(members):
        print "Members and child_properties of different length for", path_uu

    for i in range(len(members)):
        print i
        cp[i][1]['reverse'] = reverses[i]
        cp[i][1]['type'] = 'detail'
        cp[i][0] = members[i]

    r.setAttr(path_uu, 'members', members)
    r.setAttr(path_uu, 'child_properties', cp)
    make_uforms.makeHeadAnnotation(r, path_uu)
    return path_uu

###
def makeCuts( members, deldict ):
    """Takes a single list of members and a dictionary of items to be deleted. Returns a list of lists of contiguous non-deleted items. """
    result_chains = []
    current_chain = []
    for member in members:
        if deldict.has_key(member):
            if len(current_chain) > 0:
                result_chains.append(current_chain)
                current_chain = []
        else:
            current_chain.append(member)
    if len(current_chain) > 0:
        result_chains.append(current_chain)
    return(result_chains)

###
def tryMergeEnds(chains):
    """Check to see if the ends of two collections of chains should be merged."""
    for endpoint in r.getAttr(chains[0][0], 'endpoints'):
        if endpoint in r.getAttr(chains[-1][-1], 'endpoints'):
            last_chain = chains.pop()
            last_chain.extend(chains[0])
            chains[0] = last_chain
            break
    return(chains)
            

###
def orderBorders( r, face ):
    (borders, reverses) = graph.getExternalBoundary( r, [face] )
    if utils.testSetEquality( borders, r.getAttr(face, 'borders') ) == 1:
        r.setAttr(face, 'borders', borders)
    else:
        print "orderBorders: problem with", face
    
###
def test():
    country_graph = uuid._('~016350a250d46d11d9956d40d900543a33')
    components = r.getAttr(country_graph, 'components')
    earth_shape = uuid._('~01813c884040e4100a988906ee3215121e')

    for component in [components[4]]:
        cshape = r.getAttr(component, 'shape')
        r.setAttr(cshape, 'is_line', 0)
        faces = r.getAttr(component, 'members')
        #addBoundaryWithSense(r, faces, path_uu=cshape) 
        borders = r.getAttr(cshape, 'members')
        for border in borders:
            make_uforms.makeCountryBorderUForm(r, border)
        make_uforms.makePathFromChain(r, borders, path_uu=cshape)
        r.setAttr(component, 'borders_of_valence_1', borders)
                
        deldict = {}
        for border in borders:
            deldict[border] = 1
        
        for face in faces:
            print 
            borders = r.getAttr(face, 'borders')
            chains = makeCuts(borders, deldict)
            for border in borders:
                if deldict.has_key(border):
                    deldict[border] += 1
                else:
                    deldict[border] = 1

            if len(chains) > 1:
                chains = tryMergeEnds(chains)

            for chain in chains:
                print map(r.getName, chain)

            for chain in chains:
                reverses = getReversesAlongChain(r, chain)
                path_uu = make_uforms.makePathFromChain(r, chain, reverses)
                r.setAttr(path_uu, 'is_line', 1)
                print path_uu
                make_uforms.addChildPath(r, cshape, path_uu)

        #make_uforms.addChildPath(r, earth_shape, cshape)

if __name__ == '__main__':
    test()
