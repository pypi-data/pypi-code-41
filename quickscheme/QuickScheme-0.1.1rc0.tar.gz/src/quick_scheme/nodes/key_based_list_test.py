''' Unit Tests For SchemeNode '''

import json
import logging
import unittest

from quick_scheme.field import Field
from .key_based_list import KeyBasedList, KeyBasedListInst, KeyBasedListNode
from .node import SchemeNode


def clean_dict(data):
    ''' return clean version of a dict to compare '''
    if data is None:
        return data
    return json.dumps(data, sort_keys=True, indent=2)


class TestKeyBasedList(unittest.TestCase):
    '''Field tests'''

    def test_quick_key_based_list_creation(self):
        ''' Test class _name field '''
        for ltype in [int, Field.STR, dict, KeyBasedListNode]:
            kbl = KeyBasedList(item_type=ltype)
            self.assertEqual(kbl.TYPE, ltype)
            #self.assertIsInstance(kbl, KeyBasedListNode)
            self.assertTrue(issubclass(kbl, KeyBasedListNode))
            for preserve_order in [True, False]:
                kbl = KeyBasedListInst(
                    item_type=ltype, preserve_order=preserve_order)
                self.assertEqual(kbl.TYPE, ltype)
                self.assertEqual(kbl.PRESERVE_ORDER, preserve_order)

    def test_quick_key_based_list_values_dict(self):
        ''' test KeyBasedList values using dict '''
        data = {
            'test': {'one': 'one'},
            'test2': {'one': 'two'}
        }
        kbl = KeyBasedListInst(item_type=dict, data=data)
        self.assertDictEqual(kbl.quick_scheme.get_data(), data)

    def test_quick_key_based_list_values_open_node(self):
        ''' test KeyBasedList values using Open Node '''
        data_in = {
            'test': {
                'one': 'one'
            },
            'test2': {
                'one': 'two'
            }

        }
        data_out = {
            'test': {
                'id': 'test',
                'one': 'one'
            },
            'test2': {
                'id': 'test2',
                'one': 'two'
            }

        }

        class OpenNode(SchemeNode):
            ''' Test Open Node '''
            ALLOW_UNDEFINED = True
            FIELDS = [
                Field('id', identity=True, always=False),
                Field('data', brief=True, always=False),
            ]
        kbl = KeyBasedListInst(item_type=OpenNode, data=data_in)
        self.assertEqual(clean_dict(
            kbl.quick_scheme.get_data()), clean_dict(data_out))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
