'''
Created on Aug 15, 2016
@author: Niels Lubbes

This module is for classifying real structures and singularities 
of weak Del Pezzo surfaces of degree between 1 and 7.

'''
import time

from ns_lattice.sage_interface import sage_identity_matrix
from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_QQ
from ns_lattice.sage_interface import sage_Subsets
from ns_lattice.sage_interface import sage_VectorSpace
from ns_lattice.sage_interface import sage_vector
from ns_lattice.sage_interface import sage_Graph

from ns_lattice.div_in_lattice import get_divs
from ns_lattice.div_in_lattice import get_indecomp_divs
from ns_lattice.div_in_lattice import get_ak

from ns_lattice.dp_root_bases import get_graph
from ns_lattice.dp_root_bases import get_ext_graph
from ns_lattice.dp_root_bases import get_dynkin_type
from ns_lattice.dp_root_bases import convert_type
from ns_lattice.dp_root_bases import get_root_bases_orbit
from ns_lattice.dp_root_bases import is_root_basis

from ns_lattice.dp_involutions import basis_to_involution
from ns_lattice.dp_involutions import is_integral_involution

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.class_div import Div

from ns_lattice.class_eta import ETA


class DPLattice:
    '''
    Represents an equivalence class of the Neron-Severi lattice 
    of a real weak del Pezzo surface, together with an involution "M"
    and a set of effective (-2)-classes "d_lst". The effective (-2)-classes
    form the basis of a root system.
    
        ( ZZ<e0,e1,...,er>, M, d_lst )
    
    From these objects it is possible to compute the remaining attributes of 
    this class. 
    
    If <e0,e1,...,er> is a basis for the Neron-Severi lattice of the 
    projective plane P^2 blown up in r points then the the canonical 
    class k equals 
        k=-3e0+e1+...+er.
    The intersection product is in this case -e0^2=e1^2=...=er^2=-1 with
    remaining intersections zero.
    
    Otherwise if <e0,e1,...,er> is a basis for the Neron-Severi lattice of the 
    P^1xP^1 blown up in r points then the the canonical 
    class k equals 
        k=-2*(e0+e1).
    The intersection product is in this case -h*e1=e2^2=...=er^2=-1 with
    remaining intersections zero.         
    

    Attributes
    ----------
    M : sage_matrix<sage_ZZ>
        A matrix which correspond to an involution of the lattice
        <e0,e1,...,er> with r=rank-1 and 2 <= r <= 8.
    
    Md_lst : list<Div>
        A list of "Div" objects that correspond to the eigenvectors
        of eigenvalue 1 of M. These "Div" objects form a basis of
        a root subsystem.

    Mtype : string
        A String that denotes the  Dynkin type of "Md_lst".
        
    d_lst : list<Div>
        A list of "Div" objects d such that d*d==-2 and d*k=0
        where k denotes the canonical class. These elements 
        represent effective (-2)-classes.

    type : string
        A String that denotes the Dynkin type of "d_lst".
 
    m1_lst : list<Div>
        A list of "Div" objects "m" such that
        m*m==-1==m*k and m*d>=0 for all d in d_lst, 
        where k denotes the canonical class.        
        These elements represent (-1)-classes that cannot be written 
        as the sum of two effective classes. 
        In other words, the classes are indecomposable.
        
    fam_lst : list<Div>
        A list of "Div" objects "f" such that 
        f*f==0, f*(-k)==2 and m*d>=0 
        for all d in d_lst, where k denotes the canonical class.
                
    real_d_lst : list<Div>
        A list "Div" objects that represent indecomposable and 
        real (-2)-classes. Thus these classes are send to itself by M.
        Geometrically these classes correspond to real isolated singularities.
        
        
    real_m1_lst : list<Div>
        A list "Div" objects that represent indecomposable and 
        real (-1)-classes. Thus these classes are send to itself by M.
        Geometrically these classes correspond to real lines.
        
        
    real_fam_lst : list<Div>
        A list "Div" objects that represent real classes in "self.fam_lst".
        Thus these classes are send to itself by M.
        Geometrically these classes correspond to a real families of conics.        
   
    or_lst : list<Div>
        A list of "Div" objects that represents roots that are orthogonal to
        "self.d_lst".  

    sr_lst : list<Div>
        A list of "Div" objects that represents roots that are contained in
        the subspace spanned by "self.d_lst".  
    
    G : sage_GRAPH
        The Cremona invariant for the current lattice.
        
    SG : sage_GRAPH
        Simple family graph (see self.get_SG()).
    
    SG_data : [int, int, list<int>, list<int>, bool, bool, bool, bool ]
        A list of of data that characterizes the simple family graph (see self.get_SG()).
    '''

    def __init__( self, d_lst, Md_lst, M ):
        '''
        Constructor.
        
        Returns
        -------
        DPLattice
            A DPLattice class whose attributes are set according to input:
                * DPLattice.M
                * DPLattice.Md_lst
                * DPLattice.d_lst
            The remaining attributes of DPLattice can be computed 
            from these attributes.
                    
            In order for this object to make sense, it is required that the 
            involution "M" preserves "d_lst" as a set. Geometrically this 
            means that the involution sends isolated singularities to isolated 
            singularities.  
        '''

        self.d_lst = d_lst
        self.Md_lst = Md_lst
        self.M = M

        self.m1_lst = None
        self.fam_lst = None
        self.real_d_lst = None
        self.real_m1_lst = None
        self.real_fam_lst = None
        self.Mtype = None
        self.type = None
        self.or_lst = None
        self.sr_lst = None
        self.G = None

        self.SG = None
        self.SG_data = None


    def set_attributes( self, level = 9 ):
        '''
        Sets attributes of this object, depending
        on the input level.
        For constructing a classification we instantiate
        many DPLattice objects. This method allows us 
        to minimize the number of attributes that computed
        (thus we use lazy evaluation).
        
        Parameter
        ---------
        self: DPLattice
            At least self.M, self.Md_lst and self.d_lst        
            should be initialized.
        
        level : int
            A non-negative number.
        '''

        # M, Md_lst and d_lst are set.

        if self.m1_lst == None:
            all_m1_lst = get_divs( get_ak( self.get_rank() ), 1, -1, True )
            self.m1_lst = get_indecomp_divs( all_m1_lst, self.d_lst )

        if level < 1: return

        if self.fam_lst == None:
            all_fam_lst = get_divs( get_ak( self.get_rank() ), 2, 0, True )
            self.fam_lst = get_indecomp_divs( all_fam_lst, self.d_lst )

        if level < 2: return

        if self.real_d_lst == None:
            self.real_d_lst = [ d for d in self.d_lst if d.mat_mul( self.M ) == d ]

        if level < 3: return

        if self.real_m1_lst == None:
            self.real_m1_lst = [ m1 for m1 in self.m1_lst if m1.mat_mul( self.M ) == m1 ]

        if level < 4: return

        if self.real_fam_lst == None:
            self.real_fam_lst = [ f for f in self.fam_lst if f.mat_mul( self.M ) == f ]

        if level < 5: return

        if self.or_lst == None:
            self.or_lst = []
            for m2 in get_divs( get_ak( self.get_rank() ), 0, -2, True ):
                if [m2 * d for d in self.d_lst] == len( self.d_lst ) * [0]:
                    self.or_lst += [m2]

        if level < 6: return

        if self.sr_lst == None:
            V = sage_VectorSpace( sage_QQ, self.get_rank() )
            W = V.subspace( [d.e_lst for d in self.d_lst] )
            self.sr_lst = []
            for m2 in get_divs( get_ak( self.get_rank() ), 0, -2, True ):
                if sage_vector( m2.e_lst ) in W:
                    self.sr_lst += [ m2 ]

        if level < 7: return

        if self.type == None:
            self.type = get_dynkin_type( self.d_lst )

        if level < 8: return

        if self.Mtype == None:
            self.Mtype = get_dynkin_type( self.Md_lst )

        if level < 9: return

        if self.G == None:
            self.G = get_ext_graph( self.d_lst + self.m1_lst, self.M )




    def get_rank( self ):
        '''
        Parameters
        ----------
        self : DPLattice
            We expect self.M != None.
        
        Returns
        -------
        int
            Integer denoting rank of lattice.
        '''
        return self.M.dimensions()[0]


    def get_degree( self ):
        '''
        Parameters
        ----------
        self : DPLattice
            We expect self.M != None.        
        
        Returns
        -------
        int
            Integer denoting the degree of weak del Pezzo surface with
            "self" its corresponding Neron-Severi lattice.
        '''
        return 10 - self.get_rank()


    def get_numbers( self ):
        '''
        Parameters
        ----------
        self : DPLattice
        
        Returns
        -------
        list<int>
            List of 6 integers:
                
                0: #indecomposable (-2)-classes 
                1: #indecomposable (-1)-classes
                2: #families of conics
                
                3: #real effective (-2)-classes 
                4: #real indecomposable (-1)-classes
                5: #real families of conics                
            
            where # stands for number of.
            
            Note that a divisor class is indecomposable 
            if it is effective and cannot be written as 
            the sum of two effective classes.
        '''
        self.set_attributes( 6 )
        return ( len( self.d_lst ),
                 len( self.m1_lst ),
                 len( self.fam_lst ),
                 len( self.real_d_lst ),
                 len( self.real_m1_lst ),
                 len( self.real_fam_lst ) )


    def contains_fam_pair( self ):
        '''
        Parameters
        ----------
        self : DPLattice
        
        Returns
        -------
        bool
            True if self.real_fam_lst contains two Div classes 
            with intersection one. Geometrically this means that a 
            weak del Pezzo surface with a Neron-Severi lattice that
            is isomorphic to this one, must be birational to P1xP1
            (ie. fiber product of the projective line with itself).             
        '''
        self.set_attributes( 6 )
        for f1 in self.real_fam_lst:
            for f2 in self.real_fam_lst:
                if f1 * f2 == 1:
                    return True
        return False


    def is_real_minimal( self ):
        '''
        Parameters
        ----------
        self : DPLattice
        
        Returns
        -------
        bool
            True if self.m1_lst does not contain classes u and v 
            such that either  
            * u.mat_mul( self.M ) == v and u*v==0, or 
            * u.mat_mul( self.M ) == u.
            This means that self is the DPLattice of a 
            real-minimal weak del Pezzo surface. Thus no
            disjoint complex conjugate exceptional curves
            or real exceptional curves can be contracted.          
        '''
        self.set_attributes( 0 )
        for u in self.m1_lst:
            v = u.mat_mul( self.M )
            if v * u == 0 or v == u:
                return False
        return True


    def get_marked_Mtype( self ):
        '''
        We mark Mtype with a '-symbol to distinguish between real 
        structures of the same Dynkin type that are not conjugate.
        '''
        if self.get_degree() not in [6, 4, 2]:
            return self.Mtype

        self.set_attributes( 8 )
        if ( self.get_degree(), self.Mtype ) not in [ ( 6, 'A1' ), ( 4, '2A1' ), ( 2, '3A1' ) ]:
            return self.Mtype

        mark = ''
        if list( self.M.T[0] ) != [1] + ( self.get_rank() - 1 ) * [0]:
            # in this case e0 is not send to e0 by the involution self.M
            mark = "'"

        return self.Mtype + mark


    def get_real_type( self ):
        '''
        Gets the Dynkin type (self.type) of self.d_lst. 
        The components of the Dynkin diagram that are preserved by
        the involution induced by the real structure are marked. 
                 
        For example, {A2} means that the elements in the root bases
        for the A2 root systems are preserved elementwise by the involution.
        We write [A2] if the root bases is preserved by the involution
        as a whole but not element wise.
        We write 2A2 if the two A2 root bases are interchanged by the 
        involution. Instead of 3A2 we may write for example [A2]+{A2}+2A2. 
        
                         
        Returns
        -------
        string
            Dynkin types of components 
        '''
        comp_lst = get_graph( self.d_lst ).connected_components()
        comp_lst.reverse()  # smaller components first
        if comp_lst == []:
            return 'A0'

        # construct list of types
        type_lst = []
        for comp in comp_lst:
            c_lst = [ self.d_lst[i] for i in comp ]
            mc_lst = []
            elementwise = True
            for c in c_lst:
                mc = c.mat_mul( self.M )
                mc_lst += [mc]
                if c != mc:
                    elementwise = False
            mc_lst.sort()
            type = get_dynkin_type( c_lst )

            if set( mc_lst ) == set( c_lst ) and c_lst != []:
                if elementwise:
                    type_lst += ['{' + type + '}']
                else:
                    type_lst += ['[' + type + ']']
            else:
                type_lst += [type]

        # construct string
        out = ''
        while type_lst != []:
            type = type_lst[0]
            num = type_lst.count( type )
            if num != 1: out += str( num )
            out += type + '+'
            type_lst = [ elt for elt in type_lst if elt != type ]
        out = out[:-1]  # remove last plus

        return out


    def get_basis_change( self, B ):
        '''
        Parameters
        ----------
        self : DPLattice
            
        B : sage_matrix<sage_ZZ>   
            A matrix whose rows correspond to generators of 
            a new basis. We assume that the intersection
            matrix for this basis is the default
            diagonal matrix with diagonal (1,-1,...,-1).
        
        Returns
        -------
        DPLattice
            A new "DPLattice" object, which represents the current  
            lattice with respect to a new basis.
                
        '''
        self.set_attributes( 6 )

        d_lst_B = [ d.get_basis_change( B ) for d in self.d_lst ]
        Md_lst_B = [ Md.get_basis_change( B ) for Md in self.Md_lst ]
        M_B = ~( B.T ) * self.M * ( B.T )  # ~B is inverse of B, new involution after coordinate change

        dpl = DPLattice( d_lst_B, Md_lst_B, M_B )
        dpl.Mtype = self.Mtype
        dpl.type = self.type
        dpl.m1_lst = [ m1.get_basis_change( B ) for m1 in self.m1_lst ]
        dpl.fam_lst = [ fam.get_basis_change( B ) for fam in self.fam_lst ]
        dpl.real_d_lst = [ d.get_basis_change( B ) for d in self.real_d_lst ]
        dpl.real_m1_lst = [ m1.get_basis_change( B ) for m1 in self.real_m1_lst ]
        dpl.real_fam_lst = [ fam.get_basis_change( B ) for fam in self.real_fam_lst ]

        return dpl


    def get_SG( self ):
        '''
        The simple family graph associated to the 
        Neron-Severi lattice of a weak del Pezzo surface
        is defined as the incidence diagram of self.real_fam_lst,
        with the edges labeled <=1 removed. 
        All vertices are labeled with the index of the element in 
        self.real_fam_lst. 
        
        In the mathematical version (see arxiv paper) the vertices 
        are labeled with the dimension of the linear series, which is 
        always 1 with one exception: 
        If len(self.real_fam_lst)==0 and rank==3, then
        the simple family graph consists of a single vertex labeled 2. 
        
        Example
        -------
        # The following graph is related to the E8 root system:
        #
        dpl = DPLattice.get_cls( 9 )[0]
        assert set(dpl.get_SG().num_verts()) == {2160}
        assert set(dpl.get_SG().get_degree()) == {2095}
        assert set(dpl.get_SG().edge_labels()) == {2,3,4,5,6,7,8}

        
        Returns
        -------
        sage_GRAPH, [int, int, list<int>, list<int>, bool, bool, bool, bool ]
            The simple family graph self.SG and a list self.SG_data 
            associated to the current DPLattice object.
            Here self.SG_data consists of data that describes self.SG.
            This method also initializes self.SG and self.SG_data.
        '''

        if self.SG != None:
            return self.SG, self.SG_data

        if self.get_rank() == 9 and self.get_numbers()[-1] > 800:
            NSTools.p( 'Initializing simple family graph of current DPLattice object...', self.get_rank(), self.get_marked_Mtype(), self.get_real_type() )

        f = self.real_fam_lst
        f_range = range( len( f ) )

        self.SG = sage_Graph()
        self.SG.add_vertices( f_range )
        for i in f_range:
            for j in f_range:
                if f[i] * f[j] > 1:
                    self.SG.add_edge( i, j, f[i] * f[j] )

        self.SG_data = [ self.SG.num_verts(),  # number of vertices
                         self.SG.num_edges(),  # number of edges
                         sorted( list( set( self.SG.degree() ) ) ),  # possible numbers of outgoing edges
                         sorted( list( set( self.SG.edge_labels() ) ) ),  # possible edge labels
                         self.SG.is_clique(),  # True iff the graph is complete.
                         self.SG.is_connected(),
                         self.SG.is_vertex_transitive(),
                         self.SG.is_edge_transitive()]

        return self.SG, self.SG_data


    @staticmethod
    def get_bas_lst( rank = 9 ):
        '''
        See [Algorithm 5, http://arxiv.org/abs/1302.6678] for more info. 
        
        Parameters
        ----------
        rank : int
            An integer in [3,...,9].    
        
        Returns
        -------
        list<DPLattice>
            A list of "DPLattice" objects dpl such that dpl.d_lst 
            is the bases of a root subsystem and dpl.Mtype == A0. 
            The list contains exactly one representative for all 
            root subsystems up to equivalence.  
             
            The list represents a classification of root 
            subsystems of the root system with Dynkin type either:
                A1, A1+A2, A4, D5, E6, E7 or E8,
            corresponding to ranks 3, 4, 5, 6, 7, 8 and 9 respectively 
            (eg. A1+A2 if rank equals 4, and E8 if rank equals 9).
            Note that the root systems live in a subspace of 
            the vector space associated to the Neron-Severi lattice 
            of a weak Del Pezzo surface.
        '''
        # check whether classification of root bases is in cache
        key = 'get_bas_lst__' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        NSTools.p( 'start' )

        A = [ 12, 23, 34, 45, 56, 67, 78]
        B = [ 1123, 1145, 1456, 1567, 1678, 278 ]
        C = [ 1127, 1347, 1567, 234, 278, 308 ]
        D = [ 1123, 1345, 1156, 1258, 1367, 1247, 1468, 1178 ]

        dpl_lst = []
        for ( lst1, lst2 ) in [ ( A, [] ), ( A, B ), ( A, C ), ( [], D ) ]:

            # restrict to divisors in list, that are of rank at most "max_rank"
            lst1 = [ Div.new( str( e ), rank ) for e in lst1 if rank >= Div.get_min_rank( str( e ) ) ]
            lst2 = [ Div.new( str( e ), rank ) for e in lst2 if rank >= Div.get_min_rank( str( e ) ) ]

            # the involution is trivial
            Md_lst = []
            M = sage_identity_matrix( sage_QQ, rank )

            # loop through the lists
            sub1 = sage_Subsets( range( len( lst1 ) ) )
            sub2 = sage_Subsets( range( len( lst2 ) ) )
            eta = ETA( len( sub1 ) * len( sub2 ), 20 )
            for idx2_lst in sub2:
                for idx1_lst in sub1:

                    eta.update( 'get_bas_lst rank =', rank )

                    d_lst = [ lst1[idx1] for idx1 in idx1_lst ]
                    d_lst += [ lst2[idx2] for idx2 in idx2_lst ]

                    if not is_root_basis( d_lst ):
                        continue

                    dpl = DPLattice( d_lst, Md_lst, M )

                    if dpl not in dpl_lst:
                        dpl.set_attributes()
                        dpl_lst += [dpl]

        # cache output
        dpl_lst.sort()
        NSTools.get_tool_dct()[key] = dpl_lst
        NSTools.save_tool_dct()

        return dpl_lst


    @staticmethod
    def get_inv_lst( rank = 9 ):
        '''
        Outputs a list representing a classification of root 
        subsystems that define unimodular involutions on the 
        Neron-Severi lattice of a weak del Pezzo surface.
        We consider root subsystems of the root system with Dynkin 
        type either:
            A1, A1+A2, A4, D5, E6, E7 or E8,
        corresponding to ranks 3, 4, 5, 6, 7, 8 and 9 respectively 
        (eg. A1+A2 if rank equals 4, and E8 if rank equals 9).
        Note that root systems live in a subspace of 
        the vector space associated to the Neron-Severi lattice 
        of a weak Del Pezzo surface.        
        
                
        Parameters
        ----------
        max_rank : int
            An integer in [3,...,9].           
    
        Returns
        -------
        list<DPLattice>
            A list of "DPLattice" objects dpl such that dpl.Md_lst 
            is the bases of a root subsystem and dpl.type == A0. 
            The list contains exactly one representative for 
            root subsystems up to equivalence, so that the root
            subsystem defines a unimodular involution.  
        '''
        # check cache
        key = 'get_inv_lst__' + str( rank )
        if False and key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        bas_lst = DPLattice.get_bas_lst( rank )

        NSTools.p( 'rank =', rank )

        amb_lst = []
        inv_lst = []
        eta = ETA( len( bas_lst ), 1 )
        for bas in bas_lst:
            eta.update( bas.type )

            M = basis_to_involution( bas.d_lst, rank )
            if not is_integral_involution( M ):
                continue
            inv = DPLattice( [], bas.d_lst, M )
            inv.set_attributes()

            NSTools.p( 'Found type of involution: ', bas.type )

            # real structures with different Dynkin types may be equivalent
            if inv not in inv_lst:
                inv_lst += [ inv ]
            else:
                inv_prv = [inv2 for inv2 in inv_lst if inv == inv2][0]
                inv_lst = [inv2 for inv2 in inv_lst if not inv2 == inv]
                amb_lst += [inv, inv_prv]
                if inv > inv_prv:
                    inv_lst += [inv]
                else:
                    inv_lst += [inv_prv]
                NSTools.p( '\tAmbitious type:', inv.Mtype, '==', inv_prv.Mtype,
                           ' inv>inv_prv: ', inv > inv_prv,
                           ' ambitious types =', [ amb.Mtype for amb in amb_lst if amb == inv ] )


        # store in cache
        inv_lst.sort()
        NSTools.get_tool_dct()[key] = inv_lst
        NSTools.save_tool_dct()

        return inv_lst


    @staticmethod
    def get_cls_slow( rank = 7 ):
        '''        
        Use get_cls_real_dp() for a faster method. This method does not terminate
        within reasonable time if rank>7. We still keep the method in order to 
        compare the outcomes in case rank<=9.
        
        Parameters
        ----------
        max_rank : int
            An integer in [3,...,9].           
    
        Returns
        -------
        list<DPLattice>
            A list of DPLattice objects corresponding to Neron-Severi lattices 
            of weak Del Pezzo surfaces of degree (10-rank). The list contains
            exactly one representative for each equivalence class.
              
            All the Div objects referenced in the DPLattice objects of 
            the output have the default intersection matrix:
                diagonal matrix with diagonal: (1,-1,...,-1). 
        '''
        # check cache
        key = 'get_cls_slow__' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]

        inv_lst = DPLattice.get_inv_lst( rank )
        bas_lst = DPLattice.get_bas_lst( rank )


        # we fix an involution up to equivalence and go through
        # all possible root bases for singularities.
        dpl_lst = []
        eta = ETA( len( bas_lst ) * len( inv_lst ), 20 )
        for inv in inv_lst:
            for bas in bas_lst:

                orbit_lst = get_root_bases_orbit( bas.d_lst )
                eta.update( 'len( orbit_lst ) =', len( orbit_lst ) )

                for d_lst in orbit_lst:

                    # check whether involution inv.M preserves d_lst
                    dm_lst = [ d.mat_mul( inv.M ) for d in d_lst ]
                    dm_lst.sort()
                    if dm_lst != d_lst:
                        continue

                    # add to classification if not equivalent to objects
                    # in list, see "DPLattice.__eq__()".
                    dpl = DPLattice( d_lst, inv.Md_lst, inv.M )
                    if dpl not in dpl_lst:
                        dpl.set_attributes()
                        dpl_lst += [dpl]

        # store in cache
        dpl_lst.sort()
        NSTools.get_tool_dct()[key] = dpl_lst
        NSTools.save_tool_dct()

        return dpl_lst


    @staticmethod
    def get_num_types( inv, bas, bas_lst ):
        '''
        Returns the number of root bases in the 
        eigenspace of eigenvalue 1 of the involution 
        defined by M.inv.   
        
        If this number is unknown, then -1 is returned.

        This method is used by get_cls() before 
        calling seek_bases().
        
        Parameters
        ----------
        inv : DPLattice
        
        bas : DPLattice
        
        bas_lst : list<DPLattice>
            We expect this to be the output of get_bas_lst()
            Thus a list of inequivalent DPLattice objects
                  
        Returns
        -------
        int
            If there does not exists a DPLattice in bas_lst whose type is 
            inv.Mtype and bas.type combined, then return 0. 
            Otherwise return either -1 or the 
            number of root bases in the eigenspace of eigenvalue 1 
            of the involution defined by M.inv. 
            We expect this number to be at most 3.                         
        '''

        # check whether the combined type exists in bas_lst
        t1_lst = convert_type( inv.Mtype )
        t2_lst = convert_type( bas.type )
        type_exists = False
        for bas2 in bas_lst:
            if sorted( t1_lst + t2_lst ) == convert_type( bas2.type ):
                type_exists = True
                break
        if not type_exists:
            return 0

        # computes the roots in the eigenspace of eigenvalue 1
        # of the involution defined by inv
        r_lst = get_divs( get_ak( inv.get_rank() ), 0, -2, True )
        s_lst = [ r for r in r_lst if r.mat_mul( inv.M ) == r ]


        if len( s_lst ) == 30:  # D6 since #roots=60=2*30
            if bas.type in ['2A1', 'A3', '4A1', '2A1+A3', 'A5']:
                return 2
            if bas.type in ['3A1', 'A1+A3']:
                return 3
            return 1

        if len( s_lst ) == 63:  # E7 since #roots=126=2*63
            if bas.type in ['3A1', '4A1', 'A5', 'A1+A3', '2A1+A3', 'A1+A5']:
                return 2
            return 1

        return -1


    @staticmethod
    def get_part_roots( inv ):
        '''
        Return two subsets of roots using the input involution.
        
        This method is used by get_cls().        
                    
        Parameters
        ----------
        inv : DPLattice
            We expect inv.type=='A0'.
            We will use inv.Mtype and inv.M. 
        
        Returns
        -------
        list<Div>, list<Div>
            Let R be defined by the list
                get_divs( get_ak( inv.get_rank() ), 0, -2, True )
            whose elements are Div objects.
            If r is a Div object, then M(r) is shorthand notation for 
                r.mat_mul(inv.M).
            The two returned lists correspond respectively to                       
                S := { r in R | M(r)=r }            
            and
                Q union Q' := { r in R | M(r) not in {r,-r} and r*M(r)>0 }
            where Q = M(Q').                        
        '''
        r_lst = get_divs( get_ak( inv.get_rank() ), 0, -2, True )
        s_lst = [ r for r in r_lst if r.mat_mul( inv.M ) == r ]
        tq1_lst = [ r for r in r_lst if r.mat_mul( inv.M ) not in [r, r.int_mul( -1 )] ]
        tq_lst = [ q for q in tq1_lst if q * q.mat_mul( inv.M ) >= 0 ]

        q_lst = []
        for q in sorted( tq_lst ):
            if q not in q_lst and q.mat_mul( inv.M ) not in q_lst:
                q_lst += [q]

        # q_lst += [ q.int_mul( -1 ) for q in q_lst ]

        NSTools.p( 'r_lst      =', len( r_lst ), r_lst )
        NSTools.p( 's_lst      =', len( s_lst ), s_lst )
        NSTools.p( 'tq1_lst    =', len( tq1_lst ), tq1_lst )
        NSTools.p( 'tq_lst     =', len( tq_lst ), tq_lst )
        NSTools.p( 'q_lst      =', len( q_lst ), q_lst )
        NSTools.p( '       M -->', len( q_lst ), [q.mat_mul( inv.M ) for q in q_lst] )
        NSTools.p( 'inv.Md_lst =', inv.Mtype, inv.Md_lst, ', rank =', inv.get_rank() )

        return s_lst, q_lst


    @staticmethod
    def seek_bases( inv, d_lst, r_lst, eq = False, num = -1, b_lst = [], bas_lst = [] ):
        '''
        Look for root bases in a given set of roots whose Dynkin type 
        is the same as a given root bases. 
        
        This method is used by get_cls().
        
        Parameters
        ----------
        inv : DPLattice
            We use inv.Md_lst and inv.M for when creating a 
            new DPLattice object.
        
        d_lst : list<Div>
            We use the intersection matrix associated to d_lst. 
        
        r_lst : list<Div>     
            A list of roots in which to look for root bases.
        
        eq : boolean
            If True, then the returned bases are pairwise
            non-equivalent. By default False, in which case
            only bases that differ by a permutation of elements
            are considered equivalent.
        
        num : int
            If num>0, then the method will terminate if 
            the number of bases found is equal to num.
            If num==-1, then the method continues until
            all possible bases have been reached.
        
        b_lst : list<Div>
            Used for recursive calling this method and 
            represents (a subset of) a candidate root bases.
        
        bas_lst : list<DPLattice>
            Used for recursive calling this method and
            is the list of DPLattice objects that
            is returned by this method. 
            
        Returns 
        -------
        list<DPLattice>
            A list of DPLattice objects "bas"
            such that bas.type is equal to the Dynkin type of d_lst            
            and bas.Mtype==inv.Mtype and bas.M==inv.M.
            
            If eq==True, then the lattice objects are pairwise
            non-equivalent.
            
            If num>0, then the method terminates if the number 
            of bases that are found is equal to num.
        '''

        # check whether the constructed basis defines a new DPLattice object
        if len( b_lst ) == len( d_lst ):

            # check if a permutation of b_lst occurred
            if not eq:
                for bas in bas_lst:
                    if set( bas.d_lst ) == set( b_lst ):
                        return bas_lst

            # create a new lattice object
            bas = DPLattice( b_lst, inv.Md_lst, inv.M )

            # check whether there is an equivalent object in bas_lst
            if eq and bas in bas_lst:
                return bas_lst

            # return bas_lst appended with the new DPLattice object
            return bas_lst + [bas]

        else:

            # construct list with intersection numbers
            s = d_lst[ len( b_lst ) ]
            m_lst = [ d * s for d in d_lst[:len( b_lst )] ]

            # go through all possible roots to build up a basis like d_lst
            for r in r_lst:

                # check intersection number properties
                if [b * r for b in b_lst] == m_lst:

                    # recursive call
                    bas_lst = DPLattice.seek_bases( inv, d_lst, r_lst, eq, num, b_lst + [r], bas_lst )

                    # break out of loop if num bases are found
                    if num > 0 and len( bas_lst ) == num:
                        break

            return bas_lst


    @staticmethod
    def import_cls( cls_lst, inv ):
        '''
        This method is used by get_cls().
        
        Parameters
        ----------
        cls_lst : list<DPLattice>
            A list of DPLattice objects of rank "inv.get_rank()-1". 
            These lattices correspond to Neron-Severi lattices 
            of weak Del Pezzo surfaces.
            
        inv : DPLattice
            A DPLattice object representing an involution.
            We expect inv.Md_lst to be set.
        
        Returns
        -------
        list<DPLattice>
            A list of compatible DPLattice objects in cls_lst that are 
            converted so as to have the same rank and involution matrix as 
            inv.get_rank() and inv.M, respectively. 
            The returned list always contains inv itself.
        '''
        out_lst = []
        for cls in cls_lst:

            # convert divisors to new rank
            Md_lst = [ Div.new( str( d ), inv.get_rank() ) for d in cls.Md_lst ]
            d_lst = [ Div.new( str( d ), inv.get_rank() ) for d in cls.d_lst ]

            # import if the involution is compatible
            if set( Md_lst ) == set( inv.Md_lst ):
                NSTools.p( 'importing: ', ( inv.get_rank(), cls.get_marked_Mtype(), cls.get_real_type() ), Md_lst, '==', inv.Md_lst )
                out = DPLattice( d_lst, inv.Md_lst, inv.M )
                out.set_attributes()
                out_lst += [ out ]

        # always ensure that at least inv object is contained
        if out_lst == []:
            return [inv]

        # we expect that inv is contained in the out_lst
        # for correctness of the get_cls() algorithm.
        assert inv in out_lst

        return out_lst


    @staticmethod
    def get_cls( rank = 9 ):
        '''
        Parameters
        ----------
        rank : int
            An integer in [1,...,9].           
                   
        Returns
        -------
        list<DPLattice>
            A list of DPLattice objects corresponding to Neron-Severi lattices 
            of weak Del Pezzo surfaces of degree (10-rank). The list contains
            exactly one representative for each equivalence class.
              
            All the Div objects referenced in the DPLattice objects of 
            the output have the default intersection matrix:
                diagonal matrix with diagonal: (1,-1,...,-1).
                
            If rank<3 then the empty list is returned. 
        '''
        if rank < 3:
            return []

        # check cache
        key = 'get_cls_' + str( rank )
        if key in NSTools.get_tool_dct():
            return NSTools.get_tool_dct()[key]
        NSTools.p( 'rank =', rank )

        # collect all lattices with either d_lst==[] of Md_lst==[]
        bas_lst = DPLattice.get_bas_lst( rank )
        inv_lst = DPLattice.get_inv_lst( rank )

        # we loop through all involutions
        NSTools.p( 'start looping through inv_lst: ', len( inv_lst ), [inv.get_marked_Mtype() for inv in inv_lst] )
        dpl_lst = []
        for inv in inv_lst:

            NSTools.p( 'looping through inv_lst:', ( rank, inv.get_marked_Mtype(), inv.Md_lst ) )


            # recover the known classification
            if inv.Mtype == 'A0':
                NSTools.p( 'Since Mtype equals A0 we recover the classification from bas_lst.' )
                dpl_lst += [bas for bas in bas_lst]
                continue


            # partition the roots into two sets
            s_lst, q_lst = DPLattice.get_part_roots( inv )


            # import classification for rank-1
            bas1_lst = DPLattice.import_cls( DPLattice.get_cls( rank - 1 ), inv )
            NSTools.p( 'looping through inv_lst continued after recursive call:', ( rank, inv.get_marked_Mtype(), inv.Md_lst ) )


            # correct partition of roots (bas1_lst always contains inv)
            if len( bas1_lst ) > 1:
                e = Div.new( 'e' + str( rank - 1 ), inv.get_rank() )
                s_lst = [ s for s in s_lst if s * e != 0 ]
                q_lst = [ q for q in q_lst if q * e != 0 ]
            NSTools.p( 'bas1_lst =', len( bas1_lst ), [( bas1.Mtype, bas1.type ) for bas1 in bas1_lst] )
            NSTools.p( 's_lst    =', len( s_lst ), s_lst )
            NSTools.p( 'q_lst    =', len( q_lst ), q_lst )


            # collect all possible root bases in s_lst and q_lst
            bas2_lst = []
            bas3_lst = []
            visited_type_lst = []
            eta = ETA( len( bas_lst ), 1 )
            for bas in bas_lst:

                # display progress info
                eta.update( 'get_cls seeking bases in s_lst and q_lst: ', ( rank, inv.get_marked_Mtype(), bas.get_real_type() ) )

                # each type in bas_lst is treated only once
                if bas.type in visited_type_lst:
                    continue
                visited_type_lst += [bas.type]

                # collect bases of type bas.type in s_lst
                if DPLattice.get_num_types( inv, bas, bas_lst ) != 0:
                    bas2_lst += DPLattice.seek_bases( inv, bas.d_lst, s_lst )

                # collect bases of type bas.type in q_lst
                if 2 * len( bas.d_lst ) > rank - 1:
                    continue  # the rank of a root subsystem is bounded by rank-1
                tmp_lst = DPLattice.seek_bases( inv, bas.d_lst, q_lst )
                for tmp in tmp_lst:
                    tmp.d_lst += [d.mat_mul( inv.M ) for d in tmp.d_lst ]
                    if is_root_basis( tmp.d_lst ):  # the roots and their involutions might have intersection product 1
                        tmp.d_lst.sort()
                        bas3_lst += [tmp]


            # debug info
            NSTools.p( 'Setting Dynkin types of', len( bas2_lst + bas3_lst ), 'items...please wait...' )
            eta = ETA( len( bas2_lst + bas3_lst ), len( bas2_lst + bas3_lst ) / 10 )
            for bas in bas2_lst + bas3_lst:
                bas.type = get_dynkin_type( bas.d_lst )
                bas.Mtype = get_dynkin_type( bas.Md_lst )
                eta.update( bas.get_rank(), bas.get_marked_Mtype(), bas.type )
            bas1_lst.sort()
            bas2_lst.sort()
            bas3_lst.sort()
            t_lst1 = [bas.type for bas in bas1_lst]
            t_lst2 = [bas.type for bas in bas2_lst]
            t_lst3 = [bas.type for bas in bas3_lst]
            lst1 = sorted( list( set( [( t, t_lst1.count( t ) ) for t in t_lst1] ) ) )
            lst2 = sorted( list( set( [( t, t_lst2.count( t ) ) for t in t_lst2] ) ) )
            lst3 = sorted( list( set( [( t, t_lst3.count( t ) ) for t in t_lst3] ) ) )
            NSTools.p( 'inv      =', inv.get_marked_Mtype(), ', rank =', rank )
            NSTools.p( 'bas1_lst =', len( bas1_lst ), lst1 )
            NSTools.p( 'bas2_lst =', len( bas2_lst ), lst2 )
            NSTools.p( 'bas3_lst =', len( bas3_lst ), lst3 )


            # construct a list of combinations of DPLattice objects in bas1_lst bas2_lst and
            comb_lst = []
            total = len( bas1_lst ) * len( bas2_lst ) * len( bas3_lst )
            step = total / 10 if total > 10 else total
            eta = ETA( total, step )
            for bas1 in bas1_lst:
                for bas2 in bas2_lst:
                    for bas3 in bas3_lst:
                        eta.update( 'last loop in get_cls: ( bas1.type, bas2.type, bas3.type )=', ( bas1.type, bas2.type, bas3.type ) )
                        d_lst = bas1.d_lst + bas2.d_lst + bas3.d_lst  # notice that d_lst can be equal to []
                        if len( d_lst ) > rank - 1:
                            continue  # the rank of a root subsystem is bounded by rank-1
                        if is_root_basis( d_lst ):
                            dpl = DPLattice( d_lst, inv.Md_lst, inv.M )
                            if dpl not in dpl_lst:
                                dpl.set_attributes()
                                dpl_lst += [dpl]
                                NSTools.p( '\t appended: ', ( rank, dpl.get_marked_Mtype(), dpl.get_real_type() ), ', ( bas1.type, bas2.type, bas3.type ) =', ( bas1.type, bas2.type, bas3.type ) )

        # store in cache
        #
        dpl_lst.sort()
        NSTools.get_tool_dct()[key] = dpl_lst
        NSTools.save_tool_dct()

        return dpl_lst


    # overloading of "=="
    # returns True if isomorphic as Neron-Severi lattices
    def __eq__( self, other ):

        # compared with None?
        if type( self ) != type( other ):
            return False

        # cardinality of classes agree?
        if len( self.d_lst ) != len( other.d_lst ):
            return False
        self.set_attributes( 0 )
        other.set_attributes( 0 )
        if len( self.m1_lst ) != len( other.m1_lst ):
            return False
        self.set_attributes( 1 )
        other.set_attributes( 1 )
        if len( self.fam_lst ) != len( other.fam_lst ):
            return False
        self.set_attributes( 2 )
        other.set_attributes( 2 )
        if len( self.real_d_lst ) != len( other.real_d_lst ):
            return False
        self.set_attributes( 3 )
        other.set_attributes( 3 )
        if len( self.real_m1_lst ) != len( other.real_m1_lst ):
            return False
        self.set_attributes( 4 )
        other.set_attributes( 4 )
        if len( self.real_fam_lst ) != len( other.real_fam_lst ):
            return False
        self.set_attributes( 5 )
        other.set_attributes( 5 )
        if len( self.or_lst ) != len( other.or_lst ):
            return False
        self.set_attributes( 6 )
        other.set_attributes( 6 )
        if len( self.sr_lst ) != len( other.sr_lst ):
            return False

        # Dynkin type effective (-2)-classes agree?
        self.set_attributes( 7 )
        other.set_attributes( 7 )
        if self.type != other.type:
            return False

        # Mtype may differ for equivalent DPLattice objects

        # check Cremona invariant
        self.set_attributes( 9 )
        other.set_attributes( 9 )
        if not self.G.is_isomorphic( other.G, edge_labels = True ):
            return False

        return True


    # operator overloading for !=
    def __ne__( self, other ):
        return not self.__eq__( other )


    # operator overloading for <
    # Used for sorting lists of DPLattice objects:
    #     <http://stackoverflow.com/questions/1227121/compare-object-instances-for-equality-by-their-attributes-in-python>
    def __lt__( self, other ):

        if self.get_rank() != other.get_rank():
           return self.get_rank() < other.get_rank()

        if len( self.Md_lst ) != len( other.Md_lst ):
           return len( self.Md_lst ) < len( other.Md_lst )

        self.set_attributes( 8 )
        other.set_attributes( 8 )

        if self.Mtype != other.Mtype:
            return self.Mtype < other.Mtype

        if self.get_marked_Mtype() != other.get_marked_Mtype():
            return self.get_marked_Mtype() < other.get_marked_Mtype()

        if len( self.d_lst ) != len( other.d_lst ):
            return len( self.d_lst ) < len( other.d_lst )

        if self.type != other.type:
            return self.type < other.type

        # more real lines implies smaller self.type!

        if len( self.real_m1_lst ) != len( other.real_m1_lst ):
            return len( self.real_m1_lst ) > len( other.real_m1_lst )

        if len( self.m1_lst ) != len( other.m1_lst ):
            return len( self.m1_lst ) > len( other.m1_lst )

        if len( self.real_fam_lst ) != len( other.real_fam_lst ):
            return len( self.real_fam_lst ) > len( other.real_fam_lst )

        if len( self.fam_lst ) != len( other.fam_lst ):
            return len( self.fam_lst ) > len( other.fam_lst )


    # overloading of "str()": human readable string representation of object
    def __str__( self ):

        self.set_attributes()

        s = '\n'
        s += 50 * '=' + '\n'

        s += 'Degree          = ' + str( self.get_degree() ) + '\n'
        s += 'Rank            = ' + str( self.get_rank() ) + '\n'
        s += 'Intersection    = ' + str( list( self.m1_lst[0].int_mat ) ) + '\n'
        s += 'Real structure  = ' + str( self.get_marked_Mtype() ) + '\n'
        s += 'Singularities   = ' + str( self.type ) + '\n'
        s += 'Cardinalities   = ' + '(' + str( len( self.or_lst ) ) + ', ' + str( len( self.sr_lst ) ) + ')\n'

        arrow = '  --->  '

        s += 'Real involution:\n'
        b_lst = [Div( row ) for row in sage_identity_matrix( sage_ZZ, self.get_rank() ).rows() ]
        for b in b_lst:
            s += '\t' + str( b ) + arrow + str( b.mat_mul( self.M ) ) + '\n'

        s += 'Indecomposable (-2)-classes:\n'
        for d in self.d_lst:
            s += '\t' + str( d ) + arrow + str( d.mat_mul( self.M ) ) + '\n'
        s += '\t#real = ' + str( len( self.real_d_lst ) ) + '\n'

        s += 'Indecomposable (-1)-classes:\n'
        for m1 in self.m1_lst:
            s += '\t' + str( m1 ) + arrow + str( m1.mat_mul( self.M ) ) + '\n'
        s += '\t#real = ' + str( len( self.real_m1_lst ) ) + '\n'

        s += 'Classes of conical families:\n'
        for fam in self.fam_lst:
            s += '\t' + str( fam ) + arrow + str( fam.mat_mul( self.M ) ) + '\n'
        s += '\t#real = ' + str( len( self.real_fam_lst ) ) + '\n'

        s += 50 * '=' + '\n'

        return s


