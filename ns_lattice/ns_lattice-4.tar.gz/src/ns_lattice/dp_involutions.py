'''
Created on Aug 11, 2016
@author: Niels Lubbes

Classification of unimodular involutions of Neron-Severi lattice 
of weak del Pezzo surfaces.
'''

from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_QQ
from ns_lattice.sage_interface import sage_matrix
from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_diagonal_matrix

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.class_div import Div

from ns_lattice.div_in_lattice import get_ak


def complete_basis( d_lst ):
    '''
    Parameters
    ----------
    d_lst : list<Div>
        A list of "Div" objects.
    
    Returns
    -------
    sage_matrix<sage_QQ>
        Returns a square matrix over QQ of full rank. The first columns
        correspond to the elements in d_lst (where d_lst is sorted). 
        The appended columns are orthogonal to the first "len(d_lst)" columns.
         
    Examples
    --------
        We explain with 3 examples where the dotted (:) vertical lines 
        denote which columns are appended. 
          
          | 0  0 : 1  0  0  0 | | 0  0  0 : 1  0  0 | | 0  0  0  1 : -3  0 |  
          | 0  0 : 0 -1  0  0 | | 0  0  0 : 0 -1  0 | | 1  0  0 -1 :  1  0 |
          | 0  0 : 0  0 -1  0 | | 1  0  0 : 0  0 -1 | |-1  1  0 -1 :  1  0 |
          | 1  0 : 0  0  0 -1 | |-1  1  0 : 0  0 -1 | | 0 -1  0 -1 :  1  0 |
          |-1  1 : 0  0  0 -1 | | 0 -1  1 : 0  0 -1 | | 0  0  1  0 :  0  1 |
          | 0 -1 : 0  0  0 -1 | | 0  0 -1 : 0  0 -1 | | 0  0 -1  0 :  0  1 |
             
    '''
    # sort
    d_lst = [ d for d in d_lst]
    d_lst.sort()

    # extend with orthogonal vectors
    row_lst = [ d.e_lst for d in d_lst]
    ext_lst = []
    for v_lst in  sage_matrix( sage_ZZ, row_lst ).right_kernel().basis():
        ext_lst += [ [-v_lst[0]] + list( v_lst[1:] ) ]  # accounts for signature (1,rank-1)
    mat = sage_matrix( sage_QQ, row_lst + ext_lst ).transpose()

    # verify output
    if mat.rank() < d_lst[0].rank():
        raise Error( 'Matrix expected to have full rank: ', d_lst, '\n' + str( mat ) )
    de_lst = [ Div( ext ) for ext in ext_lst ]
    for de in de_lst:
        for d in d_lst:
            if d * de != 0:
                raise Error( 'Extended columns are expected to be orthogonal: ', de, d, de_lst, d_lst, list( mat ) )

    return mat


def is_integral_involution( M ):
    '''
    Parameters
    ----------
    M : sage_matrix
        A matrix M.
    
    Returns
    -------
    bool
        Returns True if the matrix is an involution, 
        preserves inner product with signature (1,r) 
        and has integral coefficients.
    '''

    nrows, ncols = M.dimensions()

    # check whether involution
    if M * M != sage_identity_matrix( nrows ):
        return False

    # check whether inner product is preserved
    S = sage_diagonal_matrix( [1] + ( ncols - 1 ) * [-1] )
    if M.transpose() * S * M != S:
        return False

    # check whether coefficients are integral
    for r in range( nrows ):
        for c in range( ncols ):
            if M[r][c] not in sage_ZZ:
                return False

    # check whether canonical class is preserved
    ak = get_ak( nrows )
    if ak.mat_mul( M ) != ak:
        return False

    return True


def basis_to_involution( d_lst, rank ):
    '''
    Parameters
    ----------
    d_lst : list<Div>
        A list of "Div" objects of rank "rank".
    
    rank : int
        An integer in [3,...,9].
    
    Returns
    -------
    sage_MATRIX<sage_QQ>
        Returns matrix over QQ that correspond to an involution of 
            ZZ<h,e1,...,er>
        here r=rank-1. The first columns
        correspond to the elements in d_lst (where d_lst is sorted). 
        The appended columns are orthogonal to the first "len(d_lst)" columns.    
    '''
    if d_lst == []:
        return sage_identity_matrix( sage_QQ, rank )

    l = len( d_lst )
    V = complete_basis( d_lst )
    D = sage_diagonal_matrix( l * [-1] + ( rank - l ) * [1] )
    M = V * D * V.inverse()  # MV=VD

    return M

