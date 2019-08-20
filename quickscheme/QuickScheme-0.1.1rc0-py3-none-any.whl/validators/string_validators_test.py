''' Unit Tests For SchemeNode '''

import logging
import unittest

from .string_validators import ALPHANUM
from .string_validators import choice_validator, charset_validator, length_validator
from .string_validators import regex_validator, string_validator


class MockValue():
    ''' Mock Field Value '''

    def __init__(self, value):
        ''' set value '''
        self.value = value
        self.quick_scheme = self
        self.node = self

    def path_str(self):
        ''' path '''
        return ".mock.key"

    def name(self):
        ''' Get name '''
        return "MockValue"

    def get(self):
        ''' Return value '''
        return self.value


class TestStringValidators(unittest.TestCase):
    '''String Validators tests'''

    def validate_all(self, validator, dataset):
        ''' Validate all in dataset against this validator '''
        for value, expected in dataset:
            self.assertEqual(validator(MockValue(value)), expected,
                             "Invalid result for value '%s', expected '%s'" % (value, expected))

    def test_choice_validator_no_args(self):
        ''' Test String Choice Validators '''
        validator = choice_validator(one_of=None, not_one_of=None)
        self.validate_all(validator, [
            ('', True),
            (None, True),
            ("one", True),
            ("two", True)
        ])

    def test_choice_validator_one_of(self):
        ''' Test String Choice Validators '''
        validator = choice_validator(one_of=['one', ''], not_one_of=None)
        self.validate_all(validator, [
            ('', True),
            (None, False),
            ("one", True),
            ("two", False)
        ])

    def test_choice_validator_not_one_of(self):
        ''' Test String Choice Validators '''
        validator = choice_validator(not_one_of=['one', ''], one_of=None)
        self.validate_all(validator, [
            ('', False),
            (None, True),
            ("one", False),
            ("two", True)
        ])

    def test_choice_validator_both(self):
        ''' Test String Choice Validators '''
        validator = choice_validator(
            one_of=['one', ''], not_one_of=['two', ''])
        self.validate_all(validator, [
            ('', False),
            (None, False),
            ("one", True),
            ("two", False)
        ])

    def test_length_validator_both(self):
        ''' Test String Length Validators '''
        validator = length_validator(min_len=1, max_len=5)
        self.validate_all(validator, [
            ('', False),
            ("a", True),
            ("one", True),
            ("three", True),
            ("1234567890", False)
        ])

    def test_length_validator_min(self):
        ''' Test String Length Validators '''
        validator = length_validator(min_len=1)
        self.validate_all(validator, [
            ('', False),
            ("a", True),
            ("one", True),
            ("three", True),
            ("1234567890", True)
        ])

    def test_length_validator_max(self):
        ''' Test String Length Validators '''
        validator = length_validator(max_len=5)
        self.validate_all(validator, [
            ('', True),
            ("a", True),
            ("one", True),
            ("three", True),
            ("1234567890", False)
        ])

    def test_length_validator_none(self):
        ''' Test String Length Validators '''
        validator = length_validator()
        self.validate_all(validator, [
            ('', True),
            ("a", True),
            ("one", True),
            ("three", True),
            ("1234567890", True)
        ])

    def test_charset_validator_none(self):
        ''' Test String Charset Validators '''
        validator = charset_validator()
        self.validate_all(validator, [
            ('', True),
            ("a", True),
            ("one", True),
            ("three", True),
            ("1234567890", True)
        ])

    def test_charset_validator_start(self):
        ''' Test String Charset Validators '''
        validator = charset_validator(start_with="at23456789")
        self.validate_all(validator, [
            ('', True),
            ("a", True),
            ("one", False),
            ("three", True),
            ("1234567890", False)
        ])

    def test_charset_validator_full(self):
        ''' Test String Charset Validators '''
        validator = charset_validator(charset="atone23456789")
        self.validate_all(validator, [
            ('', True),
            ("a", True),
            ("one", True),
            ("three", False),
            ("1234567890", False)
        ])

    def test_charset_validator_both(self):
        ''' Test String Charset Validators '''
        validator = charset_validator(
            charset="atone23456789", start_with="anet23456789")
        self.validate_all(validator, [
            ('', True),
            ("a", True),
            ("one", False),
            ("three", False),
            ("1234567890", False)
        ])

    def test_regex_validator(self):
        ''' Test String Regex Validator '''
        validator = regex_validator(pattern="^[a-zA-Z0-9]*@[a-zA-Z.]+$")
        self.validate_all(validator, [
            ('', False),
            ("a", False),
            ("one", False),
            ("three", False),
            ("1234567890", False),
            ("@", False),
            ("a@", False),
            ("@a", True),
            ("one@domain.com", True),
            ("three@a", True),
            ("1234567890@", False),
            ("1234567890@1234567890", False),
            (None, False),
        ])

    def validate_string_validator(self, dataset):
        ''' Run validator tests '''
        for value, args, expected in dataset:
            validator = string_validator(**args)
            self.assertEqual(validator(MockValue(value)), expected,
                             "Invalid result for value '%s', expected '%s'" % (value, expected))

    def test_string_validator(self):
        ''' Test Unified String Validator '''
        dataset = [
            ("", dict(min_len=2, max_len=5), False),
            ("", dict(min_len=2, max_len=5, alt_choices=['*', '']), True),
            ("a", dict(min_len=2, max_len=5), False),
            ("z", dict(min_len=2, max_len=5,
                       alt_choices=['*', '']), False),

            ("", dict(min_len=2, max_len=5, one_of=["", "az"]), False),
            ("", dict(min_len=2, max_len=5, alt_choices=['*', '']), True),
            ("a", dict(min_len=2, max_len=5), False),
            ("z", dict(min_len=2, max_len=5, alt_choices=['*', '']), False),

            ("*", dict(min_len=2, max_len=5, alt_choices=['*', '']), True),
            ("az", dict(min_len=2, max_len=5, one_of=["", "az"]), True),
            ("az", dict(min_len=2, max_len=5, one_of=["", "ab"]), False),
            ("a1b2c3", dict(min_len=2, max_len=5,
                            alt_choices=['*', '']), False),
            ("a1b2c", dict(min_len=2, max_len=5,
                           alt_choices=['*', '']), True),

            ("*", dict(min_len=2, max_len=5, charset=ALPHANUM,
                       alt_choices=['*', '']), True),
            ("az", dict(min_len=2, max_len=5), True),
            ("a1b2c3", dict(min_len=2, max_len=5, charset=ALPHANUM,
                            alt_choices=['*', '']), False),
            ("a!b2c", dict(min_len=2, max_len=5, charset=ALPHANUM,
                           alt_choices=['*', '']), False),
            ("*", dict(min_len=2, max_len=5, charset=ALPHANUM,
                       alt_choices=['*', '']), True),


            ("*", dict(min_len=2, max_len=5, charset=ALPHANUM), False),
            ("***", dict(min_len=2, max_len=5, charset=ALPHANUM), False),
            ("az", dict(min_len=2, max_len=5), True),
            ("a1b2c3", dict(min_len=2, max_len=5, charset=ALPHANUM,
                            alt_choices=['*', '']), False),
            ("a!b2c", dict(min_len=2, max_len=5, charset=ALPHANUM,
                           alt_choices=['*', '']), False),
            ("*", dict(min_len=2, max_len=5, charset=ALPHANUM,
                       alt_choices=['*', '']), True),

            ("*", dict(charset=ALPHANUM), False),
            ("***", dict(charset=ALPHANUM), False),
            ("az", dict(), True),
            ("a1b2c3", dict(charset=ALPHANUM, alt_choices=['*', '']), True),
            ("a!b2c", dict(charset=ALPHANUM,
                           alt_choices=['*', '']), False),
            ("*", dict(charset=ALPHANUM, alt_choices=['*', '']), True),


            ("*", dict(charset=ALPHANUM), False),
            ("***", dict(charset=ALPHANUM), False),
            ("az", dict(), True),
            ("a1b2c3", dict(charset=ALPHANUM), True),
            ("a!b2c", dict(charset=ALPHANUM), False),
            ("*", dict(alt_choices=['*', '']), True),


            ("", dict(alt_choices=['*'], allow_blank=False), False),
            ("", dict(alt_choices=['*'], allow_blank=True), True),
            ("", dict(allow_blank=True), True),
            ("", dict(allow_blank=True, alt_choices=['*', '']), True),
            ("", dict(min_len=1, allow_blank=False), False),

        ]
        self.validate_string_validator(dataset)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
