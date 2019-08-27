import os
import unittest
from .mapper import Mapper
from unittest.mock import Mock

mockDestinationUser1 = {'guid': '1', 'external_id': 'not-matching-pl-101', 'email': 'user1@pleio.test', 'name': 'User 1'}
mockDestinationUser2 = {'guid': '2', 'external_id': 'pl-102', 'email': 'user2@pleio.test', 'name': 'User 2'}
mockDestinationUser3 = {'guid': '3', 'external_id': None, 'email': 'user-not-in-list@pleio.test', 'name': 'To be banned'}


class TestMapper(unittest.TestCase):
    def setUp(self):
        self.source = os.path.join(os.path.dirname(__file__), '../fixtures/test_users.csv')

        self.destination = Mock()
        self.destination.get_users = Mock(return_value=[
            mockDestinationUser1,
            mockDestinationUser2,
            mockDestinationUser3
        ])

        self.mapper = Mapper(self.source, self.destination)

    def test_initialize(self):
        self.mapper.initialize()
        self.assertEqual(len(self.mapper.on_source['email'].keys()), 7)
        self.assertEqual(len(self.mapper.on_destination['email'].keys()), 3)

    def test_users_to_update(self):
        self.mapper.initialize()

        actual = [ u['email'] for u in self.mapper.users_to_update() ]

        expected = [
            'user1@pleio.test', 'user2@pleio.test', 'user3@pleio.test', 'user4@pleio.test',
            'user5@pleio.test', 'user6@pleio.test', 'user7@pleio.test'
        ]

        self.assertEqual(actual, expected)

        actual = list(self.mapper.users_to_update())

        self.assertEqual(actual[0].get('guid'), '1')
        self.assertEqual(actual[1].get('guid'), '2')
        self.assertEqual(actual[2].get('guid'), None)

    def test_users_to_ban(self):
        self.mapper.initialize()

        actual = list(self.mapper.users_to_ban())

        self.assertEqual(actual, [mockDestinationUser3])

    def test_count(self):
        self.mapper.initialize()

        actual = self.mapper.count()
        expected = {
            'source': 7,
            'destination': 3
        }

        self.assertEqual(actual, expected)
