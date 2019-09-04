"""Tests for HOTP logic."""

from rest_framework.test import APITestCase

from rest_multi_factor.algorithms import HOTPAlgorithm
from rest_multi_factor.factories.user import UserFactory
from rest_multi_factor.factories.auth import AuthFactory
from rest_multi_factor.plugins.hotp.models import HOTPDevice


class VerificationTests(APITestCase):
    """Tests for HOTP verification implementation."""

    @classmethod
    def setUpTestData(cls):
        """Set up the test data within the test db."""
        cls.user = UserFactory()
        cls.auth = AuthFactory()

        cls.device = HOTPDevice.objects.create(user=cls.user)
        cls.relate = HOTPDevice.challenge.objects.create(
            device=cls.device, token=cls.auth
        )

        cls.algorithm = HOTPAlgorithm()

    def test_successful_verification(self):
        """Test the scenario's of a successful HOTP verification."""
        for i in (0, 1, 2):
            description = "HOTP not verified for `i={0}`".format(i)
            calculated = self.algorithm.calculate(self.device.secret, i)
            confirmed = self.relate.verify(calculated, save=False)

            self.assertTrue(confirmed, description)
            self.relate.confirm = False
            self.device.counter = 0

    def test_unsuccessful_verification(self):
        """Test the scenario's of a unsuccessful HOTP verification."""
        for i in (3, 4, 5):
            description = "HOTP verified for `i={0}`".format(i)
            calculated = self.algorithm.calculate(self.device.secret, i)
            confirmed = self.relate.verify(calculated, save=False)

            self.assertFalse(confirmed, description)
            self.device.counter = 0
