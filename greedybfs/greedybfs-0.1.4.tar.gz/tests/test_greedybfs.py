#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `greedybfs` package."""


import unittest

from greedybfs.greedybfs import gbfs


class TestGreedybfs(unittest.TestCase):
    """Tests for `greedybfs` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""
        test_graph = {
            "a": [['s',253], ['t', 329], ['z',374]],
            "s": [['f', 176], ['o', 380], ['r', 193]],
            "f": [['b', 0]]
        }
        assert gbfs('a','b',test_graph) == ['s', 'f', 'b']
