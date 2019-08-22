''' Unit Tests For Fields '''

import logging
import unittest

from quick_scheme.field import Field


class TestFields(unittest.TestCase):
    '''Field tests'''

    def test_field_name(self):
        ''' Test getting action_desc'''
        field = Field('test')
        self.assertEqual(field.name, 'test')

    def test_defaults(self):
        ''' Test Default Values '''
        field = Field('test')
        self.assertEqual(field.identity, False)
        self.assertEqual(field.has_default, False)
        self.assertEqual(field.default, '')
        self.assertEqual(field.required, False)
        self.assertEqual(field.ftype, Field.STR)
        self.assertEqual(field.always, True)

    def test_invalid_attr(self):
        ''' Test invalid attributes Values '''
        field = Field('test')
        with self.assertRaises(AttributeError) as _:
            _ignore = field.invalid_param
            value = True
            self.assertTrue(value, "This should never run")

    def test_set_values(self):
        ''' Test Default Values '''
        def_list = ['item']
        field = Field('test', identity=True, ftype=list,
                      default=def_list, required=True)

        self.assertEqual(field.identity, True)
        self.assertEqual(field.has_default, True)
        self.assertListEqual(field.default, def_list)
        self.assertEqual(field.required, True)
        self.assertEqual(field.ftype, list)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
