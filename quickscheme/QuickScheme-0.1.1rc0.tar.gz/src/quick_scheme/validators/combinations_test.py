''' Unit Tests For SchemeNode '''

import logging
import unittest

from .combinations import validate_all, validate_any

from .string_validators_test import MockValue


def false_validator(field_value):
    ''' Returns False '''
    return False


def true_validator(field_value):
    ''' Returns True '''
    return True


class TestValidatorCombinations(unittest.TestCase):
    '''String Validators tests'''

    def validate_dataset(self, validator_type, dataset):
        ''' Validate all in dataset against this validator '''
        for validator_list, expected in dataset:
            validator = validator_type(*validator_list)
            self.assertEqual(validator(MockValue("true")), expected,
                             "Invalid result for validator_list '%s', expected '%s'" % (
                                 validator_list, expected))

    def test_validate_all(self):
        ''' Test Validate All '''
        dataset = [
            ([], True),
            ([true_validator], True),
            ([true_validator, true_validator, true_validator], True),
            ([true_validator, true_validator, false_validator], False),
            ([false_validator, true_validator, false_validator], False),
            ([false_validator], False)
        ]
        self.validate_dataset(validate_all, dataset)

    def test_validate_any(self):
        ''' Test Validate All '''
        dataset = [
            ([], False),
            ([true_validator], True),
            ([true_validator, true_validator, true_validator], True),
            ([true_validator, true_validator, false_validator], True),
            ([false_validator, true_validator, false_validator], True),
            ([false_validator], False),
            ([false_validator, false_validator], False),
            ([false_validator, false_validator,  false_validator], False),
            ([false_validator, false_validator,  true_validator], True)
        ]
        self.validate_dataset(validate_any, dataset)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
