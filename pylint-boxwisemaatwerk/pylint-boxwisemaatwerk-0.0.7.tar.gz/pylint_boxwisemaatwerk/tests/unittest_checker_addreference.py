"""
This file demonstrates common uses for the Python unittest module
https://docs.python.org/2/library/unittest.html
"""

import pytest
import unittest

import astroid
import sys
import pylint
from pylint.checkers import imports
from pylint.interfaces import UNDEFINED
from pylint.testutils import CheckerTestCase, Message, set_config

sys.path.insert(0, 'C:\dev\pylint-boxwisemaatwerk\pylint_boxwisemaatwerk')

import boxwise_plugin

class TestAddReference(CheckerTestCase):
    CHECKER_CLASS = boxwise_plugin.AddReferenceChecker

    def test_finds_ne_addreferences(self):
        node_a, node_b, node_c = astroid.extract_node("""
        clr.AddReference("Wms.RemotingImplementation")   #@
        clr.AddReference("Wms.RemotingObjects")   #@
        clr.AddReference("TranCon.Shared")        #@
        """)
        self.checker.visit_call(node_a)
        self.checker.visit_call(node_b)
        with self.assertAddsMessages(
            Message(
                msg_id='AddReference-cant-be-found',
                node=node_c,
                confidence=UNDEFINED
            ),
        ):
            self.checker.visit_call(node_c)

    def test_nonboxwise_addreference(self):
        node_a, node_b, node_c = astroid.extract_node("""
        clr.AddReference("System.Core")      #@
        clr.AddReference("Wms.RemotingImplementation")             #@
        clr.AddReference("Wms.RemotingObjects")             #@
        """)

        with self.assertNoMessages():
            self.checker.visit_call(node_a)
            self.checker.visit_call(node_b)
            self.checker.visit_call(node_c)


    def test_non_addreferencecalls(self):
        node_a, node_b, node_c = astroid.extract_node("""
        clr.AddReferenceToFile("TranCon.Deleted")                       #@
        RemotingImplementation.Updatebatch("TranCon.Deleted")           #@
        print 'trancon.ads'                                             #@
        """)

        with self.assertNoMessages():
            self.checker.visit_call(node_a)
            self.checker.visit_call(node_b)
            self.checker.visit_call(node_c)
