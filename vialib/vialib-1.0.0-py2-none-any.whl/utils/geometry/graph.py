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

# graphs.py implements basic routines on graphs represented by u-forms 

from MAYA.VIA import repos, uuid
from MAYA.utils import scalablecoll
from MAYA.utils.geometry import utils

graph_role = uuid._('~011c5fbf78506211d9b0e92179616d6480')
graph_node_role = uuid._('~01c9a8fc08506211d995200aa670f75d99')
graph_component_role = uuid._('~0134db12c2506311d98492343127a95000')
graph_edge_role = uuid._('~017194bc9ce4d611d9b31b3efa58dd0d21')

r = repos.Repository('localhost:6200')

""" these classes and methods help for country border merging.
They should not be taken as analytically complete or definitive."""

class node:
    def __init__(self, uu=None):
	if uu==None:
	    uu = uuid.UUID()
	self.uu = uu

###
class edge:
    def __init__(self, endpoints=None, faces=None, uu=None):
	self.endpoints = endpoints
	self.faces = faces
	if uu==None:
	    uu = uuid.UUID()
	self.uu = uu

    def __eq__(self, other):
	if utils.testSetEquality(self.endpoints, other.endpoints) == 1:
	    if utils.testSetEquality(self.faces, other.faces) == 1:
		return 1
	return 0

###
def makeSymmetric( r, graph ):
    """takes all the nodes in a graph, looks up the nodes, and checks that each link between two nodes is reciprocated."""
    neighbor_table = {}
    nodes = scalablecoll.new(r, graph)
    for node in nodes:
        neighbor_table[node] = r.getAttr( node, 'neighbors' )
    for node in nodes:
        try:
            for neighbor in neighbor_table[node]:
                if node not in neighbor_table[neighbor]:
                    neighbor_table[neighbor].append(node)
        except:
            pass

###
def cleanNeighbors( r, graph ):
    """makes sure that there aren't repetitions of neighbours (don't use in multigraphs)"""
    nodes = scalablecoll.new(r, graph)
    dict = {}
    for node in nodes:
        neighbors = r.getAttr( node, 'neighbors' )
        try:
            for x in neighbors:
                dict[x] = 1
        except:
            continue
    neighbors = dict.keys()
    r.setAttr( node, 'neighbors', neighbors )

###
def checkEndpointEdges( graph_uu ):
    for face in scalablecoll.new(r, graph_uu):
        utils.removeDuplicates(face, 'borders')        # no multigraphs!
        for border in r.getAttr(face, 'borders'):
            for endpoint in r.getAttr(border, 'endpoints'):
                edges = r.getAttr(endpoint, 'edges') or []
                if border not in edges:
                    edges.append(border)
                    print "Appending", r.getName(border)
                    r.setAttr(endpoint, 'edges', edges)
        print "Checked edges for", r.getName( face )

###
def buildComponents( r, graph ) :
    """find components in a graph by computing transitive closure of the nodes"""
    components_uuids = []
    # these nodes have already been assigned to a component
    processed_nodes = {}
    # check to see if this u-form plays the graph role
    if graph_role not in r.getAttr( graph, 'roles' ):
        print 'U-form', graph, 'does not play the role graph.'
        return
    # nodes in the graph
    nodes = r.getAttr( graph, 'members' )
    for node in nodes:        
        # this node has already been assigned to a component
        if processed_nodes.has_key(node): continue
        # if this node has no neighbors, skip it
        if r.getAttr( node, 'neighbors' ) == None:
            processed_nodes[node] = 1
            continue
        else :
            component = transitive_closure(r, node )
        # check for duplicates in case I screwed up!
        clean_component = []
        for x in component :
            if x not in clean_component:
                clean_component.append( x )
        component = clean_component
        print "Component: ", component
        # make component u-form
        component_uuid = uuid.UUID()
        components_uuids.append(component_uuid)
        r.setAttr( component_uuid, 'roles', graph_component_role )
        r.setAttr( component_uuid, 'members', component )

        links = []
        for x in component:
            r.setAttr( x, 'component', component_uuid )
            processed_nodes[x] = 1
            neighbors = r.getAttr( x, 'neighbors' )
            try:
                for y in neighbors :
                    links.append([x, y])
            except:
                pass
        r.setAttr( component_uuid, 'links', links )
    r.setAttr( graph, 'components', components_uuids )

###
def transitiveClosure(r, node ):
    print "Building transitive closure of ", r.getAttr( node, 'name' )

    # check to see if this u-form plays the graph role
    if graph_node_role not in r.getAttr( node, 'roles' ):
        print 'U-form', node, 'does not play the role graph node.'
        return

    # this will hold the list of nodes
    component = []
    waiting_nodes = r.getAttr( node, 'neighbors' )
    # this will describe the link-structure inside the component
    links = []

    # go through this loop until component stops growing
    while( waiting_nodes != [] ) :
        # get neighbors
        active_node = waiting_nodes.pop()
        # if we've used this node then carry on
        if active_node in component :
            continue
        
        component.append(active_node)

        neighbors = r.getAttr( active_node, 'neighbors' )

        if neighbors == None:
            continue
        else:
            for x in neighbors :
                if x not in component :
                    print "Appending ", r.getAttr( x, 'name' )
                    waiting_nodes.append( x )

    return component

