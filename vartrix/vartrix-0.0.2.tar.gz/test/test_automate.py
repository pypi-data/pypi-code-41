# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 08:47:20 2019

@author: Reuben
"""

import os
import unittest

import ruamel.yaml as yml

from vartrix.container import Container
from vartrix.view import View
from vartrix.namespace import Name_Space
from vartrix import automate

base = {'alias.one': 5,
        'alias.two': 7,
        'alias.three': 11,
        'alias.four': 17}

namespace = Name_Space(Container)
container = namespace.get('test', base)

def get_c():
    f = namespace.get('test', base)
    return f

def set_csv_root():
    automate.set_root(os.path.dirname(os.path.abspath(__file__)))

def get_fname():
    root = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(root, 'automation_sets.yml')
    return fname    

def get_test_data():
    fname = get_fname()
    set_csv_root()
    with open(fname) as f:
        sets = yml.safe_load(f)
    return sets


class Automated():
    def __init__(self, set_name):
        dotkeys = ['alias']
        self.params = View(namespace.get('test'), dotkeys)
        self.set_name = set_name
        self.prepare_sequence_names = []
        self.finish_sequence_names = []
        self.prepare_method_names = []
        self.finish_method_names = []
        self.method_a_calls = []
        self.method_b_calls = []
        self.method_c_calls = []
        self.method_d_calls = []
        def get_methods_dct():
            return {'method_a': [], 'method_b': [], 'method_c': [], 'method_d': []}
        def get_dct():
            return {'seq_1': get_methods_dct(),
                    'seq_2': get_methods_dct(),
                    'seq_3': get_methods_dct(),
                    'seq_4': get_methods_dct()}
        self.alias_one_history = get_dct()
        self.alias_two_history = get_dct()
        self.alias_three_history = get_dct()
        self.alias_four_history = get_dct()
        
    def prepare(self):
        self.prepare = True

    def prepare_sequence(self, seq_name):
        self.prepare_sequence_names.append(seq_name)

    def prepare_method(self, method_name):
        self.prepare_method_names.append(method_name)

    def append_history(self, seq_name, method_name):
        self.alias_one_history[seq_name][method_name].append(self.params.one)
        self.alias_two_history[seq_name][method_name].append(self.params.two)
        self.alias_three_history[seq_name][method_name].append(self.params.three)
        self.alias_four_history[seq_name][method_name].append(self.params.four)

    def method_a(self, seq_name, val_dct, label_dct):
        self.method_a_calls.append({'val_dct': val_dct,
                                    'label_dct': label_dct})
        self.append_history(seq_name, 'method_a')

    def method_b(self, seq_name, val_dct, label_dct):
        self.method_b_calls.append({'val_dct': val_dct,
                                    'label_dct': label_dct})
        self.append_history(seq_name, 'method_b')

    def method_c(self, seq_name, val_dct, label_dct):
        self.method_c_calls.append({'val_dct': val_dct,
                                    'label_dct': label_dct})
        self.append_history(seq_name, 'method_c')
    
    def method_d(self, seq_name, val_dct, label_dct):
        self.method_d_calls.append({'val_dct': val_dct,
                                    'label_dct': label_dct})
        self.append_history(seq_name, 'method_d')

    def finish_method(self, method_name):
        self.finish_method_names.append(method_name)

    def finish_sequence(self, seq_name):
        self.finish_sequence_names.append(seq_name)

    def finish(self):
        self.finish = True


class Test_Automator(unittest.TestCase):
    def test_run_seq_1(self):
        container = get_c()
        fname = get_fname()
        set_csv_root()
        a = automate.Automator(container, fname)
        automated = Automated('set_1')
        a.run('set_1', automated)
        
        expected_one = {
            'seq_1': {
                'method_a': [0, 2, 3, 4],
                'method_b': [],
                'method_c': [],
                'method_d': []},
            'seq_2': {
                'method_a': [5, 5, 5, 5, 5, 5],
                'method_b': [0, 0, 0, 2, 2, 2, 3, 3, 3, 4, 4, 4],
                'method_c': [],
                'method_d': []},
            'seq_3': {
                'method_a': [],
                'method_b': [],
                'method_c': [0, 0, 2, 2, 3, 3, 4, 4],
                'method_d': []},
            'seq_4': {
                'method_a': [],
                'method_b': [],
                'method_c': [11, 13, 14, 11, 13, 14],
                'method_d': []}}
        self.assertDictEqual(automated.alias_one_history, expected_one)

        expected_two = {'seq_1': {'method_a': [7, 7, 7, 7], 'method_b': [], 'method_c': [], 'method_d': []}, 'seq_2': {'method_a': [2, 2, 3, 3, 4, 4], 'method_b': [2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4], 'method_c': [], 'method_d': []}, 'seq_3': {'method_a': [], 'method_b': [], 'method_c': [7, 7, 7, 7, 7, 7, 7, 7], 'method_d': []}, 'seq_4': {'method_a': [], 'method_b': [], 'method_c': [12, 14, 16, 12, 14, 16], 'method_d': []}}
        self.assertDictEqual(automated.alias_two_history, expected_two)

        expected_three = {'seq_1': {'method_a': [11, 11, 11, 11], 'method_b': [], 'method_c': [], 'method_d': []}, 'seq_2': {'method_a': [6, 6, 7, 7, 8, 8], 'method_b': [6, 7, 8, 6, 7, 8, 6, 7, 8, 6, 7, 8], 'method_c': [], 'method_d': []}, 'seq_3': {'method_a': [], 'method_b': [], 'method_c': [11, 11, 11, 11, 11, 11, 11, 11], 'method_d': []}, 'seq_4': {'method_a': [], 'method_b': [], 'method_c': [11, 11, 11, 11, 11, 11], 'method_d': []}}
        self.assertDictEqual(automated.alias_three_history, expected_three)

        expected_four = {'seq_1': {'method_a': [17, 17, 17, 17], 'method_b': [], 'method_c': [], 'method_d': []}, 'seq_2': {'method_a': [4, 5, 4, 5, 4, 5], 'method_b': [17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17], 'method_c': [], 'method_d': []}, 'seq_3': {'method_a': [], 'method_b': [], 'method_c': [4, 5, 4, 5, 4, 5, 4, 5], 'method_d': []}, 'seq_4': {'method_a': [], 'method_b': [], 'method_c': [4, 4, 4, 5, 5, 5], 'method_d': []}}
        self.assertDictEqual(automated.alias_four_history, expected_four)



class Test_Aliases(unittest.TestCase):
    pass


class Test_Vector(unittest.TestCase):
    def get_vec_1(self):
        d = {'labels': ['a', 'b'],
             'alias_1': [1, 2],
             'alias_2': [3, 4]}
        return automate.Vector_Factory.new(d, 'vec_1')
    
    def test_init_labelled(self):
        v = self.get_vec_1()
        expected = [{'alias_1': 1, 'alias_2': 3}, {'alias_1': 2, 'alias_2': 4}]
        self.assertListEqual(v.data, expected)
        self.assertListEqual(v.labels, ['a', 'b'])
        
    def test_get_lst_labelled(self):
        v = self.get_vec_1()
        lst = v.get_lst()
        self.assertListEqual(lst, [{'alias_1': 1, 'alias_2': 3},
                                   {'alias_1': 2, 'alias_2': 4}])

    def test_get_label_lst_labelled(self):
        v = self.get_vec_1()
        lst = v.get_label_lst()
        self.assertListEqual(lst, [{'vec_1': 'a'},
                                   {'vec_1': 'b'}])

    def get_vec_unlabelled(self):
        d = {'alias_1': [1, 2],
             'alias_2': [3, 4]}
        return automate.Vector_Factory.new(d, 'vec_unlabelled')
    
    def test_init_unlabelled(self):
        v = self.get_vec_unlabelled()
        expected = [{'alias_1': 1, 'alias_2': 3}, {'alias_1': 2, 'alias_2': 4}]
        self.assertListEqual(v.data, expected)
        self.assertListEqual(v.labels, [0, 1])
        
    def test_get_lst_unlabelled(self):
        v = self.get_vec_unlabelled()
        lst = v.get_lst()
        self.assertListEqual(lst, [{'alias_1': 1, 'alias_2': 3},
                                   {'alias_1': 2, 'alias_2': 4}])

    def test_get_label_lst_unlabelled(self):
        v = self.get_vec_unlabelled()
        lst = v.get_label_lst()
        self.assertListEqual(lst, [{'vec_unlabelled': 0},
                                   {'vec_unlabelled': 1}])


    def get_vec_2(self):
        d = {'labels': ['c', 'd'],
             'alias_3': [5, 6],
             'alias_4': [7, 8]}
        return automate.Vector_Factory.new(d, 'vec_2')
    
    def test_get_lst_nested(self):
        v = self.get_vec_1()
        v2 = self.get_vec_2()
        v.set_child(v2)
        lst = v.get_lst()
        expected = [
            {'alias_1': 1, 'alias_2': 3, 'alias_3': 5, 'alias_4': 7},
            {'alias_1': 1, 'alias_2': 3, 'alias_3': 6, 'alias_4': 8},
            {'alias_1': 2, 'alias_2': 4, 'alias_3': 5, 'alias_4': 7},
            {'alias_1': 2, 'alias_2': 4, 'alias_3': 6, 'alias_4': 8}]
        self.assertListEqual(lst, expected)

    def test_get_label_lst_nested(self):
        v = self.get_vec_1()
        v2 = self.get_vec_2()
        v.set_child(v2)
        lst = v.get_label_lst()
        expected = [{'vec_1': 'a', 'vec_2': 'c'},
                    {'vec_1': 'a', 'vec_2': 'd'},
                    {'vec_1': 'b', 'vec_2': 'c'},
                    {'vec_1': 'b', 'vec_2': 'd'}]
        self.assertListEqual(lst, expected)

    def test_csv(self):
        automate.root = os.path.dirname(os.path.abspath(__file__))
        dct = {'style': 'csv', 'filename': 'test_data.csv'}
        v = automate.Vector_Factory.new(dct, 'csv_vec')
        lst = v.get_lst()
        expected = [{'alias_1': 2, 'alias_2': 3},
                    {'alias_1': 5, 'alias_2': 7}]
        self.assertListEqual(lst, expected)
        expected = [{'csv_vec': 'row_one'},
                    {'csv_vec': 'row_two'}]
        lst = v.get_label_lst()
        


class Test_List_Vector(unittest.TestCase):
    def get_d_1(self):
        d = {'alias_1': [1, 2],
             'alias_2': [3, 4]}
        return d
    
    def test_transpose_dict(self):
        d = self.get_d_1()
        v = automate.List_Vector('test_name')
        d_test = v.transpose_dict(d)
        expected = [{'alias_1': 1, 'alias_2': 3}, {'alias_1': 2, 'alias_2': 4}]
        self.assertListEqual(d_test, expected)
    
    
class Test_Vectors(unittest.TestCase):
    def make_vectors(self):
        d = {'vec_1': {'labels': ['a', 'b'],
                       'alias_1': [1, 2],
                       'alias_2': [3, 4]},
             'vec_2': {'labels': ['c', 'd'],
                       'alias_3': [5, 6],
                       'alias_4': [7, 8]}}
        v = automate.Vectors(d)    
        return v
    
    def test_loop(self):
        v = self.make_vectors()
        val_lst, label_lst = v.loop(['vec_1', 'vec_2'])
        self.assertListEqual(val_lst, [{'alias_1': 1, 'alias_2': 3, 'alias_3': 5, 'alias_4': 7},
                                       {'alias_1': 1, 'alias_2': 3, 'alias_3': 6, 'alias_4': 8},
                                       {'alias_1': 2, 'alias_2': 4, 'alias_3': 5, 'alias_4': 7},
                                       {'alias_1': 2, 'alias_2': 4, 'alias_3': 6, 'alias_4': 8}])
        self.assertListEqual(label_lst, [{'vec_1': 'a', 'vec_2': 'c'},
                                         {'vec_1': 'a', 'vec_2': 'd'},
                                         {'vec_1': 'b', 'vec_2': 'c'},
                                         {'vec_1': 'b', 'vec_2': 'd'}])


class Test_Sequencer(unittest.TestCase):
    def get_s(self):
        all_data = get_test_data()
        data = all_data['set_1']
        s = automate.Sequencer(data['sequences'],
                               data['aliases'],
                               data['vectors'])
        return s
    
    def test_seq_1(self):
        s = self.get_s()
        sd = s.sequence('seq_1')
        expected = {'method_a': {'val_list':
                                    [{'alias.one': 0},
                                     {'alias.one': 2},
                                     {'alias.one': 3},
                                     {'alias.one': 4}],
                                'label_lst': 
                                    [{'vec_1': 0},
                                     {'vec_1': 1},
                                     {'vec_1': 2},
                                     {'vec_1': 3}]}}
        self.assertDictEqual(sd, expected)
        
    def test_seq_2(self):
        s = self.get_s()
        sd = s.sequence('seq_2')
        expected = {
            'method_b': {
                'val_list': [
                    {'alias.one': 0, 'alias.two': 2, 'alias.three': 6},
                    {'alias.one': 0, 'alias.two': 3, 'alias.three': 7},
                    {'alias.one': 0, 'alias.two': 4, 'alias.three': 8},
                    {'alias.one': 2, 'alias.two': 2, 'alias.three': 6},
                    {'alias.one': 2, 'alias.two': 3, 'alias.three': 7},
                    {'alias.one': 2, 'alias.two': 4, 'alias.three': 8},
                    {'alias.one': 3, 'alias.two': 2, 'alias.three': 6},
                    {'alias.one': 3, 'alias.two': 3, 'alias.three': 7},
                    {'alias.one': 3, 'alias.two': 4, 'alias.three': 8},
                    {'alias.one': 4, 'alias.two': 2, 'alias.three': 6},
                    {'alias.one': 4, 'alias.two': 3, 'alias.three': 7},
                    {'alias.one': 4, 'alias.two': 4, 'alias.three': 8}],
                'label_lst': [
                    {'vec_1': 0, 'vec_2': 'a'},
                    {'vec_1': 0, 'vec_2': 'b'},
                    {'vec_1': 0, 'vec_2': 'c'},
                    {'vec_1': 1, 'vec_2': 'a'},
                    {'vec_1': 1, 'vec_2': 'b'},
                    {'vec_1': 1, 'vec_2': 'c'},
                    {'vec_1': 2, 'vec_2': 'a'},
                    {'vec_1': 2, 'vec_2': 'b'},
                    {'vec_1': 2, 'vec_2': 'c'},
                    {'vec_1': 3, 'vec_2': 'a'},
                    {'vec_1': 3, 'vec_2': 'b'},
                    {'vec_1': 3, 'vec_2': 'c'}]}, 
            'method_a': {'val_list': [
                    {'alias.two': 2, 'alias.three': 6, 'alias.four': 4},
                    {'alias.two': 2, 'alias.three': 6, 'alias.four': 5},
                    {'alias.two': 3, 'alias.three': 7, 'alias.four': 4},
                    {'alias.two': 3, 'alias.three': 7, 'alias.four': 5},
                    {'alias.two': 4, 'alias.three': 8, 'alias.four': 4},
                    {'alias.two': 4, 'alias.three': 8, 'alias.four': 5}],
                'label_lst': [
                    {'vec_2': 'a', 'vec_3': 'four'},
                    {'vec_2': 'a', 'vec_3': 'five'},
                    {'vec_2': 'b', 'vec_3': 'four'},
                    {'vec_2': 'b', 'vec_3': 'five'},
                    {'vec_2': 'c', 'vec_3': 'four'},
                    {'vec_2': 'c', 'vec_3': 'five'}]}}
        self.assertDictEqual(sd, expected)
        
    
    def test_seq_3(self):
        s = self.get_s()
        sd = s.sequence('seq_3')
        expected = {
            'method_c': {
                'val_list': [
                    {'alias.one': 0, 'alias.four': 4},
                    {'alias.one': 0, 'alias.four': 5},
                    {'alias.one': 2, 'alias.four': 4},
                    {'alias.one': 2, 'alias.four': 5},
                    {'alias.one': 3, 'alias.four': 4},
                    {'alias.one': 3, 'alias.four': 5},
                    {'alias.one': 4, 'alias.four': 4},
                    {'alias.one': 4, 'alias.four': 5}],
                'label_lst': [
                    {'vec_1': 0, 'vec_3': 'four'},
                    {'vec_1': 0, 'vec_3': 'five'},
                    {'vec_1': 1, 'vec_3': 'four'},
                    {'vec_1': 1, 'vec_3': 'five'},
                    {'vec_1': 2, 'vec_3': 'four'},
                    {'vec_1': 2, 'vec_3': 'five'},
                    {'vec_1': 3, 'vec_3': 'four'},
                    {'vec_1': 3, 'vec_3': 'five'}]}}
        self.assertDictEqual(sd, expected)
        

    def test_seq_4(self):
        s = self.get_s()
        sd = s.sequence('seq_4')
        expected = {
            'method_c': {
                'val_list': [
                    {'alias.four': 4, 'alias.one': 11, 'alias.two': 12},
                    {'alias.four': 4, 'alias.one': 13, 'alias.two': 14},
                    {'alias.four': 4, 'alias.one': 14, 'alias.two': 16},
                    {'alias.four': 5, 'alias.one': 11, 'alias.two': 12},
                    {'alias.four': 5, 'alias.one': 13, 'alias.two': 14},
                    {'alias.four': 5, 'alias.one': 14, 'alias.two': 16}],
                'label_lst': [
                    {'vec_3': 'four', 'vec_4': 'a'},
                    {'vec_3': 'four', 'vec_4': 'b'},
                    {'vec_3': 'four', 'vec_4': 'c'},
                    {'vec_3': 'five', 'vec_4': 'a'},
                    {'vec_3': 'five', 'vec_4': 'b'},
                    {'vec_3': 'five', 'vec_4': 'c'}]}}
        self.assertDictEqual(sd, expected)