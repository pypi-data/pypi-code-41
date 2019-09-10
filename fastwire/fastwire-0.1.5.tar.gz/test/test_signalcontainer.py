# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 22:46:33 2019

@author: Reuben
"""

import fastwire

import unittest


class Test_SignalContainer(unittest.TestCase):
    
    def test_unnamed_signal(self):
        sc = fastwire.SignalContainer()
        signal = sc.signal()
        self.assertEqual(signal.__class__, fastwire.Signal)
        
    def test_named_signal(self):
        sc = fastwire.SignalContainer()
        signal = sc.signal('this_name')
        self.assertEqual(signal.name, 'this_name')
        
    def test_create_on_demand(self):
        sc = fastwire.SignalContainer()
        signal = sc['this_name']
        self.assertEqual(signal.name, 'this_name')
        self.assertEqual(signal.__class__, fastwire.Signal)

    def test_get(self):
        sc = fastwire.SignalContainer()
        wire = sc.get('this_name')
        self.assertEqual(wire.name, 'this_name')
        
    def test_get_repeated(self):
        sc = fastwire.SignalContainer()
        wire_1 = sc.get('this_name')
        wire_2 = sc.get('this_name')
        self.assertEqual(wire_1, wire_2)