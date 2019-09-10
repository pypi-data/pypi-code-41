# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 21:17:55 2019

@author: Reuben
"""

import fastwire

import unittest
from timeit import timeit

class Test_Performance(unittest.TestCase):


    def test_signal_emit_performance(self):
        signal = fastwire.Signal()

        def connected(a):
            pass

        def f(a):
            pass
            
        signal.connect(connected)
        e = signal.emit
        n = 100000
        t_ref = timeit('f(5)', globals={'f': f}, number=n)
        t_test = timeit('e(a=5)',
                        globals={'e': e},
                        number=n)
        self.assertTrue(t_test/t_ref < 8)
        
        
    def test_wire_emit_performance(self):
        wire = fastwire.Wire()

        def connected(a):
            pass

        def f(a):
            pass
            
        wire.connect(connected)
        e = wire.emit
        n = 100000
        t_ref = timeit('f(5)', globals={'f': f}, number=n)
        t_test = timeit('e(a=5)',
                        globals={'e': e},
                        number=n)
        self.assertTrue(t_test/t_ref < 1.5)        