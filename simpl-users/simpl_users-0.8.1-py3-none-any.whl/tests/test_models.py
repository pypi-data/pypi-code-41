from test_plus.test import TestCase

from .factories import UserFactory


class TestUser(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test__str__(self):
        self.assertEqual(
            self.user.__str__(),
            self.user.email,
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.user.get_absolute_url(),
            '/apis/users/{}/'.format(self.user.pk),
        )
