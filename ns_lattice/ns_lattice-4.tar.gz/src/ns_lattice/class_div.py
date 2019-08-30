'''
Created on Aug 11, 2016
@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_diagonal_matrix
from ns_lattice.sage_interface import sage_vector


class Div:
    '''Element in Neron-Severi lattice.
    
    The class represents a divisor class in the Neron-Severi lattice
    with respect to the standard basis:
        <e0,e1,e2,...>
    
    
    Attributes
    ----------            
    e_lst : list<sage_ZZ>
        List describes a divisor in terms of the standard basis. 
    
    int_mat : sage_matrix<sage_ZZ>
        A matrix over ZZ of rank "len(e_lst)" represents
        the unimodular intersection product for the divisor. 
        
    '''

    # static variable
    #
    short_output = True


    # static list of intersection matrices
    #
    int_mat_lst = []


    def __init__( self, e_lst = 9 * [0], int_mat = None ):
        '''        
        Return
        ------
        Div
            Constructor (called when instantiating object).
              
            If "int_mat==None" then the default 
            diagonal matrix has signature (+-...-). 
            This matrix determines the intersection
            product of divisors.
        '''

        self.e_lst = list( e_lst )


        #
        # equal "self.int_mat" for each instantiated Div object references
        # to a unique matrix, so that no new matrix is instantiated for each
        # Div object. Maybe this is already ensured by Sage library, but just
        # to be on the safe side.
        #
        if int_mat == None:
            int_mat = sage_diagonal_matrix( sage_ZZ, [1] + ( self.rank() - 1 ) * [-1] )
        if int_mat not in Div.int_mat_lst:
            Div.int_mat_lst += [int_mat]
        idx = Div.int_mat_lst.index( int_mat )
        self.int_mat = Div.int_mat_lst[idx]



    @staticmethod
    def new( lbl, rank = 9 ):
        '''
        Parameters
        ----------
        lbl : string 
            A string with format as output of "self.get_label()".
        
        rank : int 
            Integer representing rank of Neron-Severi lattice in which "Div" lives.
        
        Returns
        -------
            The "Div" corresponding to the label 
            such that "len(self.e_lst)>=rank".
        '''

        c = Div( rank * [0] )  # zero divisor class

        if 'e' in lbl:

            s = lbl
            if 'e0' in s:

                # cases: 'e0...', '-e0...', '3e0...' or '-2e0...'
                if s[0:2] == 'e0':
                    c.e_lst = [1]
                    s = s[2:]
                elif s[0:3] == '-e0':
                    c.e_lst = [-1]
                    s = s[3:]
                else:  # '3e0...' or '-2e0...'
                    c.e_lst = [ int( s.split( 'e0' )[0] ) ]  # [4] if lbl='4h+3e...'
                    s = s.split( 'e0' )[1]  # for example '+3e2-2e5+6e7+e8'

            else:
                c.e_lst = [0]
                s = lbl

            coef_e = ''
            idx = 0
            last_i = 0  # ei
            while idx < len( s ):
                if s[idx] != 'e':
                    coef_e += s[idx]
                    idx += 1
                elif s[idx] == 'e':
                    coef_i = ''
                    idx += 1
                    while idx < len( s ) and s[idx] not in ['+', '-']:
                        coef_i += s[idx]
                        idx += 1
                    i = int( coef_i )
                    if coef_e == '-': coef_e = '-1'
                    if coef_e in ['+', '']: coef_e = '1'
                    c.e_lst += ( i - last_i - 1 ) * [0] + [int( coef_e )]
                    coef_e = ''
                    last_i = i

        else:  # label of (-2)-class

            if rank > 9:
                raise ValueError( 'For (-2)-classes we expect the rank to be at most 9: ', rank )

            # check whether the label is negative
            if lbl[0] == '-':
                neg = True
                lbl = lbl[1:]
            else:
                neg = False

            # '12' ---> e1-e2
            if len( lbl ) == 2:
                c.e_lst[ int( lbl[0] ) ] = 1
                c.e_lst[ int( lbl[1] ) ] = -1

            # '1123' ---> e0-e1-e2-e3
            elif len( lbl ) == 4 and lbl[0] == '1':
                c.e_lst[0] = int( lbl[0] )
                c.e_lst[ int( lbl[1] ) ] = -1
                c.e_lst[ int( lbl[2] ) ] = -1
                c.e_lst[ int( lbl[3] ) ] = -1

            # '212' ---> 2e0-e3-e4-...-e8
            elif len( lbl ) == 3 and lbl[0] == '2':
                c.e_lst = 9 * [-1]
                c.e_lst[0] = int( lbl[0] )
                c.e_lst[ int( lbl[1] ) ] = 0
                c.e_lst[ int( lbl[2] ) ] = 0
                if rank != 9 and set( c.e_lst[rank:] ) != set( [0] ):
                    raise ValueError( 'Rank too low for label: ', rank, lbl )
                c.e_lst = c.e_lst[:rank]

            # '308' ---> 3e0-e1-e2-...-e7-2e8
            elif len( lbl ) == 3 and lbl[0] == '3' and lbl[1] == '0':
                c.e_lst = 9 * [-1]
                c.e_lst[0] = int( lbl[0] )
                c.e_lst[ int( lbl[2] ) ] = -2

            else:  # unknown label
                raise ValueError( 'Label has incorrect format: ', lbl )

            # for example '-12'=[0,-1,1,0,0,...]
            if neg:
                c.e_lst = [ -e for e in c.e_lst ]


        # end handling label of (-2)-class


        # update rank
        c.e_lst = c.e_lst + ( rank - len( c.e_lst ) ) * [0]

        return c


    def rank( self ):
        return len( self.e_lst )


    def is_positive( self ):
        '''
        Returns
        -------
        bool
            Return True iff the first nonzero entry of the self.e_lst 
            is positive. The zero divisor is also positive.
        '''
        for e in self.e_lst:
            if e != 0:
                return e > 0
        return True


    @staticmethod
    def get_min_rank( lbl ):
        '''
        Parameters
        ----------
        lbl : string
            A string with format as output of "self.get_label()".
        
        Returns
        -------
        int
            The minimal rank of the "Div" object with a given label.
        
        Examples
        --------
        >>> get_min_rank('78')
        9
            
        >>> get_min_rank('301')
        9
            
        >>> get_min_rank('12')
        3
        '''
        d = Div.new( lbl )
        lst = [ e for e in d.e_lst ]
        while lst[-1] == 0 and lst != []:
            lst.pop()

        return len( lst )


    def get_basis_change( self, B ):
        '''
        Parameters
        ----------
        B : sage_matrix   
            A matrix whose rows correspond to generators of 
            a new basis. We assume that the intersection matrix 
            for this basis is the default diagonal matrix with 
            diagonal (1,-1,...,-1).
        
        Returns
        -------
        Div
            A new "Div" object, which represents the current divisor  
            with respect to a new basis.                
        '''
        new_int_mat = B * self.int_mat * B.T
        new_e_lst = self.mat_mul( ~( B.T ) ).e_lst

        return Div( new_e_lst, new_int_mat )


    def __get_minus_two_label( self ):
        '''
        Private helper method for "get_label()"
        
        Parameters
        ----------
            self : Div 
                self*self==-2 and self.rank<=9.
        
        Returns
        -------
        string 
            See output documents for self.get_label()
        '''

        if self * self != -2 or self.rank() > 9:
            raise ValueError( 'Unexpected input for __get_mt_label: ', self.e_lst )

        # first non-zero coefficient negative?
        neg = [e < 0 for e in self.e_lst if e != 0][0]

        # check whether the label should start with minus symbol
        if neg:
            tmp = [-e for e in self.e_lst]
        else:
            tmp = self.e_lst

        # set of non-zero coefficients for ei.
        oset = set( [ e for e in tmp[1:] if e != 0 ] )

        # e1-e2 ---> '12'
        if tmp[0] == 0 and oset == set( [1, -1] ):
            lbl = ''
            for i in range( 1, len( tmp ) ):
                if tmp[i] != 0:
                    lbl += str( i )

        # e0-e1-e2-e3 ---> '1123'
        elif tmp[0] == 1 and oset == set( 3 * [-1] ):
            lbl = '1'
            for i in range( 1, len( tmp ) ):
                if tmp[i] != 0:
                    lbl += str( i )

        # 2e0-e3-e4-...-e8 ---> '212'
        elif tmp[0] == 2 and oset == set( 6 * [-1 ] ):
            lbl = '2'
            for i in range( 1, len( tmp ) ):
                if tmp[i] == 0:
                    lbl += str( i )

        # 3e0-e1-e2-...-e7-2e8 ---> '308'
        elif tmp[0] == 3 and oset == set( 7 * [-1 ] + [-2] ):
            lbl = '30'
            for i in range( 1, len( tmp ) ):
                if tmp[i] == -2:
                    lbl += str( i )

        if neg:
            lbl = '-' + lbl  # for example: 12 --> -12

        return lbl


    def get_abbr_label( self ):
        '''
        Returns
        -------
        string        
            We describe the output label in terms of  examples.
            
                > e1                --->  'e1'
                > e1-e2             --->  'e12'                  
                > 2e0-e1-e2-e4-e5   --->  '2e1245'
                > e0-e1             --->  '1e1'  
        
            This options only works for special cases.
            The cases which are covered are (-1)- and (-2)-classes, 
            and classes of conical families on weak Del Pezzo surfaces,
            with respect to the basis with intersection product
            defined by the diagonal matrix with diagonal (1,-1,...,-1).                        
        '''
        np1 = len( [e for e in self.e_lst[1:] if e == 1] )
        nm1 = len( [e for e in self.e_lst[1:] if e == -1] )
        n01 = len( [e for e in self.e_lst[1:] if e > 1 or e < -1] )

        if n01 == 0 and self[0] in range( 0, 10 ):

            # e1
            if self[0] == 0 and np1 == 1 and nm1 == 0:
                return 'e' + str( self.e_lst.index( 1 ) )

            # e1-e2
            if self[0] == 0 and np1 == 1 and nm1 == 1:
                return 'e' + str( self.e_lst.index( 1 ) ) + str( self.e_lst.index( -1 ) )

            # 2h-e1-e2-e3-e4-e5 or h-e1
            if self[0] in range( 0, 10 ) and np1 == 0 and nm1 > 0:
                lbl = str( self[0] ) + 'e'
                for i in range( 1, len( self.e_lst ) ):
                    if self[i] != 0:
                        lbl += str( i )
                return lbl

        raise ValueError( 'Input is not treated by this function (use get_label() instead):', self.e_lst )


    def get_label( self, abbr = False ):
        '''
        Parameters
        ----------
            abbr : boolean 
            
        Returns
        -------
        string
            We describe the output label in terms of examples.
                
            If "abbr==True" and self*self==-2 and self.rank()<=9:
            
                >  e1-e2                ---> '12'
                > -e1+e2                ---> '-12'
                >  e0-e1-e2-e3          ---> '1123'
                >  2e0-e3-e4-...-e8     ---> '212'
                >  3e0-e1-e2-...-e7-2e8 ---> '308'
                > -3e0+e1+e2+...+e7+2e8 ---> '-308'  
                
            For the remaining cases not treated above:
            
                > 3e0-2e1-13e2-4e3  ---> '3e0-2e1-13e2-4e3'                                                    
        '''

        divK = Div( [-3] + ( self.rank() - 1 ) * [1] )

        # treat cases for (-2)-label
        #
        if abbr and self * self == -2 and self.rank() <= 9 and self * divK == 0:
            return self.__get_minus_two_label()


        # from this point on we treat the general case
        #
        lbl = ''
        for i in range( 0, len( self.e_lst ) ):
            val = self[i]
            if val != 0:

                if val == 1:
                    if lbl != '': lbl += '+'
                elif val == -1:
                    lbl += '-'
                else:
                    if val > 1 and lbl != '':
                        lbl += '+'
                    lbl += str( val )

                lbl += 'e' + str( i )

        return lbl


    def mat_mul( self, M ):
        '''
        Parameters
        ----------
            M : sage_matrix
                A matrix with self.rank() columns.
        
        Returns
        -------
        Div
            Returns a "Div" object that is a result of 
            applying the linear transformation corresponding
            to "M" to itself. 
        '''
        v = sage_vector( self.e_lst ).column()
        return Div( ( M * v ).list() )


    def int_mul( self, n ):
        '''
        Parameters
        ----------
            n : int
        
        Returns
        -------
        Div
            Returns a "Div" object that is a result of multiplying 
            with the scalar "n". 
        '''
        return self.mat_mul( sage_diagonal_matrix( self.rank() * [n] ) )


    # operator overloading for ==
    def __eq__( self, other ):
        return self.e_lst == other.e_lst


    # operator overloading for !=
    def __ne__( self, other ):
        return not self.__eq__( other )


    # operator overloading for <
    # Used for sorting lists of "Div"-objects:
    #     <http://stackoverflow.com/questions/1227121/compare-object-instances-for-equality-by-their-attributes-in-python>
    def __lt__( self, other ):
        '''
        Parameters
        ----------
            other : Div

        Returns
        -------
        bool
 
            Here are some examples to explain 
            the ordering we use for div classes
                            
            e1 < e2
            e0-e1-e2 < e0-e1-e3
            1123 < 308  
            1123 < 1124
            12 < 1123 
            12 < 13
            12 < 34
        '''
        if self.rank() != other.rank():
           return self.rank() < other.rank()

        a = self.e_lst
        b = other.e_lst

        if sum( a ) == sum( b ) == 1 and set( a ) == set( b ) == {0, 1}:
            return b < a  # e1 < e2

        a = [a[0]] + [ -elt for elt in reversed( a[1:] )]
        b = [b[0]] + [ -elt for elt in reversed( b[1:] )]

        return a < b  # lexicographic order


    # operator overloading for *
    def __mul__( self, div ):
        '''
        Parameters
        ----------
        div : Div
        
        Returns
        -------
        Div
            The intersection product of "self" and 
            "div" wrt. to matrix "self.int_mat".
        '''

        row_vec = sage_vector( sage_ZZ, self.e_lst ).row()
        col_vec = sage_vector( sage_ZZ, div.e_lst ).column()
        mat = self.int_mat

        v = row_vec * mat * col_vec

        return v[0][0]


    # operator overload for +
    def __add__( self, div ):
        v = sage_vector( sage_ZZ, self.e_lst ) + sage_vector( sage_ZZ, div.e_lst )
        return Div( list( v ) )


    # operator overload for -
    def __sub__( self, div ):
        v = sage_vector( sage_ZZ, self.e_lst ) - sage_vector( sage_ZZ, div.e_lst )
        return Div( list( v ) )


    # operator overloading for []
    def __getitem__( self, index ):
        return self.e_lst[index]


    # operator overloading for []
    def __setitem__( self, index, item ):
        self.e_lst[index] = item


    # overloading for str(.): human readable string representation of object
    def __str__( self ):
        if Div.short_output:
            return self.get_label()
        else:
            return str( self.e_lst )


    # overloading "__repr__()" as well, since python call this for Div objects in a list
    def __repr__( self ):
        return self.__str__()


    # so that lists of this object can be used with set()
    def __hash__( self ):
        return hash( self.__str__() + '__' + str( self.rank() ) )
