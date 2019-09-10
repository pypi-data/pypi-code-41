# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 15:36:55 2019

@author: Reuben
"""

import unittest

from vartrix import get_container, Name_Space, Container

class Test_Name_Space(unittest.TestCase):
    def test_init(self):
        ns = Name_Space()
        
    def test_create(self):
        ns = Name_Space(obj_cls=Container)
        container = ns.create('test')
        self.assertTrue(isinstance(container, Container))
        self.assertEqual(container.name, 'test')
        
    def test_create_dct(self):
        ns = Name_Space(obj_cls=Container)
        dct = {'a.b': 5, 'c.d': 7}
        container = ns.create('test', dct=dct)
        self.assertTrue(isinstance(container, Container))
        self.assertEqual(container.name, 'test')
        self.assertDictEqual(container, dct)
    
    def test_get_create(self):
        ns = Name_Space(obj_cls=Container)
        container = ns.get('test')
        self.assertTrue(isinstance(container, Container))
        self.assertEqual(container.name, 'test')
        
    def test_get_dct_create(self):
        ns = Name_Space(obj_cls=Container)
        dct = {'a.b': 5, 'c.d': 7}
        container = ns.get('test', dct=dct)
        self.assertTrue(isinstance(container, Container))
        self.assertEqual(container.name, 'test')
        self.assertDictEqual(container, dct)

    def test_get_repeated(self):
        ns = Name_Space(obj_cls=Container)
        container1 = ns.get('test')
        container2 = ns.get('test')
        self.assertTrue(container1 is container2)

class Test_get_container(unittest.TestCase):
    def test_get_container_create(self):
        container = get_container('test')
        self.assertTrue(isinstance(container, Container))
        self.assertEqual(container.name, 'test')

    def test_get_container_repeated(self):
        container1 = get_container('test2')
        container2 = get_container('test2')
        self.assertTrue(container1 is container2)

