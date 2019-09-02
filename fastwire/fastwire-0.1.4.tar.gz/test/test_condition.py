# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 20:40:47 2019

@author: Reuben
"""

import fastwire

import unittest


class My_Condition():
    name = 'default'
    def check(self, a, **kwargs):
        ''' The main check call - must return a boolean '''
        if a < 10:
            return True
        else:
            return False


class Test_Condition(unittest.TestCase):
    

    def test_add_condition(self):
        signal = fastwire.Signal()

        class A():
            def connected(self, a):
                self._a = a

        a = A()
        signal.connect(a.connected)

        signal.add_condition(My_Condition())
        
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)
        signal.emit(a=15)
        self.assertEqual(a._a, val)
        
    def test_remove_condition(self):
        signal = fastwire.Signal()

        class A():
            def connected(self, a):
                self._a = a

        a = A()
        signal.connect(a.connected)

        signal.add_condition(My_Condition())
        signal.remove_condition(My_Condition.name)
        
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)
        signal.emit(a=15)
        self.assertEqual(a._a, 15)