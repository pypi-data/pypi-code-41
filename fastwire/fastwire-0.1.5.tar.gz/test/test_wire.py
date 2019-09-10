# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 09:22:35 2019

@author: Reuben
"""

import fastwire

import unittest

class Test_Wire(unittest.TestCase):
    
    def test_name_arg(self):
        wire = fastwire.Wire('test_name')
        self.assertEqual(wire.name, 'test_name')
        
    def test_name_kwarg(self):
        wire = fastwire.Wire(name='test_name')
        self.assertEqual(wire.name, 'test_name')

    def test_doc_arg(self):
        wire = fastwire.Wire('test_name', 'test_doc')
        self.assertEqual(wire.doc, 'test_doc')
        
    def test_doc_kwarg(self):
        wire = fastwire.Wire(name='test_name', doc='test_doc')
        self.assertEqual(wire.doc, 'test_doc')
        
    def test_attrs_kwarg(self):
        dct = {'a': 5}
        wire = fastwire.Wire(name='test_name', attrs=dct)
        self.assertEqual(wire.attrs, dct)
    
    def test_method_emit(self):
        wire = fastwire.Wire()

        class A():
            def connected(self, a):
                self._a = a
                return a

        a = A()
        wire.connect(a.connected)
        wire.emit(5)
        self.assertEqual(a._a, 5)