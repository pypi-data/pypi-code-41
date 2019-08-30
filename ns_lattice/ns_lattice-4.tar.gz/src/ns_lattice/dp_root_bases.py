'''
Created on Aug 11, 2016
@author: Niels

See [http://arxiv.org/abs/1302.6678] for more info.

Classification of root subsystems of root systems
of type either A1, A1+A2, A4, D5, E6, E7 or E8.
'''
import time

from ns_lattice.sage_interface import sage_VectorSpace
from ns_lattice.sage_interface import sage_vector
from ns_lattice.sage_interface import sage_QQ
from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_Graph
from ns_lattice.sage_interface import sage_Partitions
from ns_lattice.sage_interface import sage_RootSystem
from ns_lattice.sage_interface import sage_Subsets
from ns_lattice.sage_interface import sage_Combinations
from ns_lattice.sage_interface import sage_Permutations

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.class_div import Div

from ns_lattice.div_in_lattice import get_divs
from ns_lattice.div_in_lattice import get_indecomp_divs
from ns_lattice.div_in_lattice import get_ak


def is_root_basis( d_lst ):
    '''
    Parameters
    ----------
    d_lst : list<Div> 
        A list of lists of "Div" objects "d", 
        such that d*d=-2 and d*(-3h+e1+...+er)=0 
        where r=rank-1 and rank in [3,...,7].
               
    Returns
    -------
    bool
        True if input is the empty list or if divisors 
        in "d_lst" are linear independent as vectors
        and their pairwise product is either -2, 0 or 1.               
    '''

    # check empty-list
    if d_lst == []:
        return True

    # check pairwise inner product
    for i in range( len( d_lst ) ):
        for j in range( len( d_lst ) ):
            if d_lst[i] * d_lst[j] not in [0, 1, -2]:
                return False

    # check linear independence
    # Linear independent vectors with pairwise positive intersection product
    # must form a root basis. Thus vectors of positive roots in the corresponding
    # root system are all positive
    #
    V = sage_VectorSpace( sage_QQ, d_lst[0].rank() )
    W = V.subspace( [d.e_lst for d in d_lst] )
    return W.rank() == len( d_lst )


def get_graph( d_lst ):
    '''
    Parameters
    ----------
    d_lst : list<Div>
        A list of "Div" objects.

    Returns
    -------
    sage_Graph

        A labeled "Graph()" where the elements
        of "d_lst" are the vertices.
        Different vertices are connected if
        their corresponding intersection product
        is non-zero and the edge is labeled with
        the intersection product.
    '''
    G = sage_Graph()
    G.add_vertices( range( len( d_lst ) ) );

    for i in range( len( d_lst ) ):
        for j in range( len( d_lst ) ):
            if d_lst[i] * d_lst[j] > 0 and i != j:
                G.add_edge( i, j, d_lst[i] * d_lst[j] )

    return G


def get_ext_graph( d_lst, M ):
    '''
    Parameters
    ----------
    d_lst : list<Div> 
        A list of "Div" objects of equal rank.
        
    M : sage_matrix<sage_ZZ>   
        A square matrix with integral coefficients
        of rank "d_lst[0].rank()" 
    
    Returns
    -------
        A labeled "sage_Graph()" where the elements 
        of "d_lst" are the vertices. 
        A pair of non-orthogonal vertices are connected 
        by and edge labeled with their 
        non-zero intersection product. 
        Two vertices which are related 
        via M are connected with an edge labeled 1000.
        Labeled self-loops are also included.        
    '''
    NSTools.p( 'd_lst =', len( d_lst ), d_lst, ', M =', list( M ) )

    G = sage_Graph()
    G.add_vertices( range( len( d_lst ) ) )

    for i in range( len( d_lst ) ):
        for j in range( len( d_lst ) ):
            if d_lst[i] * d_lst[j] != 0:
                G.add_edge( i, j, d_lst[i] * d_lst[j] )

    for i in range( len( d_lst ) ):
        j = d_lst.index( d_lst[i].mat_mul( M ) )
        G.add_edge( i, j, 1000 )

    return G


