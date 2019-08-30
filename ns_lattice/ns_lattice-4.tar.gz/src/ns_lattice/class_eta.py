'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 27, 2018

@author: Niels Lubbes
'''

from ns_lattice.sage_interface import sage_n

from ns_lattice.class_ns_tools import NSTools

import time


class ETA( object ):
    '''
    For estimating the time it takes for a loop in a program to terminate 
    (ETA=estimated time of arrival).
    During the loop feedback is printed.  
    '''

    def __init__( self, total, ival ):
        '''
        Should be called before a loop in starts.        
        
        Parameters
        ----------
        total: int
            Number of times the loop needs to be traced.
        
        ival : int
            Nonzero number of traced loops in program until
            feedback about etimated end time is printed        
        '''

        # total number of loops
        self.total = total

        # number of loops after which eta is updated
        self.ival = 1
        if ival > 0:
            self.ival = ival

        # loop counter
        self.counter = 0

        # times
        self.ini_time = self.time()  # time when method was called
        self.prv_time = self.ini_time  # time which is updated after ival loops.
        self.eta_time = 0  # estimated time of arrival in minutes


    def time( self ):
        return time.time()


    def update( self, *info_lst ):
        '''
        Should be called inside a loop.
        
        Prints an estimation for the time it takes for a program to 
        terminate (ETA for short). We refer to the program termination 
        as arrival.
        
        Parameters
        ----------
        *info_lst : string
            Variable length argument list consisting of 
            additional information that is printed together with ETA.
        '''

        if self.counter % self.ival == 0:
            cur_time = self.time()

            ival_time = ( cur_time - self.prv_time ) / ( 60 * self.ival )
            passed_time = sage_n( ( cur_time - self.ini_time ) / 60, digits = 5 )
            self.eta_time = sage_n( ival_time * ( self.total - self.counter ), digits = 5 )

            s = ''
            for info in info_lst:
                s += str( info ) + ' '

            NSTools.p( 'ETA =', self.eta_time, 'm,',
                       'counter =', self.counter, '/', self.total, ',',
                       'time =', passed_time, 'm,',
                       'info =', s )

            # update previous time
            self.prv_time = cur_time


        # increase counter
        self.counter += 1

