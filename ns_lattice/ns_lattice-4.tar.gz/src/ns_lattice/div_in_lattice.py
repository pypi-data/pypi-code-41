'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 11, 2016
@author: Niels Lubbes

Algorithm for computing elements in a unimodular lattice.
We use this algorithm in the context of Neron-Severi lattices
of weak del Pezzo surfaces.

See 
    Arxiv: "Computing curves on real rational surfaces"

'''

import time

from ns_lattice.sage_interface import sage_Combinations
from ns_lattice.sage_interface import sage_Compositions
from ns_lattice.sage_interface import sage_Partitions
from ns_lattice.sage_interface import sage_ZZ
from ns_lattice.sage_interface import sage_Permutations

from ns_lattice.class_ns_tools import NSTools
from ns_lattice.class_div import Div


def get_divs( d, dc, cc, perm = False ):
    '''
    Computes divisors in unimodular lattice with prescribed intersection product. 
    
    Parameters
    ---------- 
    d : Div    
        object d0*e0 + d1*e1 +...+ dr*er such that 
            * product signature equals (1,d.rank()-1)
            * d0>0
            * d1,...,dr<=0                         
    dc : int 
        A positive integer.
    
    cc : int        
        Self intersection.
        
    perm : boolean
        If True, then generators are permuted.      
    
    Returns
    -------
    list<Div> 
    
        Returns a sorted list of "Div" objects
        
            * c = c0*e0 + c1*e1 +...+ cr*er
          
        such that 
                        
            * d.rank() == r+1
            * dc       == d*c   (signature = (1,rank-1))
            * cc       == c*c   (signature = (1,rank-1))           
        
        and each Div object satisfies exactly one
        of the following conditions:    
        
            * c == ei - ej   for 0>i>j>=r,
            * c == ei        for i>0, or          
            * c0 > 0,   c1,...,cr <= 0
                           
        If "perm" is False, then then only one representative
        for each c is returned up to permutation of ei for i>0. 
        For example, e0-e1-e2 and e0-e1-e3 are considered equivalent, 
        and only e0-e1-e2 is returned, since e0-e1-e2>e0-e1-e3 
        (see "get_div_set()" for the ordering). In particular,
        c1 >= c2 >= ... >= cr.  
        
    Note
    ----
        If d=[3]+8*[-1], (dc,cc)==(0,-2) and perm=False 
        then the Div classes are 
        '12', '1123', '212' and '308'.
        See "Div.get_label()" for the notation.
        These classes correspond to the (-2)-classes 
        in the Neron-Severi lattice associated to 
        a weak del Pezzo surface.
        
        If perm==False then only one representative
        for each q is returned up to permutation of 
        ei for i>0. For example, e0-e1-e2 and e0-e1-e3
        are considered equivalent, and only e0-e1-e2
        is returned, since e0-e1-e2>e0-e1-e3 
        (see "Div.__lt__()" for the ordering).             
    '''

    # check if input was already computed
    #
    key = 'get_divs_' + str( ( d, dc, cc, perm ) )
    if key in NSTools.get_tool_dct():
        return NSTools.get_tool_dct()[key]

    # construct div set
    #
    NSTools.p( 'Constructing div set classes for ', ( d, dc, cc, perm ) )
    out_lst = []

    # compute classes of the form ei or ei-ej for i,j>0
    #
    if ( dc, cc ) == ( 1, -1 ) or ( dc, cc ) == ( 0, -2 ):

        m2_lst = []  # list of divisors of the form ei-ej for i,j>0
        m1_lst = []  # list of divisors of the form ei for i>0
        if perm:

            # Example:
            #     >>> list(Combinations( [1,2,3,4], 2 ))
            #     [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
            # Notice that r=d.rank()-1 if c = c0*e0 + c1*e1 +...+ cr*er.
            #
            for comb in sage_Combinations( range( 1, d.rank() ), 2 ):
                m2_lst += [ Div.new( str( comb[0] ) + str( comb[1] ), d.rank() ) ]
            m1_lst += [Div.new( 'e' + str( i ), d.rank() ) for i in range( 1, d.rank() )]

        else:

            # up to permutation of the generators
            # we may assume that i==1 and j==2.
            #
            m2_lst += [ Div.new( '12', d.rank() ) ]
            m1_lst += [ Div.new( 'e1', d.rank() ) ]

        # add the classes that satisfy return
        # specification to the output list
        #
        for c in m1_lst + m2_lst:
            if  ( dc, cc ) == ( d * c, c * c ):
                out_lst += [c]

    #
    # Note: cc = c0^2 - c1^2 -...- cr^2
    #
    c0 = 0
    cur_eq_diff = -1
    while True:

        c0 = c0 + 1
        dc_tail = d[0] * c0 - dc  #    = d1*c1 +...+ dr*cr
        dd_tail = d[0] ** 2 - d * d  # = d1^2  +...+ dr^2
        cc_tail = c0 ** 2 - cc  #      = c1^2  +...+ cr^2

        # not possible according to io-specs.
        #
        if dc_tail < 0 or dd_tail < 0 or cc_tail < 0:
            NSTools.p( 'continue... (c0, dc_tail, dd_tail, cc_tail) =', ( c0, dc_tail, dd_tail, cc_tail ) )
            if dd_tail < 0:
                raise Exception( 'dd_tail =', dd_tail )
            continue

        # Cauchy-Schwarz inequality <x,y>^2 <= <x,x>*<y,y> holds?
        #
        prv_eq_diff = cur_eq_diff
        cur_eq_diff = abs( dc_tail * dc_tail - dd_tail * cc_tail )
        if prv_eq_diff == -1:
            prv_eq_diff = cur_eq_diff

        NSTools.p( 'prv_eq_diff =', prv_eq_diff, ', cur_eq_diff =', cur_eq_diff, ', dc_tail^2 =', dc_tail * dc_tail, ', dd_tail*cc_tail =', dd_tail * cc_tail, ', (c0, dc_tail, dd_tail, cc_tail) =', ( c0, dc_tail, dd_tail, cc_tail ) )

        if prv_eq_diff < cur_eq_diff and dc_tail * dc_tail > dd_tail * cc_tail:
            NSTools.p( 'stop by Cauchy-Schwarz inequality...' )
            break  # out of while loop

        # obtain all possible [d1*c1+1,...,dr*cr+1]
        #
        r = d.rank() - 1
        if perm and len( set( d[1:] ) ) != 1:
            p_lst_lst = sage_Compositions( dc_tail + r, length = r )
        else:
            p_lst_lst = sage_Partitions( dc_tail + r, length = r )

        # data for ETA computation
        total = len( p_lst_lst )
        counter = 0
        ival = 5000

        # obtain [c1,...,cr] from [d1*c1+1,...,dr*cr+1]
        #
        for p_lst in p_lst_lst:

            # ETA
            if counter % ival == 0:
                start = time.time()
            counter += 1
            if counter % ival == 0:
                passed_time = time.time() - start
                NSTools.p( 'ETA in minutes =', passed_time * ( total - counter ) / ( ival * 60 ), ' (', counter, '/', total, '), c0 =', c0, ', prv_eq_diff =', prv_eq_diff, ', cur_eq_diff =', cur_eq_diff )

            # dc_tail=d1*c1 +...+ dr*cr = p1 +...+ pr  with pi>=0
            p_lst = [ p - 1 for p in p_lst]

            # obtain c_tail=[c1,...,cr] from [p1,...,pr]
            valid_part = True
            c_tail = []  # =[c1,...,cr]
            for i in range( 0, len( p_lst ) ):
                if p_lst[i] == 0 or d[i + 1] == 0:
                    c_tail += [p_lst[i]]
                else:
                    quo, rem = sage_ZZ( p_lst[i] ).quo_rem( d[i + 1] )
                    if rem != 0:
                        valid_part = False
                        break  # out of i-for-loop
                    else:
                        c_tail += [ quo ]
            if not valid_part:
                continue

            # add to out list if valid
            #
            c = Div( [c0] + c_tail )
            if c.rank() == d.rank() and ( dc, cc ) == ( d * c, c * c ):
                if perm and len( set( d[1:] ) ) == 1:
                    # since d1==...==dr we do not have to
                    # check each permutation.
                    for pc_tail in sage_Permutations( c_tail ):
                        out_lst += [Div( [c0] + list( pc_tail ) )]
                else:
                    out_lst += [c]

    # sort list of "Div" objects
    out_lst.sort()


    # cache output
    NSTools.get_tool_dct()[key] = out_lst
    NSTools.save_tool_dct()

    return out_lst


def get_indecomp_divs( c_lst, d_lst ):
    '''
    Parameters
    ----------
    c_lst : list<Div>        
        Typically output of "get_divs(...)"
    d_lst : list<Div>
        Typically a list of (-2)-classes.

    Returns
    -------
    list<Div>
        Returns a list of "Div" objects c in c_lst, 
        so that c*d >= 0 for all d in "d_lst".                
        
    Note
    ----
    If the Div object represent effective divisor classes in 
    a the Neron-Severi lattice of a weak del Pezzo 
    surface and if d_lst are the classes of singularities,
    then the output correspond to "indecomposable" classes.
    Such classes cannot be written as the sum of effective 
    divisors.    
    '''

    # check positivity against "d_lst"
    out_lst = []
    for c in c_lst:
        indecomp = True
        for d in d_lst:
            if d * c < 0:
                indecomp = False
                break  # out of for loop
        if indecomp:
            out_lst += [c]

    return out_lst


def get_ak( rank ):
    '''
    Parameters
    ----------
    rank : int
    
    Returns
    -------
    Div
        A Div object of given rank of the form
        
            3e0 - e1 - ... - er
        
        Mathematically this is the anticanonical 
        class of the blowup of the projective plane.    
    '''
    return Div( [3] + ( rank - 1 ) * [-1] )

