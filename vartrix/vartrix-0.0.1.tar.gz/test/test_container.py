# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 19:31:41 2019

@author: Reuben
"""


import unittest

from vartrix.container import Container

def get_c():
    c = Container()
    c.set('a.b', 5)
    c.set('b.c', 7)
    return c

class View_Mock():
    def _view_update(self, key, val):
        self.key = key
        self.val = val
        
    def refresh(self):
        self.refresh_val = True

    def check_refresh(self):
        if self.dirty:
            self.refresh()
        

class Test_Container(unittest.TestCase):
    def test_instantiate(self):
        c = Container()
        self.assertTrue(isinstance(c, dict))

    def test_load_on_init(self):
        dct = {'a.b': 6}
        c = Container(dct)
        self.assertDictEqual(dct, c)

    def test_register_observer(self):
        c = Container()
        b = View_Mock()
        c.register_observer('a', b)
        self.assertIn(b, c._observers['a'])
        
    def test_update_observers(self):
        c = Container()
        b = View_Mock()
        c.register_observer('a', b)
        c.update_observers('a.test_key', 4)
        self.assertEqual(b.key, 'test_key')
        self.assertEqual(b.val, 4)    
    
    def test_dict_set_item(self):
        c = Container()
        c['a'] = 6

    def test_dict_get_item(self):
        c = Container()
        c['a'] = 6
        self.assertEqual(c['a'], 6)
        
    def test_set(self):
        c = Container()
        c.set('a.b', 6)
        self.assertEqual(c['a.b'], 6)

    def test_get(self):
        c = Container()
        c.set('a.b', 6)
        self.assertEqual(c.get('a.b'), 6)

    def test_lset(self):
        c = Container()
        c.lset(['a', 'b'], 6)
        expected = {'a.b': 6}
        self.assertDictEqual(c, expected)

    def test_lget(self):
        c = Container()
        c.lset(['a', 'b'], 6)
        self.assertEqual(c.lget(['a', 'b']), 6)
        
    def test_dset(self):
        c = Container()
        dct = {'a.b': 6}
        c.dset(dct)
        self.assertDictEqual(c, dct)
    
    def test_nest(self):
        c = Container()
        ret = c._nest(['a', 'b', 'c', 'd'], 5)
        expected = {'a': {'b': {'c': {'d': 5}}}}
        self.assertDictEqual(ret, expected)
        
    def test_nested(self):
        c = get_c()
        ret = c.nested()
        expected = {'a': {'b': 5},
                    'b': {'c': 7}}
        self.assertDictEqual(ret, expected)
        
    def test_load(self):
        c = Container()
        dct = {'a.b': 6}
        c.load(dct)
        self.assertDictEqual(dct, c)
        
    def test_refresh_observer_on_load(self):
        dct = {'a.b': 6}
        c = Container(dct)
        b = View_Mock()
        c.register_observer('a', b)
        dct2 = {'a.b': 7,
                'a.e': 45}
        c.load(dct2)
        self.assertEqual(b.refresh_val, True)

    def test_combine(self):
        d1 = {'b': 5}
        d2 = {'d': 7}
        c1 = Container(d1)
        c2 = Container(d2)
        c = Container.combine({'c1': c1, 'c2': c2})
        expected = {'c1.b': 5,
                    'c2.d': 7}
        self.assertEqual(c, expected)
        
    def test_merge(self):
        d1 = {'a.b': 5}
        d2 = {'c.d': 7}
        c1 = Container(d1)
        b1 = View_Mock()
        c1.register_observer('a', b1)
        c2 = Container(d2)
        b2 = View_Mock()
        c2.register_observer('c', b2)
        c = Container.merge([c1, c2])
        expected = {'a.b': 5,
                    'c.d': 7}
        self.assertEqual(c, expected)
        self.assertIn(b1, c._observers['a'])
        self.assertIn(b2, c._observers['c'])
        
    def test_context(self):
        dct = {'a.b': 6, 'a.c': 7}
        c = Container(dct)
        new1 = {'a.b': 66}
        new2 = {'a.c': 77}
        with c.context(new1):
            expected1 = {'a.b': 66, 'a.c': 7}
            self.assertDictEqual(c, expected1)
            with c.context(new2):
                expected2 = {'a.b': 66, 'a.c': 77}
                self.assertDictEqual(c, expected2)
            self.assertDictEqual(c, expected1)
        self.assertDictEqual(dct, c)