def get_dynkin_type( d_lst ):
    '''
    Parameters
    ----------
    d_lst : list<Div>
        A list of lists of "Div" objects "d" of 
        the same rank, such that 
            d*d=-2 and d*(-3h+e1+...+er)=0 
        where 
            r=rank-1 and rank in [3,...,9].  
        We assume that "is_root_basis(d_lst)==True":
        linear independent, self intersection number -2
        and pairwise product either 0 or 1.            
                     
    Returns
    -------
    string
        Returns a string denoting the Dynkin type of a 
        root system with basis "d_lst".  
        Returns 'A0' if "d_lst==[]".
    
    Note
    ----
        For example:
        [<1145>, <1123>, <23>, <45>, <56>, <78>] --> '3A1+A3'
        where <1145> is shorthand for "Div.new('1145')".      
        
    Raises
    ------
    ValueError
        If the Dynkin type of d_lst cannot be recognized.
         
    '''
    if d_lst == []: return 'A0'

    # check whether values are cached
    #
    construct_dynkin_types = True
    max_r = d_lst[0].rank() - 1
    key = 'get_dynkin_type_' + str( max_r )
    for r in range( max_r, 8 + 1 ):
        if 'get_dynkin_type_' + str( r ) in NSTools.get_tool_dct():
            key = 'get_dynkin_type_' + str( r )
            construct_dynkin_types = False

    # construct list of dynkin types if values are not cached
    #
    if construct_dynkin_types:
        NSTools.p( 'Constructing list of Dynkin types... max_r =', max_r )

        ade_lst = []
        for comb_lst in sage_Combinations( max_r * ['A', 'D', 'E'], max_r ):
            for perm_lst in sage_Permutations( comb_lst ):
                ade_lst += [perm_lst]
        #
        # "ade_lst" contains all combinations of 'A', 'D', 'E'
        # and looks as follows:
        #
        #     ade_lst[0] = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A']
        #     ade_lst[1] = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'D']
        #     ade_lst[2] = ['A', 'A', 'A', 'A', 'A', 'A', 'D', 'A']
        #     ...
        #     ade_lst[?] = ['A', 'D', 'A', 'D', 'A', 'D', 'E', 'A']
        #     ...
        #     ade_lst[-1]= ['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']
        #

        type_lst = []
        ts_lst = []
        for ade in ade_lst:
            for r in range( 1, max_r + 1 ):
                for p_lst in sage_Partitions( r + max_r, length = max_r ):

                    # obtain type list
                    t_lst = [( ade[i], p_lst[i] - 1 ) for i in range( max_r ) if  p_lst[i] != 1]
                    t_lst.sort()

                    # obtain Root system
                    # or continue if invalid Cartan/Dynkin type
                    if ( 'D', 2 ) in t_lst or ( 'D', 3 ) in t_lst:
                        continue
                    try:
                        rs = sage_RootSystem( t_lst )
                    except ValueError as err:
                        continue  # not a valid Cartan type

                    # obtain graph G
                    mat = list( -1 * rs.cartan_matrix() )
                    G = sage_Graph()
                    G.add_vertices( range( len( mat ) ) );
                    for i in range( len( mat ) ):
                        for j in range( len( mat[0] ) ):
                           if mat[i][j] == 1:
                               G.add_edge( i, j )

                    # obtain string for type
                    # Example: [(A,1),(A,1),(A,1),(A,3)] ---> '3A1+A3'
                    tmp_lst = [t for t in t_lst]
                    ts = ''
                    while len( tmp_lst ) > 0:
                        t = tmp_lst[0]
                        c = tmp_lst.count( t )
                        while t in tmp_lst:
                            tmp_lst.remove( t )
                        if ts != '':
                            ts += '+'
                        if c > 1:
                            ts += str( c )

                        ts += t[0] + str( t[1] )

                    # add to type_lst if new
                    if ts not in ts_lst:
                        type_lst += [( G, ts, t_lst )]
                        ts_lst += [ts]
                        NSTools.p( 'added to list: ', ts, '\t\t...please wait...' )

        NSTools.p( 'Finished constructing list of Dynkin types.' )
        # cache the constructed "type_lst"
        NSTools.get_tool_dct()[key] = type_lst
        NSTools.save_tool_dct()

    # end if
    else:
        type_lst = NSTools.get_tool_dct()[key]
    G1 = get_graph( d_lst )

    # loop through all types and check equivalence
    for ( G2, ts, t_lst ) in type_lst:
        if G1.is_isomorphic( G2 ):
            return ts

    raise ValueError( 'Could not recognize Dynkin type: ', d_lst )


