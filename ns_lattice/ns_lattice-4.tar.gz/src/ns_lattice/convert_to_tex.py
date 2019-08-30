'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Dec 14, 2017
@author: Niels Lubbes
'''

from ns_lattice.class_div import Div

from ns_lattice.class_dp_lattice import DPLattice

from ns_lattice.class_ns_tools import NSTools

from ns_lattice.sage_interface import sage_identity_matrix


def cls_to_tex():
    '''
    Create tex code for the output of DPLattice.get_cls()
    
  
    Returns
    -------
    string
        A string representing a table of tables in Tex format.
        The table represent the classification of Neron-Severi
        lattice of weak del Pezzo surfaces.       
    '''

    # create a list of occuring divisors
    #
    div_lst = []
    for rank in range( 3, 9 + 1 ):
        for dpl in DPLattice.get_cls( rank ):

            # construct list for involution (e0,...,er)|-->(i0,...,ir)
            i_lst = [Div( row ).mat_mul( dpl.M ) for row in sage_identity_matrix( rank ) ]

            # add each divisor that occurs to div_lst
            for elt in i_lst + dpl.d_lst:
                div_lst += [   Div( elt.e_lst + ( 9 - len( elt.e_lst ) ) * [0] ) ]
    div_lst = list( set( div_lst ) )
    div_lst.sort()
    e0 = Div( [1, 0, 0, 0, 0, 0, 0, 0, 0 ] )
    div_lst.remove( e0 )
    div_lst = [e0] + div_lst


    # create dictionary characters for elements in div_lst
    #
    abc = 'abcdefghijklmnopqrstuvwxyz'
    ch_lst = []
    ch_lst += [ '\\frac{' + ch1 + '}{' + ch2 + '}\\!' for ch1 in '0123456789' for ch2 in '0123456789' ]
    ch_lst += [ '\\frac{' + ch1 + '}{' + ch2 + '}\\!' for ch1 in '0123456789' for ch2 in 'abcdef' ]


    NSTools.p( '(len(ch_lst), len(div_lst)) =', ( len( ch_lst ), len( div_lst ) ) )

    assert len( ch_lst ) >= len( div_lst )


    # create legend and dictionary
    #
    lgd_lst = []
    sym_dct = {}
    for i in range( len( div_lst ) ):
        sym_dct.update( {str( div_lst[i] ):ch_lst[i]} )
        lgd_lst += [['$' + ch_lst[i] + '$ :', ( '$' + str( div_lst[i] ) + '$' ).replace( 'e', 'e_' ) ]]
    while len( lgd_lst ) % 3 != 0:
        lgd_lst += [['', '']]
    nnrows = len( lgd_lst ) / 3

    # create tex for legend
    #
    tex_lgd = ''
    tex_lgd += '\\begin{table}\n'
    tex_lgd += '\\setstretch{1.4}\n'
    tex_lgd += '\\tiny\n'
    tex_lgd += '\\caption{Classification of Neron-Severi lattices of weak del Pezzo surfaces (see THM{nsl})}\n'
    tex_lgd += '\\label{tab:nsl}\n'
    tex_lgd += 'A dictionary for symbols in the columns $\\sigma_A$ and $B$:\n\\\\\n'
    tex_lgd += '\\begin{tabular}{@{}l@{}l@{~~~~}l@{}l@{~~~~}l@{}l@{}}\n'
    for idx in range( nnrows ):
        c1, c2, c3, c4, c5, c6 = lgd_lst[idx] + lgd_lst[idx + nnrows] + lgd_lst[idx + 2 * nnrows]
        tex_lgd += c1 + ' & ' + c2 + ' & ' + c3 + ' & ' + c4 + ' & ' + c5 + ' & ' + c6
        tex_lgd += '\\\\\n'
    tex_lgd += '\\end{tabular}\n'
    tex_lgd += '\\end{table}\n\n'

    # number of rows of the big table
    #
    nrows = 57

    # dictionary for replacing string symbols
    #
    rep_dct = {'A':'A_', 'D':'D_', 'E':'E_', '{':'\\underline{', '[':'\\udot{', ']':'}'}

    # create classification table
    #
    tab_lst = []

    # rank 1 and 2
    tab9 = [['i  ', '$9$', "$A_0 $", '$A_0$', '$0$', '$1$', '']]
    tab8 = [['ii ', '$8$', "$A_0 $", '$A_0$', '$0$', '$2$', ''],
            ['iii', '$8$', "$A_0 $", '$A_0$', '$0$', '$1$', ''],
            ['iv ', '$8$', "$A_0 $", '$A_0$', '$1$', '$1$', ''],
            ['v  ', '$8$', "$A_0 $", '$A_1$', '$0$', '$1$', '']]
    tab_lst += [ tab9, tab8 ]

    # rank 3,4,5,6,7,8 and 9
    idx = 0
    Mtype_lst = ['A1', '4A1']  # for breaking up table for degree 2 case
    for rank in range( 3, 9 + 1 ):

        tab = []
        for dpl in DPLattice.get_cls( rank ):

            col1 = '$' + str( idx ) + '$'

            col2 = '$' + str( dpl.get_degree() ) + '$'

            col3 = '$' + str( dpl.get_marked_Mtype() ) + '$'
            for key in rep_dct:
                col3 = str( col3 ).replace( key, rep_dct[key] )

            col4 = '$' + str( dpl.get_real_type() ) + '$'
            for key in rep_dct:
                col4 = str( col4 ).replace( key, rep_dct[key] )

            col5 = '$' + str( dpl.get_numbers()[4] ) + '$'

            col6 = '$' + str( dpl.get_numbers()[5] ) + '$'

            i_lst = [ str( Div( rw ).mat_mul( dpl.M ) ) for rw in sage_identity_matrix( rank ) ]
            col7 = ''
            for i in i_lst:
                col7 += sym_dct[i]
            if col7 in ['012', '0123', '01234', '012345', '0123456', '01234567', '012345678']:
                col7 = ''

            col8 = ''
            for d in dpl.d_lst:
                col8 += sym_dct[str( d )]

            # these subroot systems cannot be realized as weak del Pezzo surfaces
            if col4 in ['$7\underline{A_1}$', '$8\underline{A_1}$', '$4\underline{A_1}+\underline{D_4}$']:
                col1 = '$\\times$'

            # break (sometimes) the table for degree 2 according to Mtype
            if dpl.get_degree() == 2 and dpl.Mtype in Mtype_lst:
                nheaders = len( tab ) / nrows  # each header shifts the row number
                while len( tab ) % nrows != nrows - 1 - nheaders:  # add rows until end of table
                    tab += [7 * ['']]
                Mtype_lst.remove( dpl.Mtype )

            # add row
            tab += [[col1, col2, col3, col4, col5, col6, '$' + col7 + '||\!' + col8 + '$' ]]
            idx += 1

        tab_lst += [ tab ]


    # reformat table
    #
    #         i     d     A     B     E     G     Ac%Bc
    hl = '@{~}l@{~~~}l@{~~~}l@{~~}l@{~~}l@{~~}l@{~~}l@{}'
    hrow = ['', 'd', '$D(A)$', '$D(B)$', '$\#E$', '$\#G$', '$\sigma_A||B$']
    etab_lst = []
    etab = [hrow]
    tab_idx = 0
    for tab in tab_lst:

        for row in tab:
            if len( etab ) >= nrows:
                etab_lst += [etab]
                etab = [hrow]
            etab += [row]

        if len( etab ) < nrows and tab_idx <= 3:
            etab += [7 * [''], 7 * ['']]  # add two empty rows to separate tables with different rank
        else:
            while len( etab ) < nrows:
                etab += [7 * ['']]  # add empty rows to fill up table
            etab_lst += [etab]
            etab = [hrow]

        tab_idx += 1
    NSTools.p( 'etab_lst: ', [len( etab ) for etab in etab_lst] )


    # create tex for main classification table
    #
    tex_tab = ''
    tab_idx = 0
    for etab in etab_lst:

        if tab_idx % 2 == 0:
            tex_tab += '\\begin{table}\n'
            tex_tab += '\\setstretch{1.6}\n'
            tex_tab += '\\centering\\tiny\n'
            tex_tab += '\\begin{tabular}{@{}l@{\\hspace{1cm}}l@{}}\n'
        elif tab_idx % 2 == 1:
            tex_tab += '&\n'

        tex_tab += '\\begin{tabular}{' + hl + '}\n'
        for row in etab:
            col1, col2, col3, col4, col5, col6, col78 = row
            tex_tab += col1 + ' & ' + col2 + ' & ' + col3 + ' & ' + col4 + ' & '
            tex_tab += col5 + ' & ' + col6 + ' & ' + col78
            tex_tab += ' \\\\\n'
            if row == hrow:
                tex_tab += '\\hline\n'

        tex_tab += '\\end{tabular}\n'

        if tab_idx % 2 == 1:
            tex_tab += '\\end{tabular}\n'
            tex_tab += '\\end{table}\n\n'

        tab_idx += 1

    if tab_idx % 2 == 1:
        tex_tab += '&\n'
        tex_tab += '\\end{tabular}\n\n'

    # creating tex for commands
    tex_cmd = ''
    tex_cmd += '\\newcommand{\\udot}[1]{\\tikz[baseline=(todotted.base)]{\\node[inner sep=1pt,outer sep=0pt] (todotted) {$#1$};\\draw[densely dotted] (todotted.south west) -- (todotted.south east);}}'
    tex_cmd += '\n'
    tex_cmd += '\\newcommand{\\udash}[1]{\\tikz[baseline=(todotted.base)]{\\node[inner sep=1pt,outer sep=0pt] (todotted) {$#1$};\\draw[densely dashed] (todotted.south west) -- (todotted.south east);}}'
    tex_cmd += '\n\n'

    out = tex_cmd + tex_lgd + tex_tab

    return out

