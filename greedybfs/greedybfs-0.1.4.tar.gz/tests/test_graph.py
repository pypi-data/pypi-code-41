#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from greedybfs.graph import Graph

class TestGraph(unittest.TestCase):
    """Tests for `greedybfs` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.grabh = Graph()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        # print(self.grabh.nodes)
        self.grabh = None

    # def test_000_something(self):
    #     """Test something."""
    #     test_graph = {grabh
    #         "a": [['s',253], ['t', 329], ['z',374]],
    #         "s": [['f', 176], ['o', 380], ['r', 193]],
    #         "f": [['b', 0]]
    #     }
    #     assert gbfs('a','b',test_graph) == ['s', 'f', 'b']

    def test_add_node(self):
        self.grabh.add_node('d')
        print(self.grabh.nodes)

    def test_add_edge_w_node(self):
        self.grabh.add_node('a')
        self.grabh.add_node('b')
        self.grabh.add_edge('a', 'b', 12)
        print(self.grabh.nodes)
        assert(self.grabh.get_edge('a', 'b') == 12)

    
    def test_add_edge_wo_node(self):
        self.grabh.add_edge('c', 'a', 20)
        self.assertRaises(AttributeError, self.grabh.get_edge, 'a', 'c')
        print(self.grabh.nodes)
        assert(self.grabh.get_edge('c', 'a') == 20)
    
    def test_delete_node(self):
        self.grabh.add_node('t_d_n_1')
        self.grabh.add_node('t_d_n_2')
        self.grabh.add_node('t_d_n_3')
        # before_nodes = self.grabh.nodes
        node_to_delete = 't_d_n_2'
        self.grabh.delete_node(node_to_delete)
        after_delete_nodes = self.grabh.nodes
        x = node_to_delete in after_delete_nodes
        print(x)
        assert(x == False)

    # delete node not in graph
    def test_delete_node_1(self):
        self.assertRaises(AttributeError, self.grabh.delete_node, 'random_node')

    def test_delete_edge(self):
        self.grabh.add_edge('b', 'a', 30)
        assert(self.grabh.get_edge('b', 'a') == 30)
        self.grabh.delete_edge('b', 'a')
        self.assertRaises(AttributeError, self.grabh.get_edge, 'b', 'a')
    
    # delete edge not in graph
    def test_delete_edge_(self):
        self.grabh.add_node('t_d_e_1')
        self.grabh.add_node('t_d_e_2')
        self.assertRaises(AttributeError, self.grabh.get_edge, 't_d_e_1', 't_d_e_2')
    
    # default update
    def update_edge(self):
        self.grabh.add_edge('u_e_1', 'u_e_2', 90)
        self.grabh.update_edge('u_e_1', 'u_e_2', 100)
        assert(self.grabh.get_edge('u_e_1', 'u_e_2') == 100)


    # update with weight not specifed
    def update_edge_1(self):
        self.grabh.add_edge('u_e_1', 'u_e_2', 90)
        self.grabh.update_edge('u_e_1', 'u_e_2')
        self.assertRaises(AttributeError, self.grabh.get_edge, 'u_e_1', 'u_e_2')

    
    # when edge is not in graph
    def update_edge_2(self):
        self.grabh.add_node('u_e_2_1')
        self.grabh.add_node('u_e_2_2')
        self.assertRaises(AttributeError, self.grabh.update_edge, 'u_e_2_1', 'u_e_2_2', 234)


    # when node is not in graph
    def update_edge_3(self):
        self.assertRaises(AttributeError, self.grabh.update_edge, 'random_1', 'random_2', 234)
    
    # when weight is not number
    def update_edge_4(self):
        self.grabh.add_node('u_e_4_1')
        self.grabh.add_node('u_e_4_2')
        self.assertRaises(AttributeError, self.grabh.update_edge, 'u_e_4_1', 'u_e_4_2', 'dfdsf')
