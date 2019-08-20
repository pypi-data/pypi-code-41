''' Unit Tests For SchemeNode '''

import logging
import unittest

from .base_node import ProxyAccess
from .nodes.node import SchemeNode


class MyEmptyNode(SchemeNode):
    ''' Empty Scheme Node '''


class TestProxyAccess(unittest.TestCase):
    '''ProxyAccess tests'''

    def test_proxy_access(self):
        ''' Test default proxy access'''
        node = MyEmptyNode(None, data={})
        proxy = ProxyAccess(node)
        self.assertEqual(proxy.name, "MyEmptyNode")

    def test_proxy_access_non_exist_silent(self):
        ''' Test silent error for non-existent'''
        node = MyEmptyNode(None, data={})
        proxy = ProxyAccess(node)
        self.assertIsNone(proxy.non_existent)

    def test_proxy_access_non_exist(self):
        ''' Test non-silent error for non-existent'''
        node = MyEmptyNode(None, data={})
        proxy = ProxyAccess(node, silent=False)
        with self.assertRaises(AttributeError) as ex:
            _ = proxy.non_existent
        self.assertEqual(
            "Failed to find attribute '_non_existent' in MyEmptyNode", str(ex.exception))

    def test_proxy_access_null_object_silent(self):
        ''' Test silent error for null'''
        proxy = ProxyAccess(None)
        self.assertIsNone(proxy.non_existent)

    def test_proxy_access_null_object_(self):
        ''' Test silent error for null'''
        proxy = ProxyAccess(None, silent=False)
        with self.assertRaises(AttributeError) as ex:
            self.assertIsNone(proxy.non_existent)
        self.assertEqual(
            "Failed to find attribute '_non_existent': No Object", str(ex.exception))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
