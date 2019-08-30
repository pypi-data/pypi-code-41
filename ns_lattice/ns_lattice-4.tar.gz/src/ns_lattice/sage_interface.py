'''
Use of this source code is governed by a 
MIT-style license that can be found in the 
LICENSE file.
Created on Jul 12, 2017
@author: Niels Lubbes

Sage has a complicated import structure and it 
is not possible to simply import each need 
module. It seems that "from sage.all import *" 
is the only option. Therefore we introduce an 
interface to Sage so that in the code, it is 
clear, which libraries of Sage we use. Moreover, 
we specify below from which modules in the Sage 
library we import. 

We explain the naming scheme with the following 
two examples. The interface method for 
"PolynomialRing()" is called 
"sage_PolynomialRing()". However the interface 
method for "sage_eval()" is not called 
"sage_sage_eval()" but instead "sage__eval()". 
The variable "ZZ" is called "sage_ZZ".


For the Parameters section in the documentation 
of types we will use the following abbrevations:

sage_POLY: 
    sage.rings.polynomial.multi_polynomial_element.MPolynomial_polydict
    The type of an element in sage_PolynomialRing 

sage_RING:
    sage.rings.*
    The type of a ring. For example sage_QQ or sage_ZZ or sage_NumberField.

sage_GRAPH:
    sage.graphs.graph
    The type of a Graph.
'''

from sage.all import *
from sage.structure.sage_object import register_unpickle_override

#################################################
# sage.structure                                #
#################################################

# from sage.structure.proof.proof import proof
sage_proof = proof

# from sage.structure.sage_object import save
def sage_save( *args, **kwargs ):
    return save( *args, **kwargs )

# from sage.structure.sage_object import load
def sage_load( *args, **kwargs ):
    return load( *args, **kwargs )

# from sage.structure.sage_object import register_unpickle_override
def sage_register_unpickle_override( *args, **kwargs ):
    register_unpickle_override( *args, **kwargs )


#################################################
# sage.misc                                     #
#################################################

# from sage.misc.sage_eval import sage_eval
def sage__eval( *args, **kwargs ):
    return sage_eval( *args, **kwargs )

# from sage.misc.functional import n
def sage_n( *args, **kwargs ):
    return n( *args, **kwargs )


#################################################
# sage.symbolic                                 #
#################################################

# from sage.symbolic.ring import SR
sage_SR = SR

# from sage.symbolic.relation import solve
def sage_solve( *args, **kwargs ):
    return solve( *args, **kwargs )


#################################################
# sage.rings                                    #
#################################################

# from sage.rings.integer_ring import ZZ
sage_ZZ = ZZ

# from sage.rings.rational_field import QQ
sage_QQ = QQ

# import sage.rings.invariant_theory
sage_invariant_theory = invariant_theory

# from sage.rings.fraction_field import FractionField
def sage_FractionField( *args, **kwargs ):
    return FractionField( *args, **kwargs )

# from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
# http://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/polynomial_ring_constructor.html
def sage_PolynomialRing( *args, **kwargs ):
    return PolynomialRing( *args, **kwargs )

# from sage.rings.number_field.number_field import NumberField
def sage_NumberField( *args, **kwargs ):
    return NumberField( *args, **kwargs )


#################################################
# sage.modules                             #
#################################################

# from sage.modules import VectorSpace
def sage_VectorSpace( *args, **kwargs ):
    return VectorSpace( *args, **kwargs )


#################################################
# sage.matrix                                   #
#################################################

# from sage.matrix.constructor import matrix
def sage_matrix( *args, **kwargs ):
    return matrix( *args, **kwargs )

# from sage.matrix.constructor import identity_matrix
def sage_identity_matrix( *args, **kwargs ):
    return identity_matrix( *args, **kwargs )

# from sage.matrix.constructor import diagonal_matrix
def sage_diagonal_matrix( *args, **kwargs ):
    return diagonal_matrix( *args, **kwargs )

# from sage.matrix.constructor import vector
def sage_vector( *args, **kwargs ):
    return vector( *args, **kwargs )


#################################################
# sage.arith                                    #
#################################################

# from sage.arith.misc import factor
def sage_factor( *args, **kwargs ):
    return factor( *args, **kwargs )

# from sage.arith.misc import gcd
def sage_gcd( *args, **kwargs ):
    return gcd( *args, **kwargs )


#################################################
# sage.calculus                                 #
#################################################

# from sage.calculus.functional import diff
def sage_diff( *args, **kwargs ):
    return diff( *args, **kwargs )

# from sage.calculus.functional import expand
def sage_expand( *args, **kwargs ):
    return expand( *args, **kwargs )

# from sage.calculus.var import var
def sage_var( *args, **kwargs ):
    return var( *args, **kwargs )


#################################################
# sage.combinat                                 #
#################################################

# from sage.combinat.composition import Compositions
def sage_Compositions( *args, **kwargs ):
    return Compositions( *args, **kwargs )

# from sage.combinat.combination import Combinations
def sage_Combinations( *args, **kwargs ):
    return Combinations( *args, **kwargs )

# from sage.combinat.partitions import Partitions
def sage_Partitions( *args, **kwargs ):
    return Partitions( *args, **kwargs )

# from sage.combinat.permutations import Partitions
def sage_Permutations( *args, **kwargs ):
    return Permutations( *args, **kwargs )

# from sage.subset import Subsets
def sage_Subsets( *args, **kwargs ):
    return Subsets( *args, **kwargs )

# from sage.combinat.root_system.root_system import RootSystem
def sage_RootSystem( *args, **kwargs ):
    return RootSystem( *args, **kwargs )


#################################################
# sage.graphs                                   #
#################################################

# from sage.graphs.graph import Graph
def sage_Graph( *args, **kwargs ):
    return Graph( *args, **kwargs )






