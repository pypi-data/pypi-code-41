import unittest

from ptscore.manager import Manager
from ptscore.storage.memorydb import MemoryDB


class TestManager(unittest.TestCase):

    def test_create_secret(self):
        manager = Manager(MemoryDB())
        plaintext = 'Lorem ipsum dolor sit amet'
        create_response = manager.create_secret(plaintext, 3600, False)
        self.assertEqual(len(create_response['secret_request_string']), 76, 'Secret Request String Not 76 Characters')
        self.assertEqual(len(create_response['wipe_request_string']), 76, 'Wipe Request String Not 76 Characters')

    def test_get_secret(self):
        manager = Manager(MemoryDB())
        plaintext = 'Lorem ipsum dolor sit amet'
        create_response = manager.create_secret(plaintext, 3600, False)
        get_response = manager.get_secret(create_response['secret_request_string'])
        # Test Secret Matches
        self.assertEqual(get_response['secret'], plaintext, 'Retrieved Secret Does Not Match Stored Secret')
        # Test Totally Wrong Secret Request String
        with self.assertRaises(ValueError) as e:
            manager.get_secret(create_response['secret_request_string'][::-1])
        self.assertEqual(type(e.exception).__name__, 'ValueError',
                         'Invalid Secret Request String (Reversed) Does Not Raise Error')
        # Test Secret Request String With Invalid UUID
        invalid_request = 'x' + create_response['secret_request_string'][1:]
        with self.assertRaises(ValueError) as e:
            manager.get_secret(invalid_request)
        self.assertEqual(type(e.exception).__name__, 'ValueError',
                         'Invalid Secret Request String (Invalid UUID) Does Not Raise Error')
        # Test Secret Request String With Invalid Fernet Key
        invalid_request = create_response['secret_request_string'][:-1] + '*'
        with self.assertRaises(ValueError) as e:
            manager.get_secret(invalid_request)
        self.assertEqual(type(e.exception).__name__, 'ValueError',
                         'Invalid Secret Request String (Invalid Fernet Key) Does Not Raise Error')

    def test_get_consumable_secret(self):
        manager = Manager(MemoryDB())
        plaintext = 'Lorem ipsum dolor sit amet'
        create_response = manager.create_secret(plaintext, 3600, True)
        get_response = manager.get_secret(create_response['secret_request_string'])
        self.assertEqual(get_response['secret'], plaintext)
        with self.assertRaises(LookupError):
            manager.get_secret(create_response['secret_request_string'])


if __name__ == '__main__':
    unittest.main()
