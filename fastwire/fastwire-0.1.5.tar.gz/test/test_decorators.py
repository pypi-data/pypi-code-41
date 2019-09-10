# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 22:47:12 2019

@author: Reuben
"""

import fastwire

import unittest


class Test_Signal_Decorators(unittest.TestCase):
    
    def test_receive(self):
        signal = fastwire.Signal()

        class A(fastwire.Wired):
            @fastwire.receive(signal)
            def connected(self, a):
                self._a = a

        a = A()
        self.assertEqual(len(signal._receivers.keys()), 1)

        
    def test_supply(self):
        signal = fastwire.Signal(receiver_limit=1)

        class A(fastwire.Wired):
            @fastwire.supply(signal)
            def connected(self, a):
                self._a = a

        a = A()
        self.assertEqual(len(signal._receivers.keys()), 1)

        
    def test_receive_emit(self):
        signal = fastwire.Signal()

        class A(fastwire.Wired):
            @fastwire.receive(signal)
            def connected(self, a):
                self._a = a

        a = A()
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)


    def test_fn_receive_emit(self):
        signal = fastwire.Signal()

        test = [0]
        
        @fastwire.fn_receive(signal)
        def connected(a):
            test[0] = a

        val = 5.7
        signal.emit(a=val)
        self.assertEqual(test[0], val)


class Test_Wire_Decorators(unittest.TestCase):
    
    def test_receive(self):
        wire = fastwire.Wire()

        class A(fastwire.Wired):
            @fastwire.receive(wire)
            def connected(self, a):
                self._a = a

        a = A()
        self.assertFalse(wire._emit == wire.emit)

        
    def test_supply(self):
        wire = fastwire.Wire()

        class A(fastwire.Wired):
            @fastwire.supply(wire)
            def connected(self, a):
                self._a = a

        a = A()
        self.assertFalse(wire._emit == wire.emit)

        
    def test_receive_emit(self):
        wire = fastwire.Wire()

        class A(fastwire.Wired):
            @fastwire.receive(wire)
            def connected(self, a):
                self._a = a

        a = A()
        val = 5.7
        wire.emit(a=val)
        self.assertEqual(a._a, val)


    def test_fn_receive_emit(self):
        wire = fastwire.Wire()

        test = [0]
        
        @fastwire.fn_receive(wire)
        def connected(a):
            test[0] = a

        val = 5.7
        wire.emit(a=val)
        self.assertEqual(test[0], val)

class Test_Box_Decorators(unittest.TestCase):
    def test_receive_emit_box(self):
        box = fastwire.SignalBox()
        box.add('test')

        class A(fastwire.Wired):
            @fastwire.receive('test_signal', box=box)
            def connected(self, a):
                self._a = a

        a = A()
        signal = box['test_signal']
        self.assertEqual(signal.name, 'test_signal')
        self.assertEqual(len(signal._receivers.keys()), 1)
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)
        
    def test_receive_emit_box_decorator(self):
        box = fastwire.SignalBox()
        box.add('test')

        class A(fastwire.Wired):
            @box.receive('test_signal')
            def connected(self, a):
                self._a = a

        a = A()
        signal = box['test_signal']
        self.assertEqual(len(signal._receivers.keys()), 1)
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)
        
    def test_supply_emit_box_decorator(self):
        box = fastwire.SignalBox()
        box.add('test')

        class A(fastwire.Wired):
            @box.supply('test_signal')
            def connected(self, a):
                self._a = a

        a = A()
        signal = box['test_signal']
        self.assertEqual(signal.name, 'test_signal')
        self.assertEqual(len(signal._receivers.keys()), 1)
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)
        
    def test_fn_receive_emit_box(self):
        box = fastwire.SignalBox()
        box.add('test')

        test = [0]
        
        @fastwire.fn_receive('test_signal', box=box)
        def connected(a):
            test[0] = a
            
        signal = box['test_signal']
        self.assertEqual(len(signal._receivers.keys()), 1)
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(test[0], val)
        
        
class Test_Container_Decorators(unittest.TestCase):
    def test_receive_emit_container(self):
        container = fastwire.SignalContainer()

        class A(fastwire.Wired):
            @fastwire.receive('test_signal', container=container)
            def connected(self, a):
                self._a = a

        a = A()
        signal = container['test_signal']
        self.assertEqual(len(signal._receivers.keys()), 1)
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)
        
    def test_receive_emit_container_decorator(self):
        container = fastwire.SignalContainer()

        class A(fastwire.Wired):
            @container.receive('test_signal')
            def connected(self, a):
                self._a = a

        a = A()
        signal = container['test_signal']
        self.assertEqual(len(signal._receivers.keys()), 1)
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)
        

    def test_supply_emit_container_decorator(self):
        container = fastwire.SignalContainer()

        class A(fastwire.Wired):
            @container.supply('test_signal')
            def connected(self, a):
                self._a = a

        a = A()
        signal = container['test_signal']
        self.assertEqual(len(signal._receivers.keys()), 1)
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(a._a, val)

        
    def test_fn_receive_emit_container(self):
        container = fastwire.SignalContainer()

        test = [0]
        
        @fastwire.fn_receive('test_signal', container=container)
        def connected(a):
            test[0] = a

        signal = container['test_signal']
        self.assertEqual(len(signal._receivers.keys()), 1)
        val = 5.7
        signal.emit(a=val)
        self.assertEqual(test[0], val)