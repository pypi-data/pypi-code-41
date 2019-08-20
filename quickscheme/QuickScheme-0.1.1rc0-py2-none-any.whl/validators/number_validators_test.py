''' Unit Tests For SchemeNode '''

import logging
import unittest

from .number_validators import minmax_validator

from .string_validators_test import MockValue


class TestNumberValidators(unittest.TestCase):
    '''Number Validators tests'''

    def validate_all(self, validator, dataset):
        ''' Validate all in dataset against this validator '''
        for value, expected in dataset:
            self.assertEqual(validator(MockValue(value)), expected,
                             "Invalid result for value '%s', expected '%s'" % (value, expected))

    def test_minmax_validator_both(self):
        ''' Test Min/Max Validators '''
        validator = minmax_validator(min_value=1, max_value=10)
        self.validate_all(validator, [
            (1, True),
            (0, False),
            (-1, False),
            (10, True),
            (11, False)
        ])

    def test_minmax_validator_min(self):
        ''' Test Min/Max Validators '''
        validator = minmax_validator(min_value=1)
        self.validate_all(validator, [
            (1, True),
            (0, False),
            (-1, False),
            (10, True),
            (11, True)
        ])

    def test_minmax_validator_max(self):
        ''' Test Min/Max Validators '''
        validator = minmax_validator(max_value=10)
        self.validate_all(validator, [
            (1, True),
            (0, True),
            (-1, True),
            (10, True),
            (11, False)
        ])

    def test_minmax_validator_none(self):
        ''' Test Min/Max Validators '''
        validator = minmax_validator()
        self.validate_all(validator, [
            (1, True),
            (0, True),
            (-1, True),
            (10, True),
            (11, True)
        ])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
