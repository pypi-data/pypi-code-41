# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 22:22:31 2019

@author: Reuben
"""

import fastwire

import unittest


class Test_Signal(unittest.TestCase):
    
    
    def test_name_arg(self):
        signal = fastwire.Signal('test_name')
        self.assertEqual(signal.name, 'test_name')
        
    def test_name_kwarg(self):
        signal = fastwire.Signal(name='test_name')
        self.assertEqual(signal.name, 'test_name')

    def test_doc_arg(self):
        signal = fastwire.Signal('test_name', 'test_doc')
        self.assertEqual(signal.doc, 'test_doc')
        
    def test_doc_kwarg(self):
        signal = fastwire.Signal(name='test_name', doc='test_doc')
        self.assertEqual(signal.doc, 'test_doc')
        
    def test_attrs_kwarg(self):
        dct = {'a': 5}
        signal = fastwire.Signal(name='test_name', attrs=dct)
        self.assertEqual(signal.attrs, dct)
    
    def test_method_connect(self):
        signal = fastwire.Signal()

        class A():
            def connected(self, a):
                self._a = a

        a = A()
        receiver_id = signal.connect(a.connected)
        self.assertEqual(list(signal._receivers.keys()), [receiver_id])

    def test_method_disconnect(self):
        signal = fastwire.Signal()

        class A():
            def connected(self, a):
                self._a = a

        a = A()
        receiver_id = signal.connect(a.connected)
        signal.disconnect(receiver_id)
        self.assertEqual(list(signal._receivers.keys()), [])


    def test_method_weakref(self):
        signal = fastwire.Signal()

        class A():
            def connected(self, a):
                self._a = a

        a = A()
        receiver_id = signal.connect(a.connected)
        del a
        self.assertEqual(list(signal._receivers.keys()), [])


    def test_function_connect(self):
        signal = fastwire.Signal()

        def connected(self, a):
            self._a = a

        receiver_id = signal.connect(connected)
        self.assertEqual(list(signal._receivers.keys()), [receiver_id])


    def test_function_disconnect(self):
        signal = fastwire.Signal()

        def connected(self, a):
            self._a = a

        receiver_id = signal.connect(connected)
        signal.disconnect(receiver_id)
        self.assertEqual(list(signal._receivers.keys()), [])


    def test_function_weakref(self):
        signal = fastwire.Signal()

        def connected(self, a):
            self._a = a

        receiver_id = signal.connect(connected)
        del connected
        self.assertEqual(list(signal._receivers.keys()), [])
         
    def test_emit(self):
        signal = fastwire.Signal()

        class A():
            def connected(self, a):
                self._a = a

        a = A()
        signal.connect(a.connected)
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)
        
    def test_mute(self):
        signal = fastwire.Signal()

        class A():
            def connected(self, a):
                self._a = a

        a = A()
        signal.connect(a.connected)

        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)
        signal.mute()
        signal.emit(a=56.1)
        self.assertEqual(a._a, val)
        signal.unmute()
        signal.emit(a=56.1)
        self.assertEqual(a._a, 56.1)
        
        
    def test_fetch(self):
        signal = fastwire.Signal(receiver_limit=1)

        class A():
            def connected(self, a):
                return a

        a = A()
        signal.connect(a.connected)

        val = 5.7
        ret = signal.fetch(a=val)
        self.assertEqual(ret, val)
            
    