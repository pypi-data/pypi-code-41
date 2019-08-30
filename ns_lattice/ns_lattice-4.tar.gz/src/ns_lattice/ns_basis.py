'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Feb 9, 2017
@author: Niels Lubbes
'''
from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_matrix
from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_Permutations
from ns_lattice.sage_interface import sage_Subsets

from ns_lattice.class_div import Div

from ns_lattice.div_in_lattice import get_indecomp_divs
from ns_lattice.div_in_lattice import get_ak
from ns_lattice.div_in_lattice import get_divs

from ns_lattice.class_dp_lattice import DPLattice

from ns_lattice.class_eta import ETA

from ns_lattice.class_ns_tools import NSTools


def get_bases_lst( a_lst, M, d_lst, m1_lst, perm = False ):
    '''
    Returns a list of basis with specified generators.
    
    Parameters
    ----------
    a_lst : list<Div>
        A list of linear independent Div objects of 
        the same rank with 3<=rank<=9.
        It is required that
        "set(a_lst)==set([ a.mat_mul(M) for a in a_lst ])".
    
    M : sage_matrix<sage_ZZ>
        A unimodular matrix representing an involution.
    
    d_lst : list<Div>
        A list of Div objects d of the same rank as any
        element in "a_lst", so that "d*k==0" and "d*d==-2".
        These represent a root basis for the indecomposable 
        (-2)-classes in the Neron-Severi lattice of a 
        weak del Pezzo surface.   

    m1_lst : list<Div>
        A list of Div objects d of the same rank as any
        element in "a_lst", so that "d*k==d*d==-1".
        These represent (-1)-classes in the Neron-Severi 
        lattice of a weak del Pezzo surface.     
    
    perm : bool
        If False, then we consider two bases the same if the 
        generators of the first basis can be obtained from 
        the second basis via a permutation matrix.
    
    Returns
    -------
    list<tuple<Div>>
        A list of tuples of Div objects. Each tuple of Div objects
        represents a basis for the Neron-Severi lattice determined
        by d_lst and m1_lst. The bases are of the form          
            < a1,...,as, b1,...,bt >
        with the following property
            * a1,...,as are defined by the input "a_lst"
            * bi is an element in m1_lst such that bi*bj=am*bi=0 
              for all 1<=i<j<=t and 1<=m<=s              
        If "a_lst==[]" then "[[]]" is returned.   
               
    '''
    key = 'get_bases_lst__' + str( ( a_lst, M, d_lst, m1_lst, perm ) ) + '__' + str( M.rank() )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]


    if a_lst == []:
        return [[]]

    if len( a_lst ) == a_lst[0].rank():
        return [tuple( a_lst )]

    e_lst = []
    for m1 in get_indecomp_divs( m1_lst, d_lst ):
        if set( [ m1 * a for a in a_lst ] ) != {0}:
            continue
        if m1 * m1.mat_mul( M ) > 0:
            continue
        e_lst += [m1]

    bas_lst = []
    for e in e_lst:

        Me = e.mat_mul( M )
        new_d_lst = [ d for d in d_lst if d * e == d * Me == 0 ]
        new_m1_lst = [ m1 for m1 in m1_lst if m1 * e == m1 * Me == 0 ]
        add_lst = [e]
        if e != Me: add_lst += [Me]
        bas2_lst = get_bases_lst( a_lst + add_lst, M, new_d_lst, new_m1_lst, perm )

        if perm:
            bas_lst += bas2_lst
        else:
            for bas2 in bas2_lst:
                found = False
                for bas in bas_lst:
                    # check whether the two bases are the same up to
                    # permutation of generators
                    if set( bas ) == set( bas2 ):
                        found = True
                        break  # break out of nearest for loop
                if not found:
                    NSTools.p( 'found new basis: ', bas2, ', bas2_lst =', bas2_lst )
                    bas_lst += [bas2]

    # cache output
    NSTools.get_tool_dct()[key] = bas_lst
    NSTools.save_tool_dct()

    return bas_lst


def get_webs( dpl ):
    '''
    Returns lists of families of conics for each possible complex basis change.
    The n-th family in each list correspond to a fixed family wrt.
    different bases for each n. 
    
    Parameters
    ----------
    dpl : DPLattice
        Represents the Neron-Severi lattice of a weak del Pezzo surface. 
        
    Returns
    -------
    list<list<Div>>
        A list of lists of Div objects. 
        Each Div object f has the property that 
        f*(3e0-e1-...-er)=2, f*f==0 and f*d>=0 for all d in dpl.d_lst.
        Such a Div object corresponds geometrically to a family of conics.
        For each index i, the i-th entry of each list of Div object corresponds
        to the same family of conics.          
    '''
    key = 'get_webs__' + str( dpl ).replace( '\n', '---' )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]

    ak = get_ak( dpl.get_rank() )
    all_m1_lst = get_divs( ak, 1, -1, True )
    akc, cc = ( 3, 1 )
    M = sage_identity_matrix( dpl.get_rank() )

    fam_lst_lst = []
    for e0 in get_divs( ak, akc, cc, True ):
        NSTools.p( 'e0 =', e0 )
        for B_lst in get_bases_lst( [e0], M, dpl.d_lst, all_m1_lst, True ):
            B = sage_matrix( sage_ZZ, [ d.e_lst for d in B_lst ] )
            dplB = dpl.get_basis_change( B )
            fam_lst_lst += [ dplB.real_fam_lst ]

    # reduce fam_lst
    pat_lst_lst = []
    rfam_lst_lst = []
    for fam_lst in fam_lst_lst:
        pat_lst = [ 0  if fam[0] != 1 else 1 for fam in fam_lst ]
        if pat_lst not in pat_lst_lst:
            pat_lst_lst += [ pat_lst ]
            rfam_lst_lst += [ fam_lst ]


    # cache output
    NSTools.get_tool_dct()[key] = rfam_lst_lst
    NSTools.save_tool_dct()

    return rfam_lst_lst


def contains_perm( f_lst_lst, c_lst ):
    '''
    Parameters
    ----------
    f_lst_lst : list<list<Div>>
        A list of lists containing Div objects.
    
    c_lst : list<Div>
        A list of Div objects
    
    Returns:
    --------
    bool
        Returns True if after a permutation of the generators
        (e1,...,er) the list c_lst is contained in f_lst_lst. 
        For example if c_lst equals [ e0-e1, 2e0-e2-e3-e4-e5 ] 
        then is contained in [ ..., [e0-e2, 2e0-e1-e3-e4-e5], ... ].
    
    '''
    if c_lst == []:
        return [] in f_lst_lst

    for perm in sage_Permutations( range( c_lst[0].rank() - 1 ) ):
        pc_lst = [ Div( [c[0]] + [ c[i + 1] for i in perm ], c.rank() ) for c in c_lst ]
        for f_lst in f_lst_lst:
            if set( f_lst ) == set( pc_lst ):
                return True

    return False


def triples( dpl, mval ):
    '''
    Parameters
    ----------
    dpl  : DPLattice
    mval : integer
    
    Returns
    -------
    list<(Div,Div,Div)>
        List of triples in "dpl.fam_lst":
            [ (a,b,c),... ]
        so that 
            (1) There does not exists e in "dpl.m1_lst"
                with the property that a*e==b*e==c*e==0.
            (2) 1 <= max( a*b, a*c, b*c ) <= mval.
    '''
    key = 'triples__' + str( dpl ).replace( '\n', '---' ) + '---' + str( mval )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]

    f_lst = dpl.fam_lst
    e_lst = dpl.m1_lst

    # obtain list of triples (a,b,c) in f_lst
    # that are not orthogonal to any element in e_lst
    t_lst = []
    idx_lst_lst = sage_Subsets( range( len( f_lst ) ), 3 )
    eta = ETA( len( idx_lst_lst ), 500000 )
    for idx_lst in idx_lst_lst:
        eta.update( 't_lst' )

        t = [ f_lst[idx] for idx in idx_lst ]
        if t[0] * t[1] > mval: continue
        if t[0] * t[2] > mval: continue
        if t[1] * t[2] > mval: continue

        # elements in f_lst correspond to divisor classes of curves on a
        # surface and thus t[i]*t[j]>=1 for all i,j \in {0,1,2} so that i!=j.

        cont = False
        for e in e_lst:
            if [f * e for f in t] == [0, 0, 0]:
                cont = True
                break
        if cont: continue

        if not contains_perm( t_lst, t ):
            t_lst += [t]

    NSTools.p( 't_lst =', t_lst )

    # cache output
    NSTools.get_tool_dct()[key] = t_lst
    NSTools.save_tool_dct()

    return t_lst