###
def addMissingNeighbors( r, component ):
    members = r.getAttr(component, 'members')
    neigh_dict = {}
    for member in members:
        neigh_dict[member] = []
    for link in r.getAttr(component, 'links'):
        neigh_dict[link[0]].append(link[1])
        neigh_dict[link[1]].append(link[0])
    for mem in neigh_dict.keys():
        final = []
        for x in neigh_dict[mem]:
            if x not in final:
                final.append(x)
        r.setAttr(mem, 'neighbors', final)
        print r.getAttr(mem, 'name'), r.getAttr(final[0], 'name')

### create and edge between 2 nodes
def makeLink(r, uuid1, uuid2 ):
    neighbors1 = r.getAttr( uuid1, 'neighbors' )
    if neighbors1 == None:
        neighbors1 = []
    if uuid2 not in neighbors1:
        neighbors1.append( uuid2 )
        r.setAttr( uuid1, 'neighbors', neighbors1 )
        
    neighbors2 = r.getAttr( uuid2, 'neighbors' )
    if neighbors2 == None:
        neighbors2 = []
    if uuid1 not in neighbors2:
        neighbors2.append( uuid1 )
        r.setAttr( uuid2, 'neighbors', neighbors2 )

    for x in (uuid1, uuid2):
        roles = r.getAttr( x, 'roles' )
        if graph_node_role not in roles:
            roles.append(graph_node_role)
        r.setAttr( x, 'roles', roles)

    ## create edge u-form
    edge_uf = uform.UForm()
    edge_uf['roles'] = graph_edge_role
    edge_uf['endpoints'] = [uuid1, uuid2]
    r.setAttr(edge_uf)
    return(edge_uf.uuid)
            
###
def getExternalBoundary( r, faces ):
    border_collection = {}
    node2borders = {} #this keeps a hash from vertices to the borders they join
    outer_collection = [] # this is an unordered collection of external borders
    reverses = [0]#boolean array giving the sense of each segment

    # first, build a hash table saying how often each border appears 
    for face in faces:
        borders = r.getAttr( face, 'borders' )
        for border_uu in borders:
            if border_collection.has_key(border_uu):
                if border_collection[border_uu] == 1:
                    border_collection[border_uu] = 2
                else:
                    pass
            else:
                border_collection[border_uu] = 1

    # any border that appeared only once is on the edge of the shape
    for border in border_collection.keys():
        if border_collection[border] == 1:
            outer_collection.append(border)

    # outer_collection.reverse() # this is sometimes useful

    ### now we need to get the shapes in the right order
    first_border = outer_collection[0]
    final_collection = [first_border]
    first_point = r.getAttr(first_border, 'endpoints')[0]
    current_point = r.getAttr(first_border, 'endpoints')[1]

    while( current_point != first_point ):
        borders = r.getAttr(current_point, 'edges')
        #print "Borders:", map( r.getName, borders )
        for border in borders:
            if border not in outer_collection:
                continue
            if border in final_collection:
                continue
            else:
                final_collection.append(border)
                endpoints = r.getAttr(border, 'endpoints')
                if endpoints[0] == current_point:
                    reverses.append(0)
                    current_point = endpoints[1]
                    break
                if endpoints[1] == current_point:
                    reverses.append(1)
                    current_point = endpoints[0]
                    break
                break
            break

    return (final_collection, reverses)        

###
# this function takes (the beginning of) a chain and works out which point is at its end 
def getEndpoint( chain ):
    # check args
    if( type(chain)!=type([]) or not uuid.isa(chain[0]) or graph_edge_role not in r.getAttr(chain[0], 'roles') ):
        print "Chain must be a list of u-forms playing the graph edge role."
        return -1
    endpoints0 = r.getAttr(chain[0], 'endpoints')
    endpoints1 = r.getAttr(chain[1], 'endpoints')
    for candidate in endpoints0:
        # if this point isn't in the endpoints of the next edge
        if candidate not in endpoints1:
            endpoints0.remove(candidate)
            # but the other endpoint is
            if endpoints0[0] in endpoints1:
                # then we've found the enndpoint that begins the chain
                return(candidate)
    # otherwise the chains don't meet
    print "First two edges do not produce a definitive starting point."
    return -1


###
def test() :
    country_graph = uuid._('~016350a250d46d11d9956d40d900543a33')
    canada_mainland = uuid._('~016c6007f2d47011d988b606081bbf2c86')
    checkEndpointEdges(country_graph)
    
###
if __name__ == '__main__':
    test()
