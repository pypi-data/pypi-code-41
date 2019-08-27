import os
import unittest
from .dict_reader import UserDictReader


class TestDictReader(unittest.TestCase):
    def setUp(self):
        self.source = os.path.join(os.path.dirname(__file__), '../fixtures/test_users.csv')

    def test_reader(self):
        with open(self.source) as file_source:
            reader = UserDictReader(file_source)
            rows = list(reader)

        firstRow = {
            'name': 'User 1',
            'email': 'user1@pleio.test',
            'external_id': 'pl-101',
            'avatar': 'avatar.jpg',
            'profile': {
                'location': 'Amsterdam',
                'occupation': 'Tester'
            }
        }

        secondRow = {
            'name': 'User 2',
            'email': 'user2@pleio.test',
            'external_id': 'pl-102',
            'avatar': 'missing_avatar.jpg',
            'profile': {
                'location': '',
                'occupation': 'Another tester'
        }}

        thirdRow = {
            'name': 'User 3',
            'email': 'user3@pleio.test',
            'external_id': 'pl-103',
            'avatar': '',
            'profile': {
                'location': '',
                'occupation': ''
        }}

        self.assertEqual(rows[0], firstRow)
        self.assertEqual(rows[1], secondRow)
        self.assertEqual(rows[2], thirdRow)
