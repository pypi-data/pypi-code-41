import unittest
from click.exceptions import  BadParameter
from .cli import validate_secret, validate_source, validate_destination


class TestValidateSecret(unittest.TestCase):
    def test_validate_secret(self):
        with self.assertRaises(BadParameter):
            validate_secret(None, None, '')

        actual = validate_secret(None, None, '12345')
        self.assertEqual('12345', actual)

    def test_validate_source(self):
        with self.assertRaises(BadParameter):
            validate_source(None, None, '')

        actual = validate_source(None, None, './users.csv')
        self.assertEqual('./users.csv', actual)

    def test_validate_destination(self):
        with self.assertRaises(BadParameter):
            validate_destination(None, None, '')

        with self.assertRaises(BadParameter):
            validate_destination(None, None, 'http://www.pleio.test')

        actual = validate_destination(None, None, 'http://localhost')
        self.assertEqual('http://localhost', actual)

        actual = validate_destination(None, None, 'https://www.pleio.test')
        self.assertEqual('https://www.pleio.test', actual)
