import os
import unittest
from unittest.mock import Mock, ANY
from .worker import Worker

mockUser = {'email': 'test@test.com', 'name': 'Test'}
mockUserWithAvatar = {'email': 'test@test.com', 'name': 'Test', 'avatar': './avatar.jpg'}
mockInvalidUser = {'email': 'test@test.com'}

mockResponse = {'user': {'guid': '42', 'email': 'test@test.com', 'name': 'Test'}}

mockJob1 = ('UPDATE', mockUser, )
mockJob2 = ('STOP', mockUser, )


class TestWorker(unittest.TestCase):
    def setUp(self):
        self.queue = Mock()
        self.source = os.path.join(os.path.dirname(__file__), '../fixtures/test_users.csv')

        self.destination = Mock()
        self.queue.get = Mock(side_effect=[mockJob1, mockJob2])

        self.worker = Worker(self.queue, self.source, self.destination)

    def test_run(self):
        self.worker.run()
        self.assertEqual(self.queue.get.call_count, 2)

    def test_update_invalid_user(self):
        with self.assertLogs('pleio_profile_sync_client.worker', level='ERROR') as logger:
            actual = self.worker.update_user(mockInvalidUser)
            self.assertEqual(False, actual)
            self.assertEqual(logger.output, [
                'ERROR:pleio_profile_sync_client.worker:Skipping user, required fields: [guid, email]'
            ])

    def test_update_user(self):
        self.worker.update_user(mockUser)
        self.destination.post_user.assert_called_with(mockUser)
        self.destination.post_avatar.assert_not_called()

    def test_update_user_with_avatar(self):
        self.destination.post_user = Mock(return_value=mockResponse)
        self.worker.update_user(mockUserWithAvatar)

        self.destination.post_user.assert_called_with(mockUserWithAvatar)
        self.destination.post_avatar.assert_called_with('42', ANY)

    def test_ban_user(self):
        self.worker.ban_user({ 'guid': 42 })
        self.destination.ban_user.assert_called_with(42)
