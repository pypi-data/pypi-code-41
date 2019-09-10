# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 08:58:09 2019

@author: Reuben

Conditions apply logic to whether or not particular receivers receive 
particular signals. They are designed to be open, so that you can add your
own condition classes with your own logic.

"""

class Condition():
    ''' Template class for a signal condition 
    
    Class attributes:
        name (str): A class attribute that gives their name. 
    
    '''
    name = 'default'
    def check(self, **kwargs):
        ''' The main check call - must return a boolean 
        
        All Condition classes must implement a method called 'check'. The 
        check method is passed a set of key word arguments provided by the
        sender and the receiver.
        '''
        raise NotImplementedError()