def convert_type( type ):
    '''
    Converts a Dynkin type string to a sorted list of 
    irreducible Dynkin types.
     
    For example if type is '2A1+D4', then the output is 
    ['A1','A1','D4']. If the type is '2A1+A2+A3', 
    then the output is ['A1','A1','A2','A3'].     
    We exclude elements that are equal to 'A0'.
        
    Parameters
    ----------
    type: string
        A string representing a Dynkin type. 
        We assume that an irreducible rootsystem
        occurs with multiplicity at most 9. 
        For example '10A1' is not allowed, but '9A1'
        is allowed. 
    
    Returns
    -------
    list<string>
        A list of string representing the Dynkin type 
        of an irreducible root system.
    '''
    t_lst = type.split( '+' )
    out_lst = []
    for t in t_lst:
        if t[0] not in ['A', 'D', 'E']:
            mult, subtype = int( t[0] ), t[1:]
        else:
            mult, subtype = 1, t
        out_lst += mult * [ subtype ]
    out_lst = [out for out in out_lst if out != 'A0']
    return sorted( out_lst )


def get_root_bases_orbit( d_lst, positive = True ):
    '''
    Computes the orbit of a root base under the Weyl group.
    
    Parameters
    ----------
    d_lst : list<Div>
        A list of lists of "Div" objects "d" of the same rank or the empty list.    

    positive : bool
    
    Returns
    -------
    list<list<Div>>
        A list of distinct lists of "Div" objects "d" of the same rank. 
        such that d*d=-2 and d*(-3h+e1+...+er)=0 where r=rank-1.
        
        If "d_lst" is the empty list, then "[]" is returned.
        
        Otherwise we return a list of root bases such that each root basis
        is obtained as follows from a root "s" such that s*s=-2 
        and s*(-3h+e1+...+er)=0: 
        
            [ d + (d*s)d for d in d_lst ]
        
        We do this for all possible roots in [s1,s2,s3,...]: 
        
            [ [ d + (d*s1)d for d in d_lst ],  [ d + (d*s2)d for d in d_lst ], ... ]
         
        Mathematically, this means that we consider the Weyl group 
        of the root system with Dynkin type determined by the rank of elements 
        in "d_lst". The Dynkin type is either 
            A1, A1+A2, A4, D5, E6, E7 or E8.
        We return the orbit of the elements in "d_lst" under
        the action of the Weyl group.
                
        If "positive==True" then the roots in the basis are all positive
        and thus of the form 
            <ij>, <1ijk>, <2ij>, <30i>
        with i<j<k. 
        For example '15' and '1124' but not '-15' or '-1124'. 
        See "Div.get_label()" for the notation.                           
    '''
    if d_lst == []:
        return [[]]

    rank = d_lst[0].rank()

    # in cache?
    key = 'get_root_bases_orbit_' + str( d_lst ) + '_' + str( rank )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]

    # obtain list of all positive (-2)-classes
    m2_lst = get_divs( get_ak( rank ), 0, -2, True )
    # m2_lst += [ m2.int_mul( -1 ) for m2 in m2_lst]
    NSTools.p( 'd_lst  =', len( d_lst ), d_lst, ', m2_lst =', len( m2_lst ), m2_lst )

    # data for ETA computation
    counter = 0
    total = len( m2_lst )
    ival = 5000

    d_lst.sort()
    d_lst_lst = [d_lst]
    for cd_lst in d_lst_lst:

        total = len( m2_lst ) * len( d_lst_lst )
        for m2 in m2_lst:

            # ETA
            if counter % ival == 0:
                start = time.time()
            counter += 1
            if counter % ival == 0:
                passed_time = time.time() - start
                NSTools.p( 'ETA in minutes =', passed_time * ( total - counter ) / ( ival * 60 ), ', len(d_lst_lst) =', len( d_lst_lst ), ', total =', total )

            #
            # The action of roots on a root base is by reflection:
            #     cd - 2(cd*m2/m2*m2)m2
            # Notice that m2*m2==-2.
            #
            od_lst = [ cd + m2.int_mul( cd * m2 ) for cd in cd_lst]
            # print( 'm2 =', m2, ', od_lst =', od_lst, ', cd_lst =', cd_lst, ', d_lst_lst =', d_lst_lst, ' positive =', positive )

            od_lst.sort()
            if od_lst not in d_lst_lst:
                d_lst_lst += [od_lst]

    # select positive roots if positive==True
    pd_lst_lst = []
    for d_lst in d_lst_lst:
        if positive and '-' in [ d.get_label( True )[0] for d in d_lst ]:
            continue  # continue with for loop since a negative root in basis
        pd_lst_lst += [d_lst]

    # cache output
    NSTools.get_tool_dct()[key] = pd_lst_lst
    NSTools.save_tool_dct()

    NSTools.p( '#orbit(' + str( d_lst ) + ') =', len( pd_lst_lst ) )

    return pd_lst_lst









